---
name: g6-versioning-lifecycle-standardizer
description: SkillForge SemVer, release-scope and lifecycle governance for managed
  artifacts, immutable accepted versions, compatibility, upgrade and rollback.
metadata:
  stable_id: O6-SKL-006
  visible_id: G6
  display_name: G6-Versioning & Lifecycle Standardizer
  version: 3.4.2
  domain: governance
  functional_role: NORMAL
  lifecycle: production
  strictness: S3
  builder_framework_ref: INC_SKILLFORGE
  framework_id: INC_SKILLFORGE
  framework_name: SkillForge
  framework_membership: MEMBER
  framework_registry_ref: INC_SKILL_NAMESPACE_REGISTRY
  next_version_backlog_ref: INC_SKILLFORGE_UNIFIED_BACKLOG
  release_scope_lifecycle_contract_ref: INC_RELEASE_SCOPE_LIFECYCLE_V1
  carry_forward_manifest_contract_ref: INC_SKILLFORGE_CARRY_FORWARD_MANIFEST_V1
---

## Current release policy (PRIOR_RELEASE)
For release/build/promotion decisions, use `INC_AUTONOMOUS_RELEASE_ACCEPTANCE_V1`
at `../g0-skill-architect-builder/references/autonomous-release-policy-v1.md`. Available local/API/plugin/simulation tests are required;
unavailable third-party/runner/user/native-host assurance is optional and nonblocking.
This supersedes conflicting release-only clauses below or in detailed references.
Security, authorization, integrity and truthful runtime evidence remain mandatory.

# G6-Versioning & Lifecycle Standardizer v3.4.2 - Released
## Purpose
Own semantic version impact, release-scope freeze, lifecycle transitions, compatibility, upgrade and rollback while preserving immutable evidence for every accepted version.

## Version-impact dimensions
Evaluate impact separately for:
- SkillForge framework release;
- individual Skill bytes/contracts;
- shared registry/schema/contract;
- documentation-only artifact;
- backlog-only mutable state;
- runtime/configuration state.

A backlog entry by itself does not bump a Skill. A changed shared contract consumed by a Skill may require a version change even if the Skill prose changes only slightly.

## SemVer
Use evidence-based SemVer:
- MAJOR — incompatible public/governance/runtime contract change requiring consumer migration;
- MINOR — backward-compatible capability or contract addition;
- PATCH — backward-compatible correction with no new capability contract.

Do not infer the framework's final SemVer from number of backlog items. Determine it only after the accepted release scope is frozen and compatibility is analyzed.

Accepted/published version bytes are immutable. Corrections always create a new version.

## Release-scope freeze
Use `INC_RELEASE_SCOPE_LIFECYCLE_V1`.

Before a target release is finalized:
1. backlog owner presents eligible items in the required numbered table;
2. owner selects target Change IDs;
3. selected IDs become the immutable release-scope snapshot;
4. any post-freeze addition/removal records an explicit scope change and re-runs SemVer/compatibility impact.

Unselected backlog items remain open/deferred.

## Lifecycle
Minimum lifecycle:
`DISCOVER -> QUALIFY -> SELECT -> BUILD -> VALIDATE -> INSTALL/DEPLOY -> SMOKE -> ACTIVATE -> OPERATE -> UPGRADE | ROLLBACK | DEPRECATE -> RETIRE/UNINSTALL`.

Lifecycle state is independent from SemVer.

## Provider-neutral release lifecycle
Apply `INC_GITHUB_USAGE_BOUNDARY_V1`. The lifecycle state `RELEASED` is not defined by existence of a GitHub Actions run, runner, tag or GitHub Release object. Release identity is the accepted immutable artifact/source identity plus required certification and governed publication/read-back. Provider-specific distribution objects are additional channel states and become blocking only when the selected distribution profile explicitly requires them.

## Upgrade compatibility
Before upgrade, record current/target version, changed contracts/schemas/registries, backward/forward compatibility, required migration, duplicate/coexistence risk, rollback target, rollback trigger and preservation/restore evidence.

Unsupported incompatible transitions block `UPGRADE_COMPATIBILITY_FAILED` rather than being forced through.

## Rollback
Material releases/upgrades identify a known-good rollback target unless technically impossible and explicitly approved. Failed smoke/activation/compatibility/data-integrity gates require rollback or a fail-closed blocked state. Never destroy the only known-good accepted artifact before replacement verification.

## Runtime
Normal Skill invocation never bumps versions or changes lifecycle. Mutation occurs only in an authorized version/lifecycle transaction.

## Previous-version carry-forward semantics — HARD GATE

Cross-cutting contract: `INC_SKILLFORGE_CARRY_FORWARD_MANIFEST_V1`.

A new SkillForge release is not a valid version transition merely because changed files pass. Before G12 entry, G0 must prove a deterministic previous-to-current carry-forward projection.

G6 semantics:
- unchanged items preserve stable identity and content digest;
- modified items require explicit revalidation scope and preserve lineage;
- retired items require owner-approved reason plus successor/historical reference;
- missing prior items without approved retirement are UNRESOLVED and block release;
- new items are explicit NEW rows;
- post-certification source change invalidates the carry-forward digest and reopens version validation.

G6 owns the version/lifecycle meaning of these dispositions. G0 owns snapshot generation, manifest validation and release orchestration. G12/G13 certify the same bound digests.

## Runtime installed-version attestation semantics

Cross-cutting contract: `INC_SKILLFORGE_RUNTIME_VERSION_ATTESTATION_V1`.

G6 owns comparison semantics, not runtime discovery. The runtime proof itself is produced by the active host/package surface and orchestrated by G0/G16.

Rules:
- compare normalized numeric SemVer core for required minimums; prerelease/candidate labels do not make a lower numeric core satisfy a higher minimum;
- release manifest/profile supplies required minimum SkillForge/G16/G18 versions and allowed package/component digests;
- an exact digest allow-list, when present, overrides version-only sufficiency;
- installed/runtime evidence and source/repository version are distinct facts;
- accepted release bytes remain immutable; a different digest under the same accepted version is a conflict;
- runtime mismatch blocks material work but may permit explicitly marked read-only audit under the attestation contract.

## Installation/configuration lifecycle — HARD GATE
Contract: `INC_G6_INSTALLATION_CONFIGURATION_LIFECYCLE_V1` in `references/installation-configuration-lifecycle-v1.yaml`.

Every installable SkillForge release resolves a compatibility tuple across `source_version`, `package_version`, `setup_schema_version`, `profile_schema_version` and `edition_id`. Each upgrade declares setup impact exactly as `NONE | MINIMAL | REQUIRED`; compatible no-op upgrades ask no repeated setup questions, additive changes ask only newly required values, and incompatible changes require guided migration plus a verified rollback target. Community-channel lag is a release-policy choice only and MUST NOT delay an approved critical security remediation or create an independently developed core.

## Integration
G0 owns qualification/release orchestration; G2 consumes version for names; G1 starts the governed archive/deploy transaction and preserves known-good artifacts; G7 carries version/lifecycle metadata; G10 maintains stable references without fragile over-pinning; G11 logs material version events; G12/G13 test/evaluate compatibility; G14 packages; G15 reports material releases/deprecations.

## Gates
`DPGA_COMPLETE`, `GOVERNANCE_PROPAGATION_COMPLETE`, `VERSION_LIFECYCLE_RESOLVED`, `PREVIOUS_VERSION_CARRY_FORWARD_COMPLETE`, `RUNTIME_VERSION_ATTESTATION_REQUIREMENTS_RESOLVED_WHEN_APPLICABLE`, `RELEASE_SCOPE_FROZEN_WHEN_REQUIRED`, `UPGRADE_COMPATIBILITY_RESOLVED`, `ROLLBACK_TARGET_RESOLVED_WHEN_REQUIRED`.

## Failure states
`VERSION_CONFLICT | IMMUTABLE_VERSION_VIOLATION | LIFECYCLE_TRANSITION_INVALID | REGISTRY_VERSION_MISMATCH | RELEASE_SCOPE_NOT_FROZEN | RELEASE_SCOPE_DRIFT | UPGRADE_COMPATIBILITY_FAILED | ROLLBACK_TARGET_UNRESOLVED | SUCCESS_VERIFIED`.

## Critical controls
- `G6-CC-01` — version bump type has evidence-based SemVer rationale.
- `G6-CC-02` — accepted bytes are immutable; correction uses new version.
- `G6-CC-03` — lifecycle state is explicit and distinct from version.
- `G6-CC-04` — runtime version/lifecycle mutation occurs only in authorized transaction.
- `G6-CC-05` — release scope is owner-selected/frozen before final version assembly; post-freeze drift is explicitly governed.
- `G6-CC-06` — material upgrade compatibility and rollback target are resolved before activation.
- `G6-CC-07` — every new SkillForge release has a complete previous-to-current carry-forward manifest with zero unresolved rows before certification.

Mandatory FAIL blocks `SUCCESS_VERIFIED`; evidence-required controls retain stable evidence refs.

Runtime exit gate: `CRITICAL_CONTROLS_VERIFIED`. Build-Time compilation gate: `CRITICAL_CONTROLS_COMPILED`.

## Mandatory G16 cross-surface generation gate
Contract: `INC_G16_CROSS_SURFACE_EXECUTION_DELIVERY_V1`.

When this Skill generates a prompt, instruction, work order, Handoff, report, command file, execution artifact, or operational file intended for another Chat/Work/Codex/agent surface, it MUST resolve/apply latest G16 before generation. No G16 => `BLOCKED_G16_NOT_APPLIED`.

Administrative/infrastructure execution MUST follow: PowerShell -> official API -> official CLI -> structured browser/connected tool -> visual UI. On Windows Codex with verified direct terminal capability, PowerShell 7 is the mandatory first candidate. Lower-priority fallback requires an approved reason code.

Generated cross-surface artifacts MUST be persisted to governed GitHub/SharePoint under G1/G17 placement, verified by remote read-back, and transferred only by verified remote link or stable reference. Direct local/sandbox file delivery, direct cross-surface attachment, or inline full-file delivery as a substitute for governed publication is prohibited. Secrets/MFA/credentials never enter prompts, Handoffs, logs, or generated handoff artifacts.

## Four-lane release lifecycle — HARD GATE
For governed platform/Skill releases, model Stable, Candidate, Next and Hotfix as distinct lifecycle lanes. Every selected backlog item has one target release. Candidate scope locks explicitly; ordinary late items route to Next. Hotfix is exceptional and must forward-merge after release. A live session remains pinned to its active certified release/digest until an explicit activation/migration event.


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

Privacy responsibility: Bind consent to exact version and bytes; invalidate stale grants on any change.

## Private installation and user-specific parameterization — SkillForge 3.0.4
The distributable contains no owner-specific service IDs, credential values, site/folder URLs, tenant IDs, or private evidence. Use `config/setup-service-catalog.json` and `setup/CHATGPT_FIRST_RUN.md` for the setup plan. Resolve configuration through a user-authorized private external profile, pinned by exact SHA-256; validate current connector identity/permissions/readback for every real action. Missing bindings must produce a read-only/configuration-needed result, never invented values or silent mutation. G20 is a separate setup-runtime candidate; this is not a claim of automatic ChatGPT plugin execution. Public feedback remains OFF until a particular sanitized payload and destination receive explicit owner permission.
Relevant optional service families: `GITHUB_PRIVATE`.
