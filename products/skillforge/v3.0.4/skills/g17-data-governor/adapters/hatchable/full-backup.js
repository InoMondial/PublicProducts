import { config, db, storage } from 'hatchable';

function hex(bytes) {
  return [...new Uint8Array(bytes)].map(b => b.toString(16).padStart(2, '0')).join('');
}

async function sha256(value) {
  return hex(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(value)));
}


function quoteIdentifier(value) {
  if (typeof value !== 'string' || !value || value.includes('\0')) throw new Error('BACKUP_IDENTIFIER_INVALID');
  return '"' + value.replace(/"/g, '""') + '"';
}
function rowsOf(result) {
  if (!result || !Array.isArray(result.rows)) throw new Error('BACKUP_QUERY_RESULT_UNVERIFIED');
  return result.rows;
}

// Discovery is only a query plan, never the authoritative backup. All final
// metadata and table reads execute in ONE provider-native read-only snapshot.
async function captureConsistentSnapshot() {
  const initial = rowsOf(await db.query('SELECT current_schema() AS schema_name'));
  const schemaName = initial[0]?.schema_name;
  if (!schemaName) throw new Error('BACKUP_SCHEMA_UNRESOLVED');
  const metadata = [
    {name: 'sr', sql: "SELECT current_schema() AS schema_name, current_database() AS database_name, version() AS postgres_version, current_setting('transaction_isolation') AS isolation, current_setting('transaction_read_only') AS readonly, txid_current_snapshot()::text AS snapshot", params: []},
    {name: 'tables', sql: `SELECT table_name, table_type
       FROM information_schema.tables
      WHERE table_schema = $1 AND table_type = 'BASE TABLE'
      ORDER BY table_name`, params: [schemaName]},
    {name: 'columns', sql: `SELECT table_name,column_name,data_type,udt_name,is_nullable,column_default,
            ordinal_position,character_maximum_length,numeric_precision,numeric_scale,
            datetime_precision,is_identity,identity_generation,is_generated,generation_expression
       FROM information_schema.columns
      WHERE table_schema=$1
      ORDER BY table_name,ordinal_position`, params: [schemaName]},
    {name: 'keyColumns', sql: `WITH tc AS MATERIALIZED (
       SELECT table_name,table_schema,constraint_schema,constraint_name,constraint_type
         FROM information_schema.table_constraints
        WHERE table_schema=$1 AND constraint_type IN ('PRIMARY KEY','UNIQUE','FOREIGN KEY')
     ), rc AS MATERIALIZED (
       SELECT constraint_schema,constraint_name,unique_constraint_schema,unique_constraint_name
         FROM information_schema.referential_constraints WHERE constraint_schema=$1
     ), kc AS MATERIALIZED (
       SELECT table_name,table_schema,constraint_schema,constraint_name,column_name,
              ordinal_position,position_in_unique_constraint
         FROM information_schema.key_column_usage WHERE table_schema=$1
     )
     SELECT tc.table_name,tc.constraint_name,tc.constraint_type,kc.column_name,kc.ordinal_position,
            fkc.table_schema AS foreign_table_schema,fkc.table_name AS foreign_table_name,
            fkc.column_name AS foreign_column_name
       FROM tc
       LEFT JOIN kc ON tc.constraint_schema=kc.constraint_schema AND tc.constraint_name=kc.constraint_name
                   AND tc.table_schema=kc.table_schema AND tc.table_name=kc.table_name
       LEFT JOIN rc ON tc.constraint_type='FOREIGN KEY' AND tc.constraint_schema=rc.constraint_schema
                   AND tc.constraint_name=rc.constraint_name
       LEFT JOIN kc fkc ON rc.unique_constraint_schema=fkc.constraint_schema
                       AND rc.unique_constraint_name=fkc.constraint_name
                       AND kc.position_in_unique_constraint=fkc.ordinal_position
      ORDER BY tc.table_name,tc.constraint_name,kc.ordinal_position`, params: [schemaName]},
    {name: 'referentialRules', sql: `SELECT constraint_name, unique_constraint_name, match_option, update_rule, delete_rule
       FROM information_schema.referential_constraints
      WHERE constraint_schema=$1
      ORDER BY constraint_name`, params: [schemaName]},
    // PostgreSQL projects expose one CHECK for each NOT NULL column; those
    // are already carried by information_schema.columns.is_nullable. The
    // original table_constraints CHECK view takes >5 s and triggers the
    // provider timeout when embedded in a full read-only snapshot.
    // Capture nontrivial table CHECK constraints via column usage instead.
    {name: 'checks', sql: `SELECT DISTINCT u.table_name,c.constraint_name,c.check_clause
       FROM information_schema.check_constraints c
       JOIN information_schema.constraint_column_usage u
         ON c.constraint_schema=u.constraint_schema AND c.constraint_name=u.constraint_name
      WHERE c.constraint_schema=$1
      ORDER BY u.table_name,c.constraint_name`, params: [schemaName]},
    {name: 'checksInventory', sql: `SELECT constraint_name,constraint_schema,check_clause
       FROM information_schema.check_constraints
      WHERE constraint_schema=$1
      ORDER BY constraint_name`, params: [schemaName]},
    {name: 'sequenceDefs', sql: `SELECT sequence_name,data_type,start_value,minimum_value,maximum_value,increment,cycle_option
       FROM information_schema.sequences
      WHERE sequence_schema=$1
      ORDER BY sequence_name`, params: [schemaName]},
    {name: 'views', sql: `SELECT table_name AS view_name, view_definition, check_option, is_updatable
       FROM information_schema.views
      WHERE table_schema=$1
      ORDER BY table_name`, params: [schemaName]},
    {name: 'triggers', sql: `SELECT trigger_name,event_manipulation,event_object_table,action_statement,
            action_orientation,action_timing,action_condition
       FROM information_schema.triggers
      WHERE trigger_schema=$1
      ORDER BY event_object_table,trigger_name,event_manipulation`, params: [schemaName]},
    {name: 'routines', sql: `SELECT routine_name,routine_type,data_type,routine_definition
       FROM information_schema.routines
      WHERE routine_schema=$1
      ORDER BY routine_name`, params: [schemaName]}
  ];
  const readOnly = {sql: 'SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY', params: []};
  const planKeys = ['tables', 'columns', 'sequenceDefs'];
  const planQueries = planKeys.map(name => metadata.find(q => q.name === name));
  // Count and capture each result once. Re-running expensive information_schema
  // joins merely to count them can exceed the provider's transaction time budget.
  const packedQuery = q => ({sql: `WITH backup_rows AS MATERIALIZED (${q.sql})
    SELECT count(*)::text AS exact_count, COALESCE(jsonb_agg(to_jsonb(backup_rows)), '[]'::jsonb) AS payload FROM backup_rows`, params:q.params});
  const unpack = (result, code) => {
    const rows = rowsOf(result), one = rows[0];
    if (rows.length !== 1 || !Array.isArray(one?.payload) || String(one.exact_count) !== String(one.payload.length)) throw new Error(code);
    return one.payload;
  };
  const discovery = await db.transaction([readOnly, ...planQueries.map(packedQuery)]);
  if (!Array.isArray(discovery?.results) || discovery.results.length !== 4) throw new Error('BACKUP_DISCOVERY_UNVERIFIED');
  const plan = Object.fromEntries(planKeys.map((key,i) => [key, unpack(discovery.results[i+1], 'BACKUP_METADATA_TRUNCATED')]));
  if (plan.tables.length > 200 || plan.sequenceDefs.length > 400) throw new Error('BACKUP_SNAPSHOT_PLAN_LIMIT');
  const dataQueries = [], byteaColumns = {}, numericColumns = {};
  for (const t of plan.tables) {
    const table = t.table_name, columns = plan.columns.filter(c => c.table_name === table);
    if (!columns.length) throw new Error('BACKUP_TABLE_COLUMNS_MISSING');
    const bytea = columns.filter(c => c.data_type === 'bytea').map(c => c.column_name);
    byteaColumns[table] = bytea;
    const exactNumeric = columns.filter(c => ['bigint','numeric','decimal'].includes(c.data_type)).map(c=>c.column_name);
    numericColumns[table] = exactNumeric;
    const selectList = columns.map(c => bytea.includes(c.column_name)
      ? `encode(${quoteIdentifier(c.column_name)},'base64') AS ${quoteIdentifier(c.column_name)}`
      : exactNumeric.includes(c.column_name) ? `${quoteIdentifier(c.column_name)}::text AS ${quoteIdentifier(c.column_name)}` : quoteIdentifier(c.column_name)).join(',');
    const qualified = quoteIdentifier(schemaName) + '.' + quoteIdentifier(table);
    dataQueries.push({sql: `SELECT ${selectList} FROM ${qualified} ORDER BY ${quoteIdentifier(columns[0].column_name)}`, params: []});
  }
  const sequenceQueries = plan.sequenceDefs.map(s => ({
    sql: `SELECT last_value::text AS last_value,is_called FROM ${quoteIdentifier(schemaName)}.${quoteIdentifier(s.sequence_name)}`, params: []
  }));
  const preamble = [readOnly];
  if (plan.tables.length) preamble.push({sql: 'LOCK TABLE '+plan.tables.map(t=>quoteIdentifier(schemaName)+'.'+quoteIdentifier(t.table_name)).join(',')+' IN ACCESS SHARE MODE NOWAIT',params:[]});
  const queries = [...preamble, ...metadata.map(packedQuery), ...dataQueries.map(packedQuery), ...sequenceQueries];
  const tx = await db.transaction(queries);
  if (!Array.isArray(tx?.results) || tx.results.length !== queries.length) throw new Error('BACKUP_SNAPSHOT_RESULT_UNVERIFIED');
  const captured = Object.fromEntries(metadata.map((q,i) => [q.name, unpack(tx.results[i+preamble.length], 'BACKUP_METADATA_TRUNCATED')]));
  const info = captured.sr[0];
  if (info?.schema_name !== schemaName || info?.isolation !== 'repeatable read' || info?.readonly !== 'on' || !info?.snapshot) {
    throw new Error('BACKUP_CONSISTENT_SNAPSHOT_NOT_PROVEN');
  }
  for (const key of planKeys) {
    if (JSON.stringify(plan[key]) !== JSON.stringify(captured[key])) throw new Error('BACKUP_SCHEMA_CHANGED_RETRY_REQUIRED');
  }
  // Every catalog CHECK must be represented either as a real table CHECK
  // constraint or as an existing NOT NULL column. Do not silently omit an
  // unsupported constraint merely to meet the provider transaction limit.
  const explicitChecks = new Set(captured.checks.map(c => c.constraint_name + '|' + c.check_clause));
  const notNullColumns = new Set(captured.columns.filter(c => c.is_nullable === 'NO')
                                                     .map(c => c.column_name));
  for (const check of captured.checksInventory) {
    if (explicitChecks.has(check.constraint_name + '|' + check.check_clause)) continue;
    const match = /^"?([A-Za-z0-9_]+)"? IS NOT NULL$/i.exec(String(check.check_clause).trim());
    if (!match || !notNullColumns.has(match[1])) {
      throw new Error('BACKUP_CHECK_CONSTRAINT_UNACCOUNTED');
    }
  }
  // Only full named CHECK clauses need a separate restore statement. All
  // NOT NULL properties are already available in schema.columns.
  if (captured.keyColumns.some(c => c.constraint_type === 'FOREIGN KEY' && !c.foreign_column_name)) {
    throw new Error('BACKUP_FOREIGN_KEY_METADATA_INCOMPLETE');
  }
  let index = preamble.length + metadata.length;
  const data = {}, counts = {}, tableDigests = {};
  for (let i = 0; i < plan.tables.length; i++) {
    const table = plan.tables[i].table_name;
    const rows = unpack(tx.results[index+i], 'BACKUP_TABLE_ROWS_TRUNCATED');
    data[table] = rows; counts[table] = rows.length;
    tableDigests[table] = await sha256(JSON.stringify(rows));
  }
  index += plan.tables.length;
  const sequences = plan.sequenceDefs.map((s,i) => {
    const rows = rowsOf(tx.results[index+i]);
    if (rows.length !== 1 || rows[0].last_value == null || typeof rows[0].is_called !== 'boolean') throw new Error('BACKUP_SEQUENCE_STATE_UNVERIFIED');
    return {...s, state: rows[0]};
  });
  return {...captured, data, counts, tableDigests, byteaColumns, numericColumns, sequences, schemaName,
    consistency: {mode: 'POSTGRES_REPEATABLE_READ_READ_ONLY', snapshot: info.snapshot,
      metadata_and_table_data_same_transaction: true, exact_row_counts_verified: true,
      metadata_counts_verified: true, concurrent_ddl_guard: 'BOUNDED_ACCESS_SHARE_RELATION_LOCKS',
      sequence_state: 'NON_MVCC_CAPTURE_RESTORE_MUST_NOT_LOWER_BELOW_DATA_MAXIMUM'}};
}

export async function generateFullBackup(body = {}) {
  if (!config.PROVIDER_PROJECT_ID || !config.PROVIDER_PROJECT_SLUG) throw new Error('BACKUP_PROFILE_UNBOUND');
  const createdAt = new Date().toISOString();
  const {sr, schemaName, tables, columns, keyColumns, referentialRules, checks,
    sequences, views, triggers, routines, data, counts, byteaColumns, numericColumns, tableDigests, consistency}
    = await captureConsistentSnapshot();
  const indexes = Array.isArray(body?.index_inventory) ? body.index_inventory : [];

  const backup = {
    backup_format: 'HOF_HATCHABLE_SINGLE_FILE_V2',
    portability_target: 'PostgreSQL',
    created_at: createdAt,
    consistency,
    source: {
      provider: 'Hatchable',
      project_id: config.PROVIDER_PROJECT_ID,
      project_slug: config.PROVIDER_PROJECT_SLUG,
      schema: schemaName,
      database_name: sr[0].database_name,
      postgres_version: sr[0].postgres_version
    },
    restore_contract: {
      self_contained: true,
      external_schema_files_required: false,
      external_data_files_required: false,
      bytea_encoding: 'base64',
      exact_numeric_encoding: 'bigint_numeric_decimal_as_text_cast_using_schema_types',
      native_provider_backup: false,
      sequence_restore_rule: 'Restore each sequence at or beyond both captured state and maximum restored dependent key; sequence counters are not MVCC state.',
      generator: 'custom Hatchable admin function',
      notes: 'Table data and metadata are captured in one repeatable-read read-only database transaction. The artifact contains schema metadata, constraints, optional caller-supplied index inventory, sequences/state, views, triggers, routines, all base-table data in the current Hatchable project database schema, row counts and SHA-256 digests. Hatchable blocks direct pg_catalog index introspection; data backup completeness does not depend on index inventory, but restore performance tuning may require approved index DDL from migrations/source control.'
    },
    embedded_source_ddl: Array.isArray(body?.source_ddl) ? body.source_ddl : [],
    schema: {
      tables,
      columns,
      key_constraints: keyColumns,
      referential_rules: referentialRules,
      checks,
      indexes,
      sequences,
      views,
      triggers,
      routines,
      bytea_columns: byteaColumns,
      exact_numeric_text_columns: numericColumns
    },
    counts,
    table_digests_sha256: tableDigests,
    data
  };

  backup.manifest = {
    table_count: tables.length,
    sequence_count: sequences.length,
    view_count: views.length,
    trigger_count: triggers.length,
    routine_count: routines.length,
    total_rows: Object.values(counts).reduce((a,b)=>a+b,0),
    payload_sha256_before_manifest: await sha256(JSON.stringify(backup))
  };

  // The embedded size includes its own decimal representation. Resolve the
  // bounded fixed point rather than recording the pre-manifest byte count.
  backup.manifest.final_size_bytes = 0;
  let finalWithSize, finalBytes;
  for (let attempt = 0; attempt < 8; attempt++) {
    finalWithSize = JSON.stringify(backup);
    finalBytes = new TextEncoder().encode(finalWithSize);
    if (backup.manifest.final_size_bytes === finalBytes.length) break;
    backup.manifest.final_size_bytes = finalBytes.length;
  }
  if (new TextEncoder().encode(JSON.stringify(backup)).length !== backup.manifest.final_size_bytes) {
    throw new Error('BACKUP_SIZE_MANIFEST_UNSTABLE');
  }
  finalWithSize = JSON.stringify(backup);
  finalBytes = new TextEncoder().encode(finalWithSize);
  const finalSha = await sha256(finalWithSize);
  const compactTs = createdAt.replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z');
  const key = `exports/INCDB_HATCHABLE_FULL_${compactTs}_FMT2_${finalSha.slice(0,8).toUpperCase()}.json`;
  const url = await storage.put(key, finalBytes, 'application/json');

  return {
    ok: true,
    backup_format: backup.backup_format,
    key,
    url,
    bytes: finalBytes.length,
    sha256: finalSha,
    counts,
    table_digests_sha256: tableDigests,
    manifest: backup.manifest
  };
}