---
name: g9-token-context-efficiency-standardizer
description: SkillForge provider-neutral resource, quota, credit, capacity and FinOps
  policy governor with low-overhead truthful telemetry, zero-model collectors, dual-protection
  provider controls, bounded optimization and governed future-improvement intake.
metadata:
  stable_id: O6-SKL-009
  visible_id: G9
  display_name: G9-Token & Context Efficiency Standardizer
  version: 5.4.2
  domain: governance
  complexity_profile: FULL
  functional_role: QUALITY
  lifecycle: production
  strictness: S3
  governance_owner: INOMondial Inc.
  builder_framework_ref: INC_SKILLFORGE
  framework_id: INC_SKILLFORGE
  framework_name: SkillForge
  framework_membership: MEMBER
  framework_registry_ref: INC_SKILL_NAMESPACE_REGISTRY
  next_version_backlog_ref: INC_SKILLFORGE_UNIFIED_BACKLOG
  backlog_intake_event_contract_ref: INC_BACKLOG_INTAKE_EVENT_V1
  resource_policy_ref: INC_RESOURCE_POLICY_PROFILE
  telemetry_target_ref: INC_LOG_STORE
  runtime_profile_ref: INC_GOVERNANCE_RUNTIME_PROFILE_V1
  dpga_contract_ref: INC_DPGA_ASSURANCE_RECORD_V1
  critical_control_contract_ref: INC_CRITICAL_CONTROL_ASSURANCE_V1
  data_resource_optimization_ref: INC_G9_G17_DATA_RESOURCE_OPTIMIZATION_V1
  resource_finops_control_plane_ref: INC_G9_RESOURCE_FINOPS_CONTROL_PLANE_V1
  resource_adapter_profile_ref: INC_RESOURCE_ADAPTER_PROFILE
  provider_capability_profile_ref: INC_PROVIDER_CAPABILITY_PROFILE
  provider_resource_profile_registry_ref: INC_PROVIDER_RESOURCE_PROFILE_REGISTRY_V1
  data_governor_ref: G17-SKL-002
---

## Current release policy (PRIOR_RELEASE)
For release/build/promotion decisions, use `INC_AUTONOMOUS_RELEASE_ACCEPTANCE_V1`
at `../g0-skill-architect-builder/references/autonomous-release-policy-v1.md`. Available local/API/plugin/simulation tests are required;
unavailable third-party/runner/user/native-host assurance is optional and nonblocking.
This supersedes conflicting release-only clauses below or in detailed references.
Security, authorization, integrity and truthful runtime evidence remain mandatory.


# G9-Token & Context Efficiency Standardizer v5.4.2 - Released
## 1. Objective
Use the lowest sufficient execution profile while preserving correctness, evidence, safety, approval, deadline and explicit user constraints. Optimization covers execution capability, reasoning, context, tools, loops/retries/subagents/tests, output and available quota/resource signals. Never manufacture work merely to consume quota.

## 2. Zero-load routine path
Routine managed runtime (`RC0–RC2`) does not load the full optimizer just for compliance. G0/G9 compile a small activity resource map at Build-Time; host/runtime resolves it deterministically.

Default: `deterministic/tool -> smallest sufficient capability -> smallest JIT context -> relevant tools only -> bounded pass -> compact truthful telemetry`.

## 3. Independent dimensions
Never auto-collapse Artifact Complexity, Security, Test Profile, Resource Class, Execution Tier or Resource State. Surplus does not imply strongest model; scarcity does not lower critical work below safety/quality floor.

## 4. Compiled resource profile
For each materially distinct activity compile:
`activity_type -> RC -> desired execution tier/capability -> required/conditional/skipped modules -> context/tool limits -> retry/loop/subagent/test ceilings -> escalation triggers -> measurement policy`.

Separate Build resource plan from Runtime resource plan. Child Skills carry minimum stable references, not the full G9 policy.

## 5. Enforcement truthfulness
G9 recommends/decides desired profile; Host/Orchestrator enforces it. `ENFORCED_ROUTING` is used only with verified host control; otherwise `ADVISORY_ROUTING`. Never claim a model/reasoning/speed change without host confirmation.

## 6. Telemetry and overhead
Measure only what the execution surface actually exposes. Relevant dimensions can include:
- model/capability request vs actual;
- input/output/total usage counters when exposed;
- context loaded/retrieved size or bounded proxy;
- tool-call count and material tool-result size;
- retries/loops/subagents/tests/evaluators;
- external writes/read-backs;
- latency and provider cost when exposed;
- quota/reset/burn/forecast signals when exposed.

Every dimension is explicitly `MEASURED | ESTIMATED | UNAVAILABLE` or the compatible G11 semantic equivalent. Estimates never replace missing actuals and cannot be reported as actual usage.

Telemetry is sent through G11 compact semantic contracts; do not create a parallel resource database/schema.

## 7. Material-change reforecasting
Reclassify/reforecast on material events only: significant context/tool growth, risk increase, lower-profile quality failure, scope growth, retry/no-progress loop, materially changed cost/burn/quota, reset threat or explicit audit/optimization request. Do not poll/reforecast every microstep.

## 8. Quality/safety floor
Security, approval, release integrity, required testing/evidence and explicit user constraints cannot be optimized away. Prefer deferring lower-value optional work before weakening required quality.

## 9. Governed learning intake
If runtime/build/test/release observes a recurring resource inefficiency or future improvement that would materially improve later runs, emit/return `INC_BACKLOG_INTAKE_EVENT_V1` as `SYSTEM_DISCOVERED` with evidence/confidence/occurrence where available.

This never self-modifies Production, never recursively loads G0 during ordinary runtime, and never creates work solely to optimize itself. Backlog owner performs dedupe/correlation/qualification.

## 10. Integration
G1 artifact/read-back integrity cannot be skipped for savings. G11 persists only factual available telemetry. G15 required notifications/decisions cannot be suppressed solely for resource savings. G12/G13 proportional testing/evaluation is preserved.

### G17 data/query resource architecture
Contract: `INC_G9_G17_DATA_RESOURCE_OPTIMIZATION_V1`.

For material persistence/query work, optimize in this order before prompt/token micro-compression:
1. storage/authority placement;
2. query execution location;
3. projection and row bounds;
4. server-side filtering/sorting/aggregation;
5. joins or bounded batching instead of N+1;
6. keyset/cursor pagination for growing datasets;
7. transaction and round-trip shape;
8. index/query-plan design;
9. cache/state placement only with explicit staleness/TTL/invalidation semantics;
10. tool route and result shape;
11. model-context minimization;
12. stronger model/capability advisory only when it is likely to produce a materially better architecture.

G17 owns data/query/database architecture and provider adapters. G9 owns resource optimization. G11 owns telemetry. No duplicate resource database or provider-specific consumer contract is allowed.

Provider resource claims use `MEASURED | VALIDATED_ESTIMATE | UNKNOWN`. Derived savings must identify their measured basis; modeled savings are labeled estimated scenarios.

Required owner mentions, security, encryption, project isolation, read-back, evidence, backup and migration/rollback are non-optimizable invariants.


## 11. Provider-neutral Resource / FinOps control plane — HARD GATE
Contracts:
- `INC_G9_RESOURCE_FINOPS_CONTROL_PLANE_V1` — `references/resource-finops-control-plane-v1.yaml`
- `INC_RESOURCE_ADAPTER_PROFILE` — `references/resource-adapter-profile-contract-v1.yaml`
- `INC_PROVIDER_CAPABILITY_PROFILE` and `INC_PROVIDER_RESOURCE_PROFILE_REGISTRY_V1` are canonically owned under G17 provider-profile references.

Canonical flow:
`provider/service -> approved adapter -> G11 semantic normalization -> G17 persistence/query -> G9 bounded analysis/forecast/optimization -> G15 alerts/decisions`.

G9 owns provider-neutral resource/cost/quota/credit/capacity policy, cadence classes, source precedence, forecasts, anomalies, prevention and unit economics. G9 MUST NOT become a provider-specific implementation layer or create a parallel database.

For provider resource decision truth use `MEASURED | VALIDATED_ESTIMATE | UNKNOWN`. G11 acquisition statuses may remain `MEASURED | PARTIAL | DERIVED | ESTIMATED | UNAVAILABLE`; PARTIAL/DERIVED/ESTIMATED may map to `VALIDATED_ESTIMATE` only with explicit validation/provenance, otherwise map to `UNKNOWN`. Quota percentage/delta MUST NOT be converted to raw tokens without an authoritative conversion source, and provider/project formulas MUST NOT be invented.

Acquisition is event/inline/push first. Five-minute polling is reserved for hard operational headroom that can interrupt work. Broad five-minute browser/UI monitoring is prohibited. Billing/cost reconciliation is daily/event based unless provider-specific operational evidence proves otherwise. Routine collectors/watchers make zero model/LLM calls.

Every provider/service introduced or materially depended on MUST have a G17-owned resource/capability profile before Production. Consumer Skills MUST NOT directly bind provider-specific APIs when an approved adapter exists.

Dual protection:
- Layer 1 — SkillForge-owned minimum decision-grade telemetry/history/threshold/forecast/RCA/prevention.
- Layer 2 — provider-native safeguards such as budgets, alerts, quotas, schedulers, backup/retention, health/webhooks/security controls.
Layer 2 supplements Layer 1 and cannot silently replace it.

Paid add-ons, top-ups, purchases, plan upgrades, quota increases or paid monitoring activation require explicit owner approval and cost/benefit disclosure. The activation route authority is G16 `INC_MACHINE_ROUTE_BEFORE_VISUAL_UI_V1`; no provider-local competing route ladder may override it.

Stage-30 A10 registry baseline contains 11 provider/service profile entries. The existing Hatchable adapter is the only currently implemented adapter in this registry; the other 10 entries are explicit `GAP_NOT_IMPLEMENTED_BLOCKS_PRODUCTION`. A10 does not deploy a live DB schema, watcher/poller, provider setting or paid/native safeguard. Those require later bounded implementation/activation gates plus final G12/G13.

Validation: `scripts/validate_resource_finops_profile.py`; deterministic tests: `tests/test_resource_finops_control_plane.py`.

## 12. Compiled runtime regression — HARD GATE
Contract: `INC_G9_COMPILED_RUNTIME_REGRESSION_V1` in `references/compiled-runtime-regression-v1.yaml`.

Normal configured runtime MUST use the compiled minimum-sufficient governance profile and MUST NOT recursively activate build-only or installer-only governance. G19 activation is permitted only for packaging/distribution/build intent. G20 activation is permitted only for setup/install/upgrade/health/repair intent. Regression tests compare equivalent workloads and identical functional requirements; mandatory security, approval, logging, continuity, failure and evidence controls remain non-optimizable. Measured context/token deltas are preferred; reproducible proxies are explicitly labeled ESTIMATED.

## 13. External reserve request source gate
`G9_EXTERNAL_CHANGE_REQUEST.md` remains `BLOCKED_SOURCE_REQUIRED` in `INC_SOURCE_REFERENCE_REGISTRY` because exact source bytes are unavailable.

Therefore v5.4.2 does **not** claim implementation of the provisional Weekly Useful-Surplus Reserve formula, currency/provenance fields or exact skip semantics from that source. The existing general reserve/reset-threat optimization behavior remains; source-specific behavior waits for exact readback or explicit owner substitute authorization.

## 14. Critical controls
- `G9-CC-01` deterministic/metadata/diff checks precede heavier work where sufficient.
- `G9-CC-02` Resource Class remains independent from artifact complexity/security.
- `G9-CC-03` required quality/security/approval/release/testing/evidence is never optimized away.
- `G9-CC-04` unavailable actual telemetry is not fabricated/replaced by estimates.
- `G9-CC-05` material resource inefficiency may create governed SYSTEM_DISCOVERED intake, but cannot self-modify Production or recursively load G0.
- `G9-CC-06` source-specific reserve behavior is not claimed while `G9_EXTERNAL_CHANGE_REQUEST.md` is source-blocked.
- `G9-CC-07` material data/query work applies `INC_G9_G17_DATA_RESOURCE_OPTIMIZATION_V1` before token micro-optimization and preserves all non-optimizable security/integrity/owner-attention gates.
- `G9-CC-08` every Production provider/service resolves a G17-owned adapter/resource/capability profile; direct consumer provider binding is prohibited when an approved adapter exists.
- `G9-CC-09` routine collectors use zero model calls; broad five-minute browser/UI polling is prohibited.
- `G9-CC-10` resource truth is MEASURED/VALIDATED_ESTIMATE/UNKNOWN and quota deltas are never converted into token facts without authoritative conversion evidence.
- `G9-CC-11` paid provider changes require explicit owner approval plus cost/benefit disclosure, and activation inherits the G16 machine-first/UI-last authority.
- `G9-CC-12` G11 owns semantic normalization, G17 owns persistence/adapters, G15 owns alert/decision delivery, and a parallel G9 resource database is prohibited.

## 15. Stop condition
Stop when one sufficient resource profile/advisory is resolved or the governed task completes. Do not add optimization narration to trivial work unless requested.

## Mandatory G16 cross-surface generation gate
Contract: `INC_G16_CROSS_SURFACE_EXECUTION_DELIVERY_V1`.

When this Skill generates a prompt, instruction, work order, Handoff, report, command file, execution artifact, or operational file intended for another Chat/Work/Codex/agent surface, it MUST resolve/apply latest G16 before generation. No G16 => `BLOCKED_G16_NOT_APPLIED`.

Administrative/infrastructure execution MUST follow: PowerShell -> official API -> official CLI -> structured browser/connected tool -> visual UI. On Windows Codex with verified direct terminal capability, PowerShell 7 is the mandatory first candidate. Lower-priority fallback requires an approved reason code.

Generated cross-surface artifacts MUST be persisted to governed GitHub/SharePoint under G1/G17 placement, verified by remote read-back, and transferred only by verified remote link or stable reference. Direct local/sandbox file delivery, direct cross-surface attachment, or inline full-file delivery as a substitute for governed publication is prohibited. Secrets/MFA/credentials never enter prompts, Handoffs, logs, or generated handoff artifacts.



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

Privacy responsibility: Never skip a file, archive, or remote surface to save tokens or compute.

## Private installation and user-specific parameterization — SkillForge 3.0.4
The distributable contains no owner-specific service IDs, credential values, site/folder URLs, tenant IDs, or private evidence. Use `config/setup-service-catalog.json` and `setup/CHATGPT_FIRST_RUN.md` for the setup plan. Resolve configuration through a user-authorized private external profile, pinned by exact SHA-256; validate current connector identity/permissions/readback for every real action. Missing bindings must produce a read-only/configuration-needed result, never invented values or silent mutation. G20 is a separate setup-runtime candidate; this is not a claim of automatic ChatGPT plugin execution. Public feedback remains OFF until a particular sanitized payload and destination receive explicit owner permission.
Relevant optional service families: `LOCAL_ONLY`.
