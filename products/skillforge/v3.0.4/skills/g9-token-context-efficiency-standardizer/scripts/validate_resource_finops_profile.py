#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

try:
    import yaml
except Exception:
    yaml = None

CONTRACT_ID = "INC_G9_RESOURCE_FINOPS_CONTROL_PLANE_V1"
ADAPTER_PROFILE_ID = "INC_RESOURCE_ADAPTER_PROFILE"
CAPABILITY_PROFILE_ID = "INC_PROVIDER_CAPABILITY_PROFILE"
G16_ROUTE_REF = "INC_MACHINE_ROUTE_BEFORE_VISUAL_UI_V1"

G9_TRUTH = {"MEASURED", "VALIDATED_ESTIMATE", "UNKNOWN"}
G11_MEASUREMENT = {"MEASURED", "PARTIAL", "DERIVED", "ESTIMATED", "UNAVAILABLE"}
CADENCE = {"C0_EVENT", "C1_FAST", "C2_OPERATIONAL", "C3_DAILY", "C4_BILLING_EVENT", "C5_ON_CHANGE"}
ACQUISITION = {"A0_INLINE", "A1_PUSH", "A2_FAST_POLL", "A3_OPS_POLL", "A4_DAILY_RECONCILE", "A5_BILLING_EVENT", "A6_ON_CHANGE", "A7_UI_FALLBACK"}
PERSISTENCE = {"P0_NONE", "P1_EVENT_FACT", "P2_STATE_CHANGE", "P3_TIME_SERIES", "P4_BILLING_LEDGER", "P5_REFERENCE"}
AVAILABILITY = {"INCLUDED_FREE", "INCLUDED_LIMITED", "PAID_ADDON", "SEPARATE_PLAN", "UNKNOWN", "NOT_AVAILABLE"}
ACTIVATION = {"NOT_REVIEWED", "RECOMMENDED", "APPROVED", "ACTIVE", "VERIFIED", "REJECTED", "NOT_APPLICABLE"}
PROTECTION = {"L1", "L2", "BOTH", "NONE"}
CAPABILITY_DOMAINS = {
    "COST_AND_BUDGET", "QUOTA_AND_CAPACITY", "OBSERVABILITY_AND_LOGGING",
    "ALERTING_AND_INCIDENT", "SCHEDULING_AND_AUTOMATION", "DATA_PROTECTION",
    "SECURITY_AND_ACCESS", "RELIABILITY_AND_RESILIENCE", "LIFECYCLE_AND_GOVERNANCE",
    "SUPPORT_AND_SERVICE",
}
SOURCE_PRECEDENCE = [
    "AUTHORITATIVE_PROVIDER_BILLING_COST_USAGE",
    "AUTHORITATIVE_PROVIDER_QUOTA_RATE_LIMIT_CREDIT",
    "EXACT_LOCAL_RUNTIME_TELEMETRY",
    "PROVIDER_EXPORT_REPORT",
    "PROVIDER_NATIVE_ALERT_EVENT",
    "BOUNDED_UI_RECONCILIATION",
    "VALIDATED_ESTIMATE",
    "UNKNOWN_UNAVAILABLE",
]

class ValidationError(ValueError):
    pass


def _req(obj: Mapping[str, Any], key: str) -> Any:
    value = obj.get(key)
    if value in (None, "", [], {}):
        raise ValidationError(f"MISSING_REQUIRED:{key}")
    return value


def _list(value: Any, key: str) -> list[Any]:
    if not isinstance(value, list) or not value:
        raise ValidationError(f"INVALID_LIST:{key}")
    return value


def map_measurement_truth(status: str, *, estimate_validated: bool = False) -> str:
    status = str(status or "").upper()
    if status == "MEASURED":
        return "MEASURED"
    if status in {"PARTIAL", "DERIVED", "ESTIMATED"} and estimate_validated:
        return "VALIDATED_ESTIMATE"
    return "UNKNOWN"


def validate_profile(profile: Mapping[str, Any]) -> dict[str, Any]:
    if profile.get("schema") != ADAPTER_PROFILE_ID:
        raise ValidationError("INVALID_SCHEMA")
    if profile.get("control_plane_ref") != CONTRACT_ID:
        raise ValidationError("CONTROL_PLANE_REF_REQUIRED")
    if profile.get("activation_route_authority") != G16_ROUTE_REF:
        raise ValidationError("G16_ROUTE_AUTHORITY_REQUIRED")
    if profile.get("consumer_direct_provider_binding") != "FORBIDDEN":
        raise ValidationError("CONSUMER_DIRECT_PROVIDER_BINDING_FORBIDDEN")

    for key in ("provider_ref", "adapter_ref", "adapter_file_ref", "capability_profile_ref", "checked_at"):
        _req(profile, key)
    _list(_req(profile, "service_refs"), "service_refs")
    _list(_req(profile, "hierarchy"), "hierarchy")
    _list(_req(profile, "authoritative_sources"), "authoritative_sources")

    if profile.get("collector_model_calls") != 0:
        raise ValidationError("COLLECTOR_MODEL_CALLS_MUST_BE_ZERO")
    overhead = _req(profile, "observability_overhead_budget")
    for key in ("api_calls_per_day", "db_rows_per_day", "compute_runtime", "storage_per_month", "known_monetary_cost"):
        if key not in overhead:
            raise ValidationError(f"OVERHEAD_BUDGET_FIELD_REQUIRED:{key}")

    precedence = _req(profile, "source_precedence")
    if precedence != SOURCE_PRECEDENCE:
        raise ValidationError("SOURCE_PRECEDENCE_DRIFT")

    meters = _list(_req(profile, "meters"), "meters")
    for meter in meters:
        for key in ("meter_ref", "unit", "cadence", "acquisition_mode", "persistence_class", "truth_state"):
            _req(meter, key)
        if meter["cadence"] not in CADENCE:
            raise ValidationError(f"INVALID_CADENCE:{meter['meter_ref']}")
        if meter["acquisition_mode"] not in ACQUISITION:
            raise ValidationError(f"INVALID_ACQUISITION:{meter['meter_ref']}")
        if meter["persistence_class"] not in PERSISTENCE:
            raise ValidationError(f"INVALID_PERSISTENCE:{meter['meter_ref']}")
        if meter["truth_state"] not in G9_TRUTH:
            raise ValidationError(f"INVALID_TRUTH_STATE:{meter['meter_ref']}")
        if meter["acquisition_mode"] == "A7_UI_FALLBACK" and meter["cadence"] == "C1_FAST":
            raise ValidationError(f"UI_FAST_POLL_FORBIDDEN:{meter['meter_ref']}")
        if meter.get("quota_delta_to_tokens") is True:
            raise ValidationError(f"QUOTA_DELTA_TOKEN_CONVERSION_FORBIDDEN:{meter['meter_ref']}")
        if meter.get("invented_project_formula") is True:
            raise ValidationError(f"INVENTED_PROVIDER_FORMULA_FORBIDDEN:{meter['meter_ref']}")

    caps = _list(_req(profile, "capability_inventory"), "capability_inventory")
    domains = {str(x.get("domain") or "") for x in caps}
    if domains != CAPABILITY_DOMAINS:
        missing = sorted(CAPABILITY_DOMAINS - domains)
        extra = sorted(domains - CAPABILITY_DOMAINS)
        raise ValidationError(f"CAPABILITY_DOMAIN_COVERAGE_INVALID:missing={missing}:extra={extra}")

    for cap in caps:
        domain = cap.get("domain")
        availability = _req(cap, "availability")
        if availability not in AVAILABILITY:
            raise ValidationError(f"INVALID_AVAILABILITY:{domain}")
        protection = _req(cap, "protection_layer")
        if protection not in PROTECTION:
            raise ValidationError(f"INVALID_PROTECTION_LAYER:{domain}")
        activation = _req(cap, "activation_status")
        if activation not in ACTIVATION:
            raise ValidationError(f"INVALID_ACTIVATION_STATUS:{domain}")
        _req(cap, "owner_skill")
        _req(cap, "verification_method")
        _req(cap, "rollback_method")
        if availability in {"PAID_ADDON", "SEPARATE_PLAN"} and activation in {"ACTIVE", "VERIFIED"}:
            if not cap.get("owner_approval_ref"):
                raise ValidationError(f"PAID_ACTIVATION_OWNER_APPROVAL_REQUIRED:{domain}")
            if not cap.get("cost_benefit_disclosure_ref"):
                raise ValidationError(f"PAID_ACTIVATION_COST_BENEFIT_REQUIRED:{domain}")

    if profile.get("raw_provider_payload_persistence") not in {"OMIT_BY_DEFAULT", "BOUNDED_SECURE_REFERENCE_ONLY"}:
        raise ValidationError("RAW_PROVIDER_PAYLOAD_POLICY_INVALID")
    if profile.get("parallel_g9_database") != "PROHIBITED":
        raise ValidationError("PARALLEL_G9_DATABASE_FORBIDDEN")
    if profile.get("g17_persistence_path") != "REQUIRED":
        raise ValidationError("G17_PERSISTENCE_PATH_REQUIRED")
    if profile.get("g11_semantic_normalization") != "REQUIRED":
        raise ValidationError("G11_NORMALIZATION_REQUIRED")
    if profile.get("g15_alert_delivery") != "REQUIRED_WHEN_ALERT_OR_DECISION_EXISTS":
        raise ValidationError("G15_ALERT_ROUTE_REQUIRED")

    return {
        "result": "PASS",
        "provider_ref": profile["provider_ref"],
        "meter_count": len(meters),
        "capability_domain_count": len(domains),
        "collector_model_calls": 0,
        "activation_route_authority": G16_ROUTE_REF,
        "paid_changes_autonomously_authorized": False,
        "independent_g12_g13": False,
    }


def load_file(path: Path) -> Mapping[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    if yaml is None:
        raise ValidationError("YAML_LIBRARY_UNAVAILABLE")
    return yaml.safe_load(text)


BASELINE_PROVIDER_SERVICES = {
    "OPENAI_CHATGPT",
    "OPENAI_API",
    "AZURE",
    "HATCHABLE",
    "MICROSOFT_GRAPH_M365",
    "POWER_AUTOMATE",
    "GITHUB",
    "TRELLO",
    "MCP_SERVERS",
    "PLUGINS_CONNECTORS",
    "WINDOWS_HOSTS",
}


def validate_registry(registry: Mapping[str, Any]) -> dict[str, Any]:
    if registry.get("schema") != "INC_PROVIDER_RESOURCE_PROFILE_REGISTRY_V1":
        raise ValidationError("INVALID_PROVIDER_REGISTRY_SCHEMA")
    if registry.get("control_plane_ref") != CONTRACT_ID:
        raise ValidationError("PROVIDER_REGISTRY_CONTROL_PLANE_REF_REQUIRED")
    profiles = _list(_req(registry, "profiles"), "profiles")
    by_ref = {}
    for profile in profiles:
        ref = str(_req(profile, "provider_service_ref"))
        if ref in by_ref:
            raise ValidationError(f"DUPLICATE_PROVIDER_PROFILE:{ref}")
        by_ref[ref] = profile
        state = _req(profile, "adapter_state")
        if state not in {"IMPLEMENTED", "GAP_NOT_IMPLEMENTED_BLOCKS_PRODUCTION"}:
            raise ValidationError(f"INVALID_ADAPTER_STATE:{ref}")
        if state == "IMPLEMENTED":
            _req(profile, "adapter_ref")
            _req(profile, "adapter_file_ref")
        else:
            if profile.get("activation_status") in {"ACTIVE", "VERIFIED"}:
                raise ValidationError(f"GAP_PROVIDER_CANNOT_BE_ACTIVE:{ref}")
            if profile.get("production_disposition") != "BLOCKED_UNTIL_ADAPTER_AND_PROFILE_RESOLVE":
                raise ValidationError(f"GAP_PROVIDER_MUST_BLOCK_PRODUCTION:{ref}")
        if profile.get("activation_route_authority") != G16_ROUTE_REF:
            raise ValidationError(f"G16_ROUTE_AUTHORITY_REQUIRED:{ref}")
        if profile.get("collector_model_calls") != 0:
            raise ValidationError(f"COLLECTOR_MODEL_CALLS_MUST_BE_ZERO:{ref}")
        if profile.get("consumer_direct_provider_binding") != "FORBIDDEN":
            raise ValidationError(f"CONSUMER_DIRECT_PROVIDER_BINDING_FORBIDDEN:{ref}")
        if profile.get("paid_change_policy") != "EXPLICIT_OWNER_APPROVAL_REQUIRED":
            raise ValidationError(f"PAID_CHANGE_POLICY_INVALID:{ref}")
    observed = set(by_ref)
    if observed != BASELINE_PROVIDER_SERVICES:
        missing = sorted(BASELINE_PROVIDER_SERVICES - observed)
        extra = sorted(observed - BASELINE_PROVIDER_SERVICES)
        raise ValidationError(f"BASELINE_PROVIDER_COVERAGE_INVALID:missing={missing}:extra={extra}")
    return {
        "result": "PASS",
        "profile_count": len(profiles),
        "implemented_count": sum(1 for x in profiles if x["adapter_state"] == "IMPLEMENTED"),
        "gap_count": sum(1 for x in profiles if x["adapter_state"] != "IMPLEMENTED"),
        "production_ready": all(x["adapter_state"] == "IMPLEMENTED" for x in profiles),
        "independent_g12_g13": False,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--registry", action="store_true")
    args = parser.parse_args()
    try:
        payload = load_file(Path(args.input))
        result = validate_registry(payload) if args.registry else validate_profile(payload)
    except Exception as exc:
        print(json.dumps({"result": "BLOCKED", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
