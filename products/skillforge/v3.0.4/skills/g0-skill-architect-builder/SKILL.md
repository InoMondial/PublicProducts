---
name: g0-skill-architect-builder
description: Root SkillForge governance Builder for creating, upgrading, migrating,
  splitting, merging and standardizing managed Skills/artifacts. Qualify first, resolve
  truthful framework membership, mandatory backlog topology, Build-Time/Runtime applicability
  and minimum runtime profiles, verify propagation, and validate with available evidence
  and publish under the owner-authorized release policy.
metadata:
  stable_id: O6-SKL-003
  visible_id: G0
  display_name: G0-Skill Architect / Builder
  version: 3.8.6
  domain: governance
  complexity_profile: FULL
  functional_role: META
  lifecycle: production
  strictness: S4
  governance_owner: INOMondial Inc.
  builder_framework_ref: INC_SKILLFORGE
  framework_id: INC_SKILLFORGE
  framework_name: SkillForge
  framework_membership: MEMBER
  framework_registry_ref: INC_SKILL_NAMESPACE_REGISTRY
  framework_membership_contract_ref: INC_SKILL_FRAMEWORK_MEMBERSHIP_V1
  source_of_truth_ref: INC_MASTER_BIBLE
  standards_registry_ref: INC_STANDARDS_REGISTRY
  namespace_registry_ref: INC_SKILL_NAMESPACE_REGISTRY
  runtime_reference_registry_ref: INC_RUNTIME_REFERENCE_REGISTRY
  unified_backlog_ref: INC_SKILLFORGE_UNIFIED_BACKLOG
  unified_backlog_contract_ref: INC_SKILLFORGE_UNIFIED_BACKLOG_CONTRACT_V2
  governed_skill_backlog_contract_ref: INC_GOVERNED_SKILL_BACKLOG_CONTRACT_V1
  universal_table_contract_ref: INC_UNIVERSAL_TABLE_REFERENCEABILITY_V1
  logging_target_ref: INC_LOG_STORE
  resource_policy_ref: INC_RESOURCE_POLICY_PROFILE
  dpga_contract_ref: INC_DPGA_ASSURANCE_RECORD_V1
  propagation_matrix_ref: INC_CROSS_CUTTING_GOVERNANCE_PROPAGATION_MATRIX_V1
  runtime_profile_contract_ref: INC_GOVERNANCE_RUNTIME_PROFILE_V1
  runtime_version_attestation_contract_ref: INC_SKILLFORGE_RUNTIME_VERSION_ATTESTATION_V1
  validator_handoff_ref: INC_VALIDATOR_HANDOFF_V1
  critical_control_contract_ref: INC_CRITICAL_CONTROL_ASSURANCE_V1
  global_assurance_contract_ref: INC_CRITICAL_CONTROL_ASSURANCE_V2
  global_assurance_skill_ref: G3
  data_governor_candidate_ref: G17-SKL-002
  data_governor_storage_placement_ref: INC_G17_STORAGE_PLACEMENT_V1
  data_governor_cross_skill_integration_ref: INC_G17_CROSS_SKILL_INTEGRATION_V1
  master_roadmap_gate_ref: INC_SKILLFORGE_MASTER_ROADMAP_GATE_V1
  plugin_packaging_current_stable_ref: G17-SKL-001
  plugin_packaging_visible_ref: G19
  data_governor_visible_ref: G17
  coordination_governor_visible_ref: G16
  human_output_governor_visible_ref: G18
  g18_project_response_grammar_ref: INC_G18_GOVERNED_PROJECT_RESPONSE_GRAMMAR_V1
  exhaustive_pairwise_gate_ref: INC_SKILLFORGE_EXHAUSTIVE_PAIRWISE_GATE_V1
  skillforge_feedback_intake_ref: INC_SKILLFORGE_FEEDBACK_INTAKE_V1
  owner_backlog_coverage_ref: INC_OWNER_CONVERSATION_BACKLOG_COVERAGE_V1
  carry_forward_manifest_ref: INC_SKILLFORGE_CARRY_FORWARD_MANIFEST_V1
  skill_setup_contract_ref: INC_SKILL_SETUP_CONTRACT_V1
  structural_validation_contract_ref: INC_SKILL_SOURCE_PACKAGE_STRUCTURAL_VALIDATION_V1
  github_usage_boundary_contract_ref: INC_GITHUB_USAGE_BOUNDARY_V1
---

## Current release policy (PRIOR_RELEASE)
For release/build/promotion decisions, use `INC_AUTONOMOUS_RELEASE_ACCEPTANCE_V1`
at `references/autonomous-release-policy-v1.md`. Available local/API/plugin/simulation tests are required;
unavailable third-party/runner/user/native-host assurance is optional and nonblocking.
This supersedes conflicting release-only clauses below or in detailed references.
Security, authorization, integrity and truthful runtime evidence remain mandatory.


# g0-skill-architect-builder - compact activity router

## Authority and evidence boundary
This entrypoint remains the sole activation authority. Read only the sections required
for the present operation in `references/detailed-governance.md`; that file preserves
the full normative contract, not a second executable Skill. Resolve every relative
path inside it from this Skill directory, not the references directory. System and
host instructions take precedence. Do not treat repository source, local fixtures,
profile configuration or historical PASS labels as authenticated live evidence.
A fresh review by the same executor is not independent G12/G13 certification.
Do not widen scope, create services, change credentials or invent telemetry.

## Activation and workflow
Use for qualified Skill creation/change/release and framework backlog maintenance;
not for every ordinary Skill invocation. Prefer REUSE, ADAPT, COMPOSE, then NEW.
Resolve stable identity, Registry membership and exactly one backlog owner. Keep
builder provenance separate from MEMBER/CANDIDATE_MEMBER/EXTERNAL membership.
Classify Build-Time and Runtime separately, compile the minimum applicable profile,
and map owner requirements to implementation plus evidence before a completeness claim.

## Load by activity
For builds and modifications, read detailed sections 2, 3 and 4 and the relevant
contracts before editing. For releases, also read scope, carry-forward, compatibility
and publication sections; freeze an exact artifact and do not reuse stale certificates.
Private V3 opt-in uses impact-scoped checks, not an unconditional runner or 342-pair redo.
`run_runner_independent_ci.py` checks bound evidence consistency; it does not execute
tests or authenticate the evidence provider. Its private profile requires explicit
source/artifact-bound regression and impact files. Never pass UNBUILT as a digest.
For backlog work, use the canonical backlog plus owner-coverage gate; preserve history,
dedupe records and never mark an unimplemented obligation implemented.
For data architecture invoke G17 only when relevant. For packaging resolve G19 as a
build-time dependency; G19/G20 are not bundled runtime members of this artifact.

## Non-negotiable exit controls
Security/approval, actual persistence, immutable package identity and exact remote
readback remain required when applicable. A simulation waiver is scope-bound and
cannot authorize live secrets or become production certification. G0 cannot approve
its own production changes. No missing mandatory evidence becomes PASS.
Use G16 for actual cross-surface execution, G18 for human rendering, G11/G17 for
applicable trace/persistence, and G14/G1 for package/publication. Avoid recursive
loading of every governance Skill for ordinary runtime work.


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

Privacy responsibility: Own explicit publicization plan and deny-by-default export selection.

## Private installation and user-specific parameterization — SkillForge 3.0.4
The distributable contains no owner-specific service IDs, credential values, site/folder URLs, tenant IDs, or private evidence. Use `config/setup-service-catalog.json` and `setup/CHATGPT_FIRST_RUN.md` for the setup plan. Resolve configuration through a user-authorized private external profile, pinned by exact SHA-256; validate current connector identity/permissions/readback for every real action. Missing bindings must produce a read-only/configuration-needed result, never invented values or silent mutation. G20 is a separate setup-runtime candidate; this is not a claim of automatic ChatGPT plugin execution. Public feedback remains OFF until a particular sanitized payload and destination receive explicit owner permission.
Relevant optional service families: `GITHUB_PRIVATE`, `LOGGING`, `BACKUP`.
