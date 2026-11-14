from __future__ import annotations

import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT = "INC_G11_LOG_ENVELOPE_V1"
ENVELOPE_VERSION = "1.1"
NORMALIZATION_SCHEMA_VERSION = "1.1"

RUN_TYPES = {"BUILD", "RUNTIME", "TEST", "EVALUATION", "VALIDATION", "MAINTENANCE", "MIGRATION"}
SPEND_MODES = {"EFFICIENT", "EXPAND", "MAXIMIZE"}
RETENTION_CLASSES = {"CRITICAL", "SECURITY", "AUDIT", "STANDARD", "HIGH_VOLUME"}
DATA_CLASSIFICATIONS = {"PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"}
COMPONENT_ROLES = {"SKILL", "BUILDER", "MODEL", "TOOL", "TEST", "EVALUATOR", "SQS", "VALIDATOR", "ORCHESTRATOR"}
METRIC_SCOPES = {"MODEL_CALL", "TOOL_CALL", "RUN_AGGREGATE", "OTHER"}
COST_SOURCES = {"PROVIDER_MEASURED", "CALCULATED", "ESTIMATED", "UNAVAILABLE"}
USAGE_SOURCES = {"MEASURED", "ESTIMATED", "UNAVAILABLE"}
ATTRIBUTION_METHODS = {"DIRECT", "CHILD", "ALLOCATED"}
TOKEN_CHECK_STATUSES = {"PASS", "MISMATCH", "NOT_CHECKED"}
RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
APPROVAL_DECISIONS = {"PENDING", "APPROVED", "REJECTED", "CANCELLED"}
TELEMETRY_STATUSES = {"MEASURED", "PARTIAL", "UNAVAILABLE"}

TOKEN_COUNT_FIELDS = (
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "cache_read_input_tokens",
    "cache_creation_input_tokens",
    "reasoning_output_tokens",
)
METRIC_OPTIONAL_FIELDS = (
    "action_id",
    "model_call_id",
    "request_model",
    "response_model",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "cache_read_input_tokens",
    "cache_creation_input_tokens",
    "reasoning_output_tokens",
    "cost_value",
    "cost_currency",
    "pricing_profile_id",
    "latency_ms",
    "attributed_skill_id",
    "provider_usage_raw_json",
    "provider_usage_raw_ref",
)

REQUIRED = {
    "event": [
        "event_id", "run_id", "sequence_number", "timestamp", "component_role",
        "event_type", "severity", "message_code", "message_summary",
        "data_classification", "retention_class", "is_test",
    ],
    "action": [
        "action_id", "run_id", "sequence_number", "timestamp", "component_role",
        "actor_ref", "action_type", "risk_level", "data_classification",
        "attempt_number", "result_status", "is_test",
    ],
    "metric": [
        "metric_id", "run_id", "timestamp", "metric_scope", "provider",
        "cost_source", "usage_source", "attribution_method",
        "normalization_schema_version", "token_accounting_check_status", "is_test",
    ],
    "error": [
        "error_id", "run_id", "timestamp", "error_code", "stage", "severity",
        "retry_count", "resolution_status", "is_test",
    ],
    "approval": [
        "approval_id", "run_id", "action_summary", "risk_level", "requested_at",
        "decision", "approver_ref", "scope_summary", "is_test",
    ],
}

# Authentication/security material is forbidden. Usage counters are explicitly not secrets.
EXACT_SECRET_KEYS = {
    "access_token", "refresh_token", "id_token", "authorization", "bearer_token",
    "auth_token", "session_token", "api_key", "apikey", "password", "passwd",
    "client_secret", "private_key", "cookie", "set_cookie", "cvv", "otp", "pin",
    "security_answer", "secret", "credential", "credentials",
}
FORBIDDEN_CONTENT_KEYS = {
    "prompt", "raw_prompt", "full_prompt", "raw_response", "full_response",
    "raw_completion", "full_completion", "hidden_reasoning", "chain_of_thought",
    "reasoning_content", "system_prompt",
}
SAFE_TOKEN_COUNTER_KEYS = set(TOKEN_COUNT_FIELDS) | {
    "token_accounting_check_status", "prompt_tokens", "completion_tokens",
    "cached_tokens", "reasoning_tokens", "input_token_details", "output_token_details",
}
PHYSICAL_MAPPING_KEYS = {
    "sharepoint_list", "sharepoint_list_name", "sharepoint_column", "sharepoint_column_name",
    "physical_list_name", "physical_column_name", "list_guid", "graph_list_id",
    "queue_path", "writer_queue_path",
}
SENSITIVE_TEXT_MARKERS = (
    '"access_token"', '"refresh_token"', '"authorization"', '"api_key"',
    '"client_secret"', '"private_key"', '"password"', '"cookie"', "bearer ",
)


def _is_nonempty(value: Any) -> bool:
    return value is not None and value != ""


def _safe_id(value: Any, max_length: int = 180) -> str:
    # Reject lossy normalization: distinct caller identities must never collide.
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9._:-]{1," + str(max_length) + r"}", value):
        raise ValueError("INVALID_STABLE_IDENTITY")
    return value


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _parse_datetime(value: str, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty ISO-8601 timestamp")
    raw = value.strip()
    try:
        dt = datetime.fromisoformat(raw[:-1] + "+00:00" if raw.endswith("Z") else raw)
    except ValueError as exc:
        raise ValueError(f"{field} must be a valid ISO-8601 timestamp") from exc
    if dt.tzinfo is None:
        raise ValueError(f"{field} must include an explicit timezone")
    return dt.astimezone(timezone.utc)


def _normalize_timestamp(value: Any, field: str) -> str:
    dt = _parse_datetime(value, field)
    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _normalize_optional_timestamp(value: Any, field: str) -> str | None:
    if value is None or value == "":
        return None
    return _normalize_timestamp(value, field)


def _enum(value: Any, allowed: set[str], field: str) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise ValueError(f"invalid {field}: {value}")
    return value


def _positive_int(value: Any, field: str) -> int:
    if type(value) is not int or value < 1:
        raise ValueError(f"{field} must be an integer >= 1")
    return value


def _nonnegative_int(value: Any, field: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{field} must be an integer >= 0")
    return value


def _nonnegative_number(value: Any, field: str) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{field} must be a finite non-negative number")
    return value


def _check_forbidden(obj: Any, path: str = "root") -> None:
    if isinstance(obj, float) and not math.isfinite(obj):
        raise ValueError("NONFINITE_NUMBER_FORBIDDEN")
    if isinstance(obj, dict):
        for key, value in obj.items():
            lk = re.sub(r'([a-z0-9])([A-Z])',r'\1_\2',re.sub(r'([A-Z]+)([A-Z][a-z])',r'\1_\2',str(key).strip())).lower().replace('-','_')
            if lk in PHYSICAL_MAPPING_KEYS:
                raise ValueError(f"forbidden physical mapping field: {path}.{key}")
            if lk in FORBIDDEN_CONTENT_KEYS:
                raise ValueError(f"forbidden raw/hidden content field: {path}.{key}")
            token_counter = lk in SAFE_TOKEN_COUNTER_KEYS or lk.endswith("_tokens")
            sensitive_name = (
                lk in EXACT_SECRET_KEYS
                or "authorization" in lk
                or "password" in lk
                or "cookie" in lk
                or "private_key" in lk
                or (lk.endswith("_token") and not token_counter)
                or lk.endswith("_secret")
                or (lk.endswith("_key") and lk not in {"idempotency_key", "business_key", "lookup_key"})
            )
            raw_content_name = (
                ("prompt" in lk and not token_counter)
                or lk in FORBIDDEN_CONTENT_KEYS
                or lk in {"response_text", "response_body", "completion_text", "completion_body", "reasoning_text"}
            )
            if sensitive_name:
                raise ValueError(f"forbidden sensitive field: {path}.{key}")
            if raw_content_name:
                raise ValueError(f"forbidden raw/hidden content field: {path}.{key}")
            _check_forbidden(value, f"{path}.{key}")
            if lk.endswith("_json") and isinstance(value, str):
                _check_json_string(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            _check_forbidden(value, f"{path}[{index}]")


def _check_json_string(value: str, path: str) -> None:
    lower = value.lower()
    if any(marker in lower for marker in SENSITIVE_TEXT_MARKERS):
        raise ValueError(f"forbidden sensitive content in {path}")
    try:
        parsed = json.loads(value, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("NONFINITE_JSON")))
    except (ValueError, TypeError) as exc:
        raise ValueError("INVALID_JSON_CONTENT") from exc
    if not isinstance(parsed, (dict, list)):
        raise ValueError("JSON_OBJECT_OR_ARRAY_REQUIRED")
    _check_forbidden(parsed, path)


def _normalize_raw_usage(value: Any) -> str:
    _check_forbidden(value, "provider_usage_raw_json")
    if isinstance(value, str):
        _check_json_string(value, "provider_usage_raw_json")
        return value
    if isinstance(value, (dict, list)):
        return json.dumps(value, separators=(",", ":"), sort_keys=True, allow_nan=False)
    raise ValueError("provider_usage_raw_json must be a JSON string, object, or array")


def _merge_refs(req: dict[str, Any]) -> dict[str, Any]:
    refs = dict(req.get("refs") or {})
    source_refs = dict(req.get("source_refs") or {})
    for key, value in source_refs.items():
        if key in refs and _is_nonempty(refs[key]) and _is_nonempty(value) and refs[key] != value:
            raise ValueError(f"conflicting refs/source_refs value for {key}")
        refs[key] = value
    return refs


def _top_or_ref(req: dict[str, Any], refs: dict[str, Any], key: str, default: Any = None) -> Any:
    if _is_nonempty(req.get(key)):
        return req[key]
    if _is_nonempty(refs.get(key)):
        return refs[key]
    return default


def _retention(profile: str, requested: Any) -> str:
    value = requested or {"LIGHT": "STANDARD", "STANDARD": "STANDARD", "DEEP": "AUDIT"}[profile]
    return _enum(value, RETENTION_CLASSES, "retention_class")


def _normalize_telemetry_status(value: Any) -> str:
    return _enum(value, TELEMETRY_STATUSES, "resource telemetry status")


def _token_check(record: dict[str, Any]) -> str:
    present = [name for name in ("input_tokens", "output_tokens", "total_tokens") if name in record]
    for name in TOKEN_COUNT_FIELDS:
        if name in record:
            record[name] = _nonnegative_int(record[name], name)
    if len(present) == 3:
        return "PASS" if record["total_tokens"] == record["input_tokens"] + record["output_tokens"] else "MISMATCH"
    return "NOT_CHECKED"


def _validate_metric(record: dict[str, Any]) -> None:
    record["metric_scope"] = _enum(record["metric_scope"], METRIC_SCOPES, "metric_scope")
    record["cost_source"] = _enum(record["cost_source"], COST_SOURCES, "cost_source")
    record["usage_source"] = _enum(record["usage_source"], USAGE_SOURCES, "usage_source")
    record["attribution_method"] = _enum(record["attribution_method"], ATTRIBUTION_METHODS, "attribution_method")
    record["token_accounting_check_status"] = _token_check(record)
    if not isinstance(record.get("provider"), str) or not record["provider"].strip():
        raise ValueError("provider must be a non-empty string")
    if not isinstance(record.get("normalization_schema_version"), str) or not record["normalization_schema_version"].strip():
        raise ValueError("normalization_schema_version must be a non-empty string")

    token_values_present = any(name in record for name in TOKEN_COUNT_FIELDS)
    if token_values_present and record["usage_source"] == "UNAVAILABLE":
        raise ValueError("usage_source cannot be UNAVAILABLE when token usage values are supplied")
    if not token_values_present and record["usage_source"] != "UNAVAILABLE":
        raise ValueError("usage_source must be UNAVAILABLE when no token usage values are supplied")

    if "latency_ms" in record:
        record["latency_ms"] = _nonnegative_int(record["latency_ms"], "latency_ms")

    has_cost = "cost_value" in record and record["cost_value"] is not None
    if has_cost:
        record["cost_value"] = _nonnegative_number(record["cost_value"], "cost_value")
        if record["cost_source"] == "UNAVAILABLE":
            raise ValueError("cost_source cannot be UNAVAILABLE when cost_value is supplied")
        currency = record.get("cost_currency")
        if not isinstance(currency, str) or not re.fullmatch(r"[A-Z]{3}", currency):
            raise ValueError("cost_currency must be a three-letter uppercase currency when cost_value is supplied")
    else:
        if record["cost_source"] != "UNAVAILABLE":
            raise ValueError("cost_source must be UNAVAILABLE when cost_value is absent")
        if "cost_currency" in record and record["cost_currency"] not in (None, ""):
            raise ValueError("cost_currency cannot be supplied without cost_value")

    if "provider_usage_raw_json" in record:
        record["provider_usage_raw_json"] = _normalize_raw_usage(record["provider_usage_raw_json"])


def _validate_record(kind: str, record: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED[kind] if field not in record or record[field] in (None, "")]
    if missing:
        raise ValueError(f"{kind} missing required fields: {','.join(missing)}")

    if "sequence_number" in record:
        record["sequence_number"] = _positive_int(record["sequence_number"], f"{kind}.sequence_number")
    if "timestamp" in record:
        record["timestamp"] = _normalize_timestamp(record["timestamp"], f"{kind}.timestamp")
    if "component_role" in record:
        record["component_role"] = _enum(record["component_role"], COMPONENT_ROLES, f"{kind}.component_role")

    if kind == "event":
        record["data_classification"] = _enum(record["data_classification"], DATA_CLASSIFICATIONS, "event.data_classification")
        record["retention_class"] = _enum(record["retention_class"], RETENTION_CLASSES, "event.retention_class")
    elif kind == "action":
        record["risk_level"] = _enum(record["risk_level"], RISK_LEVELS, "action.risk_level")
        record["data_classification"] = _enum(record["data_classification"], DATA_CLASSIFICATIONS, "action.data_classification")
        record["attempt_number"] = _positive_int(record["attempt_number"], "action.attempt_number")
    elif kind == "metric":
        _validate_metric(record)
    elif kind == "error":
        record["retry_count"] = _nonnegative_int(record["retry_count"], "error.retry_count")
    elif kind == "approval":
        record["risk_level"] = _enum(record["risk_level"], RISK_LEVELS, "approval.risk_level")
        record["decision"] = _enum(record["decision"], APPROVAL_DECISIONS, "approval.decision")
        record["requested_at"] = _normalize_timestamp(record["requested_at"], "approval.requested_at")
        if _is_nonempty(record.get("decided_at")):
            record["decided_at"] = _normalize_timestamp(record["decided_at"], "approval.decided_at")
            if _parse_datetime(record["decided_at"], "approval.decided_at") < _parse_datetime(record["requested_at"], "approval.requested_at"):
                raise ValueError("approval.decided_at cannot be before approval.requested_at")


def _derive_child_id(run_id: str, kind: str, ordinal: int) -> str:
    return _safe_id(f"{run_id}:{kind}:{ordinal}", 255)


def _record(
    kind: str,
    supplied: dict[str, Any] | None,
    common: dict[str, Any],
    sequence: int,
    ordinal: int,
) -> dict[str, Any]:
    if supplied is not None and not isinstance(supplied, dict):
        raise ValueError(f"semantic_facts.{kind} entries must be objects")
    rec = dict(supplied or {})
    rec["kind"] = kind
    rec.setdefault("run_id", common["run_id"])
    # Only generate fields belonging to this semantic family. In particular,
    # metric/error/approval rows must not acquire event-only transport fields
    # that their canonical persistence contract cannot store or verify.
    if "sequence_number" in REQUIRED[kind]:
        rec.setdefault("sequence_number", sequence)
    if "timestamp" in REQUIRED[kind]:
        rec.setdefault("timestamp", common["timestamp"])
    rec.setdefault("is_test", common["is_test"])
    if "component_role" in REQUIRED[kind]:
        rec.setdefault("component_role", common["component_role"])

    if rec["run_id"] != common["run_id"]:
        raise ValueError(f"{kind}.run_id must match run.run_id")
    if rec["is_test"] is not common["is_test"]:
        raise ValueError(f"{kind}.is_test must match run.is_test")

    if kind == "event":
        rec.setdefault("event_id", _derive_child_id(common["run_id"], "event", ordinal))
        rec.setdefault("data_classification", common["data_classification"])
        rec.setdefault("retention_class", common["retention_class"])
    elif kind == "action":
        rec.setdefault("action_id", _derive_child_id(common["run_id"], "action", ordinal))
        rec.setdefault("actor_ref", common["producer_ref"])
        rec.setdefault("data_classification", common["data_classification"])
        rec.setdefault("attempt_number", common["attempt_number"])
        rec.setdefault("result_status", common["status"])
    elif kind == "metric":
        rec.setdefault("metric_id", _derive_child_id(common["run_id"], "metric", ordinal))
        rec.setdefault("provider", "UNAVAILABLE")
        rec.setdefault("metric_scope", "OTHER")
        rec.setdefault("cost_source", "UNAVAILABLE")
        rec.setdefault("usage_source", "UNAVAILABLE")
        rec.setdefault("attribution_method", "DIRECT")
        rec.setdefault("normalization_schema_version", NORMALIZATION_SCHEMA_VERSION)
        rec["token_accounting_check_status"] = _token_check(rec)
    elif kind == "error":
        rec.setdefault("error_id", _derive_child_id(common["run_id"], "error", ordinal))
        if not _is_nonempty(rec.get("error_code")) and _is_nonempty(rec.get("message_code")):
            rec["error_code"] = rec.pop("message_code")
        if not _is_nonempty(rec.get("diagnostic_summary")) and _is_nonempty(rec.get("message_summary")):
            rec["diagnostic_summary"] = rec.pop("message_summary")
    elif kind == "approval":
        rec.setdefault("approval_id", _derive_child_id(common["run_id"], "approval", ordinal))

    _validate_record(kind, rec)
    return rec


def _as_record_list(value: Any, kind: str) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list) and all(isinstance(item, dict) for item in value):
        return value
    raise ValueError(f"semantic_facts.{kind} must be an object or list of objects")


def _resource_metric(resource: dict[str, Any], common: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(resource, dict):
        raise ValueError("resource_telemetry must be an object")
    status = _normalize_telemetry_status(resource.get("status", "UNAVAILABLE"))
    metric = {key: resource[key] for key in METRIC_OPTIONAL_FIELDS if key in resource}

    usage_values_present = any(key in metric for key in TOKEN_COUNT_FIELDS)
    if status == "UNAVAILABLE" and (usage_values_present or "cost_value" in metric or "latency_ms" in metric):
        raise ValueError("resource telemetry status UNAVAILABLE cannot contain measured resource values")
    if status in {"MEASURED", "PARTIAL"} and not (usage_values_present or "cost_value" in metric or "latency_ms" in metric):
        raise ValueError(f"resource telemetry status {status} requires at least one factual resource value")

    if "usage_source" in resource:
        usage_source = _enum(resource["usage_source"], USAGE_SOURCES, "usage_source")
    else:
        usage_source = "MEASURED" if usage_values_present and status in {"MEASURED", "PARTIAL"} else "UNAVAILABLE"

    if "cost_source" in resource:
        cost_source = _enum(resource["cost_source"], COST_SOURCES, "cost_source")
    else:
        cost_source = "UNAVAILABLE"
        if "cost_value" in metric:
            raise ValueError("resource telemetry with cost_value must explicitly provide cost_source")

    metric.update(
        {
            "metric_id": resource.get("metric_id", _safe_id(f"{common['run_id']}:metric:resource", 255)),
            "metric_scope": resource.get("metric_scope", "MODEL_CALL"),
            "provider": resource.get("provider", "UNAVAILABLE"),
            "cost_source": cost_source,
            "usage_source": usage_source,
            "attribution_method": resource.get("attribution_method", "DIRECT"),
            "normalization_schema_version": resource.get("normalization_schema_version", NORMALIZATION_SCHEMA_VERSION),
            "token_accounting_check_status": "NOT_CHECKED",
        }
    )
    return metric


def _normalize_telemetry(
    req: dict[str, Any],
    facts: dict[str, Any],
    common: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    telemetry = dict(req.get("telemetry") or {})
    nested_resource = telemetry.pop("resource", None)
    top_resource = req.get("resource_telemetry")
    if nested_resource is not None and top_resource is not None and nested_resource != top_resource:
        raise ValueError("conflicting telemetry.resource and resource_telemetry")
    resource = top_resource if top_resource is not None else nested_resource

    if resource is not None:
        resource_metric = _resource_metric(resource, common)
        existing = _as_record_list(facts.get("metric"), "metric")
        existing.append(resource_metric)
        facts["metric"] = existing
        telemetry["actual_usage_status"] = _normalize_telemetry_status(resource.get("status", "UNAVAILABLE"))
    else:
        status = telemetry.get("actual_usage_status", "UNAVAILABLE")
        telemetry["actual_usage_status"] = _normalize_telemetry_status(status)
        if telemetry["actual_usage_status"] in {"MEASURED", "PARTIAL"} and not _as_record_list(facts.get("metric"), "metric"):
            raise ValueError("telemetry actual_usage_status MEASURED/PARTIAL requires factual metric data")

    return telemetry, facts


def _build_run(req: dict[str, Any], refs: dict[str, Any], common_time: str, profile: str) -> tuple[dict[str, Any], dict[str, Any]]:
    is_test = req["is_test"]
    run_id = str(_top_or_ref(req, refs, "run_id", _safe_id(req["activity_id"])))
    root_run_id = str(_top_or_ref(req, refs, "root_run_id", run_id))
    trace_id = str(_top_or_ref(req, refs, "trace_id", run_id))
    correlation_id = str(_top_or_ref(req, refs, "correlation_id", run_id))

    run_type = _enum(req.get("run_type", "TEST" if is_test else "RUNTIME"), RUN_TYPES, "run_type")
    spend_mode = _enum(req.get("spend_mode", "EFFICIENT"), SPEND_MODES, "spend_mode")
    retention = _retention(profile, req.get("retention_class"))
    attempt_number = _positive_int(req.get("attempt_number", 1), "attempt_number")

    started_raw = req.get("started_at") or req.get("timestamp") or common_time
    started_at = _normalize_timestamp(started_raw, "started_at")
    ended_at = _normalize_optional_timestamp(req.get("ended_at"), "ended_at")
    if ended_at and _parse_datetime(ended_at, "ended_at") < _parse_datetime(started_at, "started_at"):
        raise ValueError("ended_at cannot be before started_at")

    environment_ref = str(_top_or_ref(req, refs, "environment_ref", "INC_GOVERNED_RUNTIME"))
    run = {
        "run_id": run_id,
        "root_run_id": root_run_id,
        "trace_id": trace_id,
        "correlation_id": correlation_id,
        "run_type": run_type,
        "started_at": started_at,
        "status": req["status"],
        "spend_mode": spend_mode,
        "attempt_number": attempt_number,
        "environment_ref": environment_ref,
        "retention_class": retention,
        "is_test": is_test,
    }

    optional_sources = {
        "parent_run_id": _top_or_ref(req, refs, "parent_run_id"),
        "agent_id": _top_or_ref(req, refs, "agent_id"),
        "primary_skill_id": _top_or_ref(req, refs, "primary_skill_id"),
        "executing_skill_id": _top_or_ref(req, refs, "executing_skill_id", refs.get("skill_id")),
        "skill_version": _top_or_ref(req, refs, "skill_version"),
        "ended_at": ended_at,
        "result_summary": req.get("result_summary", str(req["summary"])[:1000]),
        "result_ref": _top_or_ref(req, refs, "result_ref"),
    }
    for key, value in optional_sources.items():
        if _is_nonempty(value):
            run[key] = value

    common = {
        "run_id": run_id,
        "timestamp": _normalize_timestamp(req.get("timestamp") or common_time, "timestamp"),
        "is_test": is_test,
        "component_role": _enum(req.get("component_role", "SKILL"), COMPONENT_ROLES, "component_role"),
        "data_classification": _enum(req.get("data_classification", "INTERNAL"), DATA_CLASSIFICATIONS, "data_classification"),
        "retention_class": retention,
        "attempt_number": attempt_number,
        "status": req["status"],
        "producer_ref": str(req["producer_ref"]),
    }
    return run, common


def _validate_run(run: dict[str, Any]) -> None:
    required = (
        "run_id", "root_run_id", "trace_id", "correlation_id", "run_type", "started_at",
        "status", "spend_mode", "attempt_number", "environment_ref", "retention_class", "is_test",
    )
    missing = [field for field in required if field not in run or run[field] in (None, "")]
    if missing:
        raise ValueError(f"run missing required fields: {','.join(missing)}")
    if not isinstance(run["is_test"], bool):
        raise ValueError("run.is_test must be boolean")
    if not isinstance(run["status"], str) or not run["status"].strip():
        raise ValueError("run.status must be a non-empty string")
    _enum(run["run_type"], RUN_TYPES, "run_type")
    _enum(run["spend_mode"], SPEND_MODES, "spend_mode")
    _enum(run["retention_class"], RETENTION_CLASSES, "retention_class")
    _positive_int(run["attempt_number"], "attempt_number")
    _normalize_timestamp(run["started_at"], "started_at")


def _check_duplicate_business_ids(records: list[dict[str, Any]]) -> None:
    key_by_kind = {
        "event": "event_id",
        "action": "action_id",
        "metric": "metric_id",
        "error": "error_id",
        "approval": "approval_id",
    }
    seen: set[tuple[str, str]] = set()
    for record in records:
        key = key_by_kind[record["kind"]]
        identity = (record["kind"], str(record[key]))
        if identity in seen:
            raise ValueError(f"duplicate semantic business id: {identity[0]}:{identity[1]}")
        seen.add(identity)


def compile_request(req: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(req, dict):
        raise ValueError("caller request must be an object")
    for key in ("producer_ref", "activity_id", "status", "summary", "is_test"):
        if key not in req:
            raise ValueError(f"missing caller field: {key}")
    if not isinstance(req["is_test"], bool):
        raise ValueError("is_test must be boolean")
    if not isinstance(req["producer_ref"], str) or not req["producer_ref"].strip():
        raise ValueError("producer_ref must be a non-empty string")
    if not isinstance(req["status"], str) or not req["status"].strip():
        raise ValueError("status must be a non-empty string")
    if not isinstance(req["summary"], str) or not req["summary"].strip():
        raise ValueError("summary must be a non-empty string")

    _check_forbidden(req)

    profile = req.get("profile", "LIGHT")
    if profile not in {"LIGHT", "STANDARD", "DEEP"}:
        raise ValueError("invalid profile")

    refs = _merge_refs(req)
    common_time = _utc_now()
    run, common = _build_run(req, refs, common_time, profile)
    _validate_run(run)

    facts = dict(req.get("semantic_facts") or {})
    allowed_fact_kinds = {"action", "metric", "error", "approval"}
    unknown = sorted(key for key, value in facts.items() if key not in allowed_fact_kinds and value is not None)
    if unknown:
        raise ValueError(f"unsupported semantic_facts kind(s): {','.join(unknown)}")

    telemetry, facts = _normalize_telemetry(req, facts, common)

    event_supplied = {
        "event_id": req.get("event_id", _derive_child_id(common["run_id"], "event", 1)),
        "event_type": req.get("event_type", "GOVERNED_ACTIVITY_OUTCOME"),
        "severity": req.get("severity", "INFO" if req["status"] == "SUCCEEDED" else "WARNING"),
        "message_code": req.get("message_code", f"G11_{req['status']}"),
        "message_summary": str(req["summary"])[:1000],
        "artifact_ref": req.get("artifact_ref"),
        "source_ref": req.get("source_ref"),
    }
    event_supplied = {key: value for key, value in event_supplied.items() if value not in (None, "")}

    records: list[dict[str, Any]] = []
    sequence = 1
    records.append(_record("event", event_supplied, common, sequence, 1))
    sequence += 1

    for kind in ("action", "metric", "error", "approval"):
        entries = _as_record_list(facts.get(kind), kind)
        for ordinal, entry in enumerate(entries, start=1):
            records.append(_record(kind, entry, common, sequence, ordinal))
            sequence += 1

    _check_duplicate_business_ids(records)

    producer = {
        "surface": str(req.get("surface", "CHATGPT")),
        "producer_ref": str(req["producer_ref"]),
    }
    skill_id = _top_or_ref(req, refs, "skill_id")
    if _is_nonempty(skill_id):
        producer["skill_id"] = skill_id
    skill_version = _top_or_ref(req, refs, "skill_version")
    if _is_nonempty(skill_version):
        producer["skill_version"] = skill_version
    agent_id = _top_or_ref(req, refs, "agent_id")
    if _is_nonempty(agent_id):
        producer["agent_id"] = agent_id

    return {
        "envelope_version": ENVELOPE_VERSION,
        "contract": CONTRACT,
        "envelope_id": _safe_id(req["activity_id"]),
        "profile": profile,
        "producer": producer,
        "run": run,
        "semantic_records": records,
        "telemetry": telemetry,
        "refs": refs,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        raise SystemExit("usage: compile_caller_request.py CALLER.json ENVELOPE.json")
    req = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    env = compile_request(req)
    Path(argv[2]).write_text(json.dumps(env, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(env["envelope_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
