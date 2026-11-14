#!/usr/bin/env python3
"""Read-only release closure gate. Trusted receipts must come from verified adapters.

The gate checks evidence consistency, not provider authenticity. Never construct
trusted_context from the untrusted release manifest or from model assertions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Mapping
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from pairwise_release_binding import validate_pairwise_release_binding, certificate_pairwise_error
from carry_forward_release_binding import validate as validate_carry_forward_release_binding, certificate_error as carry_forward_certificate_error

STAGES = ("prepare_g12", "prepare_g13", "publish", "deploy", "close")
IDENTITY_FIELDS = {
    "source_commit": 40,
    "backlog_blob_sha": 40,
    "package_sha256": 64,
    "bom_sha256": 64,
}
READY = {"IMPLEMENTED_SELF_TESTED", "ALREADY_SATISFIED_SELF_TESTED"}
HISTORY = {"HISTORICAL_EVIDENCE_ONLY", "SUPERSEDED_WITH_SUCCESSOR_EVIDENCE"}
POST = {"POSTDEPLOY_REQUIRED", "POSTDEPLOY_OWNER_GATED"}
PROTECTED_IDS = frozenset("SF-G8-001 SF-G8-002 SF-G8-003 SF-G17-005 SF-G17-008 SF-G17-010 SF-G17-013 SF-G17-015 SF-G17-019 SF-G17-022 SF-G17-023 SF-G17-024 SF-G17-025 SF-G11-002 SF-G11-003 SF-XCUT-032 SF-G12-001 SF-G13-001 SF-G14-001 SF-G7-003 SF-G1-004 SF-G16-006 SF-G16-008".split())
SIMULATION_SURFACE = "OFFLINE_DETERMINISTIC_SIMULATION"
SIMULATION_RESULT = "PASS_BY_SIMULATION_WAIVER"
SIMULATION_WAIVER_SCOPE = "REFERENCE_SCOPE_STAGE30_SIMULATION_ACCEPTANCE"


def _json_default(value: Any) -> str:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    raise TypeError(f"Unsupported value type: {type(value).__name__}")


def digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=True, sort_keys=True,
                         separators=(",", ":"), allow_nan=False,
                         default=_json_default).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _refs(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_text(x) for x in value)


def _time(value: Any) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc) if parsed.tzinfo else None
    except (AttributeError, TypeError, ValueError):
        return None


def evaluate(stage: str, backlog: Mapping[str, Any], backlog_bytes: bytes,
             manifest: Mapping[str, Any], trusted_context: Mapping[str, Any]) -> dict[str, Any]:
    """Return a fail-closed decision; never mutate files or call external services.

    trusted_context is a separate verified-adapter input. A PASS only establishes
    consistency with that input, not a new G12/G13 certification or authorization.
    """
    if isinstance(manifest, Mapping) and manifest.get("release_policy") == "AUTONOMOUS_EVIDENCE_BASED":
        from autonomous_release import evaluate as evaluate_autonomous_release
        return evaluate_autonomous_release(stage, backlog, backlog_bytes, manifest, trusted_context)
    if stage in {'publish', 'deploy', 'close'}:
        destination = _mapping(_mapping(trusted_context).get('destination_observation'))
        if destination.get('verified') is not True or destination.get('visibility') != 'PRIVATE':
            return {'allowed': False, 'result': 'BLOCKED', 'errors': ['ACTUAL_PRIVATE_DESTINATION_REQUIRED_OR_USE_PUBLIC_V2_GATE']}
    # Historical strict profiles retain their original evidence semantics.
    errors: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    require(stage in STAGES, "UNKNOWN_STAGE")
    manifest = _mapping(manifest)
    trusted_context = _mapping(trusted_context)
    backlog = _mapping(backlog)
    simulation_waiver = _mapping(trusted_context.get("simulation_waiver"))
    simulation_waiver_allowed = (
        simulation_waiver.get("verified") is True
        and simulation_waiver.get("decision") == "ACCEPT"
        and simulation_waiver.get("scope") == SIMULATION_WAIVER_SCOPE
        and simulation_waiver.get("accepted_tag") == SIMULATION_RESULT
        and simulation_waiver.get("owner_approved") is True
        and _text(simulation_waiver.get("decision_ref"))
        and _text(simulation_waiver.get("req_018_evidence_ref"))
        and _text(simulation_waiver.get("req_040_evidence_ref"))
        and simulation_waiver.get("real_execution_performed") is False
    )
    # Owner PRIOR_RELEASE: a bounded private simulation acceptance profile, not a
    # production certificate. Keep every ordinary independence check intact.
    same_executor_simulation = (
        simulation_waiver_allowed
        and simulation_waiver.get("profile_id") == "SF3_SIMULATION_ACCEPTANCE_20261113"
        and simulation_waiver.get("same_executor_simulation_review") is True
        and simulation_waiver.get("live_production_certification_claimed") is False
        and _mapping(manifest.get("candidate")).get("acceptance_mode") == "SIMULATION_ONLY"
    )
    require(backlog.get("canonical") is True and
            backlog.get("backlog_id") == "INC_SKILLFORGE_UNIFIED_BACKLOG",
            "CANONICAL_BACKLOG_REQUIRED")
    mission = manifest.get("mission_id")
    require(_text(mission) and mission == trusted_context.get("mission_id"), "MISSION_MISMATCH")
    require(_text(manifest.get("implementation_actor_id")) and
            manifest.get("implementation_actor_id") == trusted_context.get("implementation_actor_id"),
            "IMPLEMENTATION_ACTOR_UNVERIFIED")
    approval_id = manifest.get("approval_id")
    approvals = _mapping(trusted_context.get("owner_approvals"))
    approval = _mapping(approvals.get(approval_id)) if _text(approval_id) else {}
    require(approval.get("verified") is True and approval.get("decision") == "APPROVE" and
            approval.get("mission_id") == mission and
            approval.get("source_kind") in {"OWNER_MESSAGE", "OWNER_SIGNED_APPROVAL"} and
            _text(approval.get("source_ref")) and
            _text(trusted_context.get("required_approval_gate_id")) and
            approval.get("gate_id") == trusted_context.get("required_approval_gate_id"),
            "OWNER_APPROVAL_NOT_VERIFIED")

    candidate = _mapping(manifest.get("candidate"))
    observed = _mapping(trusted_context.get("observed_candidate"))
    identity = {k: candidate.get(k) for k in IDENTITY_FIELDS}
    for key, length in IDENTITY_FIELDS.items():
        require(isinstance(identity[key], str) and
                re.fullmatch(r"[0-9a-f]{%d}" % length, identity[key]) is not None,
                f"INVALID_IDENTITY:{key}")
        require(identity[key] is not None and identity[key] == observed.get(key),
                f"OBSERVED_IDENTITY_MISMATCH:{key}")
    require(candidate.get("backlog_blob_sha") == git_blob_sha(backlog_bytes), "BACKLOG_BYTES_CHANGED")
    require(trusted_context.get("freeze_verified") is True, "FREEZE_NOT_VERIFIED")
    require(_text(trusted_context.get("observation_ref")), "OBSERVATION_REFERENCE_REQUIRED")
    errors.extend(validate_pairwise_release_binding(candidate, trusted_context))
    errors.extend(validate_carry_forward_release_binding(candidate, trusted_context))
    digest_payload = {"identity": identity, "ledger": manifest.get("ledger")}
    if candidate.get("pairwise_gate_required") is True:
        digest_payload["pairwise"] = {
            "matrix_sha256": candidate.get("pairwise_matrix_sha256"),
            "member_set_sha256": candidate.get("pairwise_member_set_sha256"),
        }
    if candidate.get("carry_forward_gate_required") is True:
        digest_payload["carry_forward"] = {
            "manifest_sha256": candidate.get("carry_forward_manifest_sha256"),
            "previous_snapshot_sha256": candidate.get("carry_forward_previous_snapshot_sha256"),
            "current_snapshot_sha256": candidate.get("carry_forward_current_snapshot_sha256"),
        }
    if candidate.get("operational_scope_mode") == "PRIVATE_V3_RISK_PROPORTIONAL":
        digest_payload["operational_impact_scope_sha256"] = candidate.get("impact_scope_sha256")
    candidate_digest = digest(digest_payload)

    items = backlog.get("items")
    if not isinstance(items, list) or not items:
        require(False, "BACKLOG_ITEMS_REQUIRED")
        items = []
    records: dict[str, Mapping[str, Any]] = {}
    for item in items:
        row = _mapping(item)
        cid = row.get("change_id")
        if not _text(cid):
            require(False, "INVALID_CHANGE_ID")
            continue
        require(cid not in records, f"DUPLICATE_CHANGE_ID:{cid}")
        records[cid] = row
    ledger_items = manifest.get("ledger")
    if not isinstance(ledger_items, list):
        require(False, "LEDGER_REQUIRED")
        ledger_items = []
    ledger: dict[str, Mapping[str, Any]] = {}
    for item in ledger_items:
        row = _mapping(item)
        cid = row.get("change_id")
        if not _text(cid):
            require(False, "INVALID_LEDGER_ID")
            continue
        require(cid not in ledger, f"DUPLICATE_LEDGER_ID:{cid}")
        ledger[cid] = row
    operational = _mapping(backlog.get("operational_release_scope_v3"))
    proportional = operational.get("scope_mode") == "PRIVATE_V3_RISK_PROPORTIONAL"
    if candidate.get("operational_scope_mode") == "PRIVATE_V3_RISK_PROPORTIONAL":
        require(proportional, "OPERATIONAL_SCOPE_REQUIRED")
    if proportional:
        require(candidate.get("operational_scope_mode") == "PRIVATE_V3_RISK_PROPORTIONAL",
                "OPERATIONAL_SCOPE_MANIFEST_OPT_IN_REQUIRED")
        require(operational.get("status") == "OWNER_DISPOSITIONS_FINALIZED",
                "OPERATIONAL_SCOPE_NOT_FINALIZED")
        require(operational.get("authority") == "OWNER_MANDATE",
                "OPERATIONAL_SCOPE_OWNER_AUTHORITY_REQUIRED")
        decisions = _mapping(operational.get("item_dispositions"))
        require(set(decisions) == set(records) and len(decisions) == operational.get("item_count"),
                "OPERATIONAL_SCOPE_161_COVERAGE_MISMATCH")
        counts = {"RETAIN_REQUIRED": 0, "RELAX_CONDITIONAL": 0,
                  "CANCEL_RELEASE_OBLIGATION": 0}
        for cid, record in records.items():
            d = _mapping(decisions.get(cid))
            action = d.get("disposition")
            require(action in counts, f"OPERATIONAL_SCOPE_INVALID_DECISION:{cid}")
            if action in counts:
                counts[action] += 1
            require(_text(d.get("rationale")) and len(d["rationale"]) >= 20,
                    f"OPERATIONAL_SCOPE_REASON_REQUIRED:{cid}")
            require(d.get("source_priority") == record.get("priority"),
                    f"OPERATIONAL_SCOPE_PRIORITY_DRIFT:{cid}")
            if action == "CANCEL_RELEASE_OBLIGATION":
                require(cid not in PROTECTED_IDS, f"RELEASE_CRITICAL_CANCELLATION_FORBIDDEN:{cid}")
                require(_text(d.get("mitigation")), f"OPERATIONAL_SCOPE_CANCELLATION_MITIGATION_REQUIRED:{cid}")
            elif action == "RELAX_CONDITIONAL":
                require(d.get("risk_control") == "HIGH_RISK_FAIL_CLOSED",
                        f"OPERATIONAL_SCOPE_RISK_CONTROL_REQUIRED:{cid}")
        require(counts == _mapping(operational.get("decision_counts")),
                "OPERATIONAL_SCOPE_COUNT_MISMATCH")
        retained = {cid for cid, d in decisions.items()
                    if _mapping(d).get("disposition") == "RETAIN_REQUIRED"}
        require(set(ledger) == retained, "OPERATIONAL_REQUIRED_LEDGER_COVERAGE_MISMATCH")
        require(_text(operational.get("stage1_evidence_ref")),
                "OPERATIONAL_STAGE1_EVIDENCE_REQUIRED")
        impact = _mapping(trusted_context.get("impact_scope"))
        digest_value = candidate.get("impact_scope_sha256")
        require(isinstance(digest_value, str) and re.fullmatch(r"[0-9a-f]{64}", digest_value) is not None,
                "OPERATIONAL_IMPACT_DIGEST_REQUIRED")
        require(impact.get("verified") is True and impact.get("result") == "PASS"
                and impact.get("impact_scope_sha256") == digest_value
                and impact.get("bom_sha256") == candidate.get("bom_sha256")
                and impact.get("changed_critical_paths_covered") is True
                and impact.get("security_negative_tests_pass") is True
                and impact.get("prior_active_contracts_reconciled") is True
                and impact.get("unresolved_release_critical_count") == 0,
                "OPERATIONAL_IMPACT_EVIDENCE_NOT_VERIFIED")
    else:
        retained = set(records)
        require(set(ledger) == set(records), "LEDGER_COVERAGE_MISMATCH")
    scope = _mapping(_mapping(backlog.get("current_release_selection")).get("selection_scope"))
    def selected(key: str) -> set[str]:
        values = scope.get(key, [])
        require(isinstance(values, list) and all(_text(x) for x in values), f"INVALID_SELECTION:{key}")
        return set(values) if isinstance(values, list) and all(_text(x) for x in values) else set()
    post_required = selected("post_deploy_before_project_close") & retained
    post_owner = selected("post_deploy_owner_gated_nonrelease_operation") & retained
    require(not (post_required & post_owner), "AMBIGUOUS_POSTDEPLOY_SELECTION")
    require((post_required | post_owner) <= set(records), "POSTDEPLOY_SELECTION_UNKNOWN_ID")

    for cid, record in records.items():
        if cid not in retained:
            continue
        row = ledger.get(cid, {})
        disposition = row.get("disposition")
        require(row.get("record_sha256") == digest(record), f"STALE_RECORD_EVIDENCE:{cid}")
        require(_refs(row.get("evidence_refs")), f"EVIDENCE_REQUIRED:{cid}")
        if same_executor_simulation and disposition == "SIMULATION_REVIEWED":
            require(row.get("acceptance_mode") == "SIMULATION_ONLY"
                    and row.get("contract_review_complete") is True
                    and row.get("native_execution_claimed") is False
                    and row.get("independent_actor_claimed") is False
                    and _refs(row.get("test_refs"))
                    and row.get("assessment_kind") in {"CONTRACT_SIMULATION_ESTIMATE", "EXECUTED_SYNTHETIC_TEST"},
                    f"SIMULATION_ASSESSMENT_NOT_VERIFIED:{cid}")
            continue
        require(disposition in READY | HISTORY | POST, f"OPEN_OR_INVALID_DISPOSITION:{cid}")
        if disposition in READY | POST:
            require(row.get("self_tests_pass") is True and _refs(row.get("test_refs")),
                    f"SELF_TEST_EVIDENCE_REQUIRED:{cid}")
        if disposition == "HISTORICAL_EVIDENCE_ONLY":
            require(str(record.get("status", "")).startswith("HISTORICAL"), f"FALSE_HISTORICAL:{cid}")
        if disposition == "SUPERSEDED_WITH_SUCCESSOR_EVIDENCE":
            require(str(record.get("status", "")).startswith("SUPERSEDED") and
                    _text(row.get("successor_ref")), f"FALSE_SUPERSESSION:{cid}")
        if disposition == "POSTDEPLOY_REQUIRED":
            require(cid in post_required and row.get("contract_ready") is True,
                    f"UNQUALIFIED_POSTDEPLOY:{cid}")
        if disposition == "POSTDEPLOY_OWNER_GATED":
            require(cid in post_owner and row.get("contract_ready") is True and
                    row.get("live_operation_executed") is False,
                    f"UNQUALIFIED_OWNER_GATED_OPERATION:{cid}")
        if cid in post_owner:
            require(disposition == "POSTDEPLOY_OWNER_GATED", f"OWNER_GATE_MUST_REMAIN_EXPLICIT:{cid}")
        if cid in post_required:
            require(disposition == "POSTDEPLOY_REQUIRED", f"POSTDEPLOY_REVIEW_MUST_REMAIN_EXPLICIT:{cid}")

    executions = trusted_context.get("required_execution_evidence")
    require(isinstance(executions, list) and bool(executions),
            "REQUIRED_EXECUTION_EVIDENCE_MISSING")
    names: set[str] = set()
    local_surfaces = {"CODEX_LOCAL", "CODEX_WINDOWS_LOCAL"}
    if isinstance(executions, list):
        for value in executions:
            evidence = _mapping(value)
            name = evidence.get("name")
            require(_text(name), "INVALID_EXECUTION_NAME")
            if _text(name):
                require(name not in names, f"DUPLICATE_EXECUTION:{name}")
                names.add(name)
            require(evidence.get("conclusion") == "success" and
                    evidence.get("source_commit") == candidate.get("source_commit") and
                    _text(evidence.get("evidence_ref")),
                    f"REQUIRED_EXECUTION_NOT_PASS:{name}")
            surface = evidence.get("execution_surface")
            if surface == SIMULATION_SURFACE:
                require(simulation_waiver_allowed, f"SIMULATION_WAIVER_REQUIRED:{name}")
                require(evidence.get("simulation_waiver_ref") ==
                        simulation_waiver.get("decision_ref"),
                        f"SIMULATION_WAIVER_REFERENCE_INVALID:{name}")
            else:
                require(surface in local_surfaces,
                        f"EXECUTION_SURFACE_NOT_LOCAL:{name}")
            report_sha256 = evidence.get("report_sha256")
            require(isinstance(report_sha256, str) and
                    re.fullmatch(r"[0-9a-f]{64}", report_sha256) is not None,
                    f"EXECUTION_REPORT_DIGEST_INVALID:{name}")

    expected_executions = trusted_context.get("required_execution_names")
    require(isinstance(expected_executions, list) and bool(expected_executions) and
            all(_text(x) for x in expected_executions),
            "REQUIRED_EXECUTION_POLICY_MISSING")
    if isinstance(expected_executions, list) and all(_text(x) for x in expected_executions):
        require(len(expected_executions) == len(set(expected_executions)) and
                names == set(expected_executions),
                "REQUIRED_EXECUTION_SET_MISMATCH")

    certificates = _mapping(trusted_context.get("certificates"))
    requested = _mapping(manifest.get("certification_refs"))
    def certificate(role: str) -> Mapping[str, Any]:
        rid = requested.get(role)
        receipt = _mapping(certificates.get(rid)) if _text(rid) else {}
        normal_certificate = (
            receipt.get("result") == "PASS" and
            receipt.get("independence_verified") is True
        )
        simulation_certificate = (
            receipt.get("result") == SIMULATION_RESULT and
            receipt.get("independence_verified") is False and
            simulation_waiver_allowed and
            receipt.get("simulation_waiver_ref") == simulation_waiver.get("decision_ref")
        )
        require(receipt.get("role") == role and
                receipt.get("verified") is True and
                (normal_certificate or simulation_certificate) and
                receipt.get("candidate_digest") == candidate_digest and
                _text(receipt.get("actor_id")) and _text(receipt.get("evidence_ref")) and
                _time(receipt.get("completed_at")) is not None,
                f"CERTIFICATION_NOT_VERIFIED:{role}")
        require((same_executor_simulation and simulation_certificate) or
                receipt.get("actor_id") != manifest.get("implementation_actor_id"),
                f"SELF_CERTIFICATION:{role}")
        pairwise_error = certificate_pairwise_error(candidate, receipt, role)
        if pairwise_error:
            require(False, pairwise_error)
        carry_error = carry_forward_certificate_error(candidate, receipt, role)
        if carry_error:
            require(False, carry_error)
        if candidate.get("operational_scope_mode") == "PRIVATE_V3_RISK_PROPORTIONAL":
            require(receipt.get("impact_scope_sha256") == candidate.get("impact_scope_sha256"),
                    f"OPERATIONAL_IMPACT_CERTIFICATE_MISMATCH:{role}")
        return receipt

    g12: Mapping[str, Any] = {}
    if stage in {"prepare_g13", "publish", "deploy", "close"}:
        g12 = certificate("G12")
    if stage in {"publish", "deploy", "close"}:
        g13 = certificate("G13")
        require((same_executor_simulation and g12.get("result") == SIMULATION_RESULT
                 and g13.get("result") == SIMULATION_RESULT
                 and g12.get("independence_verified") is False
                 and g13.get("independence_verified") is False)
                or g13.get("actor_id") != g12.get("actor_id"), "G13_NOT_INDEPENDENT_OF_G12")
        t12, t13 = _time(g12.get("completed_at")), _time(g13.get("completed_at"))
        require(t12 is not None and t13 is not None and t13 >= t12, "CERTIFICATION_ORDER_INVALID")

    def external_receipt(name: str) -> Mapping[str, Any]:
        receipt = _mapping(trusted_context.get(name))
        normal_receipt = receipt.get("result") == "PASS"
        simulation_receipt = (
            receipt.get("result") == SIMULATION_RESULT and
            simulation_waiver_allowed and
            receipt.get("simulation_waiver_ref") == simulation_waiver.get("decision_ref")
        )
        require(receipt.get("verified") is True and
                (normal_receipt or simulation_receipt) and
                receipt.get("candidate_digest") == candidate_digest and
                receipt.get("package_sha256") == candidate.get("package_sha256") and
                _text(receipt.get("evidence_ref")) and _time(receipt.get("completed_at")) is not None,
                f"EXTERNAL_RECEIPT_NOT_VERIFIED:{name}")
        return receipt

    if stage in {"deploy", "close"}:
        publication = external_receipt("publication")
        ptime = _time(publication.get("completed_at"))
        g13time = _time(_mapping(certificates.get(requested.get("G13", ""))).get("completed_at"))
        require(ptime is not None and g13time is not None and ptime >= g13time, "PUBLICATION_ORDER_INVALID")
    if stage == "close":
        deployment = external_receipt("deployment")
        installation = external_receipt("installation")
        dtime = _time(deployment.get("completed_at"))
        itime = _time(installation.get("completed_at"))
        ptime = _time(_mapping(trusted_context.get("publication")).get("completed_at"))
        require(ptime is not None and dtime is not None and itime is not None and
                ptime <= dtime <= itime, "DEPLOY_INSTALL_ORDER_INVALID")
        require(_text(installation.get("target_surface")) and
                installation.get("target_surface") == trusted_context.get("required_install_surface"),
                "INSTALL_SURFACE_NOT_VERIFIED")
        require(_text(deployment.get("rollback_ref")), "ROLLBACK_REFERENCE_REQUIRED")
        reviews = _mapping(trusted_context.get("postdeploy_reviews"))
        for cid in post_required:
            review = _mapping(reviews.get(cid))
            rtime = _time(review.get("completed_at"))
            require(review.get("verified") is True and (review.get("result") == "PASS" or (same_executor_simulation and review.get("result") == SIMULATION_RESULT and review.get("simulation_waiver_ref") == simulation_waiver.get("decision_ref"))) and
                    review.get("candidate_digest") == candidate_digest and
                    _text(review.get("evidence_ref")) and dtime is not None and
                    rtime is not None and rtime >= dtime, f"POSTDEPLOY_REVIEW_MISSING:{cid}")
        require(trusted_context.get("handoff_readback_verified") is True and
                _text(trusted_context.get("handoff_ref")), "HANDOFF_READBACK_REQUIRED")
    return {
        "contract": "INC_G0_RELEASE_CLOSURE_GATE_V1",
        "stage": stage,
        "allowed": not errors,
        "result": ("SIMULATION_ACCEPTANCE_PASS" if same_executor_simulation else "CONSISTENCY_PASS") if not errors else "BLOCKED",
        "genuine_independent_certification": False if same_executor_simulation else None,
        "real_host_installation_claimed": False if same_executor_simulation else None,
        "candidate_digest": candidate_digest,
        "backlog_records": len(records),
        "ledger_records": len(ledger),
        "operational_scope_mode": candidate.get("operational_scope_mode"),
        "active_release_required_records": len(retained),
        "errors": sorted(set(errors)),
        "simulation_waiver_applied": simulation_waiver_allowed,
        "simulation_waiver_scope": simulation_waiver.get("scope") if simulation_waiver_allowed else None,
        "simulation_waiver_tag": simulation_waiver.get("accepted_tag") if simulation_waiver_allowed else None,
        "trust_boundary": "VERIFIED_ADAPTER_INPUT_REQUIRED_NOT_AUTHENTICATED_BY_THIS_SCRIPT",
        "authorizes_real_secret_operations": False,
    }


def load_json(path: Path) -> Any:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError("Non-finite JSON number")))


def load_backlog(path: Path) -> tuple[Mapping[str, Any], bytes]:
    import yaml
    class UniqueSafeLoader(yaml.SafeLoader):
        pass
    def unique(loader: Any, node: Any, deep: bool = False) -> dict[Any, Any]:
        loader.flatten_mapping(node)
        result: dict[Any, Any] = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if key in result:
                raise ValueError(f"Duplicate YAML key: {key}")
            result[key] = loader.construct_object(value_node, deep=deep)
        return result
    UniqueSafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique)
    data = path.read_bytes()
    parsed = yaml.load(data.decode("utf-8"), Loader=UniqueSafeLoader)
    if not isinstance(parsed, Mapping):
        raise ValueError("Backlog must be a mapping")
    return parsed, data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=STAGES, required=True)
    parser.add_argument("--backlog", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--trusted-context", type=Path, required=True)
    args = parser.parse_args()
    try:
        backlog, data = load_backlog(args.backlog)
        result = evaluate(args.stage, backlog, data, load_json(args.manifest), load_json(args.trusted_context))
    except Exception as exc:
        # Do not echo input payloads, credentials, YAML contents or provider errors.
        result = {"allowed": False, "result": "BLOCKED", "errors": ["INPUT_INVALID"],
                  "error_type": type(exc).__name__}
    print(json.dumps(result, sort_keys=True, ensure_ascii=True, indent=2))
    return 0 if result["allowed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
