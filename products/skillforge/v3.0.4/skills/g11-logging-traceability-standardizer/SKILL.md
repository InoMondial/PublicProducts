---
name: g11-logging-traceability-standardizer
description: G11-Logging & Traceability Standardizer 4.7.0 — SkillForge runtime logging
  gateway with receipt-bound traceability, material-activity boundaries, observability/correlation
  graph, resource telemetry, coverage auditing, UTF-8/RTL safety and G17-backed durable
  persistence.
metadata:
  stable_id: O6-SKL-011
  visible_id: G11
  display_name: G11-Logging & Traceability Standardizer
  version: 4.8.2
  domain: governance
  complexity_profile: FULL
  functional_role: QUALITY
  lifecycle: production
  strictness: S4
  governance_owner: INOMondial Inc.
  builder_framework_ref: INC_SKILLFORGE
  framework_id: INC_SKILLFORGE
  framework_name: SkillForge
  framework_membership: MEMBER
  framework_registry_ref: INC_SKILL_NAMESPACE_REGISTRY
  next_version_backlog_ref: INC_SKILLFORGE_UNIFIED_BACKLOG
  logging_target_ref: INC_LOG_STORE
  logging_event_contract_ref: INC_GOVERNANCE_EVENT_ENVELOPE_V1
  logging_caller_interface_ref: INC_G11_CALLER_INTERFACE_V1
  runtime_gateway_contract_ref: INC_G11_RUNTIME_GATEWAY_V1
  governed_activity_boundary_contract_ref: INC_GOVERNED_ACTIVITY_BOUNDARY_V1
  coverage_auditor_contract_ref: INC_G11_MISSING_LOG_COVERAGE_AUDITOR_V1
  backlog_intake_event_contract_ref: INC_BACKLOG_INTAKE_EVENT_V1
  logging_writer_route_ref: INC_G11_G17_DB_WRITE_ROUTE_V1
  logging_writer_envelope_ref: INC_G11_LOG_ENVELOPE_V1
  observability_correlation_profile_ref: INC_G11_OBSERVABILITY_CORRELATION_PROFILE_V1
  resource_usage_ref: INC_RESOURCE_USAGE_V1
  critical_control_contract_ref: INC_CRITICAL_CONTROL_ASSURANCE_V2
---

## Current release policy (PRIOR_RELEASE)
For release/build/promotion decisions, use `INC_AUTONOMOUS_RELEASE_ACCEPTANCE_V1`
at `../g0-skill-architect-builder/references/autonomous-release-policy-v1.md`. Available local/API/plugin/simulation tests are required;
unavailable third-party/runner/user/native-host assurance is optional and nonblocking.
This supersedes conflicting release-only clauses below or in detailed references.
Security, authorization, integrity and truthful runtime evidence remain mandatory.


# G11-Logging & Traceability Standardizer v4.8.2 - Released
## 1. Purpose
G11 owns logging meaning, semantic contracts, redaction, stable trace/correlation relations, resource-telemetry normalization, the reusable runtime logging gateway, activity-boundary enforcement, receipt semantics, missing-log coverage auditing, external-reference lineage, Persian UTF-8/RTL persistence behavior, writer-routing policy and schema-change governance. The canonical logical logging target remains `INC_LOG_STORE`.

Normal producers do not load the physical persistence schema and do not mutate physical database/SharePoint structures directly.

## 2. Canonical runtime gateway — HARD GATE
Use `INC_G11_RUNTIME_GATEWAY_V1`:

`caller -> compile -> validate/redact/normalize -> enqueue/write route -> truthful receipt`

Implementation assets remain:
- `scripts/compile_caller_request.py`
- `scripts/g11_runtime_gateway.py`
- `scripts/g11_missing_log_coverage_auditor.py`

The gateway binds receipt to `activity_id`, `run_id`, and `envelope_id`. Queue acceptance is never durable persistence proof.

Allowed receipt states include:
`G11_GATEWAY_VALIDATED | G11_ACCEPTED_FOR_PERSISTENCE | G11_PERSISTED_VERIFIED | TRACE_PERSISTENCE_PENDING | TRACE_PERSISTENCE_DEGRADED | VALIDATION_FAILED`.

`G11_GATEWAY_VALIDATED` means compile/validation only and must never be presented as enqueue/persistence success.

## 3. Governed material activity boundary — HARD GATE
Use `INC_GOVERNED_ACTIVITY_BOUNDARY_V1` for `CHAT | WORK | CODEX | AGENT | SKILL | ORCHESTRATOR | SCHEDULED | ERROR_HANDLER`.

Default boundary is one **material governed activity outcome**, not every click/tool/microstep. Aggregation is allowed only when it does not become omission. Known missing mandatory outcome logging is a governance defect.

Every applicable boundary resolves producer/surface/activity identity and one factual final semantic outcome. Child substeps log separately only when they are independently material/governed boundaries.

Material examples include important security/auth outcomes, permission changes, durable data mutation, migration/cutover/rollback, cross-surface work-unit invocation, governed artifact publication, release/deployment/certification, material failure/timeout/recovery, consequential approval/decision, and measured resource usage.

## 4. Observability and correlation profile — HARD GATE
Use `INC_G11_OBSERVABILITY_CORRELATION_PROFILE_V1` from `references/observability-correlation-profile-v1.md`.

The profile is intentionally aligned with modern observability practice while preserving SkillForge constraints:
- structured low-cardinality event classes;
- point-in-time Events for state changes/outcomes;
- Run/trace/span-style boundaries for operations with duration;
- Metric records for aggregatable numeric measurements;
- strongest available safe identity chain across project, actor, account-safe-ref, surface, run/activity/event, trace/correlation and idempotency context;
- stable external-reference graph linking GitHub, SharePoint, Teams, database, Handoff/work-unit, artifact/evidence and provider transaction records;
- no new physical table/schema merely for convenience.

Mandatory semantic event classes when the fact actually occurs:
`SECURITY_IDENTITY | MATERIAL_ACTION | DATA_TRANSACTION | CROSS_SURFACE_INVOCATION | ARTIFACT_AND_EXTERNAL_REFERENCE | RESOURCE_USAGE | FAILURE_RECOVERY | RELEASE_AND_GOVERNANCE`.

Do not fabricate unavailable IDs/telemetry. Preserve host/provider IDs only when actually exposed.

## 5. Receipt-bound success
When logging is mandatory, generic metadata such as `logging_target_ref` is not evidence that logging occurred. Terminal assurance requires the applicable gateway receipt state/evidence.

- If enqueue acceptance is sufficient for the activity policy, require `G11_ACCEPTED_FOR_PERSISTENCE` or stronger.
- If durable verification is required, only `G11_PERSISTED_VERIFIED` satisfies the logging dimension.
- Pending/degraded/missing receipt cannot be silently converted to `SUCCESS_VERIFIED`.

Approved exceptions must resolve through the G3 exception contract and remain narrow; G11 does not infer exceptions from missing capability.

## 6. Current physical route and schema boundary
Stage-27 canonical persistence route is:
`caller -> G11 compile/validate/redact/normalize -> INC_G11_LOG_ENVELOPE_V1 -> INC_G11_G17_DB_WRITE_ROUTE_V1 -> G17 relational DB -> durable read-back`.

The caller contract remains `INC_G11_CALLER_INTERFACE_V1`; callers do not change because of the physical cutover.

G11 owns semantic correctness and receipt meaning. G17 owns physical relational persistence, project scoping, transactional integrity, adapter behavior and database read-back.

The former `INC_G11_C7_WRITE_ROUTE_V1` SharePoint queue + Power Automate route is legacy-retirement-only. No new producer may select it after Stage-27 canonical cutover. Its exact source/history is archived before deletion.

Normal caller requests may not contain physical database table names, SharePoint List names, column names, IDs, raw SQL, provider project IDs or legacy queue paths.

## 7. Compact caller contract
Minimum caller fields remain:
- `producer_ref`
- `activity_id`
- `status`
- `summary`
- `is_test`

Defaults remain LIGHT/ASYNC where appropriate. Preserve caller run/root/trace/correlation IDs; derive safe deterministic IDs only where G11 owns derivation. Conflicting duplicate references fail validation.

One envelope always has one minimum factual Event. Action/Metric/Error/Approval records exist only when those facts actually occurred; never create synthetic filler.

## 8. Correlation and external-reference lineage — HARD GATE
For material activity, preserve the strongest available safe chain among:
`event_id`, `activity_id`, `root_run_id`, `run_id`, `parent_run_id`, `trace_id`, `span_id`, `correlation_id`, `idempotency_key`, `project_ref`, `producer_ref`, `surface_ref`, and conditional safe `account_ref`.

If distributed trace context is not available, use existing safe correlation identities rather than inventing W3C trace values.

Important outputs/actions reference rather than embed related records. Stable references may point to GitHub commit/PR/release/path, SharePoint drive item/file, Teams message/thread, DB/business object, Handoff/work unit, approval/decision, test/evidence/artifact, or external provider transaction/job/run.

Relations may include:
`INPUT_TO | OUTPUT_OF | EVIDENCE_FOR | PUBLISHED_AS | MUTATED_BY | APPROVED_BY | CAUSED_BY | RETRY_OF | ROLLBACK_OF | CHILD_OF | NOTIFIED_BY`.

## 9. Semantic field and validation rules
Preserve governed Run/Event/Action/Metric/Error/Approval contract fields supplied by callers and derive only fields G11 owns. Validate frozen Choice vocabularies, numeric/date types, identity consistency, RCA completeness, telemetry truthfulness and token-accounting arithmetic when applicable.

Required-but-nonderivable semantic facts fail closed rather than being filled with fake values.

Dynamic values belong in attributes/reference fields, not event-class names. Event names/classes should remain queryable and low-cardinality.

## 10. Security/redaction
Forbidden by default:
- raw/full prompts or model responses;
- hidden reasoning/chain-of-thought;
- passwords/private keys/API credentials/access or refresh tokens/cookies/OTP-MFA values/authorization headers/connection strings;
- unnecessary sensitive PII;
- physical persistence schema mappings from ordinary callers;
- raw file/document content where a stable reference is sufficient.

Safe usage counters/operational telemetry are distinct from credentials. Sensitive session/account identifiers should use safe stable/pseudonymous references or governed hashes when correlation is necessary.

## 11. Resource and token telemetry — HARD GATE
G9 owns resource policy; G11 owns safe persistence. Use `INC_RESOURCE_USAGE_V1`.

Actual telemetry status remains truthful: `MEASURED | PARTIAL | UNAVAILABLE`. Estimates never replace missing actuals.

When exposed, persist measured values such as:
- actual model/reasoning/speed profile;
- input/output/cached/reasoning tokens;
- tool-call count;
- plugin/connector invocation count;
- Skill invocation count;
- retry/evaluator count;
- duration;
- cost/credits/quota before/after/delta;
- measurement provenance.

If only aggregate quota change is exposed, log the aggregate measured value/provenance; do not fabricate exact per-run token consumption.

## 12. Sampling and noise control — HARD GATE
Never sample away mandatory high-value events including:
- CRITICAL/HIGH security/auth failures;
- approvals/owner decisions;
- durable data mutation/migration/cutover/rollback;
- destructive operations;
- release/deployment/certification;
- material failures/timeouts/recovery;
- audit-required financial/legal/data-integrity transactions.

Routine successful low-value events may be deduplicated/aggregated/sampled only when mandatory activity boundaries and coverage truth remain intact and the policy is explicit/reproducible.

Do not log every click, browser navigation, poll, formatting step or deterministic internal microstep.

## 13. UTF-8 and Persian RTL — HARD CROSS-CUTTING RULE
All G11 text serialization/transport is explicitly UTF-8. For Persian text:
- JSON/text payloads remain valid UTF-8; do not rely on platform-default encoding;
- structured logs store semantic text without corrupting machine identifiers;
- human-readable log/report rendering uses the applicable G18/G15/DocForge RTL standard;
- URL/ID/hash/path/version/code fields remain machine-clean LTR and must not contain BiDi control contamination;
- where read-back is available, round-trip/render validation is required for release acceptance.

Mojibake, replacement-character corruption, or direction corruption is a release defect.

## 14. Missing-log coverage auditor
Use `INC_G11_MISSING_LOG_COVERAGE_AUDITOR_V1`.

Compare an authoritative execution set against gateway receipts/persisted outcomes. If the authoritative denominator is unavailable, status is `NOT_MEASURABLE`; never fabricate a coverage percentage or claim 100%.

If a known mandatory execution has no receipt, report an aggregate governance defect. Do not generate one noisy notification for every missing row by default.

## 15. Governed learning/backlog intake
When a material future-version improvement/defect is discovered during runtime/build/test/release/operations, the producer may emit `INC_BACKLOG_INTAKE_EVENT_V1` through the compiled local profile/host adapter.

This is a proposal/evidence path, not autonomous mutation. Current critical failure handling still happens immediately and is not replaced by backlog capture.

## 16. Verification and receipts
ASYNC callers do not poll merely for convenience and do not claim durable PASS. REQUIRED verification coordinates real read-back. `G11_PERSISTED_VERIFIED` requires actual durable evidence.

## 17. Physical schema freeze
Normal G11 operation cannot create/delete/rename physical tables/columns/Lists or change field types/index/required/unique configuration. Stage-30 observability additions first map to the existing Run/Event/Action/Metric/Error/Approval and reference structures.

A genuine semantic gap returns `DB_SCHEMA_CHANGE_REQUIRED` and requires impact/migration/rollback/tests plus explicit owner approval.

## 18. Profiles and overhead
`LIGHT` — routine outcome only.
`STANDARD` — material workflows/publication/approval/testing/meaningful telemetry.
`DEEP` — explicit debugging/high-risk audit.

Do not log every microstep. More rows are not automatically better observability.

## 19. External change-request source gates
`G11_EXTERNAL_CHANGE_REQUEST.md` and related external deltas remain source-gated until exact bytes are read or the owner explicitly authorizes a documented substitute. This version does not claim source-unknown fields such as the provisional Inspectable Primary Trace Reference delta.

## 20. Critical controls
- `G11-CC-01` stable run/root/trace/correlation meaning across retries.
- `G11-CC-02` forbidden raw/secret/sensitive payload excluded.
- `G11-CC-03` approved G17 DB route and real read-back before verified durable PASS.
- `G11-CC-04` no unauthorized physical schema mutation.
- `G11-CC-05` no direct producer physical-store mutation; idempotency/test class preserved.
- `G11-CC-06` compact caller interface; no duplicated writer/schema responsibilities.
- `G11-CC-07` mandatory logging uses `INC_G11_RUNTIME_GATEWAY_V1` and produces a receipt bound to activity/run/envelope.
- `G11-CC-08` activity aggregation does not omit mandatory governed outcomes.
- `G11-CC-09` coverage percentage is emitted only with an authoritative denominator; otherwise `NOT_MEASURABLE`.
- `G11-CC-10` applicable Persian outbound/log text round-trips in UTF-8 and presentation direction is deterministic without contaminating machine IDs.
- `G11-CC-11` material security/data/cross-surface/artifact/resource/failure/release outcomes follow `INC_G11_OBSERVABILITY_CORRELATION_PROFILE_V1`.
- `G11-CC-12` important external outputs use stable reference lineage rather than copied payloads.
- `G11-CC-13` measured and estimated resource telemetry remain distinct; unavailable telemetry is never fabricated.
- `G11-CC-14` high-value mandatory events are never sampled away; low-value success sampling is explicit and reproducible.

## 21. Stop condition
Stop after one sufficient factual semantic outcome has passed the required gateway/receipt semantics. Do not claim persistence without receipt/read-back and do not emit redundant logs merely because more fields exist.

## Mandatory G16 cross-surface generation gate
Contract: `INC_G16_CROSS_SURFACE_EXECUTION_DELIVERY_V1`.

When this Skill generates a prompt, instruction, work order, Handoff, report, command file, execution artifact, or operational file intended for another Chat/Work/Codex/agent surface, it MUST resolve/apply latest G16 before generation. No G16 => `BLOCKED_G16_NOT_APPLIED`.

Administrative/infrastructure execution MUST follow: PowerShell -> official API -> official CLI -> structured browser/connected tool -> visual UI. On Windows Codex with verified direct terminal capability, PowerShell 7 is the mandatory first candidate. Lower-priority fallback requires an approved reason code.

Generated cross-surface artifacts MUST be persisted to governed GitHub/SharePoint under G1/G17 placement, verified by remote read-back, and transferred only by verified remote link or stable reference. Direct local/sandbox file delivery, direct cross-surface attachment, or inline full-file delivery as a substitute for governed publication is prohibited. Secrets/MFA/credentials never enter prompts, Handoffs, logs, or generated handoff artifacts.

## Release identity observability — HARD GATE
Every material build/integration/validation/promotion/rollback/runtime event for SkillForge carries `release_id`, `package_version`, applicable `skill_versions`, `source_sha`, `pipeline_version`, `artifact_digest`, `work_unit_id`, `lease_id` when applicable, and `executor_surface`. These fields correlate local-CI evidence with runtime behavior without storing high-volume event history in the Handoff file.


## Publication privacy boundary (mandatory)
Before any public write, use G8 `INC_PUBLICIZATION_PRIVACY_GATE_V2` and G12's
executable public validator. Review every file and archive member, metadata and
platform surface against exact owner consent and the final content digest.
Unknown, skipped or unreadable content blocks publication. A private release,
local test pass, or simulation waiver never authorizes public disclosure.
Keep owner/environment data outside distributable skills in an explicitly
selected, hash-verified private profile. Public exports are deny-by-default,
from a per-file reviewed allowlist; no live history or owner inventory belongs
in a generic skill. Re-check the actual destination and published bytes.

Privacy responsibility: Store full incident evidence privately; public logs contain only redacted counts.

## Private installation and user-specific parameterization — SkillForge 3.0.4
The distributable contains no owner-specific service IDs, credential values, site/folder URLs, tenant IDs, or private evidence. Use `config/setup-service-catalog.json` and `setup/CHATGPT_FIRST_RUN.md` for the setup plan. Resolve configuration through a user-authorized private external profile, pinned by exact SHA-256; validate current connector identity/permissions/readback for every real action. Missing bindings must produce a read-only/configuration-needed result, never invented values or silent mutation. G20 is a separate setup-runtime candidate; this is not a claim of automatic ChatGPT plugin execution. Public feedback remains OFF until a particular sanitized payload and destination receive explicit owner permission.
Relevant optional service families: `LOGGING`.
