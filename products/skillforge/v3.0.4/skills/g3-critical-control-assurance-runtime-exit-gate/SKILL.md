---
name: g3-critical-control-assurance-runtime-exit-gate
description: SkillForge universal low-overhead runtime exit gate for governed Skills,
  Agents, Chats, Work and managed activities, with receipt-bound logging assurance
  and explicit narrow exceptions.
metadata:
  stable_id: G03-SKL-001
  visible_id: G3
  display_name: G3-Critical Control Assurance & Runtime Exit Gate
  version: 1.1.2
  domain: governance
  complexity_profile: LITE
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
  global_assurance_contract_ref: INC_CRITICAL_CONTROL_ASSURANCE_V2
  logging_gateway_contract_ref: INC_G11_RUNTIME_GATEWAY_V1
  logging_exception_registry_ref: INC_LOGGING_ASSURANCE_EXCEPTION_REGISTRY_V1
  logging_target_ref: INC_LOG_STORE
  resource_policy_ref: INC_RESOURCE_POLICY_PROFILE
  notification_contract_ref: INC_NOTIFICATION_EVENT_V1
---

## Current release policy (PRIOR_RELEASE)
For release/build/promotion decisions, use `INC_AUTONOMOUS_RELEASE_ACCEPTANCE_V1`
at `../g0-skill-architect-builder/references/autonomous-release-policy-v1.md`. Available local/API/plugin/simulation tests are required;
unavailable third-party/runner/user/native-host assurance is optional and nonblocking.
This supersedes conflicting release-only clauses below or in detailed references.
Security, authorization, integrity and truthful runtime evidence remain mandatory.


# G3-Critical Control Assurance & Runtime Exit Gate v1.1.2 - Released
## 1. Purpose
G3 is the compact universal exit-assurance layer. It preserves Skill-local critical controls and adds a small global kernel so applicable security, resource, logging, notification and archive obligations cannot be silently forgotten.

## 2. Global assurance dimensions
1. `LOCAL_CRITICAL_CONTROLS`
2. `SECURITY_PRIVACY_PERMISSION`
3. `TOKEN_CONTEXT_OPTIMIZATION`
4. `LOGGING_TRACEABILITY`
5. `NOTIFICATION_DECISION_AND_DELIVERY`
6. `ARCHIVE_PUBLICATION_PRESERVATION`

Normal runtime carries only compact dimension states/evidence refs; provider policies load JIT on material branch/failure/evidence need.

## 3. Receipt-bound logging assurance — HARD GATE
When G11 logging is applicable and mandatory, `logging_target_ref`, metadata presence, a declared log intent, or a generic dependency reference is **not** proof that logging occurred.

Resolve `LOGGING_TRACEABILITY` from `INC_G11_RUNTIME_GATEWAY_V1` receipt evidence:
- policy requiring enqueue acceptance -> `G11_ACCEPTED_FOR_PERSISTENCE` or stronger;
- policy requiring durable verification -> `G11_PERSISTED_VERIFIED` only;
- `G11_GATEWAY_VALIDATED`, pending, degraded, missing or mismatched receipt does not satisfy a stronger requirement.

The receipt must bind the same governed `activity_id`, `run_id` and envelope/evidence identity. Mismatch fails closed.

If logging is required and the necessary receipt is absent, G3 blocks or downgrades terminal success; it does not infer that G11 probably ran.

## 4. Explicit narrow logging exceptions
Use `INC_LOGGING_ASSURANCE_EXCEPTION_REGISTRY_V1`.

An exception is valid only when all registry scope conditions match. Missing capability, producer preference, cost/resource pressure or silence is never an implicit exception.

Current bounded Candidate exception `G16-NO-RUNTIME-LOGGING-001` applies only to ordinary G16 Conversation Continuity `PERSIST_CURRENT` / `RESUME_EXPLICIT` operations. It does **not** apply to G16 Build/Test/Validation/Evaluation/Release/Migration, security incidents, material failures or explicit audit.

On a valid exception branch, `LOGGING_TRACEABILITY = EXCEPTION_NA_WITH_REASON`; do not fabricate a receipt. The exception cannot widen to another Skill or branch without a governed change.

## 5. Notification anti-noise
Every activity classifies G15 applicability, but not every activity sends. `NOT_REQUIRED` with reason is valid. If send is required, required route/render/read-back evidence must exist.

## 6. Archive/publication assurance
Every activity evaluates G1 applicability. Artifact-producing/user-deliverable file paths additionally require applicable G1 remote persistence/link evidence. Local/Windows/inline-only file completion cannot satisfy archive/publication assurance.

## 7. Independent double-check
Ordinary low-risk work uses compact self-check. G12/G13 independently double-check release/publication, destructive/irreversible work, high-consequence security/legal/financial/data-integrity activity, explicit certification, conflicting evidence or prior failed control.

## 8. Failure states
`GLOBAL_ASSURANCE_PASS | GLOBAL_ASSURANCE_FAIL | LOCAL_CONTROL_FAILURE | SECURITY_GATE_UNRESOLVED | OPTIMIZATION_CHECK_MISSING | LOGGING_RECEIPT_MISSING | LOGGING_RECEIPT_MISMATCH | TRACE_PERSISTENCE_DEGRADED | LOGGING_EXCEPTION_INVALID | NOTIFICATION_REQUIRED_NOT_VERIFIED | ARCHIVE_GATE_UNRESOLVED`.

## 9. Stop condition
Do not return terminal `SUCCESS_VERIFIED` until every applicable global dimension is PASS or a specifically permitted `N/A/EXCEPTION_NA_WITH_REASON` with evidence/rationale. Mandatory unresolved logging cannot be hidden by generic metadata.

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

Privacy responsibility: Do not override a failed or unknown privacy control with an aggregate PASS.

## Private installation and user-specific parameterization — SkillForge 3.0.4
The distributable contains no owner-specific service IDs, credential values, site/folder URLs, tenant IDs, or private evidence. Use `config/setup-service-catalog.json` and `setup/CHATGPT_FIRST_RUN.md` for the setup plan. Resolve configuration through a user-authorized private external profile, pinned by exact SHA-256; validate current connector identity/permissions/readback for every real action. Missing bindings must produce a read-only/configuration-needed result, never invented values or silent mutation. G20 is a separate setup-runtime candidate; this is not a claim of automatic ChatGPT plugin execution. Public feedback remains OFF until a particular sanitized payload and destination receive explicit owner permission.
Relevant optional service families: `LOGGING`.
