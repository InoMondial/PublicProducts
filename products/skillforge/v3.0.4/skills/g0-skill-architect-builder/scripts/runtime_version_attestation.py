#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone

CONTRACT = "INC_SKILLFORGE_RUNTIME_VERSION_ATTESTATION_V1"
ALLOWED_SURFACES = {"Chat", "Work", "Codex"}
ALLOWED_PROOF_SOURCES = {
    "CHAT_RUNTIME_PACKAGE_METADATA",
    "WORK_RUNTIME_PACKAGE_METADATA",
    "CODEX_INSTALLED_PACKAGE_INSPECTION",
    "HOST_RUNTIME_PACKAGE_METADATA",
    "HOST_PLUGIN_RUNTIME_STATUS",
}
FORBIDDEN_PROOF_SOURCES = {"HANDOFF", "GITHUB_SOURCE_ONLY", "USER_CLAIM", "ASSISTANT_INFERENCE"}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)

class AttestationError(ValueError):
    pass

def require(ok, code):
    if not ok:
        raise AttestationError(code)

def nonempty(v):
    return isinstance(v, str) and bool(v.strip())

def _semver(v):
    m = SEMVER.fullmatch(v or "")
    require(bool(m), "RUNTIME_ATTESTATION_VERSION_INVALID")
    core = tuple(int(x) for x in m.group(1, 2, 3))
    pre = None if m.group(4) is None else tuple(m.group(4).split("."))
    if pre:
        for ident in pre:
            require(not (ident.isdigit() and len(ident) > 1 and ident.startswith("0")), "RUNTIME_ATTESTATION_VERSION_INVALID")
    return core, pre

def _compare_ident(a, b):
    an, bn = a.isdigit(), b.isdigit()
    if an and bn:
        ai, bi = int(a), int(b)
        return (ai > bi) - (ai < bi)
    if an != bn:
        return -1 if an else 1
    return (a > b) - (a < b)

def compare_semver(a, b):
    ac, ap = _semver(a); bc, bp = _semver(b)
    if ac != bc:
        return (ac > bc) - (ac < bc)
    if ap is None and bp is None:
        return 0
    if ap is None:
        return 1
    if bp is None:
        return -1
    for x, y in zip(ap, bp):
        c = _compare_ident(x, y)
        if c:
            return c
    return (len(ap) > len(bp)) - (len(ap) < len(bp))

def at_least(observed, required):
    return compare_semver(observed, required) >= 0

def digest_obj(v):
    raw = json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(raw).hexdigest()

def context_fingerprint(ctx):
    fields = [ctx.get("surface"), ctx.get("runtime_instance_id"), ctx.get("account_context_fingerprint"), ctx.get("session_fingerprint")]
    require(all(nonempty(x) for x in fields), "RUNTIME_ATTESTATION_CONTEXT_REQUIRED")
    return hashlib.sha256(json.dumps(fields, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()

def _parse_time(value):
    require(nonempty(value), "RUNTIME_ATTESTATION_PROOF_TIMESTAMP_REQUIRED")
    try:
        dt = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except Exception as exc:
        raise AttestationError("RUNTIME_ATTESTATION_PROOF_TIMESTAMP_INVALID") from exc
    require(dt.tzinfo is not None and dt.utcoffset() is not None, "RUNTIME_ATTESTATION_PROOF_TIMESTAMP_TIMEZONE_REQUIRED")
    return dt.astimezone(timezone.utc)

def _now(now):
    if now is None:
        return datetime.now(timezone.utc)
    if isinstance(now, datetime):
        require(now.tzinfo is not None and now.utcoffset() is not None, "RUNTIME_ATTESTATION_VALIDATION_TIME_TIMEZONE_REQUIRED")
        return now.astimezone(timezone.utc)
    return _parse_time(now)

def _validate_freshness(evidence, required, mismatches, now):
    proof_time = _parse_time(evidence.get("proof_timestamp"))
    freshness = required.get("attestation_freshness_seconds", 900)
    future_skew = required.get("attestation_max_future_skew_seconds", 60)
    require(type(freshness) is int and freshness > 0, "RUNTIME_ATTESTATION_FRESHNESS_WINDOW_INVALID")
    require(type(future_skew) is int and future_skew >= 0, "RUNTIME_ATTESTATION_FUTURE_SKEW_INVALID")
    age = (now - proof_time).total_seconds()
    if age > freshness:
        mismatches.append("runtime_evidence:stale")
    if age < -future_skew:
        mismatches.append("runtime_evidence:future_dated")
    return proof_time

def _validate_allowlist(values, code, mismatch_code, observed_digest, mismatches):
    require(isinstance(values, list), code + "_INVALID")
    require(all(isinstance(x, str) and bool(HEX64.fullmatch(x)) for x in values), code + "_ENTRY_INVALID")
    if not values:
        mismatches.append(mismatch_code + (":allowed_package_digests_empty" if mismatch_code == "skillforge" else ":allowed_digests_empty"))
    elif observed_digest not in values:
        mismatches.append(mismatch_code + ":digest_not_allowed")

def _validate_component(name, observed, required, mismatches):
    ov = observed.get(name)
    rv = required.get(name)
    require(isinstance(ov, dict) and isinstance(rv, dict), f"RUNTIME_ATTESTATION_{name.upper()}_REQUIRED")
    require(nonempty(ov.get("version")) and nonempty(rv.get("min_version")), f"RUNTIME_ATTESTATION_{name.upper()}_VERSION_REQUIRED")
    if not at_least(ov["version"], rv["min_version"]):
        mismatches.append(f"{name}:version_below_minimum")
    require(nonempty(ov.get("digest")) and bool(HEX64.fullmatch(ov["digest"])), f"RUNTIME_ATTESTATION_{name.upper()}_DIGEST_INVALID")
    _validate_allowlist(
        rv.get("allowed_digests"),
        f"RUNTIME_ATTESTATION_{name.upper()}_ALLOWED_DIGESTS",
        name,
        ov["digest"],
        mismatches,
    )

def validate_attestation(payload, now=None):
    require(isinstance(payload, dict), "RUNTIME_ATTESTATION_PAYLOAD_REQUIRED")
    require(payload.get("contract") == CONTRACT, "RUNTIME_ATTESTATION_CONTRACT_MISMATCH")
    mode = payload.get("mode")
    require(mode in {"MATERIAL", "READ_ONLY_AUDIT"}, "RUNTIME_ATTESTATION_MODE_INVALID")

    current = payload.get("current_context")
    observed_ctx = payload.get("observed_context")
    require(isinstance(current, dict) and isinstance(observed_ctx, dict), "RUNTIME_ATTESTATION_CONTEXT_REQUIRED")
    require(current.get("surface") in ALLOWED_SURFACES, "RUNTIME_ATTESTATION_SURFACE_INVALID")
    current_fp = context_fingerprint(current)
    observed_fp = context_fingerprint(observed_ctx)

    evidence = payload.get("runtime_evidence")
    require(isinstance(evidence, dict), "RUNTIME_ATTESTATION_RUNTIME_EVIDENCE_REQUIRED")
    proof_source = evidence.get("proof_source")
    require(proof_source not in FORBIDDEN_PROOF_SOURCES, "RUNTIME_ATTESTATION_FORBIDDEN_PROOF_SOURCE")
    require(proof_source in ALLOWED_PROOF_SOURCES, "RUNTIME_ATTESTATION_PROOF_SOURCE_UNVERIFIED")
    require(nonempty(evidence.get("proof_ref")), "RUNTIME_ATTESTATION_PROOF_REF_REQUIRED")
    require(evidence.get("readback_verified") is True, "RUNTIME_ATTESTATION_RUNTIME_READBACK_REQUIRED")

    handoff = payload.get("handoff_evidence")
    require(isinstance(handoff, dict), "RUNTIME_ATTESTATION_HANDOFF_EVIDENCE_REQUIRED")
    require(handoff.get("readback_verified") is True, "RUNTIME_ATTESTATION_HANDOFF_READBACK_REQUIRED")
    require(nonempty(handoff.get("provider_revision")), "RUNTIME_ATTESTATION_HANDOFF_PROVIDER_REVISION_REQUIRED")
    require(nonempty(handoff.get("visible_ref")), "RUNTIME_ATTESTATION_HANDOFF_VISIBLE_REF_REQUIRED")

    observed = payload.get("installed")
    required = payload.get("required")
    require(isinstance(observed, dict) and isinstance(required, dict), "RUNTIME_ATTESTATION_VERSION_PROFILE_REQUIRED")
    require(nonempty(observed.get("skillforge_version")), "RUNTIME_ATTESTATION_SKILLFORGE_VERSION_REQUIRED")
    require(nonempty(required.get("skillforge_min_version")), "RUNTIME_ATTESTATION_REQUIRED_SKILLFORGE_VERSION_REQUIRED")
    require(nonempty(observed.get("package_digest")) and bool(HEX64.fullmatch(observed["package_digest"])), "RUNTIME_ATTESTATION_PACKAGE_DIGEST_INVALID")
    require(nonempty(required.get("release_manifest_digest")) and bool(HEX64.fullmatch(required["release_manifest_digest"])), "RUNTIME_ATTESTATION_RELEASE_MANIFEST_DIGEST_INVALID")
    require(nonempty(required.get("release_manifest_ref")), "RUNTIME_ATTESTATION_RELEASE_MANIFEST_REF_REQUIRED")

    mismatches = []
    if current_fp != observed_fp:
        mismatches.append("context_fingerprint_mismatch")
    if not at_least(observed["skillforge_version"], required["skillforge_min_version"]):
        mismatches.append("skillforge:version_below_minimum")
    _validate_allowlist(
        required.get("allowed_package_digests"),
        "RUNTIME_ATTESTATION_ALLOWED_PACKAGE_DIGESTS",
        "skillforge",
        observed["package_digest"],
        mismatches,
    )
    proof_time = _validate_freshness(evidence, required, mismatches, _now(now))

    _validate_component("g16", observed, required, mismatches)
    _validate_component("g18", observed, required, mismatches)

    status = "CONFORMING_RUNTIME" if not mismatches else "NONCONFORMING_RUNTIME_READ_ONLY"
    mutation_allowed = not mismatches
    receipt = {
        "contract": CONTRACT,
        "attestation_id": "rta-" + digest_obj({
            "current_context": current,
            "runtime_evidence": evidence,
            "installed": observed,
            "required": required,
            "handoff_evidence": handoff,
        })[:24],
        "surface": current["surface"],
        "context_fingerprint": current_fp,
        "status": status,
        "mutation_allowed": mutation_allowed,
        "mismatches": mismatches,
        "observed": {
            "skillforge_version": observed["skillforge_version"],
            "package_digest": observed["package_digest"],
            "g16_version": observed["g16"]["version"],
            "g16_digest": observed["g16"]["digest"],
            "g18_version": observed["g18"]["version"],
            "g18_digest": observed["g18"]["digest"],
        },
        "required": required,
        "runtime_proof_source": proof_source,
        "runtime_proof_ref": evidence["proof_ref"],
        "runtime_proof_timestamp": proof_time.isoformat().replace("+00:00", "Z"),
        "handoff_visible_ref": handoff["visible_ref"],
        "handoff_provider_revision": handoff["provider_revision"],
        "independent_proof_channels": True,
    }
    if mode == "MATERIAL" and not mutation_allowed:
        raise AttestationError("RUNTIME_ATTESTATION_MATERIAL_MUTATION_BLOCKED:" + ",".join(mismatches))
    return receipt
