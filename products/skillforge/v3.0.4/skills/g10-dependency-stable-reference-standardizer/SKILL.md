---
name: g10-dependency-stable-reference-standardizer
description: SkillForge dependency, source-registry and stable-reference governance
  for managed artifacts, separating Build-Time, Runtime, reference-only and evidence-only
  edges.
metadata:
  stable_id: O6-SKL-010
  visible_id: G10
  display_name: G10-Dependency & Stable Reference Standardizer
  version: 3.3.2
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
  source_reference_registry_ref: INC_SOURCE_REFERENCE_REGISTRY
  source_reference_registry_contract_ref: INC_SOURCE_REFERENCE_REGISTRY_V1
---

## Current release policy (PRIOR_RELEASE)
For release/build/promotion decisions, use `INC_AUTONOMOUS_RELEASE_ACCEPTANCE_V1`
at `../g0-skill-architect-builder/references/autonomous-release-policy-v1.md`. Available local/API/plugin/simulation tests are required;
unavailable third-party/runner/user/native-host assurance is optional and nonblocking.
This supersedes conflicting release-only clauses below or in detailed references.
Security, authorization, integrity and truthful runtime evidence remain mandatory.

# G10-Dependency & Stable Reference Standardizer v3.3.2 - Released
## Purpose
Represent dependencies and sources as stable, minimal and truthful references while preventing recursive Governance loading, stale source authority, fragile path/version coupling and provisional-source promotion without exact evidence.

## Dependency model
Classify dependency importance as `CORE | CONDITIONAL | CRITICAL_BRANCH` and edge type as `BUILD_TIME | RUNTIME | REFERENCE_ONLY | EVIDENCE_ONLY | REGISTRY`. Stable IDs/registry refs are preferred over copied policy bodies or transient URLs.

Build-Time proves required dependency availability, compatibility and cycle safety. Runtime loads only dependencies needed for the current activity. Conditional edges are JIT. Reference/evidence edges do not become runtime loads merely because they exist.

Runtime dependency graph must remain acyclic. Missing critical dependency, cycle or ambiguous stable reference blocks success.

## Source/reference registry
Use `INC_SOURCE_REFERENCE_REGISTRY` under `INC_SOURCE_REFERENCE_REGISTRY_V1`.

Each governed source records, as applicable, stable source ID, type, authority class, location, version/date, last verification time, freshness policy, owner, applicable Skills, content identity and status.

Authority classes: `NORMATIVE | INFORMATIVE | EVIDENCE_ONLY | PROVISIONAL`.
Status includes `ACTIVE | STALE | SUPERSEDED | BLOCKED_SOURCE_REQUIRED | HISTORICAL`.

Rules:
- a URL alone is not proof of unchanged content;
- current official guidance is revalidated when freshness matters;
- exact external Change Request bytes are required before a provisional summary becomes normative implementation input;
- historical/superseded sources remain auditable but cannot override active Registry/contract truth;
- the full source registry is not loaded by every runtime;
- G10 is registry writer authority under G0-governed change; consumers do not mutate source truth opportunistically.

## GitHub reference classification
Apply `INC_GITHUB_USAGE_BOUNDARY_V1`. Prefer repository identity, canonical path, commit/tree SHA and artifact digest for durable source/provenance references. Workflow run IDs, job IDs, runner IDs and Actions artifacts are `EVIDENCE_ONLY` unless an explicitly activated GitHub automation capability requires them. Source hosted on GitHub does not create a Runtime dependency edge to GitHub or Actions.

## Stable artifact links
For governed generated artifacts, stable references must point to the canonical GitHub/SharePoint object selected by G1. A local path, Windows location, sandbox path or unverified upload response is not a stable artifact reference. `INC_REMOTE_ARTIFACT_DELIVERY_V2` governs artifact delivery; G10 only standardizes the reference identity/freshness layer.

## Integration
G0 compiles the graph; G1 owns remote artifact routing/delivery; G7 declares dependency/source refs; G9 limits JIT loading; G12 tests critical branches/freshness; G13 penalizes stale/unnecessary coupling. G10 does not take over G1 physical routing or G6 version lifecycle.

## Gates
`DPGA_COMPLETE`, `GOVERNANCE_PROPAGATION_COMPLETE`, `DEPENDENCY_GRAPH_VALID`, `SOURCE_REFERENCE_AUTHORITY_RESOLVED`.

## Failure states
`DEPENDENCY_CYCLE | CRITICAL_DEPENDENCY_MISSING | STABLE_REFERENCE_AMBIGUOUS | SOURCE_STALE | SOURCE_AUTHORITY_CONFLICT | EXACT_SOURCE_REQUIRED | LOCAL_PATH_NOT_STABLE_REFERENCE | SUCCESS_VERIFIED`.

## Critical controls
- `G10-CC-01` — dependencies use stable references and explicit edge types.
- `G10-CC-02` — runtime dependency graph is acyclic and no full Governance stack is recursively loaded.
- `G10-CC-03` — conditional dependencies load only when needed.
- `G10-CC-04` — missing/ambiguous critical dependency blocks rather than silently bypassing.
- `G10-CC-05` — source authority/freshness is explicit; provisional/missing exact external source cannot silently become normative.
- `G10-CC-06` — generated artifact references are canonical remote refs, never local/Windows/sandbox paths presented as stable delivery authority.

Mandatory FAIL blocks `SUCCESS_VERIFIED`.
Runtime exit gate: `CRITICAL_CONTROLS_VERIFIED`. Build-Time compilation gate: `CRITICAL_CONTROLS_COMPILED`.

## Mandatory G16 cross-surface generation gate
Contract: `INC_G16_CROSS_SURFACE_EXECUTION_DELIVERY_V1`.

When this Skill generates a prompt, instruction, work order, Handoff, report, command file, execution artifact, or operational file intended for another Chat/Work/Codex/agent surface, it MUST resolve/apply latest G16 before generation. No G16 => `BLOCKED_G16_NOT_APPLIED`.

Administrative/infrastructure execution MUST follow: PowerShell -> official API -> official CLI -> structured browser/connected tool -> visual UI. On Windows Codex with verified direct terminal capability, PowerShell 7 is the mandatory first candidate. Lower-priority fallback requires an approved reason code.

Generated cross-surface artifacts MUST be persisted to governed GitHub/SharePoint under G1/G17 placement, verified by remote read-back, and transferred only by verified remote link or stable reference. Direct local/sandbox file delivery, direct cross-surface attachment, or inline full-file delivery as a substitute for governed publication is prohibited. Secrets/MFA/credentials never enter prompts, Handoffs, logs, or generated handoff artifacts.


## Logical resource configuration
Contract: `INC_LOGICAL_RESOURCE_CONFIGURATION_V1` in `references/logical-resource-configuration-contract-v1.yaml`.

Consumer Skills use stable logical references such as `artifact.primary`, `handoff.active`, `logs.durable`, `database.primary` and `backlog.target`. Every logical resource declares a resource type, capability contract and scope before provider binding. Provider URLs, account IDs and physical paths remain in the Installation Profile/provider adapter rather than consumer source.

Folder templates are valid only for hierarchical document resources. Database, API, queue, log, identity and secret-reference bindings use type-appropriate provider bindings. Resolving a target never grants permission: the active provider credential/capability must independently authorize a write. Required unresolved resources, capability mismatches, ambiguous scope or provider-ID leakage fail closed.

A provider switch that preserves business meaning changes only the compatible adapter/Installation Profile binding; the stable logical reference remains unchanged. Existing verified INOMondial mappings are migrated rather than re-asked when their authority is already proven.


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

Privacy responsibility: Check references and parameter dependencies without embedding live private targets.

## Private installation and user-specific parameterization — SkillForge 3.0.4
The distributable contains no owner-specific service IDs, credential values, site/folder URLs, tenant IDs, or private evidence. Use `config/setup-service-catalog.json` and `setup/CHATGPT_FIRST_RUN.md` for the setup plan. Resolve configuration through a user-authorized private external profile, pinned by exact SHA-256; validate current connector identity/permissions/readback for every real action. Missing bindings must produce a read-only/configuration-needed result, never invented values or silent mutation. G20 is a separate setup-runtime candidate; this is not a claim of automatic ChatGPT plugin execution. Public feedback remains OFF until a particular sanitized payload and destination receive explicit owner permission.
Relevant optional service families: `GITHUB_PRIVATE`.
