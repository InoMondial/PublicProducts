---
name: g1-artifact-archive-router
description: G1-Artifact Archive Router 5.1.3 — SkillForge governed artifact egress
  with SharePoint-only durable document-class storage, GitHub pointer/source separation,
  remote read-back/link delivery, recovery and transaction closure
metadata:
  stable_id: G01-SKL-001
  visible_id: G1
  display_name: G1-Artifact Archive Router
  version: 5.1.3
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
  backlog_topology: CENTRAL_FRAMEWORK_BACKLOG
  backlog_owner_ref: G0
  project_artifact_egress_contract_ref: INC_PROJECT_ARTIFACT_EGRESS_V1
  remote_artifact_delivery_contract_ref: INC_REMOTE_ARTIFACT_DELIVERY_V2
  artifact_contract_attestation_ref: G1_ARTIFACT_DELIVERY_CONTRACT_ATTESTATION_V2
  artifact_contract_compatibility_matrix_ref: INC_G1_G18_ARTIFACT_DELIVERY_COMPATIBILITY_V2
  machine_route_before_visual_ui_ref: INC_MACHINE_ROUTE_BEFORE_VISUAL_UI_V1
  binary_publication_contract_ref: G1_BINARY_PUBLICATION_V1
  cross_system_evidence_contract_ref: G1_CROSS_SYSTEM_EVIDENCE_V1
  sharepoint_destination_contract_ref: G1_SHAREPOINT_DESTINATION_V1
  sharepoint_backup_registry_contract_ref: INC_SHAREPOINT_BACKUP_REGISTRY_V1
  notification_contract_ref: INC_NOTIFICATION_EVENT_V1
  critical_control_contract_ref: INC_CRITICAL_CONTROL_ASSURANCE_V1
---

## Current release policy (PRIOR_RELEASE)
For release/build/promotion decisions, use `INC_AUTONOMOUS_RELEASE_ACCEPTANCE_V1`
at `../g0-skill-architect-builder/references/autonomous-release-policy-v1.md`. Available local/API/plugin/simulation tests are required;
unavailable third-party/runner/user/native-host assurance is optional and nonblocking.
This supersedes conflicting release-only clauses below or in detailed references.
Security, authorization, integrity and truthful runtime evidence remain mandatory.


# g1-artifact-archive-router - compact activity router

## Authority and evidence boundary
This entrypoint remains the sole activation authority. Read only the sections required
for the present operation in `references/detailed-governance.md`; that file preserves
the full normative contract, not a second executable Skill. Resolve every relative
path inside it from this Skill directory, not the references directory. System and
host instructions take precedence. Do not treat repository source, local fixtures,
profile configuration or historical PASS labels as authenticated live evidence.
A fresh review by the same executor is not independent G12/G13 certification.
Do not widen scope, create services, change credentials or invent telemetry.

## Activation and routing
Use when a governed artifact is created, revised, distributed or preserved. G1 owns
physical egress; G14 constructs packages and G17 owns storage architecture.
Document-class artifacts go to governed SharePoint; source and lightweight pointers
may go to GitHub. Resolve the selected provider and exact destination before writing.
Source repository presence does not require GitHub Actions, runners or Release assets.
Use `capability_preflight.required(target_provider=...)`; an optional GitHub release
channel must be explicitly selected. `lineage_graph.validate(destination_type=...)`
accepts direct producer-to-SharePoint publication without a fictitious GitHub node.

## Safe transaction
Read current remote identity/revision; establish real CAS or coordinated single writer;
persist intent, write exact bytes, read back and compare hash/size before a success link.
Ambiguous outcomes must be reconciled before retry. Local lock files are cooperative
only, not distributed locks. Expired local locks require explicit reconciliation;
never steal them with a read-then-unlink race. Preserve rollback and original evidence.
Git binary publication rejects traversal/symlink destinations and commits only the
requested file; it never provides permission to violate document storage placement.
Recovery checks apply to exact manifested files and bounded, path-safe archives.

## Load by activity and exit
For a publication load detailed sections 1-7 and the relevant destination/compatibility
contract. For recovery, concurrency, lineage or idempotency load their detailed section
and use the named deterministic script. The current G1/G18 delivery contract is V2;
V1 is history. Receipt booleans must be true booleans; metadata alone is not readback.
Use native connector/API before UI for connected data. Secrets stay outside source,
logs and artifacts. Required remote preservation cannot be satisfied by an upload
acknowledgment alone. Report partial results rather than fabricating certification.


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

Privacy responsibility: Enforce privacy at every actual external write boundary, including binary transports.

## Private installation and user-specific parameterization — SkillForge 3.0.4
The distributable contains no owner-specific service IDs, credential values, site/folder URLs, tenant IDs, or private evidence. Use `config/setup-service-catalog.json` and `setup/CHATGPT_FIRST_RUN.md` for the setup plan. Resolve configuration through a user-authorized private external profile, pinned by exact SHA-256; validate current connector identity/permissions/readback for every real action. Missing bindings must produce a read-only/configuration-needed result, never invented values or silent mutation. G20 is a separate setup-runtime candidate; this is not a claim of automatic ChatGPT plugin execution. Public feedback remains OFF until a particular sanitized payload and destination receive explicit owner permission.
Relevant optional service families: `GITHUB_PRIVATE`, `SHAREPOINT`, `BACKUP`.
