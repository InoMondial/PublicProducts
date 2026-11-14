import { config, db } from 'hatchable';

const TENANT_ID = config.GRAPH_TENANT_ID;
const SITE_ID = config.GRAPH_SITE_ID;
if (!TENANT_ID || !SITE_ID) throw new Error('EXTERNAL_GRAPH_PROFILE_REQUIRED');
const GRAPH_BASE = 'https://graph.microsoft.com/v1.0';
const LISTS = {
  "inc_runs": {
    "list_id": null,
    "display_name": "Runs",
    "target_table": "g11_runs",
    "semantic_id": "run_id",
    "columns": [
      {
        "source": "inc_run_id",
        "target": "run_id",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_parent_run_id",
        "target": "parent_run_id",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_root_run_id",
        "target": "root_run_id",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_trace_id",
        "target": "trace_id",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_correlation_id",
        "target": "correlation_id",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_run_type",
        "target": "run_type",
        "type": "Choice",
        "required": true
      },
      {
        "source": "inc_agent_id",
        "target": "agent_id",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_primary_skill_id",
        "target": "primary_skill_id",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_executing_skill_id",
        "target": "executing_skill_id",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_skill_version",
        "target": "skill_version",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_target_artifact_id",
        "target": "target_artifact_id",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_target_artifact_version_id",
        "target": "target_artifact_version_id",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_work_ref",
        "target": "work_ref",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_started_at",
        "target": "started_at",
        "type": "DateTimeUTC",
        "required": true
      },
      {
        "source": "inc_ended_at",
        "target": "ended_at",
        "type": "DateTimeUTC",
        "required": false
      },
      {
        "source": "inc_status",
        "target": "status",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_execution_tier",
        "target": "execution_tier",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_reasoning_effort",
        "target": "reasoning_effort",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_spend_mode",
        "target": "spend_mode",
        "type": "Choice",
        "required": true
      },
      {
        "source": "inc_resource_state",
        "target": "resource_state",
        "type": "Choice",
        "required": false
      },
      {
        "source": "inc_budget_policy_ref",
        "target": "budget_policy_ref",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_attempt_number",
        "target": "attempt_number",
        "type": "NumberInteger",
        "required": true
      },
      {
        "source": "inc_environment_ref",
        "target": "environment_ref",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_trigger_type",
        "target": "trigger_type",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_result_summary",
        "target": "result_summary",
        "type": "MultipleLinesTextPlain",
        "required": false
      },
      {
        "source": "inc_result_ref",
        "target": "result_ref",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_retention_class",
        "target": "retention_class",
        "type": "Choice",
        "required": true
      },
      {
        "source": "inc_is_test",
        "target": "is_test",
        "type": "YesNo",
        "required": true
      },
      {
        "source": "inc_partition_month",
        "target": "partition_month",
        "type": "SingleLineText",
        "required": false
      }
    ]
  },
  "inc_events": {
    "list_id": null,
    "display_name": "Events",
    "target_table": "g11_events",
    "semantic_id": "event_id",
    "columns": [
      {
        "source": "inc_event_id",
        "target": "event_id",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_run_id",
        "target": "run_id",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_sequence_number",
        "target": "sequence_number",
        "type": "NumberInteger",
        "required": true
      },
      {
        "source": "inc_timestamp",
        "target": "timestamp",
        "type": "DateTimeUTC",
        "required": true
      },
      {
        "source": "inc_component_role",
        "target": "component_role",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_event_type",
        "target": "event_type",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_severity",
        "target": "severity",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_message_code",
        "target": "message_code",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_message_summary",
        "target": "message_summary",
        "type": "MultipleLinesTextPlain",
        "required": true
      },
      {
        "source": "inc_artifact_ref",
        "target": "artifact_ref",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_source_ref",
        "target": "source_ref",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_data_classification",
        "target": "data_classification",
        "type": "Choice",
        "required": true
      },
      {
        "source": "inc_retention_class",
        "target": "retention_class",
        "type": "Choice",
        "required": true
      },
      {
        "source": "inc_is_test",
        "target": "is_test",
        "type": "YesNo",
        "required": true
      },
      {
        "source": "inc_partition_month",
        "target": "partition_month",
        "type": "SingleLineText",
        "required": false
      }
    ]
  },
  "inc_actions": {
    "list_id": null,
    "display_name": "Actions",
    "target_table": "g11_actions",
    "semantic_id": "action_id",
    "columns": [
      {
        "source": "inc_action_id",
        "target": "action_id",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_run_id",
        "target": "run_id",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_parent_action_id",
        "target": "parent_action_id",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_sequence_number",
        "target": "sequence_number",
        "type": "NumberInteger",
        "required": true
      },
      {
        "source": "inc_span_id",
        "target": "span_id",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_parent_span_id",
        "target": "parent_span_id",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_timestamp",
        "target": "timestamp",
        "type": "DateTimeUTC",
        "required": true
      },
      {
        "source": "inc_started_at",
        "target": "started_at",
        "type": "DateTimeUTC",
        "required": false
      },
      {
        "source": "inc_ended_at",
        "target": "ended_at",
        "type": "DateTimeUTC",
        "required": false
      },
      {
        "source": "inc_component_role",
        "target": "component_role",
        "type": "Choice",
        "required": true
      },
      {
        "source": "inc_actor_ref",
        "target": "actor_ref",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_action_type",
        "target": "action_type",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_tool_or_model",
        "target": "tool_or_model",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_target_ref",
        "target": "target_ref",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_risk_level",
        "target": "risk_level",
        "type": "Choice",
        "required": true
      },
      {
        "source": "inc_data_classification",
        "target": "data_classification",
        "type": "Choice",
        "required": true
      },
      {
        "source": "inc_approval_id",
        "target": "approval_id",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_attempt_number",
        "target": "attempt_number",
        "type": "NumberInteger",
        "required": true
      },
      {
        "source": "inc_result_status",
        "target": "result_status",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_result_ref",
        "target": "result_ref",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_is_test",
        "target": "is_test",
        "type": "YesNo",
        "required": true
      },
      {
        "source": "inc_partition_month",
        "target": "partition_month",
        "type": "SingleLineText",
        "required": false
      }
    ]
  },
  "inc_metrics": {
    "list_id": null,
    "display_name": "Metrics",
    "target_table": "g11_metrics",
    "semantic_id": "metric_id",
    "columns": [
      {
        "source": "inc_metric_id",
        "target": "metric_id",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_run_id",
        "target": "run_id",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_action_id",
        "target": "action_id",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_timestamp",
        "target": "timestamp",
        "type": "DateTimeUTC",
        "required": true
      },
      {
        "source": "inc_metric_scope",
        "target": "metric_scope",
        "type": "Choice",
        "required": true
      },
      {
        "source": "inc_model_call_id",
        "target": "model_call_id",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_provider_request_id",
        "target": "provider_request_id",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_provider_response_id",
        "target": "provider_response_id",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_provider",
        "target": "provider",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_provider_account_ref",
        "target": "provider_account_ref",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_provider_project_ref",
        "target": "provider_project_ref",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_request_model",
        "target": "request_model",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_response_model",
        "target": "response_model",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_model_version",
        "target": "model_version",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_operation_name",
        "target": "operation_name",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_service_tier",
        "target": "service_tier",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_batch",
        "target": "batch",
        "type": "YesNo",
        "required": false
      },
      {
        "source": "inc_reasoning_effort",
        "target": "reasoning_effort",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_est_input_tokens_before",
        "target": "estimated_input_tokens_before",
        "type": "Number",
        "required": false
      },
      {
        "source": "inc_est_total_tokens_before",
        "target": "estimated_total_tokens_before",
        "type": "Number",
        "required": false
      },
      {
        "source": "inc_input_tokens",
        "target": "input_tokens",
        "type": "Number",
        "required": false
      },
      {
        "source": "inc_output_tokens",
        "target": "output_tokens",
        "type": "Number",
        "required": false
      },
      {
        "source": "inc_total_tokens",
        "target": "total_tokens",
        "type": "Number",
        "required": false
      },
      {
        "source": "inc_cache_read_input_tokens",
        "target": "cache_read_input_tokens",
        "type": "Number",
        "required": false
      },
      {
        "source": "inc_cache_creation_input_tokens",
        "target": "cache_creation_input_tokens",
        "type": "Number",
        "required": false
      },
      {
        "source": "inc_reasoning_output_tokens",
        "target": "reasoning_output_tokens",
        "type": "Number",
        "required": false
      },
      {
        "source": "inc_input_audio_tokens",
        "target": "input_audio_tokens",
        "type": "Number",
        "required": false
      },
      {
        "source": "inc_output_audio_tokens",
        "target": "output_audio_tokens",
        "type": "Number",
        "required": false
      },
      {
        "source": "inc_billable_tokens",
        "target": "billable_tokens",
        "type": "Number",
        "required": false
      },
      {
        "source": "inc_cost_value",
        "target": "cost_value",
        "type": "Number",
        "required": false
      },
      {
        "source": "inc_cost_currency",
        "target": "cost_currency",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_cost_source",
        "target": "cost_source",
        "type": "Choice",
        "required": true
      },
      {
        "source": "inc_pricing_profile_id",
        "target": "pricing_profile_id",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_tool_cost_value",
        "target": "tool_cost_value",
        "type": "Number",
        "required": false
      },
      {
        "source": "inc_tool_cost_currency",
        "target": "tool_cost_currency",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_credits_consumed",
        "target": "credits_consumed",
        "type": "Number",
        "required": false
      },
      {
        "source": "inc_usage_unit",
        "target": "usage_unit",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_credit_source",
        "target": "credit_source",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_tool_calls",
        "target": "tool_calls",
        "type": "NumberInteger",
        "required": false
      },
      {
        "source": "inc_latency_ms",
        "target": "latency_ms",
        "type": "Number",
        "required": false
      },
      {
        "source": "inc_time_to_first_token_ms",
        "target": "time_to_first_token_ms",
        "type": "Number",
        "required": false
      },
      {
        "source": "inc_finish_reason",
        "target": "finish_reason",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_usage_source",
        "target": "usage_source",
        "type": "Choice",
        "required": true
      },
      {
        "source": "inc_attributed_skill_id",
        "target": "attributed_skill_id",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_attribution_method",
        "target": "attribution_method",
        "type": "Choice",
        "required": true
      },
      {
        "source": "inc_attribution_confidence",
        "target": "attribution_confidence",
        "type": "Number",
        "required": false
      },
      {
        "source": "inc_provider_usage_raw_json",
        "target": "provider_usage_raw_json",
        "type": "MultipleLinesTextPlain",
        "required": false
      },
      {
        "source": "inc_provider_usage_raw_ref",
        "target": "provider_usage_raw_ref",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_normalization_schema_version",
        "target": "normalization_schema_version",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_otel_semconv_version",
        "target": "otel_semconv_version",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_token_acct_check_status",
        "target": "token_accounting_check_status",
        "type": "Choice",
        "required": true
      },
      {
        "source": "inc_is_test",
        "target": "is_test",
        "type": "YesNo",
        "required": true
      },
      {
        "source": "inc_partition_month",
        "target": "partition_month",
        "type": "SingleLineText",
        "required": false
      }
    ]
  },
  "inc_errors": {
    "list_id": null,
    "display_name": "Errors",
    "target_table": "g11_errors",
    "semantic_id": "error_id",
    "columns": [
      {
        "source": "inc_error_id",
        "target": "error_id",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_run_id",
        "target": "run_id",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_action_id",
        "target": "action_id",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_timestamp",
        "target": "timestamp",
        "type": "DateTimeUTC",
        "required": true
      },
      {
        "source": "inc_error_code",
        "target": "error_code",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_provider_error_code",
        "target": "provider_error_code",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_stage",
        "target": "stage",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_severity",
        "target": "severity",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_retry_count",
        "target": "retry_count",
        "type": "NumberInteger",
        "required": true
      },
      {
        "source": "inc_resolution_status",
        "target": "resolution_status",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_resolved_by_action_id",
        "target": "resolved_by_action_id",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_diagnostic_summary",
        "target": "diagnostic_summary",
        "type": "MultipleLinesTextPlain",
        "required": false
      },
      {
        "source": "inc_diagnostic_ref",
        "target": "diagnostic_ref",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_is_test",
        "target": "is_test",
        "type": "YesNo",
        "required": true
      }
    ]
  },
  "inc_approvals": {
    "list_id": null,
    "display_name": "Approvals",
    "target_table": "g11_approvals",
    "semantic_id": "approval_id",
    "columns": [
      {
        "source": "inc_approval_id",
        "target": "approval_id",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_run_id",
        "target": "run_id",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_action_id",
        "target": "action_id",
        "type": "SingleLineText",
        "required": false
      },
      {
        "source": "inc_action_summary",
        "target": "action_summary",
        "type": "MultipleLinesTextPlain",
        "required": true
      },
      {
        "source": "inc_risk_level",
        "target": "risk_level",
        "type": "Choice",
        "required": true
      },
      {
        "source": "inc_requested_at",
        "target": "requested_at",
        "type": "DateTimeUTC",
        "required": true
      },
      {
        "source": "inc_decision",
        "target": "decision",
        "type": "Choice",
        "required": true
      },
      {
        "source": "inc_decided_at",
        "target": "decided_at",
        "type": "DateTimeUTC",
        "required": false
      },
      {
        "source": "inc_approver_ref",
        "target": "approver_ref",
        "type": "SingleLineText",
        "required": true
      },
      {
        "source": "inc_scope_summary",
        "target": "scope_summary",
        "type": "MultipleLinesTextPlain",
        "required": true
      },
      {
        "source": "inc_is_test",
        "target": "is_test",
        "type": "YesNo",
        "required": true
      }
    ]
  }
};
for (const [alias, spec] of Object.entries(LISTS)) {
  spec.list_id = config.GRAPH_LIST_BINDINGS?.[alias];
  if (!spec.list_id) throw new Error('EXTERNAL_LIST_BINDING_REQUIRED');
}


function fail(code, detail = null) {
  const e = new Error(code);
  e.code = code;
  e.detail = detail;
  return e;
}

function safeRef(identity) {
  const user = identity?.user || null;
  const app = identity?.application || null;
  const value = user?.email || user?.displayName || user?.id || app?.displayName || app?.id || null;
  return value ? String(value).slice(0, 255) : null;
}

function normalizeByType(value, type) {
  if (value === undefined || value === null || value === '') return null;
  if (type === 'YesNo') return Boolean(value);
  if (type === 'NumberInteger') {
    const n = Number(value);
    return Number.isFinite(n) ? Math.trunc(n) : null;
  }
  if (type === 'Number') {
    const n = Number(value);
    return Number.isFinite(n) ? n : null;
  }
  if (type === 'DateTimeUTC') {
    const d = new Date(value);
    return Number.isNaN(d.getTime()) ? null : d.toISOString();
  }
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

function canonical(value) {
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  if (value && typeof value === 'object') {
    return '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + canonical(value[k])).join(',') + '}';
  }
  return JSON.stringify(value);
}

async function sha256Text(value) {
  const bytes = new TextEncoder().encode(value);
  const digest = new Uint8Array(await crypto.subtle.digest('SHA-256', bytes));
  return [...digest].map(v => v.toString(16).padStart(2, '0')).join('');
}

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function fetchWithRetry(url, init = {}, label = 'GRAPH_FETCH') {
  const delays = [0, 400, 1200, 2500];
  let lastError = null;
  for (let i = 0; i < delays.length; i++) {
    if (delays[i]) await sleep(delays[i]);
    try {
      const response = await fetch(url, init);
      if (![429, 502, 503, 504].includes(response.status)) return response;
      lastError = fail(label + '_RETRYABLE_HTTP', { status: response.status, attempt: i + 1 });
      const retryAfter = Number(response.headers?.get?.('retry-after'));
      if (Number.isFinite(retryAfter) && retryAfter > 0 && i < delays.length - 1) {
        await sleep(Math.min(retryAfter * 1000, 5000));
      }
    } catch (error) {
      const code = String(error?.code || error?.message || '');
      lastError = error;
      if (!/rate[_ -]?limit|timeout|temporar|fetch/i.test(code) || i === delays.length - 1) throw error;
    }
  }
  throw lastError || fail(label + '_RETRY_EXHAUSTED');
}

async function dbQueryWithRetry(sql, params = []) {
  const delays = [0, 120, 350, 800, 1600];
  let lastError = null;
  for (let i = 0; i < delays.length; i++) {
    if (delays[i]) await sleep(delays[i]);
    try {
      return await db.query(sql, params);
    } catch (error) {
      lastError = error;
      const code = String(error?.code || error?.message || error || '');
      if (!/rate[_ -]?limit|too many|temporar|timeout|busy/i.test(code) || i === delays.length - 1) throw error;
    }
  }
  throw lastError || fail('DB_RETRY_EXHAUSTED');
}

async function getToken() {
  const enabled = String(await config.get('inc_g17_graph_egress_enabled') || '').toLowerCase() === 'true';
  if (!enabled) throw fail('GRAPH_EGRESS_DISABLED');
  const clientId = String(await config.get('inc_g17_graph_client_id') || '').trim();
  const clientSecret = await config.get('INC_G17_GRAPH_CLIENT_SECRET');
  if (!clientId || !clientSecret) throw fail('GRAPH_AUTH_CONFIGURATION_MISSING');

  const body = new URLSearchParams({
    client_id: clientId,
    client_secret: clientSecret,
    grant_type: 'client_credentials',
    scope: 'https://graph.microsoft.com/.default'
  });
  const response = await fetchWithRetry('https://login.microsoftonline.com/' + TENANT_ID + '/oauth2/v2.0/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body
  }, 'GRAPH_TOKEN');
  if (!response.ok) throw fail('GRAPH_TOKEN_ACQUISITION_FAILED', { status: response.status });
  const payload = await response.json();
  if (!payload?.access_token) throw fail('GRAPH_TOKEN_RESPONSE_INVALID');
  return payload.access_token;
}

async function graph(token, pathOrUrl) {
  const url = pathOrUrl.startsWith('https://') ? pathOrUrl : GRAPH_BASE + pathOrUrl;
  const response = await fetchWithRetry(url, { headers: { Authorization: 'Bearer ' + token } }, 'GRAPH_REQUEST');
  if (!response.ok) {
    let detail = null;
    try { detail = await response.json(); } catch {}
    throw fail('GRAPH_REQUEST_FAILED', { status: response.status, detail });
  }
  return response.json();
}

function sourceValue(fields, sourceName) {
  if (Object.prototype.hasOwnProperty.call(fields, sourceName)) return fields[sourceName];
  const lower = sourceName.toLowerCase();
  const key = Object.keys(fields).find(k => k.toLowerCase() === lower);
  return key ? fields[key] : undefined;
}

async function normalizeItem(spec, item) {
  const fields = item.fields || {};
  const data = {};
  const missingRequired = [];
  for (const col of spec.columns) {
    const v = normalizeByType(sourceValue(fields, col.source), col.type);
    if (col.required && (v === null || v === '')) missingRequired.push(col.target);
    data[col.target] = v;
  }
  const semanticId = data[spec.semantic_id];
  if (!semanticId) missingRequired.push(spec.semantic_id);
  const legacySpId = Number(item.id);
  if (!Number.isFinite(legacySpId)) throw fail('INVALID_SHAREPOINT_ITEM_ID', { id: item.id });

  const hashPayload = {
    list_id: spec.list_id,
    item_id: String(item.id),
    fields: data,
    createdDateTime: item.createdDateTime || null,
    lastModifiedDateTime: item.lastModifiedDateTime || null
  };
  const rawHashPayload = {
    list_id: spec.list_id,
    item_id: String(item.id),
    fields,
    createdDateTime: item.createdDateTime || null,
    lastModifiedDateTime: item.lastModifiedDateTime || null
  };
  return {
    data,
    rawFields: fields,
    semanticId,
    legacySpId,
    createdAt: item.createdDateTime || null,
    modifiedAt: item.lastModifiedDateTime || null,
    authorRef: safeRef(item.createdBy),
    editorRef: safeRef(item.lastModifiedBy),
    rowHash: await sha256Text(canonical(hashPayload)),
    rawRowHash: await sha256Text(canonical(rawHashPayload)),
    missingRequired
  };
}

function qident(v) {
  if (!/^[a-z_][a-z0-9_]*$/.test(v)) throw fail('UNSAFE_IDENTIFIER');
  return '"' + v + '"';
}

const LEGACY_INCOMPLETE_CUTOFF_MS = Date.parse('2026-08-17T06:00:00Z');

function expressionResidueFields(fields) {
  const bad = [];
  for (const [field, value] of Object.entries(fields || {})) {
    if (typeof value === 'string' && /(body\(|items\()/i.test(value)) {
      bad.push(field);
    }
  }
  return bad.sort();
}

function anomalyReasons(logical, normalized, canonicalRunIds = null) {
  const reasons = [];
  if (normalized.missingRequired.length) {
    reasons.push({ code: 'MISSING_REQUIRED_FIELDS', fields: normalized.missingRequired });
  }
  const expressionFields = expressionResidueFields(normalized.rawFields);
  if (expressionFields.length) {
    reasons.push({ code: 'POWER_AUTOMATE_EXPRESSION_RESIDUE', fields: expressionFields });
  }
  if (logical !== 'inc_runs' && canonicalRunIds) {
    const runId = normalized.data.run_id ? String(normalized.data.run_id) : null;
    if (runId && !canonicalRunIds.has(runId)) {
      reasons.push({ code: 'PARENT_RUN_NOT_CANONICAL', run_id: runId });
    }
  }
  return reasons;
}

function legacyAnomalyDisposition(normalized, reasons) {
  if (!reasons.length) return null;
  const modifiedMs = Date.parse(normalized.modifiedAt || normalized.createdAt || '');
  return Number.isFinite(modifiedMs) && modifiedMs <= LEGACY_INCOMPLETE_CUTOFF_MS
    ? 'LEGACY_PRE_REMEDIATION_ANOMALY'
    : 'INVALID_SOURCE_ANOMALY';
}

async function loadExisting(spec) {
  const table = qident(spec.target_table);
  const sem = qident(spec.semantic_id);
  const { rows } = await dbQueryWithRetry(
    `SELECT id, ${sem} AS semantic_id, legacy_sp_id, legacy_modified_at, legacy_row_hash
       FROM ${table}
      ORDER BY id`
  );
  const bySemantic = new Map();
  const byLegacy = new Map();
  for (const row of rows) {
    if (row.semantic_id !== null && row.semantic_id !== undefined) bySemantic.set(String(row.semantic_id), row);
    if (row.legacy_sp_id !== null && row.legacy_sp_id !== undefined) byLegacy.set(String(row.legacy_sp_id), row);
  }
  return { bySemantic, byLegacy };
}

async function preserveLegacyAnomaly(logical, spec, normalized, reasons, mode) {
  if (mode === 'preflight') {
    return {
      state: 'WOULD_QUARANTINE',
      semantic_id: normalized.semanticId,
      legacy_sp_id: normalized.legacySpId,
      reasons
    };
  }
  await sleep(80);
  await dbQueryWithRetry(
    `INSERT INTO g11_legacy_quarantine
      (project_ref, source_list_logical, source_list_id, legacy_sp_id, semantic_id,
       created_at_source, modified_at_source, missing_required, anomaly_reasons,
       raw_fields, row_hash, classification)
     VALUES ($1,$2,$3,$4,$5,$6,$7,$8::jsonb,$9::jsonb,$10::jsonb,$11,$12)
     ON CONFLICT (source_list_id, legacy_sp_id) DO UPDATE SET
       semantic_id = EXCLUDED.semantic_id,
       created_at_source = EXCLUDED.created_at_source,
       modified_at_source = EXCLUDED.modified_at_source,
       missing_required = EXCLUDED.missing_required,
       anomaly_reasons = EXCLUDED.anomaly_reasons,
       raw_fields = EXCLUDED.raw_fields,
       row_hash = EXCLUDED.row_hash,
       classification = EXCLUDED.classification,
       preserved_at = now()
     WHERE g11_legacy_quarantine.modified_at_source IS NULL
        OR EXCLUDED.modified_at_source IS NULL
        OR EXCLUDED.modified_at_source >= g11_legacy_quarantine.modified_at_source`,
    [
      'PRJ_MISC',
      logical,
      spec.list_id,
      normalized.legacySpId,
      normalized.semanticId ? String(normalized.semanticId) : null,
      normalized.createdAt,
      normalized.modifiedAt,
      JSON.stringify(normalized.missingRequired),
      JSON.stringify(reasons),
      JSON.stringify(normalized.rawFields || {}),
      normalized.rawRowHash,
      'LEGACY_PRE_REMEDIATION_ANOMALY'
    ]
  );
  return {
    state: 'QUARANTINED_LEGACY_ANOMALY',
    semantic_id: normalized.semanticId,
    legacy_sp_id: normalized.legacySpId,
    reasons
  };
}

async function upsertItem(logical, spec, normalized, mode, existing, canonicalRunIds) {
  const reasons = anomalyReasons(logical, normalized, canonicalRunIds);
  const disposition = legacyAnomalyDisposition(normalized, reasons);
  if (disposition === 'LEGACY_PRE_REMEDIATION_ANOMALY') {
    return preserveLegacyAnomaly(logical, spec, normalized, reasons, mode);
  }
  if (disposition === 'INVALID_SOURCE_ANOMALY') {
    return {
      state: 'INVALID_SOURCE_ANOMALY',
      semantic_id: normalized.semanticId,
      legacy_sp_id: normalized.legacySpId,
      reasons
    };
  }

  const table = qident(spec.target_table);
  const semanticKey = String(normalized.semanticId);
  const legacyKey = String(normalized.legacySpId);
  const bySemantic = existing.bySemantic.get(semanticKey) || null;
  const byLegacy = existing.byLegacy.get(legacyKey) || null;

  if (bySemantic && byLegacy && bySemantic.id !== byLegacy.id) {
    return { state: 'CONFLICT_MULTIPLE_MATCHES', semantic_id: normalized.semanticId, legacy_sp_id: normalized.legacySpId };
  }
  const row = bySemantic || byLegacy || null;

  if (row) {
    const sameSemantic = String(row.semantic_id) === semanticKey;
    const sameLegacy = Number(row.legacy_sp_id) === normalized.legacySpId;
    if (!sameSemantic || !sameLegacy) {
      return { state: 'CONFLICT_IDENTITY', semantic_id: normalized.semanticId, legacy_sp_id: normalized.legacySpId };
    }
    if (row.legacy_row_hash === normalized.rowHash) {
      return { state: 'UNCHANGED', semantic_id: normalized.semanticId, legacy_sp_id: normalized.legacySpId };
    }
    const oldModified = row.legacy_modified_at ? new Date(row.legacy_modified_at).getTime() : 0;
    const newModified = normalized.modifiedAt ? new Date(normalized.modifiedAt).getTime() : 0;
    if (newModified < oldModified) {
      return { state: 'CONFLICT_OLDER_SOURCE', semantic_id: normalized.semanticId, legacy_sp_id: normalized.legacySpId };
    }
    if (mode === 'preflight') return { state: 'WOULD_UPDATE', semantic_id: normalized.semanticId, legacy_sp_id: normalized.legacySpId };

    const cols = spec.columns.map(col => col.target);
    const sets = cols.map((col,i)=>qident(col)+' = $'+(i+1));
    const params = cols.map(col=>normalized.data[col]);
    const base = params.length;
    sets.push('legacy_created_at = $'+(base+1));
    sets.push('legacy_modified_at = $'+(base+2));
    sets.push('legacy_author_ref = $'+(base+3));
    sets.push('legacy_editor_ref = $'+(base+4));
    sets.push('legacy_row_hash = $'+(base+5));
    sets.push('source_system = $'+(base+6));
    sets.push('migrated_at = now()');
    params.push(normalized.createdAt, normalized.modifiedAt, normalized.authorRef, normalized.editorRef, normalized.rowHash, 'SHAREPOINT_LIST:' + spec.list_id, row.id);
    await sleep(80);
    await dbQueryWithRetry(`UPDATE ${table} SET ${sets.join(', ')} WHERE id = $${base+7}`, params);
    const updated = { ...row, legacy_modified_at: normalized.modifiedAt, legacy_row_hash: normalized.rowHash };
    existing.bySemantic.set(semanticKey, updated);
    existing.byLegacy.set(legacyKey, updated);
    return { state: 'UPDATED', semantic_id: normalized.semanticId, legacy_sp_id: normalized.legacySpId };
  }

  if (mode === 'preflight') return { state: 'WOULD_INSERT', semantic_id: normalized.semanticId, legacy_sp_id: normalized.legacySpId };

  const cols = ['project_ref','workload_ref', ...spec.columns.map(col=>col.target), 'legacy_sp_id','legacy_created_at','legacy_modified_at','legacy_author_ref','legacy_editor_ref','legacy_row_hash','source_system'];
  const values = [
    'PRJ_MISC',
    normalized.data.work_ref || ('G11:' + spec.target_table),
    ...spec.columns.map(col=>normalized.data[col.target]),
    normalized.legacySpId,
    normalized.createdAt,
    normalized.modifiedAt,
    normalized.authorRef,
    normalized.editorRef,
    normalized.rowHash,
    'SHAREPOINT_LIST:' + spec.list_id
  ];
  const placeholders = values.map((_,i)=>'$'+(i+1));
  await sleep(80);
  const inserted = await dbQueryWithRetry(`INSERT INTO ${table} (${cols.map(qident).join(', ')}) VALUES (${placeholders.join(', ')}) RETURNING id`, values);
  const cached = {
    id: inserted.rows[0]?.id,
    semantic_id: normalized.semanticId,
    legacy_sp_id: normalized.legacySpId,
    legacy_modified_at: normalized.modifiedAt,
    legacy_row_hash: normalized.rowHash
  };
  existing.bySemantic.set(semanticKey, cached);
  existing.byLegacy.set(legacyKey, cached);
  return { state: 'INSERTED', semantic_id: normalized.semanticId, legacy_sp_id: normalized.legacySpId };
}

async function enumerateList(token, spec, handler, maxItems = null) {
  let next = GRAPH_BASE + '/sites/' + encodeURIComponent(SITE_ID) + '/lists/' + encodeURIComponent(spec.list_id)
    + '/items?$expand=fields&$top=200';
  let count = 0;
  while (next) {
    const page = await graph(token, next);
    for (const item of page.value || []) {
      count++;
      await handler(item);
      if (maxItems && count >= maxItems) return count;
    }
    next = page['@odata.nextLink'] || null;
  }
  return count;
}

export async function g11GraphPreflight() {
  const token = await getToken();
  const site = await graph(token, '/sites/' + encodeURIComponent(SITE_ID) + '?$select=id,displayName,webUrl');
  const results = {};
  for (const [logical, spec] of Object.entries(LISTS)) {
    const meta = await graph(token, '/sites/' + encodeURIComponent(SITE_ID) + '/lists/' + encodeURIComponent(spec.list_id) + '?$select=id,displayName,webUrl');
    let sample = null;
    await enumerateList(token, spec, async item => {
      if (!sample) {
        const n = await normalizeItem(spec, item);
        sample = { semantic_id_present: Boolean(n.semanticId), missing_required: n.missingRequired, legacy_sp_id: n.legacySpId };
      }
    }, 1);
    results[logical] = { meta, sample };
  }
  return { ok: true, site, lists: results };
}

export async function g11Backfill({ mode = 'preflight', maxPerList = null } = {}) {
  if (!['preflight','backfill'].includes(mode)) throw fail('INVALID_MODE');
  const token = await getToken();
  const sourceItems = {};
  for (const [logical, spec] of Object.entries(LISTS)) {
    const items = [];
    await enumerateList(token, spec, async item => items.push(item), maxPerList);
    sourceItems[logical] = items;
    await sleep(50);
  }

  const canonicalRunIds = new Set();
  for (const item of sourceItems.inc_runs || []) {
    const normalized = await normalizeItem(LISTS.inc_runs, item);
    if (anomalyReasons('inc_runs', normalized, null).length === 0 && normalized.semanticId) {
      canonicalRunIds.add(String(normalized.semanticId));
    }
  }

  const report = {};
  let unresolved = 0;
  let quarantinedOrWouldQuarantine = 0;
  let targetExtras = 0;

  for (const [logical, spec] of Object.entries(LISTS)) {
    const existing = await loadExisting(spec);
    const canonicalSourceIds = new Set();
    const stats = {
      scanned: 0,
      INSERTED: 0,
      UPDATED: 0,
      UNCHANGED: 0,
      WOULD_INSERT: 0,
      WOULD_UPDATE: 0,
      WOULD_QUARANTINE: 0,
      QUARANTINED_LEGACY_ANOMALY: 0,
      INVALID_SOURCE_ANOMALY: 0,
      CONFLICT_IDENTITY: 0,
      CONFLICT_MULTIPLE_MATCHES: 0,
      CONFLICT_OLDER_SOURCE: 0
    };
    const examples = [];

    for (const item of sourceItems[logical] || []) {
      stats.scanned++;
      const normalized = await normalizeItem(spec, item);
      const reasons = anomalyReasons(logical, normalized, canonicalRunIds);
      if (!reasons.length && normalized.semanticId) canonicalSourceIds.add(String(normalized.semanticId));
      const result = await upsertItem(logical, spec, normalized, mode, existing, canonicalRunIds);
      stats[result.state] = (stats[result.state] || 0) + 1;
      if (result.state === 'WOULD_QUARANTINE' || result.state === 'QUARANTINED_LEGACY_ANOMALY') {
        quarantinedOrWouldQuarantine++;
      }
      if (/^CONFLICT_|^INVALID_/.test(result.state)) {
        unresolved++;
        if (examples.length < 10) examples.push(result);
      }
    }

    const extras = [...existing.bySemantic.keys()].filter(id => !canonicalSourceIds.has(id));
    if (extras.length) {
      targetExtras += extras.length;
      unresolved += extras.length;
    }
    report[logical] = {
      list_id: spec.list_id,
      target_table: spec.target_table,
      stats,
      target_extra_count: extras.length,
      target_extra_examples: extras.slice(0, 10),
      unresolved_examples: examples
    };
  }

  return {
    ok: unresolved === 0,
    mode,
    project_ref_policy: 'PRJ_MISC_FOR_LEGACY_UNATTRIBUTED',
    legacy_anomaly_policy: 'PRESERVE_EXACT_RAW_SOURCE_IN_G11_LEGACY_QUARANTINE_BEFORE_2026_08_17T06_00_00Z',
    canonical_run_count: canonicalRunIds.size,
    unresolved,
    target_extras: targetExtras,
    quarantined_or_would_quarantine: quarantinedOrWouldQuarantine,
    report
  };
}
// Host setup must resolve physical IDs; never export resolved bindings.
