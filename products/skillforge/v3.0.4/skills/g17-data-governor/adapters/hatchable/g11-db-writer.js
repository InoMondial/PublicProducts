import { db } from 'hatchable';
import { persistVerifiedRows } from 'lib/g11-write-integrity.js';

const SOURCE_SYSTEM = 'G11_DB_ADAPTER_V1';

function fail(code, detail = null) {
  const e = new Error(code);
  e.code = code;
  e.detail = detail;
  return e;
}

function projectRef(envelope) {
  const refs = envelope?.refs?.project_ref, run = envelope?.run?.project_ref;
  if (refs != null && run != null && refs !== run) throw fail('G11_PROJECT_REFERENCE_MISMATCH');
  const p = refs ?? run ?? 'PRJ_MISC';
  if (typeof p !== 'string' || !p.trim() || p !== p.trim() || p.length > 128) throw fail('PROJECT_CONTEXT_REQUIRED');
  return p;
}

function workloadRef(envelope) {
  const v = envelope?.refs?.workload_ref || envelope?.producer?.producer_ref || envelope?.envelope_id || null;
  return v ? String(v).slice(0,255) : null;
}

function partitionMonth(timestamp) {
  const d = new Date(timestamp);
  if (Number.isNaN(d.getTime())) return null;
  return d.toISOString().slice(0,7);
}

function vals(obj, keys) {
  return keys.map(k => obj?.[k] ?? null);
}

function statement(table, idColumn, keys, row, project_ref, workload_ref) {
  return { table, idColumn, row: Object.fromEntries([
    ['project_ref', project_ref], ['workload_ref', workload_ref],
    ...keys.map(k => [k, row?.[k] ?? null]), ['source_system', SOURCE_SYSTEM]
  ]) };
}

const RUN_KEYS = [
  'run_id','parent_run_id','root_run_id','trace_id','correlation_id','run_type','agent_id',
  'primary_skill_id','executing_skill_id','skill_version','target_artifact_id',
  'target_artifact_version_id','work_ref','started_at','ended_at','status','execution_tier',
  'reasoning_effort','spend_mode','resource_state','budget_policy_ref','attempt_number',
  'environment_ref','trigger_type','result_summary','result_ref','retention_class','is_test',
  'partition_month','provider_account_ref','provider_workspace_ref','account_purpose','surface_ref','host_ref'
];

const EVENT_KEYS = [
  'event_id','run_id','sequence_number','timestamp','component_role','event_type','severity',
  'message_code','message_summary','data_classification','retention_class','artifact_ref',
  'source_ref','is_test','partition_month'
];

const ACTION_KEYS = [
  'action_id','run_id','parent_action_id','sequence_number','span_id','parent_span_id',
  'timestamp','started_at','ended_at','component_role','actor_ref','action_type','tool_or_model',
  'target_ref','risk_level','data_classification','approval_id','attempt_number','result_status',
  'result_ref','is_test','partition_month'
];

const METRIC_KEYS = [
  'metric_id','run_id','action_id','timestamp','metric_scope','model_call_id',
  'provider_request_id','provider_response_id','provider',
  'provider_account_ref','provider_project_ref','request_model','response_model','model_version',
  'operation_name','service_tier','batch','reasoning_effort','estimated_input_tokens_before',
  'estimated_total_tokens_before','input_tokens','output_tokens','total_tokens',
  'cache_read_input_tokens','cache_creation_input_tokens','reasoning_output_tokens',
  'input_audio_tokens','output_audio_tokens','billable_tokens','cost_value','cost_currency',
  'cost_source','pricing_profile_id','tool_cost_value','tool_cost_currency','credits_consumed',
  'usage_unit','credit_source','tool_calls','latency_ms','time_to_first_token_ms','finish_reason',
  'usage_source','attributed_skill_id','attribution_method','attribution_confidence',
  'provider_usage_raw_json','provider_usage_raw_ref','normalization_schema_version',
  'otel_semconv_version','token_accounting_check_status','is_test','partition_month',
  'billing_mode','measurement_status','measurement_scope','source_priority','source_observed_at'
];

const ERROR_KEYS = [
  'error_id','run_id','action_id','timestamp','error_code','provider_error_code','stage','severity',
  'retry_count','resolution_status','resolved_by_action_id','diagnostic_summary','diagnostic_ref','is_test'
];

const APPROVAL_KEYS = [
  'approval_id','run_id','action_id','action_summary','risk_level','requested_at','decision',
  'decided_at','approver_ref','scope_summary','is_test'
];

export function g11WriteCapabilities() {
  return {ok:true, contract:'INC_G11_G17_WRITE_CAPABILITIES_V1',
    route:'INC_G11_G17_DB_WRITE_ROUTE_V1', envelope_version:'1.1',
    idempotency:'IMMUTABLE_EXACT_REPLAY', project_scoped:true, max_semantic_records:199,
    field_sets:{run:[...RUN_KEYS],event:[...EVENT_KEYS],action:[...ACTION_KEYS],
      metric:[...METRIC_KEYS],error:[...ERROR_KEYS],approval:[...APPROVAL_KEYS]}};
}

function validateEnvelope(e) {
  if (e?.contract !== 'INC_G11_LOG_ENVELOPE_V1') throw fail('INVALID_G11_CONTRACT');
  if (e?.envelope_version !== '1.1') throw fail('INVALID_G11_ENVELOPE_VERSION');
  const run=e?.run;
  for (const k of ['run_id','root_run_id','trace_id','correlation_id','run_type','started_at','status','spend_mode','attempt_number','environment_ref','retention_class','is_test']) {
    if (run?.[k] === undefined || run?.[k] === null || run?.[k] === '') throw fail('MISSING_RUN_FIELD',{field:k});
  }
  if (!Array.isArray(e.semantic_records) || e.semantic_records.length < 1) throw fail('MISSING_SEMANTIC_RECORDS');
  if (e.semantic_records.length > 199) throw fail('G11_WRITE_BATCH_LIMIT');
  if (typeof run.is_test !== 'boolean') throw fail('G11_IS_TEST_BOOLEAN_REQUIRED');
  if (!e.semantic_records.some(r => r.kind === 'event')) throw fail('G11_EVENT_REQUIRED');
}

function normalizedRun(e) {
  return {...e.run, partition_month: partitionMonth(e.run.started_at)};
}
function normalizedRecord(r) {
  return {...r, ...(r.kind === 'metric' ? {measurement_status: r.measurement_status ?? 'UNAVAILABLE'} : {}), partition_month: partitionMonth(r.timestamp || r.requested_at)};
}

export async function persistG11Envelope(envelope) {
  validateEnvelope(envelope);
  const p=projectRef(envelope), w=workloadRef(envelope);
  const statements=[statement('g11_runs','run_id',RUN_KEYS,normalizedRun(envelope),p,w)];
  for (const raw of envelope.semantic_records) {
    const r=normalizedRecord(raw);
    if (r.run_id !== envelope.run.run_id) throw fail('G11_CHILD_RUN_MISMATCH',{kind:r.kind});
    if (r.project_ref != null && r.project_ref !== p) throw fail('G11_PROJECT_REFERENCE_MISMATCH');
    if (r.is_test !== envelope.run.is_test) throw fail('G11_CHILD_TEST_FLAG_MISMATCH');
    switch(r.kind) {
      case 'event': statements.push(statement('g11_events','event_id',EVENT_KEYS,r,p,w)); break;
      case 'action': statements.push(statement('g11_actions','action_id',ACTION_KEYS,r,p,w)); break;
      case 'metric': statements.push(statement('g11_metrics','metric_id',METRIC_KEYS,r,p,w)); break;
      case 'error': statements.push(statement('g11_errors','error_id',ERROR_KEYS,r,p,w)); break;
      case 'approval': statements.push(statement('g11_approvals','approval_id',APPROVAL_KEYS,r,p,w)); break;
      default: throw fail('UNKNOWN_G11_RECORD_KIND',{kind:r.kind});
    }
  }

  const verified=await persistVerifiedRows(statements);
  const counts={runs:0,events:0,actions:0,metrics:0,errors:0,approvals:0};
  for (const row of verified.verified_rows) counts[row.family.slice(4)]++;
  return {
    ok:true, receipt_state:'G11_PERSISTED_VERIFIED', route:'INC_G11_G17_DB_WRITE_ROUTE_V1',
    run_id:envelope.run.run_id, project_ref:p, transaction_writes:statements.length,
    readback:counts, verification:verified.verification,
    verified_ids:verified.verified_rows, result_ids:verified.transaction.results.filter((_,i)=>i%2===0).map(x=>x.rows[0])
  };
}

export async function readG11Run(runId, expectedProjectRef) {
  const project_ref = String(expectedProjectRef || '').trim().slice(0, 128);
  if (!project_ref) throw fail('PROJECT_CONTEXT_REQUIRED');
  const run=(await db.query('SELECT * FROM g11_runs WHERE run_id=$1',[runId])).rows[0]||null;
  if(!run) return null;
  if(run.project_ref !== project_ref) throw fail('PROJECT_SCOPE_DENIED');
  const [events,actions,metrics,errors,approvals]=await Promise.all([
    db.query('SELECT * FROM g11_events WHERE run_id=$1 AND project_ref=$2 ORDER BY sequence_number,event_id',[runId,project_ref]),
    db.query('SELECT * FROM g11_actions WHERE run_id=$1 AND project_ref=$2 ORDER BY sequence_number,action_id',[runId,project_ref]),
    db.query('SELECT * FROM g11_metrics WHERE run_id=$1 AND project_ref=$2 ORDER BY timestamp,metric_id',[runId,project_ref]),
    db.query('SELECT * FROM g11_errors WHERE run_id=$1 AND project_ref=$2 ORDER BY timestamp,error_id',[runId,project_ref]),
    db.query('SELECT * FROM g11_approvals WHERE run_id=$1 AND project_ref=$2 ORDER BY requested_at,approval_id',[runId,project_ref])
  ]);
  return {run,events:events.rows,actions:actions.rows,metrics:metrics.rows,errors:errors.rows,approvals:approvals.rows};
}

export async function deleteTestRun(runId, expectedProjectRef) {
  const project_ref = String(expectedProjectRef || '').trim().slice(0, 128);
  if (!project_ref) throw fail('PROJECT_CONTEXT_REQUIRED');
  const run=(await db.query('SELECT run_id,project_ref,is_test FROM g11_runs WHERE run_id=$1',[runId])).rows[0]||null;
  if(!run) return {ok:true,deleted:false,reason:'NOT_FOUND'};
  if(run.project_ref !== project_ref) throw fail('PROJECT_SCOPE_DENIED');
  if(!run.is_test) throw fail('NON_TEST_DELETE_FORBIDDEN');
  const tx=await db.transaction([
    {sql:'DELETE FROM g11_approvals WHERE run_id=$1 AND project_ref=$2',params:[runId,project_ref]},
    {sql:'DELETE FROM g11_errors WHERE run_id=$1 AND project_ref=$2',params:[runId,project_ref]},
    {sql:'DELETE FROM g11_metrics WHERE run_id=$1 AND project_ref=$2',params:[runId,project_ref]},
    {sql:'DELETE FROM g11_actions WHERE run_id=$1 AND project_ref=$2',params:[runId,project_ref]},
    {sql:'DELETE FROM g11_events WHERE run_id=$1 AND project_ref=$2',params:[runId,project_ref]},
    {sql:'DELETE FROM g11_runs WHERE run_id=$1 AND project_ref=$2',params:[runId,project_ref]}
  ]);
  const remaining=(await db.query('SELECT count(*)::int c FROM g11_runs WHERE run_id=$1',[runId])).rows[0].c;
  return {ok:remaining===0,deleted:true,remaining,steps:tx.results.length};
}

function requiredString(obj,key,max=255){
  const v=String(obj?.[key]??'').trim();
  if(!v) throw fail('MISSING_REQUIRED_FIELD',{field:key});
  if(v.length>max) throw fail('FIELD_TOO_LONG',{field:key});
  return v;
}
function boundedLimit(v,def=100,max=500){
  const n=Number(v);
  return Number.isFinite(n)&&n>0?Math.min(Math.floor(n),max):def;
}
export async function persistG11ResourceObservation(o){
  if (typeof o?.is_test !== 'boolean') throw fail('G11_IS_TEST_BOOLEAN_REQUIRED');
  const row={
    observation_id:requiredString(o,'observation_id',128),captured_at:requiredString(o,'captured_at',64),
    provider_ref:requiredString(o,'provider_ref',64),provider_account_ref:requiredString(o,'provider_account_ref',255),
    provider_workspace_ref:o.provider_workspace_ref??null,billing_account_ref:o.billing_account_ref??null,project_ref:requiredString(o,'project_ref',128),
    resource_group_ref:o.resource_group_ref??null,service_ref:o.service_ref??null,resource_ref:o.resource_ref??null,
    meter_ref:requiredString(o,'meter_ref',128),meter_value:o.meter_value??null,meter_limit:o.meter_limit??null,meter_remaining:o.meter_remaining??null,
    unit:requiredString(o,'unit',64),reset_at:o.reset_at??null,period_start:o.period_start??null,period_end:o.period_end??null,currency:o.currency??null,
    acquisition_mode:requiredString(o,'acquisition_mode',32),persistence_class:requiredString(o,'persistence_class',32),
    measurement_status:requiredString(o,'measurement_status',32),measurement_scope:requiredString(o,'measurement_scope',64),
    source_ref:requiredString(o,'source_ref',255),source_priority:Number(o.source_priority),source_observed_at:requiredString(o,'source_observed_at',64),
    collector_ref:requiredString(o,'collector_ref',128),collector_version:o.collector_version??null,state_hash:requiredString(o,'state_hash',64),
    schema_version:requiredString(o,'schema_version',32),is_test:Boolean(o.is_test)
  };
  if(!Number.isInteger(row.source_priority)) throw fail('SOURCE_PRIORITY_REQUIRED');
  const verified=await persistVerifiedRows([{table:'g11_resource_observations',idColumn:'observation_id',row}]);
  return {ok:true,receipt_state:'G11_RESOURCE_PERSISTED_VERIFIED',route:'INC_G11_G17_RESOURCE_FINOPS_WRITE_ROUTE_V1',row:verified.transaction.results[0].rows[0],readback:{...verified.transaction.results[0].rows[0],...verified.verified_rows[0]},verification:verified.verification};
}
export async function readG11ResourceObservations(filter={}){
  const limit=boundedLimit(filter.limit);
  const account=requiredString(filter,'provider_account_ref',255);
  const project=requiredString(filter,'project_ref',128);
  const from=filter.from??'1970-01-01T00:00:00Z',to=filter.to??'9999-12-31T23:59:59Z';
  const q=await db.query('SELECT * FROM g11_resource_observations WHERE provider_account_ref=$1 AND project_ref=$2 AND captured_at >= $3 AND captured_at <= $4 ORDER BY captured_at DESC,observation_id LIMIT '+limit,[account,project,from,to]);
  if(q.rows.length===0){
    const other=await db.query('SELECT count(*)::int c FROM g11_resource_observations WHERE provider_account_ref=$1 AND project_ref<>$2',[account,project]);
    if((other.rows[0]?.c||0)>0) throw fail('PROJECT_SCOPE_DENIED');
  }
  return q.rows;
}
export async function persistG11BillingLedger(o){
  if (typeof o?.is_test !== 'boolean') throw fail('G11_IS_TEST_BOOLEAN_REQUIRED');
  const row={
    ledger_id:requiredString(o,'ledger_id',128),occurred_at:requiredString(o,'occurred_at',64),period_start:o.period_start??null,period_end:o.period_end??null,
    provider_ref:requiredString(o,'provider_ref',64),billing_account_ref:requiredString(o,'billing_account_ref',255),provider_account_ref:o.provider_account_ref??null,
    provider_workspace_ref:o.provider_workspace_ref??null,project_ref:requiredString(o,'project_ref',128),service_ref:o.service_ref??null,sku_ref:o.sku_ref??null,meter_ref:o.meter_ref??null,
    resource_ref:o.resource_ref??null,billing_event_type:requiredString(o,'billing_event_type',64),billing_mode:requiredString(o,'billing_mode',64),
    external_reference:o.external_reference??null,quantity:o.quantity??null,unit:o.unit??null,amount_original:o.amount_original??null,currency_original:o.currency_original??null,
    fx_rate_to_cad:o.fx_rate_to_cad??null,amount_cad:o.amount_cad??null,tax_amount_cad:o.tax_amount_cad??null,source_ref:requiredString(o,'source_ref',255),
    measurement_status:requiredString(o,'measurement_status',32),reconciled_at:o.reconciled_at??null,schema_version:requiredString(o,'schema_version',32),is_test:Boolean(o.is_test)
  };
  const verified=await persistVerifiedRows([{table:'g11_billing_ledger',idColumn:'ledger_id',row}]);
  return {ok:true,receipt_state:'G11_BILLING_PERSISTED_VERIFIED',route:'INC_G11_G17_RESOURCE_FINOPS_WRITE_ROUTE_V1',row:verified.transaction.results[0].rows[0],readback:{...verified.transaction.results[0].rows[0],...verified.verified_rows[0]},verification:verified.verification};
}
export async function readG11BillingLedger(filter={}){
  const limit=boundedLimit(filter.limit);
  const billing=requiredString(filter,'billing_account_ref',255);
  const project=requiredString(filter,'project_ref',128);
  const from=filter.from??'1970-01-01T00:00:00Z',to=filter.to??'9999-12-31T23:59:59Z';
  const q=await db.query('SELECT * FROM g11_billing_ledger WHERE billing_account_ref=$1 AND project_ref=$2 AND occurred_at >= $3 AND occurred_at <= $4 ORDER BY occurred_at DESC,ledger_id LIMIT '+limit,[billing,project,from,to]);
  if(q.rows.length===0){
    const other=await db.query('SELECT count(*)::int c FROM g11_billing_ledger WHERE billing_account_ref=$1 AND project_ref<>$2',[billing,project]);
    if((other.rows[0]?.c||0)>0) throw fail('PROJECT_SCOPE_DENIED');
  }
  return q.rows;
}
export async function deleteG11ResourceFinopsTestRows(testRef, expectedProjectRef){
  const ref=String(testRef||'').trim();
  if(!ref) throw fail('TEST_REF_REQUIRED');
  const project=requiredString({project_ref:expectedProjectRef},'project_ref',128);
  const resource=await db.query('SELECT project_ref FROM g11_resource_observations WHERE observation_id=$1 AND is_test=true',[ref]);
  const billing=await db.query('SELECT project_ref FROM g11_billing_ledger WHERE ledger_id=$1 AND is_test=true',[ref]);
  for(const row of [...resource.rows,...billing.rows]) if(row.project_ref!==project) throw fail('PROJECT_SCOPE_DENIED');
  const tx=await db.transaction([
    {sql:'DELETE FROM g11_resource_observations WHERE is_test=true AND observation_id=$1 AND project_ref=$2',params:[ref,project]},
    {sql:'DELETE FROM g11_billing_ledger WHERE is_test=true AND ledger_id=$1 AND project_ref=$2',params:[ref,project]}
  ]);
  return {ok:true,steps:tx.results.length};
}