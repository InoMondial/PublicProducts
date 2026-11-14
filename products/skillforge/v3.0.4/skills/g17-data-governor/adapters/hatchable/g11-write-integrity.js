import { db } from 'hatchable';

// G17-owned physical adapter. No schema change and no new logging authority.
const TABLE_IDS = Object.freeze({
  g11_runs: 'run_id', g11_events: 'event_id', g11_actions: 'action_id',
  g11_metrics: 'metric_id', g11_errors: 'error_id', g11_approvals: 'approval_id',
  g11_resource_observations: 'observation_id', g11_billing_ledger: 'ledger_id'
});
function error(code) { const e = new Error(code); e.code = code; return e; }
function requireValue(ok, code) { if (!ok) throw error(code); }
function quote(name) {
  requireValue(typeof name === 'string' && /^[a-z][a-z0-9_]*$/.test(name), 'G11_INVALID_SQL_IDENTIFIER');
  return '"' + name + '"';
}
function prepare(spec) {
  requireValue(spec && TABLE_IDS[spec.table] === spec.idColumn, 'G11_INVALID_WRITE_TARGET');
  const row = { ...spec.row };
  for (const key of [spec.idColumn, 'project_ref']) {
    requireValue(typeof row[key] === 'string' && row[key].trim() === row[key] && row[key].length > 0 && row[key].length <= 255,
      key === 'project_ref' ? 'PROJECT_CONTEXT_REQUIRED' : 'G11_SEMANTIC_ID_REQUIRED');
  }
  requireValue(row.project_ref.length <= 128, 'PROJECT_CONTEXT_TOO_LONG');
  requireValue(typeof row.is_test === 'boolean', 'G11_IS_TEST_BOOLEAN_REQUIRED');
  const columns = Object.keys(row);
  columns.forEach(quote);
  // jsonb_populate_record casts dates/numbers using the real PostgreSQL schema.
  // JSON-column strings need semantic decoding, not double encoding as a scalar.
  if (typeof row.provider_usage_raw_json === 'string') {
    try { row.provider_usage_raw_json = JSON.parse(row.provider_usage_raw_json); }
    catch { throw error('G11_INVALID_USAGE_JSON'); }
  }
  const scope = ['project_ref', 'is_test'];
  if (spec.table !== 'g11_runs' && Object.hasOwn(row, 'run_id')) scope.push('run_id');
  if (spec.table === 'g11_resource_observations') scope.push('provider_ref', 'provider_account_ref');
  if (spec.table === 'g11_billing_ledger') scope.push('provider_ref', 'billing_account_ref');
  const payloadColumns = columns.filter(k => k !== spec.idColumn && !scope.includes(k));
  requireValue(payloadColumns.length > 0, 'G11_EMPTY_WRITE_PAYLOAD');
  const table = quote(spec.table), id = quote(spec.idColumn);
  const values = columns.map(k => row[k] ?? null);
  const write = {
    sql: `INSERT INTO ${table} (${columns.map(quote).join(',')}) VALUES (${values.map((_, i) => '$' + (i + 1)).join(',')})
      ON CONFLICT (${id}) DO UPDATE SET ${id}=EXCLUDED.${id}
      WHERE ${columns.map(k => table + '.' + quote(k) + ' IS NOT DISTINCT FROM EXCLUDED.' + quote(k)).join(' AND ')}
      RETURNING id, ${id}, project_ref${spec.table === 'g11_resource_observations' ? ', state_hash' : spec.table === 'g11_billing_ledger' ? ', amount_cad' : ''}`,
    params: values
  };
  // Immutable semantic identities: a retry is a no-op only when EVERY written
  // field matches after PostgreSQL type normalization. A changed payload must
  // raise inside the transaction, not merely return zero rows and partially commit.
  const scopeKeys = [spec.idColumn, ...scope];
  const predicate = keys => keys.map(k => 'actual.' + quote(k) + ' IS NOT DISTINCT FROM expected.' + quote(k)).join(' AND ');
  const matches = keys => `EXISTS (SELECT 1 FROM ${table} actual CROSS JOIN jsonb_populate_record(NULL::${table}, $1::jsonb) expected WHERE ${predicate(keys)})`;
  const guard = {
    sql: `SELECT CAST(CASE WHEN NOT ${matches(scopeKeys)} THEN 'G11_PROJECT_SCOPE_DENIED'
      WHEN NOT ${matches(columns)} THEN 'G11_IDEMPOTENCY_CONFLICT' ELSE '1' END AS integer) AS integrity_guard`,
    params: [JSON.stringify(row)]
  };
  return { ...spec, row, columns, scope, write, guard };
}
export async function persistVerifiedRows(specs) {
  requireValue(Array.isArray(specs) && specs.length > 0 && specs.length <= 200, 'G11_WRITE_BATCH_LIMIT');
  const prepared = specs.map(prepare);
  const identities = new Set();
  for (const p of prepared) {
    const identity = p.table + ':' + p.row[p.idColumn];
    requireValue(!identities.has(identity), 'G11_DUPLICATE_SEMANTIC_ID'); identities.add(identity);
  }
  requireValue(new Set(prepared.map(p => p.row.project_ref)).size === 1, 'G11_MIXED_PROJECT_BATCH');
  let tx;
  try { tx = await db.transaction(prepared.flatMap(p => [p.write, p.guard])); }
  catch (e) {
    const message = String(e?.message || '');
    if (/G11_PROJECT_SCOPE_DENIED/.test(message)) throw error('PROJECT_SCOPE_DENIED');
    if (/G11_IDEMPOTENCY_CONFLICT/.test(message)) throw error('G11_IDEMPOTENCY_CONFLICT');
    throw e;
  }
  requireValue(Array.isArray(tx?.results) && tx.results.length === prepared.length * 2, 'G11_TRANSACTION_RESULT_UNVERIFIED');
  for (let i = 0; i < prepared.length; i++) {
    const p = prepared[i], rows = tx.results[i * 2]?.rows;
    requireValue(Array.isArray(rows) && rows.length === 1 && rows[0][p.idColumn] === p.row[p.idColumn] && rows[0].project_ref === p.row.project_ref,
      'G11_TRANSACTION_RESULT_UNVERIFIED');
  }
  // One bounded, independent server-side query; no per-record query loop and no
  // aggregate count can satisfy this exact-ID/project/complete-content predicate.
  const params = [], selects = [];
  for (const p of prepared) {
    params.push(JSON.stringify(p.row));
    const expected = '$' + params.length + '::jsonb';
    selects.push(`SELECT '${p.table}'::text AS family, actual.${quote(p.idColumn)}::text AS semantic_id, actual.project_ref, actual.id AS row_id
      FROM ${quote(p.table)} actual CROSS JOIN jsonb_populate_record(NULL::${quote(p.table)}, ${expected}) expected
      WHERE ${p.columns.map(k => 'actual.' + quote(k) + ' IS NOT DISTINCT FROM expected.' + quote(k)).join(' AND ')}`);
  }
  let rb;
  try { rb = await db.query(selects.join(' UNION ALL '), params); }
  catch { throw error('G11_EXACT_READBACK_UNAVAILABLE'); }
  requireValue(Array.isArray(rb?.rows) && rb.rows.length === prepared.length, 'G11_EXACT_READBACK_MISMATCH');
  const observed = new Map();
  for (const r of rb.rows) {
    const key = r.family + ':' + r.semantic_id;
    requireValue(!observed.has(key), 'G11_DUPLICATE_READBACK_ID'); observed.set(key, r);
  }
  for (const p of prepared) {
    const actual = observed.get(p.table + ':' + p.row[p.idColumn]);
    requireValue(actual && actual.project_ref === p.row.project_ref && actual.row_id != null, 'G11_EXACT_READBACK_MISMATCH');
  }
  return { transaction: tx, verified_rows: rb.rows, verification: 'EXACT_PROJECT_IDS_AND_ALL_WRITTEN_FIELDS', expected_count: prepared.length };
}