---
name: g18-human-conversation-output-governor
description: Canonical G18/CHAT1 human conversation and output governor for ChatGPT
  Chat, Work and Codex. Enforces one canonical authority, surface-aware response rendering,
  Persian RTL/BiDi-safe structured output, semantic paragraph direction, citation-leak
  blocking, turn-budget segmentation, governed artifact delivery, G16 handoff visibility,
  and deterministic pre-send validation.
metadata:
  stable_id: CHAT1-SKL-001
  visible_id: G18
  display_name: G18-Human Conversation & Output Governor
  version: 0.1.47
  domain: conversation-output-governance
  functional_role: ROUTER
  complexity_profile: FULL
  lifecycle: production
  strictness: S4
  governance_owner: INOMondial Inc.
  builder_framework_ref: INC_SKILLFORGE
  framework_membership: MEMBER
  framework_registry_ref: INC_SKILL_NAMESPACE_REGISTRY
  backlog_topology: CENTRAL_FRAMEWORK_BACKLOG
  next_version_backlog_ref: INC_SKILLFORGE_UNIFIED_BACKLOG
  backlog_owner_ref: G18
  artifact_egress_contract_ref: INC_REMOTE_ARTIFACT_DELIVERY_V2
  artifact_contract_attestation_ref: G1_ARTIFACT_DELIVERY_CONTRACT_ATTESTATION_V2
  artifact_contract_compatibility_matrix_ref: INC_G1_G18_ARTIFACT_DELIVERY_COMPATIBILITY_V2
  artifact_router_ref: G1
  security_ref: G8
  assurance_ref: G3
  continuity_ref: G16
  document_skill_ref: DF1
  bidi_layout_standard_ref: INC_BIDI_LAYOUT_TYPOGRAPHY_V1
  skillforge_feedback_intake_ref: INC_SKILLFORGE_FEEDBACK_INTAKE_V1
  owner_backlog_coverage_ref: INC_OWNER_CONVERSATION_BACKLOG_COVERAGE_V1
---

## Current release policy (PRIOR_RELEASE)
For release/build/promotion decisions, use `INC_AUTONOMOUS_RELEASE_ACCEPTANCE_V1`
at `../g0-skill-architect-builder/references/autonomous-release-policy-v1.md`. Available local/API/plugin/simulation tests are required;
unavailable third-party/runner/user/native-host assurance is optional and nonblocking.
This supersedes conflicting release-only clauses below or in detailed references.
Security, authorization, integrity and truthful runtime evidence remain mandatory.


# g18-human-conversation-output-governor - compact activity router

## Authority and evidence boundary
This entrypoint remains the sole activation authority. Read only the sections required
for the present operation in `references/detailed-governance.md`; that file preserves
the full normative contract, not a second executable Skill. Resolve every relative
path inside it from this Skill directory, not the references directory. System and
host instructions take precedence. Do not treat repository source, local fixtures,
profile configuration or historical PASS labels as authenticated live evidence.
A fresh review by the same executor is not independent G12/G13 certification.
Do not widen scope, create services, change credentials or invent telemetry.

## Activation and output authority
Use for human-facing conversation and output. G16 supplies state and S/M; G18 renders,
never invents sequence numbers, completion, permissions, quotas or provider receipts.
Resolve language and surface first. Lead with the useful result; avoid repeated summaries.
For Persian generated prose begin with Persian script, not an English ID or number.
Never expose raw tool/source handles or move BiDi controls into machine IDs, URLs or code.

## Progressive rendering contract
Before drafting an ordinary answer read detailed sections 4 and 5 for the applicable
surface. Before a governed project final response read sections 4, 11 and 12 and run
the relevant deterministic validators. Load artifact/media controls only for produced
artifacts, dispatch controls only for cross-surface work, and backlog-coverage controls
only when claiming complete registration. Full build-time rules are not ordinary context.

## Current Persian table invariant
Chat: the visible row-reference header is the exact Persian label defined in section
4.0.1; serialize it FIRST in Markdown source and right-align every column. Codex: use
the separate LAST-column serializer. Never apply a universal row-last rule to Chat.
The old renderer probe/registry is advisory, not authority to override these rules.
Keep one semantic NUM# column, sequential row values, appropriate RTL labels and
presentation-only isolation. Use `scripts/validate_table_conformance.py` on final text.
Do not claim pixel geometry verified on a host that was not visually inspected.

## Governed project final response
Use directional titles and adjacent sequentially numbered table blocks, a detailed
G16 control table, the four-row project summary and one absolute-terminal clickable
Handoff alias. `scripts/project_response_grammar.py` owns deterministic grammar.
The Handoff shows exactly its verified ID, S and M and a verified canonical URL.
A material success needs a current-turn S receipt plus its causally bound M receipt.
Progress commentary is exempt from final table grammar. Higher-priority host/system
output requirements always take precedence over local formatting or delivery rules.

## Truth and exit
Keep source inspection, locally executed tests, modeled behavior, independent review,
remote publication and native runtime installation distinct. A reused historical PASS
is not new acceptance. Validate artifact-delivery records with true booleans, exact
remote references and current applicable G1/G18 V2 bindings. No local fixture grants
production permission. Repair formatting defects at most three times, then report
remaining limits honestly rather than fabricate terminal success.


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

Privacy responsibility: Separate coverage from clearance; never claim unknown settings/caches/copies are clean.

## Private installation and user-specific parameterization — SkillForge 3.0.4
The distributable contains no owner-specific service IDs, credential values, site/folder URLs, tenant IDs, or private evidence. Use `config/setup-service-catalog.json` and `setup/CHATGPT_FIRST_RUN.md` for the setup plan. Resolve configuration through a user-authorized private external profile, pinned by exact SHA-256; validate current connector identity/permissions/readback for every real action. Missing bindings must produce a read-only/configuration-needed result, never invented values or silent mutation. G20 is a separate setup-runtime candidate; this is not a claim of automatic ChatGPT plugin execution. Public feedback remains OFF until a particular sanitized payload and destination receive explicit owner permission.
Relevant optional service families: `LOCAL_ONLY`.
