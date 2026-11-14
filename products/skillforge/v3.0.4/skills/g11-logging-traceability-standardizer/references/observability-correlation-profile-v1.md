# INC_G11_OBSERVABILITY_CORRELATION_PROFILE_V1

Status: Stage-30 candidate hard gate for G11 v4.7.0.
Owner: G11-Logging & Traceability Standardizer.
Physical persistence owner: G17 through `INC_G11_G17_DB_WRITE_ROUTE_V1`.
Resource-policy owner: G9 through `INC_RESOURCE_USAGE_V1`.

## 1. Objective
Provide enough structured, correlated evidence to reconstruct important system activity for security review, token/resource analysis, monitoring, dashboards, operational summaries, debugging, transaction analysis and post-incident investigation without creating high-volume noisy logs or duplicating the physical database schema.

This profile is an overlay on the current Run/Event/Action/Metric/Error/Approval model. It does not authorize a new physical table or schema change by itself.

## 2. Industry alignment
G11 follows these design principles:
- OpenTelemetry-style separation of occurrence timestamp, observed timestamp, trace context, resource/source identity, severity, event name and attributes;
- W3C Trace Context semantics for cross-component trace continuity when a compatible trace ID/span ID is available;
- OWASP security-logging guidance: capture sufficient `when / where / who / what`, log important authentication/authorization/security events, and exclude secrets/sensitive authentication material;
- named low-cardinality event classes instead of dynamic event names;
- events for point-in-time occurrences/state transitions and span/run boundaries for duration-bearing operations;
- metrics for aggregatable numeric measurements such as token counts, duration and call counts.

## 3. Mandatory material event classes
The following are mandatory when the fact actually occurs and the producer can observe it:

### SECURITY_IDENTITY
- authentication success/failure when exposed by the authorized surface;
- account/session change that materially changes execution identity;
- authorization/permission/role change;
- MFA/credential boundary failure as a semantic outcome only, never the secret value;
- security validation failure, policy block or suspicious input/output validation failure.

### MATERIAL_ACTION
- important state-changing action initiated by Chat, Work, Codex, Agent, Skill or Orchestrator;
- material create/update/delete/move/rename/archive/publish/deploy operation;
- approval or explicit owner decision attached to a consequential action.

### DATA_TRANSACTION
- durable database mutation or migration unit;
- migration/cutover/rollback/restore;
- transaction success/failure/partial state;
- idempotency/replay decision where it materially affects correctness.

### CROSS_SURFACE_INVOCATION
- manager-to-worker or Skill-to-Skill invocation when it forms a governed work boundary;
- source actor/surface, target actor/surface, work-unit reference and result/receipt reference;
- never log the full prompt or hidden reasoning.

### ARTIFACT_AND_EXTERNAL_REFERENCE
- governed artifact creation/publication/replace/delete;
- stable output ID, file/item ID, Git commit/PR/release ID, SharePoint item reference, database record/business reference, Teams message/thread ID or equivalent stable reference when exposed;
- references form a graph linking one authoritative log event to related external records without copying their full content into the log.

### RESOURCE_USAGE
- actual model/effort/speed only when host-confirmed;
- measured input/output/cached/reasoning tokens when exposed;
- tool-call count, plugin/connector invocation count, retry count, evaluator count, duration and cost/quota values when exposed;
- unavailable values remain `UNAVAILABLE`/`PARTIAL`; estimates remain separate from measured facts.

### FAILURE_RECOVERY
- material error, timeout, failed validation, degraded persistence, retry escalation, rollback, recovery checkpoint and terminal recovery outcome;
- error class/code, retryability, failed stage/work-unit and remediation/evidence reference when available;
- do not log raw stack/data payloads when they contain sensitive information.

### RELEASE_AND_GOVERNANCE
- build/release/deployment/certification outcome;
- G12/G13/G3 decision/evidence references;
- version/commit/package/deployment refs;
- policy exception/waiver with explicit approval reference.

## 4. Correlation graph — HARD GATE
Every mandatory material event uses the strongest available safe identity chain:
- `event_id` — unique occurrence;
- `activity_id` — one governed material activity boundary;
- `root_run_id` — end-to-end mission/run root;
- `run_id` — current execution run;
- `parent_run_id` — direct parent when applicable;
- `trace_id` — distributed trace identity where supported;
- `span_id` or equivalent sub-operation identity where supported;
- `correlation_id` — cross-system correlation when trace context is unavailable;
- `idempotency_key` — material state-changing retry/replay control when applicable;
- `project_ref` — canonical project identity from G17;
- `producer_ref` / actor/surface identity;
- `account_ref` — only a safe stable/pseudonymous account reference when required; never an auth secret/session token.

Do not fabricate a missing ID. If a platform provides only a subset, preserve the subset truthfully and derive only IDs explicitly owned by G11.

## 5. Reference graph — HARD GATE
Important external outputs and state changes are linked by stable references rather than embedded content.

Permitted reference types include:
- GitHub repository/commit/PR/release/path reference;
- SharePoint drive-item/file/folder reference;
- relational record/business-object reference;
- Teams message/thread reference;
- notification/approval/decision reference;
- artifact/evidence/test/report reference;
- work-unit/Handoff reference;
- external provider transaction/job/run reference.

Each reference records, when available: `ref_type`, `stable_ref`, `operation`, `relation`, and verification/read-back state. The physical storage representation remains adapter-owned.

Typical relations:
`INPUT_TO | OUTPUT_OF | EVIDENCE_FOR | PUBLISHED_AS | MUTATED_BY | APPROVED_BY | CAUSED_BY | RETRY_OF | ROLLBACK_OF | CHILD_OF | NOTIFIED_BY`.

## 6. Token/resource telemetry
Use `INC_RESOURCE_USAGE_V1` without creating a competing database.

For each material run/work unit, persist actual values when exposed:
- model class/name;
- reasoning effort/class;
- input tokens;
- output tokens;
- cached tokens;
- reasoning tokens;
- tool-call count;
- plugin/connector-call count if measurable;
- Skill invocation count if measurable;
- retry count;
- evaluator count;
- duration;
- cost/credits/quota delta if measurable;
- measurement provenance and availability state.

If account/host exposes only aggregate quota before/after rather than per-run tokens, log that as measured aggregate quota telemetry with provenance and never reverse-engineer an exact per-run token count without evidence.

## 7. Sampling, aggregation and noise control
Never sample away or suppress:
- CRITICAL/HIGH security events;
- authentication/authorization failure relevant to security;
- approvals/owner decisions;
- data mutation/migration/cutover/rollback;
- release/deployment/certification;
- material failures/timeouts/recovery;
- destructive operations;
- audit-required financial/legal/data-integrity transactions.

Routine successful low-value events MAY be aggregated/deduplicated/sampled only when:
- no mandatory governed boundary is lost;
- authoritative denominator/coverage remains available when coverage is reported;
- aggregate metrics still preserve debugging/monitoring value;
- sampling policy is explicit and reproducible.

Do not log every click, browser navigation, token of text, deterministic internal microstep or repeated poll.

## 8. Security and privacy
Never log:
- passwords, OTP/MFA values, API keys, private keys, access/refresh tokens, cookies, connection strings or raw authorization headers;
- hidden chain-of-thought/private reasoning;
- raw full prompts/responses by default;
- unnecessary sensitive PII;
- raw document/file contents when a stable reference is sufficient.

Session/account identifiers that are sensitive SHOULD be replaced by stable safe references or governed hashes where correlation is necessary.

## 9. Queryability and dashboard readiness
The minimum semantics must support later queries for:
- activity by project / actor / account-ref / surface / Skill / model / time window;
- success/failure/blocked/partial rates;
- security/auth events;
- data mutations and transaction lineage;
- cross-surface/Skill invocation graph;
- artifact/output lineage and external record navigation;
- token/cost/duration/tool-call trends;
- retries/timeouts/recovery patterns;
- release/deployment/certification history;
- missing-log coverage.

Dashboards and summaries consume G11 data; they do not redefine log semantics.

## 10. Compatibility and schema rule
Stage-30 implementation MUST first map these semantics onto existing Run/Event/Action/Metric/Error/Approval structures and existing reference fields.

If an essential semantic cannot be represented without ambiguous overloading, return `DB_SCHEMA_CHANGE_REQUIRED` with impact/migration/rollback/test plan. Do not silently add columns/tables merely for convenience.

## 11. Release acceptance
G12 must test representative positive and negative scenarios including:
- login/auth event with no credential leakage;
- permission/security change;
- DB mutation + rollback lineage;
- Chat -> Work/Codex delegation correlation;
- GitHub/SharePoint output references;
- measured and unavailable token telemetry;
- timeout/retry/recovery correlation;
- low-value routine success aggregation;
- missing-log coverage detection;
- durable G17 DB read-back.

G13 independently certifies that observability gain is material and that logging volume/privacy risk is proportionate.
