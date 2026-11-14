---
name: g17-data-governor
description: Govern durable data architecture, storage placement, provider-neutral
  persistence, migration, rollback, integrity, and database operations for SkillForge
  projects.
display_name: G17-Data Governor
stable_id: G17-SKL-002
version: 0.2.2
lifecycle: production
framework_id: INC_SKILLFORGE
framework_membership: MEMBER
backlog_topology: CENTRAL_FRAMEWORK_BACKLOG
backlog_ref: INC_SKILLFORGE_UNIFIED_BACKLOG
complexity_profile: CRITICAL
functional_role: NORMAL
operating_modes:
- ECOSYSTEM_GOVERNED
- STANDALONE_SERVICE
metadata:
  version: 0.2.2
  lifecycle: production
---

## Current release policy (PRIOR_RELEASE)
For release/build/promotion decisions, use `INC_AUTONOMOUS_RELEASE_ACCEPTANCE_V1`
at `../g0-skill-architect-builder/references/autonomous-release-policy-v1.md`. Available local/API/plugin/simulation tests are required;
unavailable third-party/runner/user/native-host assurance is optional and nonblocking.
This supersedes conflicting release-only clauses below or in detailed references.
Security, authorization, integrity and truthful runtime evidence remain mandatory.


# G17-Data Governor v0.2.2 - Released
## Purpose
G17 is the SkillForge data-governance owner for information/data architecture, storage placement, relational database design, schema evolution, provider-neutral persistence contracts, provider adapters, integrity, query/index policy, encryption-at-rest application boundaries, backup/restore/DR requirements, migration/rollback and automated database-administration policy.

G17 is not a universal "put everything in the database" rule. It decides where information belongs and preserves the correct authority for files, GitHub, document providers, spreadsheets, connected external systems, ephemeral state and databases.

## Activation
Invoke G17 when a governed activity:
- designs or materially changes a Skill that stores, queries, updates, aggregates, migrates, backs up or restores durable data;
- introduces a new entity/table/field/relation/index/schema/provider or storage authority;
- uses a file/spreadsheet as a mutable structured system of record and needs qualification;
- needs ER/database design, normalization, provider selection, adapter design or migration;
- performs destructive data changes, bulk deletion, rekeying, restore or provider cutover;
- asks G17 directly to design/optimize/build a data architecture or database from files/raw data/problem statements.

Do not invoke full G17 runtime governance for a Skill with no persistence/data-architecture obligation. Record NOT_APPLICABLE_WITH_REASON instead.

## Operating modes
### ECOSYSTEM_GOVERNED
- BUILD: G17 participates during SkillForge design/build/change.
- RUNTIME: only the minimum applicable G17 contracts are propagated to the generated Skill.

### STANDALONE_SERVICE
G17 can directly analyze a user's data/file/problem, design the normalized model, select the appropriate storage placement, generate the provider-neutral contract and prepare provider adapters/migration artifacts.

## GitHub storage boundary
Apply `INC_GITHUB_USAGE_BOUNDARY_V1`. GitHub is appropriate for versioned code, schemas, policies, migrations, registries and normative machine-readable governance. It is not the default authority for mutable business/runtime state, high-volume operational event history or database semantics. Repository presence alone never changes the storage-placement decision.

## Mandatory design workflow
1. Resolve project context. Durable DB state MUST have project_ref. Small/temporary unnamed work may use PRJ_MISC with workload_ref or domain_ref.
2. Run Storage Placement Qualification before choosing DB.
3. Define authority: LOCAL_SYSTEM_OF_RECORD | REFERENCE | DERIVED | CACHE | SNAPSHOT | EXTERNAL_SYSTEM_OF_RECORD.
4. Classify entities/data, ownership, sensitivity, retention and lifecycle.
5. Design logical model: entities/tables, PK/FK, cardinality, constraints, nullability, defaults and canonical IDs.
6. Review normalization/denormalization, update/delete anomalies and redundancy.
7. Define query patterns, indexes, pagination, aggregation, transactions, concurrency and expected volume/growth.
8. Define security/project isolation, encryption/key requirements and least privilege.
9. Resolve provider-neutral Gateway contract before provider adapter details.
10. Resolve adapter capability/limits, backup/restore, monitoring and migration/rollback.
11. Self-test G17-owned design. G12 later performs independent black-box testing and G13 independently evaluates quality.
12. Persist accepted design/change metadata through the governed backlog/registry path.

## Storage-placement contract
Choose the minimum correct authority:
- DATABASE: normalized mutable structured data requiring query/integrity/transactions.
- GITHUB: versioned code, schema, policy, migrations, registries and normative machine-readable governance.
- GOVERNED_DOCUMENT_PROVIDER: DOCX/PDF/PPTX/report/evidence/human document artifacts; G1 owns physical routing.
- SPREADSHEET: human-editable/report/import/export artifact when spreadsheet semantics are still appropriate.
- EXTERNAL_SYSTEM_REFERENCE: bank/email/CRM/calendar/Trello/etc. remains authoritative externally unless an explicit snapshot/cache/derived contract is approved.
- EPHEMERAL: temporary non-authoritative processing state.

Never duplicate a connected external system's entire dataset merely because a connector exists.

For ambiguous or material placement decisions, present options and obtain owner approval before establishing a new durable authority.

## Database architecture rules
- One default shared database infrastructure for current REFERENCE_SCOPE/SkillForge unless the owner explicitly assigns a different database/provider to a project.
- Every DB object belongs to an explicit project context; PRJ_MISC is the bounded exception for small/temporary work.
- Machine identifiers, schema/table/field names and provider-control communication are English-only.
- Canonical machine timestamps are UTC.
- Naming/data_code follows INC_G17_DB_NAMING_V1 and INC_DB_DATA_CODE_REGISTRY.
- Ordinary consumer Skills cannot issue unrestricted generic SQL or embed provider IDs.
- Provider-specific code belongs behind adapters.
- Breaking schema changes use governed migrations and expand-migrate-contract where applicable.
- Applied migration files are immutable.

## Runtime semantic operations
Ordinary runtime:
DB_GET, DB_SEARCH, DB_CREATE, DB_UPDATE, DB_DELETE, DB_TRANSACTION, DB_AGGREGATE, DB_HEALTH.

Admin-only:
DB_SCHEMA_STATUS, DB_MIGRATE, DB_BACKUP, DB_RESTORE, DB_PROVIDER_STATUS, DB_QUOTA_STATUS.

Requests use INC_G17_DB_GATEWAY_V1 and must include request_id, operation, project_ref, actor_ref, purpose and classification.

## Query/resource rules
- Filter/sort/aggregate server-side when safe.
- No unbounded full-table fetch into model context.
- Ordinary page size defaults to 50; >200 requires an explicit elevated/export path.
- Prefer keyset/cursor pagination for growing datasets.
- N+1 query patterns are failures; batch/join instead.
- Keep transactions short. Network/LLM work inside an open DB transaction is forbidden.
- Cache is OFF by default and never becomes system of record.
- G9 owns global optimization and may recommend a higher-capability model if architectural reasoning is materially model-limited.

## Security and encryption
- Deny by default; least privilege.
- Secrets/passwords/tokens/cookies/MFA/private keys never enter chat, Handoff, GitHub, ordinary DB rows, Excel or G11.
- Protected S3/S4 fields are encrypted before provider storage using the approved G17 crypto boundary.
- V1 cryptography: AES-256-GCM + HKDF-SHA-256 scoped derived keys; ROOT_KEK remains external to the DB provider.
- LLM reasoning never performs encryption/decryption over key material.
- Decrypt only the minimum rows/fields needed.
- Public/admin backup endpoints are forbidden.

## Test-data lifecycle
Every DB test:
- has TEST_RUN_ID;
- uses PRJ_TEST_* project context and tst_* object prefix;
- uses synthetic data unless explicitly authorized;
- records intended TTL/cleanup;
- cleans up and performs read-back verification.
Unattended test assets default to maximum 24-hour TTL unless a governed test requires otherwise.

## Destructive change gate
Before deleting a project/table or >5 rows in one governed operation:
- create/verify a recoverable backup/snapshot of the affected scope;
- record actor/time/reason/scope/backup reference in G11;
- execute the bounded delete;
- verify result/read-back.
No backup => BACKUP_REQUIRED_BEFORE_DELETE.

## Provider outage behavior
Reads requiring fresh authority fail closed if the provider is unavailable.
When business continuity requires a delayed write and policy permits, use the governed temporary outage buffer (for current phase: controlled Excel only when selected by G17), visibly mark outputs as DB-outage fallback, create a G11 incident and high-priority owner alert, then reconcile to the primary DB and delete the temporary file after verified success.

## Adapter policy
Provider adapters are modules under G17 by default, not separate Skills.
A provider adapter becomes its own Skill only after future G0 qualification proves an independent lifecycle/trigger/outcome.

Current REFERENCE_SCOPE selected adapter: Hatchable.
Hatchable-specific limits, scheduler, monitoring formulas and backup egress remain adapter-local. Unknown quota formulas stay UNKNOWN.

## Migration/rollback
Material migrations require:
- GOOD backup;
- manifest;
- stable-ID mapping;
- deterministic/idempotent backfill;
- reconciliation;
- cutover plan;
- tested/simulated rollback;
- observation window;
- no immediate deletion of the old authority.
Provider switches must preserve consumer semantic contracts.

## Backup/DR
G17 defines the data requirements and adapter contract; provider transport stays adapter-specific.
Current Hatchable production contract:
- one full logical backup file per physical Hatchable project/database authority per backup slot;
- the file contains ALL base tables and ALL logical project_ref workloads stored inside that same physical Hatchable project database schema;
- logical projects/project_ref values inside the same physical database do NOT receive separate backup files or separate backup jobs;
- a separate physical Hatchable project/database authority requires its own scheduler/config/credential binding and its own backup artifact stream;
- two installation-local backup slots: 03:00 and 15:00;
- SharePoint retention: 120 days with a maximum of 240 GOOD production backups;
- cleanup runs only after the current remote backup is GOOD.
Stage 19 direct Hatchable->Microsoft Graph->SharePoint proof is PASS.

## Composition boundaries
Compose; do not duplicate. The machine-readable contract is `INC_G17_CROSS_SKILL_INTEGRATION_V1`.
- G0: qualification/compiler gate and minimum runtime propagation; G17 owns data/storage/database design.
- G1: physical governed file publication/archive.
- G4: artifact/Skill classification/profile; G17 consumes classifications that affect persistence.
- G6: general version/lifecycle policy; G17 owns schema/data migration semantics.
- G7: package/metadata structure; G17 supplies project/data/storage metadata requirements.
- G8: general security/privacy/permission authority.
- G9: global resource/token optimization.
- G10: dependency/stable-reference policy; G17 preserves provider-neutral project/domain/adapter references.
- G11: logging/traceability semantics.
- G12: independent black-box testing.
- G13: independent certification.
- G14: artifact/output package integrity; G17 owns data/schema/migration artifacts included in packages.
- G15: human notification/decision gateway.
- G16: system/agent coordination.
- G19: plugin packaging/distribution/installation (deferred outside current REFERENCE_SCOPE scope).
- G18: human conversation/output governance.

## Human-readable reporting compatibility
G17 owns data truth and structured findings, not the universal human renderer. Human-facing G17 output MUST compose with the current G18 rendering contract.
For Persian Markdown tables:
- the visual requirement is `NUM#` rightmost;
- G17 MUST resolve the current surface-specific human-output serializer from current G18 authority and MUST NOT hard-code one source order for Chat, Work and Codex;
- current Chat Web owner evidence requires the Chat serializer with `NUM#` FIRST in Markdown source; Codex/Work use their separately verified profiles;
- a Persian G17 report that visibly renders `NUM#` leftmost is non-conformant and must be regenerated before send;
- G17 must not duplicate a competing general conversation/output governor; this is a mandatory compatibility constraint.

## Required references
- references/canonical-persistence-architecture.md
- references/db-gateway-contract.yaml
- references/db-naming-standard.yaml
- references/query-performance-policy.yaml
- references/identity-access-secrets-policy.yaml
- references/encryption-standard.md
- references/key-lifecycle-standard.yaml
- references/migration-rollback-standard.yaml
- references/cross-skill-integration-contract.yaml
- references/migration-manifest-template.yaml
- adapters/hatchable/capability-map.md
- adapters/hatchable/monitoring-formulas.md

## Stage 23 integration state
- Cross-Skill contract: `INC_G17_CROSS_SKILL_INTEGRATION_V1`.
- G0 Build-Time qualification/Runtime propagation integration: IMPLEMENTED_CANDIDATE.
- Provider-specific leakage into ordinary consumer logic: FORBIDDEN.
- Visible-ID ambiguity before Stage 29: resolve Data Governor by stable ID `G17-SKL-002`.

## Candidate hard gates
SUCCESS_VERIFIED is forbidden while any applies:
- Stage 29 atomic G17/G19 namespace migration incomplete;
- required G12 independent black-box validation incomplete;
- required G13 independent quality certification incomplete;
- unresolved secret/security/data-integrity failure;
- test assets not cleaned;
- provider-specific coupling leaked into ordinary consumer Skills.

## Stage 29 canonical namespace state
- Visible namespace: G17
- Stable ID: `G17-SKL-002`
- Canonical path: `skills/router/g17-data-governor/`
- Prior G17 Plugin Packaging stable lineage moved to G19 under stable ID `G17-SKL-001`; no second canonical G17 remains.
- Stage 19 remote backup proof: PASS.
- Stage 29 namespace migration: PASS.
- Final production certification remains gated by G12/G13.

## Stage 28 persistence sweep state
- Registry: `INC_G17_STAGE28_FILE_DB_CANDIDATE_REGISTRY_V1`.
- Connector-visible SharePoint file sweep/classification: PASS_CURRENT_SWEEP.
- Target persistence designs for high-confidence candidates: PASS_DESIGN.
- Default physical authority remains the existing REFERENCE_SCOPE Hatchable database; logical project isolation uses `project_ref`.
- No file is migrated merely because it is XLSX/CSV/JSON.
- Human/document/report/evidence artifacts remain files unless operational authority is independently proven.
- S4/high-sensitivity candidates are represented only by opaque refs in general GitHub governance artifacts and require restricted G8/G17 design.
- Candidate-level DB source-of-truth cutover remains OWNER_APPROVAL_REQUIRED.
- Stage 27 G11 legacy-retirement is PASS/CLOSED; the canonical G11 relational route is active and the 26 legacy SharePoint List IDs are absent from the active site.

## Mandatory G16 cross-surface generation gate
Contract: `INC_G16_CROSS_SURFACE_EXECUTION_DELIVERY_V1`.
When this Skill generates a prompt, instruction, work order, Handoff, report, command file or execution artifact for another Chat/Work/Codex/agent surface, latest G16 resolution/activation is mandatory before generation. Missing G16 blocks execution-ready output. Applicable administrative execution follows PowerShell -> official API -> official CLI -> structured browser/connected tool -> visual UI. Generated cross-surface files are remotely persisted/read back under governed GitHub/SharePoint routing and handed over only by verified link or stable reference; local/sandbox direct file handoff is not an accepted delivery path.

## Release event-history storage boundary — HARD GATE
When Handoff/checkpoint event volume becomes query-oriented or high-volume, persist normalized operational history through the governed G11/G17 structured data path rather than expanding the canonical Handoff into an event warehouse or creating per-checkpoint SharePoint files. Preserve release_id, artifact_digest, work_unit_id, lease_id, executor surface and correlation identifiers.

## Installation-state and project-data portability
Contracts: `INC_G17_INSTALLATION_STATE_PERSISTENCE_V1` and `INC_G17_PROJECT_DATA_REGISTRY_V1`.

Setup/bootstrap state must be persistable before any database dependency exists. It carries stable installation identity, environment/account context, edition/package/setup-schema identity, logical-resource bindings, auth references and migration checkpoint; raw secrets are prohibited. Durable updates use provider CAS when available, otherwise the governed single-writer path. Provider migration preserves `installation_id` and requires readback, reconciliation and rollback.

Every persistent structured workload resolves `project_ref`; small unnamed work uses `PRJ_MISC` only with `workload_ref` or `domain_ref`. SkillForge has one default shared database authority unless the owner explicitly assigns an alternate provider/database for a named project or Skill. The Project Data Registry preserves stable project identity, namespace, provider adapter/physical database references, security/cost/backup-retention/lifecycle metadata. Cross-project access is deny-by-default; mutation predicates bind `project_ref`, and a cross-project semantic-ID collision fails closed with zero mutation.

Hard gates: `PROJECT_CONTEXT_RESOLVED`, `SINGLE_DATABASE_POLICY_COMPILED`, `PROJECT_SCOPE_ENFORCED`, `PROJECT_REGISTRY_READBACK_VERIFIED`.


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

Privacy responsibility: Resolve physical IDs, custody and data inventories only from external private state.

## Private installation and user-specific parameterization — SkillForge 3.0.4
The distributable contains no owner-specific service IDs, credential values, site/folder URLs, tenant IDs, or private evidence. Use `config/setup-service-catalog.json` and `setup/CHATGPT_FIRST_RUN.md` for the setup plan. Resolve configuration through a user-authorized private external profile, pinned by exact SHA-256; validate current connector identity/permissions/readback for every real action. Missing bindings must produce a read-only/configuration-needed result, never invented values or silent mutation. G20 is a separate setup-runtime candidate; this is not a claim of automatic ChatGPT plugin execution. Public feedback remains OFF until a particular sanitized payload and destination receive explicit owner permission.
Relevant optional service families: `DATABASE`, `BACKUP`, `LOGGING`.
