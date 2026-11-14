---
name: g15-notification-human-decision-gateway
description: G15-Notification & Human Decision Gateway 4.4.2 — SkillForge Teams-first
  governed notification/human-decision gateway with deterministic UTF-8/RTL delivery,
  canonical routing/rendering and verified read-back.
metadata:
  stable_id: G15-SKL-001
  visible_id: G15
  display_name: G15-Notification & Human Decision Gateway
  version: 4.4.2
  domain: governance
  complexity_profile: FULL
  functional_role: ROUTER
  lifecycle: production
  strictness: S4
  governance_owner: INOMondial Inc.
  builder_framework_ref: INC_SKILLFORGE
  framework_id: INC_SKILLFORGE
  framework_name: SkillForge
  framework_membership: MEMBER
  framework_registry_ref: INC_SKILL_NAMESPACE_REGISTRY
  next_version_backlog_ref: INC_SKILLFORGE_UNIFIED_BACKLOG
  resource_policy_ref: INC_RESOURCE_POLICY_PROFILE
  logging_target_ref: INC_LOG_STORE
  notification_contract_ref: INC_NOTIFICATION_EVENT_V1
  universal_table_contract_ref: INC_UNIVERSAL_TABLE_REFERENCEABILITY_V1
  critical_control_contract_ref: INC_CRITICAL_CONTROL_ASSURANCE_V1
---

## Current release policy (PRIOR_RELEASE)
For release/build/promotion decisions, use `INC_AUTONOMOUS_RELEASE_ACCEPTANCE_V1`
at `../g0-skill-architect-builder/references/autonomous-release-policy-v1.md`. Available local/API/plugin/simulation tests are required;
unavailable third-party/runner/user/native-host assurance is optional and nonblocking.
This supersedes conflicting release-only clauses below or in detailed references.
Security, authorization, integrity and truthful runtime evidence remain mandatory.


# G15-Notification & Human Decision Gateway v4.4.2 - Released
## 1. Purpose
G15 is the mandatory Teams-first notification/report/human-decision boundary. It owns production priority routing, test isolation, governed writer control, target-native rendering, UTF-8/RTL correctness, pre-send validation, post-send read-back, exact-thread traceability and closed-loop owner replies.

Existing G15 rendering/routing/reply references remain applicable. This version does **not** implement the separate source-gated `G15_EXTERNAL_CHANGE_REQUEST.md` multi-channel completion delta because its exact source bytes are not available.

## 2. Single-writer event boundary — HARD GATE
Governed producers emit `INC_NOTIFICATION_EVENT_V1`; they do not independently bypass G15 to deliver governed production notifications. Only G15 or an explicitly approved adapter writes production notification traffic.

## 3. Default Teams destination
Unless the user explicitly authorizes a different destination for that message/workflow, final priority maps deterministically:
- HIGH -> `INC_G15_PRIORITY_HIGH_CHANNEL`
- MED -> `INC_G15_PRIORITY_MED_CHANNEL`
- LOW -> `INC_G15_PRIORITY_LOW_CHANNEL`

Producer/context/source channel cannot self-authorize an override. Genuine development/integration/acceptance tests use `INC_G15_TEST_CHANNEL`; production events cannot be disguised as tests.

## 4. Priority
HIGH covers blockers/crashes/serious security/legal/financial/data-integrity/archive/release failures and high-consequence decisions. MED covers important nonblocking review/action/owner gates/degraded state. LOW covers verified routine success/informational completion. Safety floors override learned/user down-prioritization.

## 5. UTF-8 and deterministic Persian RTL — HARD GATE
Every G15 outbound text payload is explicitly serialized as UTF-8 end-to-end.

For Persian human-facing content:
- HTML-capable surfaces use explicit `lang="fa"` and `dir="rtl"` on the Persian block/container when supported by the destination renderer;
- plain-text/mixed-script surfaces use Unicode BiDi isolation/marks as required so Persian punctuation/numbers and embedded LTR values render correctly;
- English/Persian blocks remain visibly separated when bilingual;
- URL, ID, hash, path, version, code and other machine identifiers remain machine-clean LTR and must not contain BiDi control characters;
- renderer/source HTML is never exposed to the user as the visible message;
- post-send read-back/render validation checks that required Persian text round-trips without mojibake, replacement characters or direction corruption.

If the destination cannot satisfy required encoding/direction semantics, return `UTF8_RTL_RENDERING_FAILED`; do not silently downgrade Persian to malformed text.

## 6. Canonical Teams rendering
Ordinary governed Teams reports/messages use canonical renderer `G15_TEAMS_NATIVE_V1` with `html_content` or a verified target-native equivalent. Flat/plain-text/Markdown/ad-hoc fallback is prohibited when the canonical contract is required.

Allowed simple Teams HTML may include headings, paragraphs, bold, breaks, lists, links, horizontal rules and language/direction containers. Avoid unsupported CSS/JavaScript/table-dependent layout.

If a human-readable table is intentionally produced on another applicable G15 surface, it must follow `INC_UNIVERSAL_TABLE_REFERENCEABILITY_V1` with first column `NUM#`. Ordinary Teams report layout continues to prefer labeled blocks/lists.

## 7. Visible report structure
Ordinary production reports remain outcome-first and scan-friendly with meaningful title/identity, status, project context, concise categorized details, inspectable quick links, next step/no-action, project progress and final search tags. Long evidence is linked rather than pasted.

## 8. Send/read-back completion — HARD GATE
Lifecycle:
`PLAN -> DESTINATION_POLICY_PASS -> PRE_SEND_CONTRACT_PASS -> UTF8_RTL_CONTRACT_PASS -> SEND_ACCEPTED -> REMOTE_READBACK_PASS -> EXACT_THREAD_TRACE -> SENT_COMPLETE`.

Read-back verifies required semantic blocks, actual route/container when known, exact evidence links, no truncation, usable thread link, and applicable UTF-8/RTL integrity. A successful API write alone is never `SENT_COMPLETE`.

## 9. Human decision and meaningful reply
Same-thread Teams reply remains default decision surface unless a native approval/card is explicitly required and actually available. Preserve full operator reply; latest valid pre-lock choice supersedes earlier choice; after irreversible lock a new reply is a new instruction. Serious/high-consequence actions require governed confirmation.

Every meaningful owner reply closes the loop in the same thread with what was understood, current state and next action. Work-triggering replies receive progress/final result/evidence in the same root thread.

## 10. Reply monitoring
G15 does not own a dedicated timer. Existing Scheduler/Dispatcher invocation, cursor/watermark filtering, owner-ID preference, outbound-ledger exclusion, processed-reply idempotency and parent-thread resolution remain required.

## 11. Priority feedback
Owner priority feedback updates classification but does not authorize route bypass. Down-prioritization cannot violate mandatory HIGH floors. Durable learning requires persistence/read-back evidence.

## 12. G11 integration
G15 dispatch/reply outcomes use G11 semantic contracts when logging applies. Persian log text follows G11 UTF-8/RTL persistence rules. Stable thread/evidence refs are logged without copying full sensitive messages.

## 13. Source-gated external multi-channel request
`G15_EXTERNAL_CHANGE_REQUEST.md` remains `BLOCKED_SOURCE_REQUIRED` in `INC_SOURCE_REFERENCE_REGISTRY`.

Therefore v4.4.2 does not claim:
- new alternate completion-channel authorization rules;
- source-unknown routing precedence between Teams and another channel;
- source-unknown primary completion-reference fields.

Those are implemented only after exact source readback or explicit owner authorization of a documented substitute.

## 14. Critical controls
Existing G15 routing/rendering/read-back/decision/single-writer/reply/override controls remain in force. Add:
- `G15-CC-09` — all outbound text is UTF-8; applicable Persian presentation is deterministic RTL and machine identifiers remain BiDi-clean.
- `G15-CC-10` — post-send read-back verifies applicable encoding/direction integrity before `SENT_COMPLETE`.

## 15. Stop condition
Noninteractive delivery stops only after canonical route/render/UTF-8-RTL contract/send/read-back/thread evidence passes, or an exact blocked/degraded state is recorded. No unsupported multi-channel behavior is claimed while the external source remains blocked.

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

Privacy responsibility: Send detailed findings only to an authorized private destination.

## Private installation and user-specific parameterization — SkillForge 3.0.4
The distributable contains no owner-specific service IDs, credential values, site/folder URLs, tenant IDs, or private evidence. Use `config/setup-service-catalog.json` and `setup/CHATGPT_FIRST_RUN.md` for the setup plan. Resolve configuration through a user-authorized private external profile, pinned by exact SHA-256; validate current connector identity/permissions/readback for every real action. Missing bindings must produce a read-only/configuration-needed result, never invented values or silent mutation. G20 is a separate setup-runtime candidate; this is not a claim of automatic ChatGPT plugin execution. Public feedback remains OFF until a particular sanitized payload and destination receive explicit owner permission.
Relevant optional service families: `TEAMS`, `MICROSOFT_CALENDAR`, `GOOGLE_CALENDAR`.
