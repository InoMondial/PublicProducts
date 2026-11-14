---
name: g7-skill-structure-metadata-standardizer
description: SkillForge canonical Skill structure and metadata governance, including
  framework membership, backlog topology, table referenceability, remote artifact
  delivery applicability, Build-Time/Runtime applicability and compiled resource metadata.
metadata:
  stable_id: O6-SKL-007
  visible_id: G7
  display_name: G7-Skill Structure & Metadata Standardizer
  version: 3.5.2
  domain: governance
  functional_role: NORMAL
  lifecycle: production
  strictness: S3
  builder_framework_ref: INC_SKILLFORGE
  framework_id: INC_SKILLFORGE
  framework_name: SkillForge
  framework_membership: MEMBER
  framework_registry_ref: INC_SKILL_NAMESPACE_REGISTRY
  framework_membership_contract_ref: INC_SKILL_FRAMEWORK_MEMBERSHIP_V1
  governed_backlog_contract_ref: INC_GOVERNED_SKILL_BACKLOG_CONTRACT_V1
  universal_table_contract_ref: INC_UNIVERSAL_TABLE_REFERENCEABILITY_V1
  remote_artifact_delivery_contract_ref: INC_REMOTE_ARTIFACT_DELIVERY_V2
  source_reference_registry_ref: INC_SOURCE_REFERENCE_REGISTRY
  next_version_backlog_ref: INC_SKILLFORGE_UNIFIED_BACKLOG
  backlog_topology: CENTRAL_FRAMEWORK_BACKLOG
  backlog_owner_ref: G0
  global_assurance_contract_ref: INC_CRITICAL_CONTROL_ASSURANCE_V2
  global_assurance_skill_ref: G3
  skill_setup_contract_ref: INC_SKILL_SETUP_CONTRACT_V1
  structural_validation_contract_ref: INC_SKILL_SOURCE_PACKAGE_STRUCTURAL_VALIDATION_V1
---

## Current release policy (PRIOR_RELEASE)
For release/build/promotion decisions, use `INC_AUTONOMOUS_RELEASE_ACCEPTANCE_V1`
at `../g0-skill-architect-builder/references/autonomous-release-policy-v1.md`. Available local/API/plugin/simulation tests are required;
unavailable third-party/runner/user/native-host assurance is optional and nonblocking.
This supersedes conflicting release-only clauses below or in detailed references.
Security, authorization, integrity and truthful runtime evidence remain mandatory.

# G7-Skill Structure & Metadata Standardizer v3.5.2 - Released
## Purpose
Define the minimum complete machine-readable structure for managed Skills while keeping builder provenance, actual framework membership, backlog topology, output/referenceability rules and artifact-egress applicability explicit without duplicating full governance policies in every package.

G7 is a Registry-backed SkillForge Governance Skill. A Skill built by SkillForge is not automatically a SkillForge member.

## Required base metadata
Every governed Skill records stable identity, visible ID, display name, version, lifecycle, functional role, complexity, governance owner, Build-Time applicability/resource plan, Runtime applicability/condition, conditional modules, resource/dependency references, escalation triggers and applicable DPGA/critical-control refs.

For Skills built or materially upgraded by SkillForge, resolve:
```yaml
builder_framework_ref: INC_SKILLFORGE
framework_membership: MEMBER | CANDIDATE_MEMBER | EXTERNAL
framework_registry_ref: INC_SKILL_NAMESPACE_REGISTRY
backlog_topology: CENTRAL_FRAMEWORK_BACKLOG | STANDALONE_SKILL_BACKLOG
next_version_backlog_ref: <stable backlog id>
backlog_owner_ref: <root/gate or standalone Skill>
backlog_contract_ref: INC_GOVERNED_SKILL_BACKLOG_CONTRACT_V1
```
When membership is MEMBER/CANDIDATE_MEMBER, also record framework ID/name.

## Framework membership
Use `INC_SKILL_FRAMEWORK_MEMBERSHIP_V1`.
- Membership resolves from Registry/metadata, never name, path, G-like label or builder provenance.
- Active governance assignments resolve SkillForge MEMBER.
- Historical pre-migration G16 candidate state does not override the current Registry; resolve the current canonical membership by stable ID.
- project/external Skills remain EXTERNAL relative to SkillForge unless separately registered.

## Mandatory backlog topology and learning
Use `INC_GOVERNED_SKILL_BACKLOG_CONTRACT_V1`.
- framework/collection with root gate -> one `CENTRAL_FRAMEWORK_BACKLOG`;
- standalone Skill -> one `STANDALONE_SKILL_BACKLOG`;
- unresolved ownership -> release blocked;
- intake origin is `USER_DIRECT | SYSTEM_DISCOVERED`;
- system discovery records evidence/context and never self-modifies Production;
- minimum record types: `INCIDENT | PROBLEM | CHANGE_REQUEST | IMPROVEMENT`;
- release scope freeze requires owner review in a `NUM#`-first priority/date/type/origin table.

## Universal table referenceability
Use `INC_UNIVERSAL_TABLE_REFERENCEABILITY_V1`.
Every applicable human-readable generated table has one semantic row-reference key `NUM#`; visible localization and source-column order are delegated to the current G18 surface serializer. It is presentation/reference numbering, not persistent business identity. Fixed machine/protocol schemas may explicitly exclude the presentation field, but human-readable views remain numbered where feasible.

## GitHub capability metadata boundary
Contract: `INC_GITHUB_USAGE_BOUNDARY_V1`.

Every Skill built or materially upgraded by SkillForge records a compact GitHub capability profile. Default is `SOURCE_COORDINATION_ONLY`; repository presence alone never creates a Runtime dependency.

Minimum semantics:
- `github_profile: SOURCE_COORDINATION_ONLY | OPTIONAL_AUTOMATION_ADAPTER | REQUIRED_EXPLICIT`;
- source/version/commit/branch/PR/provenance may be Build-Time or reference metadata;
- Runtime connector applicability defaults to `REFERENCE_ONLY | N/A`;
- Actions, Runner, required status checks, GitHub Release/Asset, GitHub Secrets/Environments and public-repository publication default to `N/A`;
- any non-default GitHub capability records activation reason, scope, tests and failure-isolation behavior.

Child Skills carry the stable contract reference and minimum profile, not a copied full GitHub policy body.

## Remote artifact delivery applicability
Use `INC_REMOTE_ARTIFACT_DELIVERY_V2` when the Skill can generate a file/document/artifact for a user or project.

Compile only a stable ref plus local applicability fields, for example:
```yaml
artifact_egress:
  applicable: true
  contract_ref: INC_REMOTE_ARTIFACT_DELIVERY_V2
  physical_router_ref: G1
  final_delivery: VERIFIED_REMOTE_LINK
  windows_or_local_authority: PROHIBITED
  temporary_remote_required: true
```

G7 does not choose physical GitHub/SharePoint destinations. G1 owns routing. A child Skill must not treat Windows/local/sandbox paths or inline Chat content as final file-delivery authority.


## Public Skill package and setup contract
Contract: `INC_SKILL_SETUP_CONTRACT_V1` → `references/skill-setup-contract-v1.yaml`.

A public/configurable Skill is expressed as Core, Contracts, Setup Contract/Schema, Recommended Defaults, applicable Adapters and Documentation. Public Core contains logical configuration/resource keys, never customer-specific physical values.

Every configurable parameter uses a stable semantic `setup_parameter_id`; `NUM#` remains presentation-only. Required metadata includes schema version, value type, scope, owner Skill, consumers, requirement state/condition, validation, sensitivity, auth mode, capability, recommended provider/default, alternatives, documentation refs, migration behavior and compatibility. Aggregation of the same setup ID is allowed only when declarations normalize compatibly; incompatible declarations fail `SETUP_PARAMETER_CONFLICT`.

Recommended defaults may preserve generic provider choices and generic destination folder/file names proven by INOMondial, but physical INOMondial paths, URLs, IDs, tenant/account values and secrets are prohibited. Actual installation values belong only to Installation Profile, Resource Map or Connection Registry. Setup-schema compatibility is versioned; incompatible changes route to G6 and G20 migration logic.

## Source/package structural validation
Contract: `INC_SKILL_SOURCE_PACKAGE_STRUCTURAL_VALIDATION_V1` → `references/structural-validation-contract-v1.yaml`.

Before candidate freeze, validate raw bytes as strict UTF-8 and parse every applicable YAML, JSON, TOML, manifest and Markdown frontmatter with its target parser. Literal escaped-newline corruption in structural YAML/frontmatter, duplicate critical keys, malformed syntax, schema mismatch or truncated release-control files are blocking.

After packaging and clean materialization, parse again and compare normalized canonical/package semantics. Exact evidence binds paths and source/package digests. A structural failure blocks installable-ready, freeze, G12-ready and release states. G12/G13 consume the exact validation evidence; they do not accept a warning-only downgrade.

## Source/reference metadata
When a Skill depends on freshness-sensitive or normative sources, carry stable refs to `INC_SOURCE_REFERENCE_REGISTRY` rather than copied source bodies. G10 owns source authority/freshness; G7 only declares the reference.

## Structure
`SKILL.md` is authoritative human/runtime policy; `GOVERNANCE.yaml` carries compiled metadata. Include manifests/notices/references/tests only when justified. Runtime/install packages contain only necessary files; full evidence/history stays externally referenced.

## Integration
G0 compiles applicability; G2 visible naming; G4 profile; G6 lifecycle; G1 physical artifact routing; G9 resources; G10 stable source/dependency refs; G12 structure/cross-cutting tests; G13 independent evaluation; G14 packaging.

## Gates
`DPGA_COMPLETE | GOVERNANCE_PROPAGATION_COMPLETE | STRUCTURE_METADATA_VALID | FRAMEWORK_MEMBERSHIP_VALID | BACKLOG_TOPOLOGY_RESOLVED | TABLE_REFERENCEABILITY_COMPILED | ARTIFACT_EGRESS_PROFILE_COMPILED_WHEN_APPLICABLE | SKILL_SETUP_CONTRACT_VALID_WHEN_CONFIGURABLE | SOURCE_PACKAGE_STRUCTURAL_VALIDATION_PASS`.

## Failure states
`STRUCTURE_METADATA_INVALID | FRAMEWORK_MEMBERSHIP_UNRESOLVED | FRAMEWORK_MEMBERSHIP_MISLABEL | BACKLOG_OWNER_UNRESOLVED | BACKLOG_REFERENCE_MISSING | TABLE_REFERENCEABILITY_MISSING | ARTIFACT_EGRESS_PROFILE_MISSING | LOCAL_ARTIFACT_DELIVERY_AUTHORITY_FORBIDDEN | SETUP_PARAMETER_CONFLICT | CUSTOMER_PHYSICAL_VALUE_IN_PUBLIC_CORE | STRUCTURAL_PARSE_FAILED | STRUCTURAL_ENCODING_INVALID | STRUCTURAL_SEMANTIC_PARITY_FAILED | SUCCESS_VERIFIED`.

## Critical controls
- `G7-CC-01` stable identity/version/lifecycle/role/complexity/owner metadata present.
- `G7-CC-02` Build-Time/Runtime applicability and resource/dependency refs explicit.
- `G7-CC-03` package contains only justified files.
- `G7-CC-04` critical-control contract/exit gate exposed.
- `G7-CC-05` builder provenance and framework membership independently resolved.
- `G7-CC-06` exactly one backlog topology/owner resolved before release.
- `G7-CC-07` applicable tabular outputs compile `INC_UNIVERSAL_TABLE_REFERENCEABILITY_V1`.
- `G7-CC-08` artifact-producing Skills compile `INC_REMOTE_ARTIFACT_DELIVERY_V2` with G1 physical routing and verified-link completion; no local/Windows artifact authority.
- `G7-CC-09` configurable Skills expose all external parameters through `INC_SKILL_SETUP_CONTRACT_V1`, use stable semantic setup IDs, reject incompatible duplicate declarations and keep actual customer physical values outside public Core.
- `G7-CC-10` strict raw-byte/parser validation and canonical/materialized-package semantic parity pass before freeze/G12/release; invalid UTF-8, malformed metadata or literal structural escape corruption fails closed.

Mandatory FAIL blocks success. Runtime exit gate: `CRITICAL_CONTROLS_VERIFIED`; Build-Time gate: `CRITICAL_CONTROLS_COMPILED`.

## Universal G3 Assurance Metadata
Every governed Skill exposes `INC_CRITICAL_CONTROL_ASSURANCE_V2` / G3 inheritance. Provider policies remain stable refs/JIT rather than copied wholesale.

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

Privacy responsibility: Separate unresolved public schemas from resolved private installation profiles.

## Private installation and user-specific parameterization — SkillForge 3.0.4
The distributable contains no owner-specific service IDs, credential values, site/folder URLs, tenant IDs, or private evidence. Use `config/setup-service-catalog.json` and `setup/CHATGPT_FIRST_RUN.md` for the setup plan. Resolve configuration through a user-authorized private external profile, pinned by exact SHA-256; validate current connector identity/permissions/readback for every real action. Missing bindings must produce a read-only/configuration-needed result, never invented values or silent mutation. G20 is a separate setup-runtime candidate; this is not a claim of automatic ChatGPT plugin execution. Public feedback remains OFF until a particular sanitized payload and destination receive explicit owner permission.
Relevant optional service families: `GITHUB_PRIVATE`.
