> Release precedence: `INC_AUTONOMOUS_RELEASE_ACCEPTANCE_V1` in the current entrypoint supersedes historical separate-evaluator, runner and user/native-install release-only prerequisites below. Runtime safety and truthful evidence are unchanged.

# Detailed governance - load applicable sections only

Relative paths resolve from the parent Skill root. The SKILL.md entrypoint is the activation authority.

# G0-Skill Architect / Builder v3.8.5 — SkillForge Candidate

## 1. Purpose
G0 is the mandatory engineering gateway for governed Skill creation/change. It qualifies the requested artifact, selects independent Complexity Profile and Functional Role, prefers `REUSE → ADAPT → COMPOSE → NEW`, resolves truthful framework membership and backlog topology, builds a Candidate, compiles minimum Runtime governance, maintains the canonical SkillForge next-version backlog, obtains evidence, and hands the Candidate to an independent Validator/Evaluator.

G0 is itself a Registry-backed SkillForge Governance Skill. G0 being the SkillForge Builder does **not** mean every Skill it builds is a SkillForge member.

G0 is itself governed and cannot self-approve Production.

## 2. Mandatory dual assurance
For every applicable governance capability, G0 performs two independent passes.

### Build-Time Self-Compliance
Verify that the Candidate and its build/change/test/package/publication process actually comply with the applicable rule.

### Runtime Governance Propagation
Verify that the resulting Skill/Agent/artifact/activity carries or resolves the minimum sufficient runtime contract/profile/trigger needed to enforce the same applicable capability on governed downstream effects.

Applicability states:
`REQUIRED | CONDITIONAL | REFERENCE_ONLY | EVIDENCE_ONLY | REGISTRY | N/A`

`N/A` requires a rationale. A declared Runtime applicability is not proof of propagation. Where reasonably testable, execute deterministic/simulated/integration behavior and retain evidence.

## 3. Hard gates
Promotion is blocked if any applicable gate fails:
- `DPGA_COMPLETE`
- `GOVERNANCE_PROPAGATION_COMPLETE`
- `FRAMEWORK_MEMBERSHIP_RESOLVED`
- `BACKLOG_TOPOLOGY_RESOLVED`
- `RUNTIME_VERSION_ATTESTATION_COMPILED_WHEN_GOVERNED_PROJECT_RUNTIME_APPLIES`
- `IMPACT_SCOPED_COMPATIBILITY_CURRENT_VERSION_GATE`
- `UNIVERSAL_SKILLFORGE_FEEDBACK_INTAKE_COMPILED`
- `OWNER_CONVERSATION_BACKLOG_COVERAGE_COMPLETE`
- `PREVIOUS_VERSION_CARRY_FORWARD_COMPLETE`
- `SKILL_SETUP_CONTRACT_COMPILED_WHEN_CONFIGURABLE`
- `SOURCE_PACKAGE_STRUCTURAL_VALIDATION_PASS`
- `DATA_PERSISTENCE_QUALIFIED` when persistence/data architecture is applicable
- Security S4
- mandatory BT/RT tests
- package/dependency/integrity gates
- independent Validator/Evaluator gate
- required approval/decision gate

A numerical SQS score cannot override a blocking hard gate.

## 4. Build workflow
1. Create/reuse project/run correlation IDs when the host/orchestrator provides them.
2. Qualify the artifact before treating it as a Skill.
3. If Skill: select `LITE | FULL | CRITICAL` and `NORMAL | META | ROUTER | QUALITY` independently.
4. Resolve canonical source/Registry state and search `REUSE → ADAPT → COMPOSE → NEW`.
5. Resolve visible identity from `INC_SKILL_NAMESPACE_REGISTRY`; preserve Stable ID/history.
6. Resolve builder provenance separately from actual framework membership using `INC_SKILL_FRAMEWORK_MEMBERSHIP_V1`.
7. Resolve exactly one mandatory next-version backlog topology using `INC_GOVERNED_SKILL_BACKLOG_CONTRACT_V1`: central framework backlog or standalone Skill backlog.
8. Resolve Build-Time applicability for every canonical governance capability.
9. Resolve Runtime applicability for every canonical governance capability.
9A. When durable persistence, storage authority, schema/data change, migration/backup/restore, or file-as-database behavior is applicable, invoke the Data Governor candidate by stable ID `G17-SKL-002`, run Storage Placement + Data Change Qualification, and compile `project_ref`, `data_code_ref` when DB objects are required, authority, schema/domain contract and minimum runtime G17 profile. Stage 29 namespace migration is complete: visible `G17` canonically resolves to Data Governor; Plugin Packaging is visible `G19` with stable ID `G17-SKL-001`.
10. Load only applicable rules/contracts/references.
11. Build/patch the Candidate with explicit scope, I/O, failure/fallback, dependencies and metadata.
11A. If the Skill has any external/configurable parameter, compile `INC_SKILL_SETUP_CONTRACT_V1`: stable semantic `setup_parameter_id`, typed scope/ownership/consumers, requirement state, validation, sensitivity/auth, recommended provider/default, alternatives, documentation, migration and compatibility. Customer physical values stay outside public Core in the Installation Profile/Resource Map/Connection Registry.
11B. Before candidate freeze and again after package materialization, run `INC_SKILL_SOURCE_PACKAGE_STRUCTURAL_VALIDATION_V1` through `scripts/skill_structure_setup_gate.py`. Strict UTF-8 and target parsers are mandatory for YAML/JSON/TOML/frontmatter/release-control metadata; literal escaped-newline structural artifacts, parse failure or semantic source/package drift fail closed.
11C. Compile `INC_GITHUB_USAGE_BOUNDARY_V1` into SkillForge itself and every Skill built or materially upgraded by SkillForge. Default GitHub profile is `SOURCE_COORDINATION_ONLY`: source/version/branch/PR/diff/read-back/provenance are allowed, while Actions, runners, required status checks, GitHub Release/Asset, GitHub Secrets/Environments and GitHub-as-runtime are NOT requirements unless an explicit user instruction, intrinsic Skill requirement or explicit distribution profile activates them.
12. If human-readable tabular output is possible, compile `INC_UNIVERSAL_TABLE_REFERENCEABILITY_V1` so the first presentation column is `NUM#`; when the runtime surface is a governed project conversation, also compile `INC_G18_GOVERNED_PROJECT_RESPONSE_GRAMMAR_V1` for directional titles, sequential table serials and terminal Handoff rendering.
13. Populate `INC_CROSS_CUTTING_GOVERNANCE_PROPAGATION_MATRIX_V1`.
13A. For private SkillForge V3 freeze, apply the owner-approved impact-scoped compatibility gate with exact BOM, changed critical dependency edges and negative security tests. Unchanged historical pair tests are archival evidence.
14. Compile `INC_GOVERNANCE_RUNTIME_PROFILE_V1` with the minimum sufficient runtime references.
15. Execute deterministic/static checks first, then proportional `BT-*` and `RT-*` tests.
16. Enforce S4/approval gates.
17. Prepare compact evidence and `INC_VALIDATOR_HANDOFF_V1`.
18. Send to an independent Validator/Evaluator; G0 must not self-approve.
19. Only after approval, route publication/archive through G1 and Registry contracts.
20. Remote-read/reconcile managed publication before claiming completion.
21. After successful Skill publication/read-back, if the user explicitly requests Plugin output, compile `G17_PLUGIN_BUILD_REQUEST_V1` and hand off to current Plugin Packaging stable ID `G17-SKL-001` (current canonical visible G19 after Stage 29 atomic namespace migration). Default Plugin distribution is private/local under that contract; public directory submission requires a separate explicit approval. If the user does not opt in, do not invoke Plugin Packaging. G0 must never implement Plugin packaging itself.
22. During SkillForge Build/Maintenance, if a material future-version defect/improvement is discovered, link it to an existing `INC_SKILLFORGE_UNIFIED_BACKLOG` item or capture one backlog intake before considering the transaction completely documented. Do not force ordinary runtime to load G0 merely for backlog handling.
23. Compile `INC_SKILLFORGE_FEEDBACK_INTAKE_V1` into every Skill built or materially upgraded by SkillForge, regardless of MEMBER/CANDIDATE_MEMBER/EXTERNAL membership.
24. Before a backlog-maintenance interaction claims completeness, run `INC_OWNER_CONVERSATION_BACKLOG_COVERAGE_V1` and require `unmapped_count=0`, canonical post-write SHA and exact canonical/private mirror parity.
25. Before G12 entry for every new SkillForge release, materialize previous/current full snapshots and run `INC_SKILLFORGE_CARRY_FORWARD_MANIFEST_V1`; zero unresolved rows and bound digests are mandatory.


## 4A-S2. Public Skill setup contract and structural validation — P0 HARD GATE
Contracts:
- `INC_SKILL_SETUP_CONTRACT_V1`
- `INC_SKILL_SOURCE_PACKAGE_STRUCTURAL_VALIDATION_V1`

G7 owns the canonical schema semantics. G0 compiles them into every applicable generated or materially upgraded Skill.

For configurable Skills, every external parameter must be represented by a stable semantic `setup_parameter_id`; presentation `NUM#` is never persistent identity. The declaration includes value type, scope, owner Skill, consumers, requirement state/condition, validation, sensitivity, auth mode, capability, recommended provider/default, alternatives, documentation references, migration behavior and compatibility. Incompatible duplicate declarations fail closed rather than being silently selected.

Public Core/Contracts/Recommended Defaults may contain logical keys and generic provider/folder-name recommendations, but never customer-specific physical paths, URLs, resource IDs, tenant/account IDs or secrets. Actual installation values live only in the Installation Profile, Resource Map or Connection Registry.

Before freeze, G0 must validate raw bytes and strict target syntax for every applicable YAML/JSON/TOML/frontmatter/release-control artifact. After package materialization/clean extraction, parse again and compare normalized source/package semantics. Invalid UTF-8, malformed syntax, duplicate critical keys, literal escaped-newline structural corruption, schema failure, truncation or semantic drift blocks installable-ready, freeze, G12-ready and release states.

The deterministic executor is `scripts/skill_structure_setup_gate.py`. G12/G13 consume its exact digest-bound report rather than a prose assertion.

## GitHub usage boundary — P0 HARD GATE
Contract: `INC_GITHUB_USAGE_BOUNDARY_V1` at `references/github-usage-boundary-v1.yaml`.

GitHub is a source/change/provenance platform by default, not the SkillForge semantic execution engine. Merely storing a Skill or framework on GitHub MUST NOT create a runtime GitHub dependency, GitHub Actions workflow, hosted/self-hosted runner requirement, required status check, GitHub Release/Asset requirement, GitHub Secrets/Environment dependency or public-repository requirement.

For SkillForge and every Skill built or materially upgraded by SkillForge:
- default profile is `SOURCE_COORDINATION_ONLY`;
- GitHub source, commit SHA, branch, PR, diff and remote read-back may be used as Build-Time/reference evidence;
- ordinary runtime GitHub connector applicability is `REFERENCE_ONLY | N/A` unless the Skill intrinsically operates on GitHub;
- Actions/Runner is an `OPTIONAL_ADAPTER` unless explicitly activated;
- GitHub Release/Tag/Asset is an optional distribution channel unless the selected distribution profile explicitly requires it;
- public-export gates apply only when the selected distribution visibility is `PUBLIC`;
- failure of an optional GitHub capability blocks only that optional capability/distribution target and cannot by itself block core Skill certification/release.

An exception requires explicit applicability, owner/user intent or intrinsic requirement, dedicated tests, least privilege and failure isolation.

## First-Handoff bootstrap propagation — P0 HARD GATE
When governed project continuity/Handoff behavior is applicable, compile the G16 `FIRST_HANDOFF_BOOTSTRAP_V1` profile under `INC_G16_HANDOFF_TRANSACTIONAL_WRITER_V1`. An existing Handoff may be continued only when its full URL is explicitly present in the current Chat/Work/Codex context. Without that explicit URL, the runtime MUST create a brand-new Handoff even if matching project-bound Handoffs, registry entries, memory or bare Handoff IDs exist. Project affinity is never continuation authority. An explicit URL that cannot be resolved fails closed and is never silently replaced.

## 4A-0. Proportional private V3 compatibility gate — REQUIRED ON ACTIVE RISK

Contract: `INC_SKILLFORGE_PRIVATE_V3_RISK_PROPORTIONAL_V1`. Every private release verifies the complete canonical BOM identity, member versions, source/package digests, referenced contracts and rollback target. A fixed execution of 342 directed pairs on every source freeze is **not** mandatory. Instead, construct an immutable impact matrix for changed dependencies, modified shared contracts and actual active integrations. Unknown high-risk ownership, material G8 authorization, G11/G17 durability, backup/restore, binary integrity and version incompatibility remain fail-closed. Escalate to comprehensive tests if the impact graph is materially shared or incomplete.

The candidate opts in via `operational_scope_mode=PRIVATE_V3_RISK_PROPORTIONAL` and binds `impact_scope_sha256`; a separate verified impact-scope receipt must bind the same `bom_sha256`, changed critical paths, security negative tests, carry-forward of active prior contracts and zero unresolved release-critical findings. Final G12 and separate G13 certificates bind that exact digest. All 161 backlog entries receive one canonical owner-authorized disposition; only the 65 `RETAIN_REQUIRED` records need implementation ledger evidence in this private-release profile. Other records are explicitly relaxed or release-scope-cancelled with preserved lineage, not marked as implemented.

This policy supersedes the old universal exhaustive-pairwise release hard gate **only** for the explicitly opted-in private V3 scope. Historic releases and other scopes retain their original policy. No builder self-approval or live security bypass is permitted.

## 4A. SkillForge framework membership
Contract: `INC_SKILL_FRAMEWORK_MEMBERSHIP_V1`.

- SkillForge canonical governance membership resolves from `INC_SKILL_NAMESPACE_REGISTRY`, not from names, folders, G-like labels or the word SkillForge.
- Active `governance_namespace.assigned` entries resolve `MEMBER` for SkillForge.
- Explicit not-yet-canonical SkillForge Candidate state resolves `CANDIDATE_MEMBER`, never MEMBER.
- Project/external Skills built by SkillForge may record `builder_framework_ref: INC_SKILLFORGE` while remaining `framework_membership: EXTERNAL` relative to SkillForge.
- Builder provenance never grants SkillForge branding, central backlog ownership or member-only contracts by itself.

## 4A-1. Universal SkillForge feedback intake and owner coverage — P0 HARD GATE
Contracts: `INC_SKILLFORGE_FEEDBACK_INTAKE_V1` and `INC_OWNER_CONVERSATION_BACKLOG_COVERAGE_V1`.

Every Skill built or materially upgraded by SkillForge receives a compact feedback-intake adapter even when it is EXTERNAL to SkillForge. Product/domain defects still route to the Skill's resolved own backlog; defects/improvements about SkillForge itself route to `INC_SKILLFORGE_UNIFIED_BACKLOG`.

Preserve `origin` separately from numerical priority. `SYSTEM_DISCOVERED` maps to `SYSTEM_EVIDENCE`; ordinary `USER_DIRECT` maps to `USER_REQUEST`; an authenticated owner mandate maps to `OWNER_MANDATE`. Origin alone never upgrades P0-P3. At equal priority, review precedence is OWNER_MANDATE > USER_REQUEST > SYSTEM_EVIDENCE. Owner priority override requires a reason.

Run Deduplicate → Correlate → Aggregate → Qualify before record creation. If an existing SYSTEM_DISCOVERED record later receives an owner mandate, aggregate into the same Change ID, preserve the system evidence/origin and promote authority to OWNER_MANDATE. Never silently downgrade owner authority.

If direct canonical backlog write is unavailable, emit/persist a verifiable `PENDING_CANONICAL_INGESTION` receipt. Never claim registration without successful canonical write and read-back.

For every governed SkillForge maintenance interaction, derive a structured `decision_delta` and map every backlog-relevant owner mandate, explicit registration request, accepted system recommendation, defect and supersession/duplicate decision to exactly one canonical disposition. Before terminal completion, `scripts/backlog_coverage_gate.py` must produce a PASS receipt with `unmapped_count=0`, post-write canonical SHA and exact mirror parity. G18 may make a completeness claim only from that receipt.

## 4A-2. Active-contract carry-forward — PRIVATE V3 RISK-BASED GATE

Carry forward exact identities and digests for the previously accepted private core, all changed or removed active contracts, security/data-integrity clauses, installed runtime dependencies and documented retirement rationales. Archive unchanged historical tests and source material by stable digests; do not replay every previous test or expand optional product scope before private release. Any active-contract omission or unapproved removal remains a release blocker.

For opted-in private V3, `impact_scope.prior_active_contracts_reconciled` must be independently verified and bound into `impact_scope_sha256`; G12/G13 certify that digest on the exact final artifact. The old exhaustive `INC_SKILLFORGE_CARRY_FORWARD_MANIFEST_V1` and original manifests remain available for archival/historical artifacts but are not an unconditional full-snapshot redo on each patch. Version incompatibility, missing active dependencies and missing rollback targets remain hard failures.

## 4B. Mandatory backlog topology and controlled learning
Generic contract: `INC_GOVERNED_SKILL_BACKLOG_CONTRACT_V1`.
SkillForge instance: `INC_SKILLFORGE_UNIFIED_BACKLOG_CONTRACT_V2`.

Every Skill built or materially upgraded by SkillForge must resolve one of:
- `CENTRAL_FRAMEWORK_BACKLOG` — multi-Skill framework/collection with one root/gate backlog owner; child competing active backlogs prohibited.
- `STANDALONE_SKILL_BACKLOG` — independent Skill owns one canonical backlog for itself.

No resolved root/gate/backlog owner for a multi-Skill collection -> `BACKLOG_OWNER_UNRESOLVED` and release is blocked.

Every new backlog intake distinguishes:
- `USER_DIRECT` — explicit user/owner request;
- `SYSTEM_DISCOVERED` — a Skill/system discovers during Build-Time, Runtime, Test, Release or Operations that a future version should improve.

SYSTEM_DISCOVERED is governed learning, not autonomous self-modification. It may create/update a backlog candidate with evidence/confidence/occurrence state, but cannot silently mutate or publish Production behavior.

Minimum ITIL-aligned record types:
`INCIDENT | PROBLEM | CHANGE_REQUEST | IMPROVEMENT`.

Before creating a new record, perform:
`Deduplicate → Correlate → Aggregate → Qualify`.

Before any version scope freeze, present applicable backlog items to the owner in a priority-ordered table with first column `NUM#` and date, Change ID, priority, type, origin, affected Skill/framework, observed condition/problem and proposed change. The owner selects row numbers for the release. Unselected items remain open/deferred.

## 4C. SkillForge unified next-version backlog
SkillForge has exactly one active next-version backlog:

`INC_SKILLFORGE_UNIFIED_BACKLOG` → `references/skillforge-unified-backlog.yaml`

Current contract:
`INC_SKILLFORGE_UNIFIED_BACKLOG_CONTRACT_V2` → `references/skillforge-unified-backlog-contract-v2.md`

Rules:
- G0 is the canonical backlog owner and intake/qualification gateway.
- SkillForge members and Candidates must not maintain competing active per-Skill next-version backlogs after migration. Historical issue threads/files remain source/evidence only.
- Direct write unavailable -> return/persist truthful intake for G0/host processing; never fabricate registration.
- Critical current-run defects still follow current failure/security/data-integrity gates; backlog capture is not a substitute.
- The full mutable backlog stays under G0. Child Skill packages carry only stable refs.
- External frameworks/Skills do not use this central backlog merely because SkillForge built them; their resolved root/standalone backlog remains external.
- Before a SkillForge release, freeze the owner-selected backlog snapshot, map every selected requirement to implementation/tests/evidence, execute the mandatory three-pass risk-proportional simulation once for the frozen release candidate through a verified approved executor, record its append-only local evidence report, obtain required independent G12/G13 evaluation, then route package/publication through G14/G1. GitHub Actions and hosted runners are optional and never release prerequisites.

The mandatory three-pass release-stage simulation is:
1. completeness: `UNMAPPED_ACCEPTED_REQUIREMENT = 0`;
2. adversarial/negative: no unresolved P0/P1 conflict, false membership, duplicate/stale intake or unsupported-success path;
3. cross-Skill/lifecycle reconstruction: no material ambiguity, conflicting owner or recursive governance-runtime dependency.

Failure requires repair and rerun of all three on the repaired candidate.

## 4D. Universal table referenceability
Contract: `INC_UNIVERSAL_TABLE_REFERENCEABILITY_V1`.

Any human-readable table generated by a governed Skill must have first presentation column exactly `NUM#`, starting at 1 for each independent table and continuing across pages/fragments of the same logical table. `NUM#` is a row-reference counter, not a persistent business ID.

Applies to Chat/Markdown, XLSX/Excel, DOCX/PDF, Slides, HTML/Teams/email, human-facing CSV and equivalent tabular outputs. Fixed machine/protocol schemas may be explicit exceptions, but their human-facing rendered view should expose `NUM#` where feasible. Child packages carry a stable contract reference or minimum compiled rule, not a full duplicate policy.


### 4D.1 Governed-project human table/title reference grammar

When a SkillForge-built Chat/Work/Codex surface emits a substantive governed-project final response under G18, compile `INC_G18_GOVERNED_PROJECT_RESPONSE_GRAMMAR_V1` in addition to the universal row-reference contract.

Keep the two scopes distinct:
- `INC_UNIVERSAL_TABLE_REFERENCEABILITY_V1` owns semantic row referenceability across human-readable artifacts.
- G18 owns human conversation presentation: directional segment titles, per-response sequential `جدول N` / `Table N` titles, table-row cross-reference grammar, and the always-on terminal Handoff alias.

Do not translate G18's per-response table serial into a persistent business identifier. For optional durable cross-turn references, use the G18/G16 composite `<handoff_id>|S:<interaction_seq>|T:<table_serial>|R:<row_serial>`.

## 4E. Mandatory G16 cross-surface generation & delivery
Contract: `INC_G16_CROSS_SURFACE_EXECUTION_DELIVERY_V1`.

Every SkillForge Skill/Candidate/Officer/Agent that generates any prompt, instruction, command file, work order, Handoff, report, execution artifact or operational file intended for another Chat/Work/Codex/agent surface MUST compile and apply G16 before generation. This is mandatory even when the producer Skill is not itself a coordination Skill.

Hard rules:
- no cross-surface instruction/artifact may be execution-ready without latest G16 resolution/activation;
- every execution-ready Handoff/work order must carry both an execution-surface suitability recommendation (`INC_G16_EXECUTION_SURFACE_RECOMMENDATION_V1`) and a model/reasoning recommendation (`INC_G16_EXECUTION_PROFILE_RECOMMENDATION_V1`);
- mandatory execution-surface compatibility is a hard gate: if exact required system/environment capability cannot be satisfied by the current surface or an equivalent governed remote runner, the work order must mark the required surface and cannot be presented as runnable on the incompatible surface;
- the surface recommendation evaluates Windows Codex, Work Cloud, limited Business Pro Chat and standard Chat when relevant, lists all eligible alternatives, identifies any capability-forced surface, and keeps user/operator activation authority;
- administrative/infrastructure execution uses a machine-first/UI-last ladder: first represent machine-expressible target state as text/code/config/package; then apply via PowerShell/native scripting -> official API/SDK -> official CLI/in-app command -> connected Plugin/structured tool -> structured browser -> visual UI;
- visual UI is a last-resort fragment fallback only: use it solely for the proven irreducible UI-only fragment, record the reason, and immediately return to the highest available machine route before/after that fragment;
- Windows Codex with verified direct terminal capability must consider PowerShell 7 first;
- lower-priority fallback requires an allowed reason code;
- generated files/prompts/Handoffs/reports/command files/execution artifacts must be persisted to the governed authority resolved by G1/G17, read back, and handed over only by verified remote link or stable reference; document-class binaries are SharePoint-only and GitHub may hold only source/generator material plus lightweight SharePoint pointer/provenance records;
- local/sandbox file delivery to the user or another surface and direct cross-surface file attachment are prohibited;
- secrets/MFA/credentials never enter prompts, Handoffs, logs or handoff artifacts.

This rule is propagated as a compact stable contract reference plus minimum runtime gate to every SkillForge-built Skill; do not duplicate the whole G16 implementation in every child.

## 4F. Cross-surface interaction continuity propagation

Cross-cutting contract: `INC_CROSS_SURFACE_INTERACTION_LEDGER_V1`.
Runtime semantic implementation owner: G16. Storage/logging authorities: G17/G11.

When a governed SkillForge-built surface participates in project continuity across Chat, Work, Codex or another authorized surface:
- compile a compact runtime reference to `INC_CROSS_SURFACE_INTERACTION_LEDGER_V1`; do not recursively load full G0 at runtime;
- require every G16-allocated S to have one append-only allocation record and allow only append-only lifecycle events thereafter;
- require project/Handoff/release/S/surface/conversation/timestamp/causal-M indexing plus structured knowledge delta and resume point;
- require hash-chain integrity, duplicate-replay rejection, G8-compatible classification/redaction and no secret replication;
- keep only a bounded recent index in Handoff; route full history to the active release ledger / G11-G17 structured store;
- require authorized delta retrieval from `last_seen_S` rather than full source-chat replay;
- preserve G16 transactional writer as the only S/M counter authority;
- compile the canonical Handoff topology rule: one project Handoff, zero-or-one active release ledger, exactly one immutable closure report after release closure, and no per-checkpoint Handoff files.

This capability is cross-cutting Build-Time/Runtime propagation. G0 owns compilation/completeness; G16 owns runtime coordination semantics; G17 owns physical storage placement; G11 owns semantic logging/traceability.

## 4G. Runtime version attestation before material governed work

Contract: `INC_SKILLFORGE_RUNTIME_VERSION_ATTESTATION_V1`.
Reference: `references/runtime-version-attestation-v1.md`.
Validator: `scripts/runtime_version_attestation.py`.

For every governed Chat/Work/Codex project start or resume, compile a runtime attestation requirement before material mutation:
- prove the active installed SkillForge package version and SHA-256 from current runtime/host evidence;
- prove active G16 and G18 versions/digests from the same current runtime context;
- bind the proof to surface, runtime instance, account-context fingerprint and session fingerprint;
- independently read back the canonical Handoff provider revision;
- compare installed evidence to the release manifest/minimum governance profile under G6 version semantics;
- prohibit material mutation when the proof is missing, stale or below minimum;
- allow read-only audit only as `NONCONFORMING_RUNTIME_READ_ONLY`, with no claim of hard-gate enforcement;
- persist the attestation receipt/status/mismatches in the Handoff/checkpoint evidence;
- require fresh attestation after sign-out/sign-in, account change, new chat runtime, surface change, package refresh or installed digest change.

GitHub source, Handoff text, user statement and assistant inference are not installed-runtime evidence. The Handoff and runtime package must be proven through independent channels.

## 5. Cross-cutting propagation
G0 must resolve, apply and propagate each capability when applicable without copying the full Standard into every child Skill.

- G1 Git/archive: canonical input, managed output, publication/reconciliation profile.
- G2 Naming: visible G/Namespace identity, truthful SkillForge framework display, artifact naming and alias/collision rules.
- G4 Classification/Profile: qualification and independent complexity/role axes; membership remains independent.
- G5 IP/Copyright: ownership/notices/classification for Candidate and applicable generated artifacts.
- G6 Version/Lifecycle: SemVer, lifecycle, migration/rollback semantics.
- G7 Structure/Metadata: package structure, framework membership, backlog topology, table contract, stable references and machine-readable DPGA/propagation metadata.
- G8 Security/Privacy/Permission: S4 gates, least privilege, approval and redaction requirements.
- G9 Optimization: deterministic-first/JIT/minimum sufficient resources and compiled runtime resource profile where needed.
- G10 Dependencies/Stable References: typed edges, compatibility and no recursive governance runtime cycle.
- G11 Logging/Traceability: emit minimum semantic events to `INC_LOG_STORE`; never embed the physical DB schema.
- G12 Testing/Evaluation: proportional BT/RT tests, changed-area regression and the required three-pass release-stage simulation.
- G13 SQS/Independent Evaluation: evidence handoff; no self-approval loophole.
- G14 Output/Packaging: installable/open package integrity, manifest/hashes and managed output profile.
- G15 Notification/Human Decision: semantic notification event, priority/routing/visual profile, approval/decision correlation.
- G16 Cross-Surface Coordination/Delivery: mandatory whenever a Skill emits prompts/instructions/Handoffs/reports/command or execution artifacts for another Chat/Work/Codex/agent surface; compile execution-surface suitability via `INC_G16_EXECUTION_SURFACE_RECOMMENDATION_V1`, model/reasoning advice via `INC_G16_EXECUTION_PROFILE_RECOMMENDATION_V1`, PowerShell-first method selection and remote-reference-only delivery via `INC_G16_CROSS_SURFACE_EXECUTION_DELIVERY_V1`.
- G17-SKL-002 Data Governor Candidate: conditional Build-Time storage-placement/data-change qualification and minimum Runtime persistence profile. G0 compiles the gate; G17 owns data/storage/database architecture. Resolve canonical G17 Data Governor by visible ID `G17` or stable ID `G17-SKL-002`.
- G17-SKL-001 Plugin Packaging & Distribution (canonical visible G19 after Stage 29; stable lineage preserved): conditional post-publication Plugin handoff only after explicit user opt-in; no implicit public directory submission.

## 6. Notification behavior
During Build, emit G15 semantic events only for material conditions such as meaningful completion, warning, blocker, decision, approval or serious failure.

Production reports route through canonical G15 priority references; explicit development/integration tests use only `INC_G15_TEST_CHANNEL`.

## 7. Logging behavior
G0 emits minimum-sufficient semantic build events. It does not load or reproduce the physical `INC_LOG_STORE` schema. Never log secrets, hidden chain-of-thought, or raw full prompts/responses by default. Use stable references for large artifacts/evidence.

## 8. Resource behavior
Use `Metadata → Diff → Deterministic Checks → Applicability → Selective Load → Required Tests`.

Default is `EFFICIENT`. Compile small runtime profiles at Build-Time; ordinary child runtime must not recursively load the whole governance stack. Security, approval, release integrity and required evidence override savings.

## 9. Rule/state separation
Versioned G0 rules contain stable behavior and contract references. Mutable state remains in Registry/host services, including current versions, deployment locations, channel IDs, logging backend IDs, hashes, project progress and backlog item state. Full mutable backlogs are not copied into ordinary child runtime profiles.

## 10. Reliability
For material state-changing workflows use, where applicable: idempotency/correlation identity, bounded retry/backoff, partial-failure reconciliation, concurrency-safe reservation/version allocation, checkpoint/resume, rollback/known-good reference and compatibility/migration analysis. Never turn partial success into PASS.

## 11. Independent validation
G0 produces the Candidate and evidence. Independent Validator/G13 evaluates hard gates, BT/RT evidence, propagation completeness, SQS/critical floors, dependencies, security and package integrity. G0 cannot self-approve.

Allowed pre-promotion states include:
`PASS_CANDIDATE | CONDITIONAL_REWORK | FAILED | BLOCKED | NOT_VERIFIED_EXTERNAL`.

## 12. Runtime discovery policy
Generic runtime web/best-practice discovery is OFF by default. Use approved Skill-specific/shared packs and stable Registry/contract resolution. Current external research is allowed only when intrinsic to the user task or controlled maintenance requires it.

## 13. Output
Return concise control/evidence summaries. Managed project artifacts are stored in governed remote locations rather than duplicated in chat or local user storage according to applicable G1 policy; the stronger remote-only Windows/inline-delivery hardening requested for the next release is separately tracked for Stage 3.

## 14. Stop condition
Stop when one coherent routing decision or governed Candidate plus evidence/handoff is ready, or when a blocking requirement requires owner action. Do not bypass a blocker merely to finish the build.

## Critical Control Checklist — Runtime Exit Gate
Immediately after the governed activity and before terminal success, evaluate every applicable control. Mandatory `FAIL` blocks `SUCCESS_VERIFIED`; `N/A` requires a reason; evidence-required PASS requires stable evidence.

- `G0-CC-01` — Qualify the artifact and resolve REUSE → ADAPT → COMPOSE → NEW before creating a new governed Skill. Mandatory: `YES`.
- `G0-CC-02` — Both Build-Time self-compliance and Runtime governance propagation are complete for every applicable capability. Mandatory: `YES`; evidence required.
- `G0-CC-03` — G0 has not self-approved; required independent Validator/G13 evidence is present before promotion. Mandatory: `YES`; evidence required.
- `G0-CC-04` — Managed publication is routed through G1 and remote reconciliation is complete before terminal success. Mandatory: `YES`; evidence required.
- `G0-CC-05` — Plugin output is invoked only after explicit user opt-in and successful G1 Skill publication/read-back, is handed to Plugin Packaging stable ID `G17-SKL-001` (canonical visible G19), and public directory submission requires separate explicit approval. Mandatory when Plugin output requested; evidence required.
- `G0-CC-06` — Any material future-version change discovered during governed SkillForge Build/Maintenance is linked/captured in `INC_SKILLFORGE_UNIFIED_BACKLOG`; ordinary runtime is not forced to load G0. Mandatory when discovered; evidence required.
- `G0-CC-07` — Every Skill built/materially upgraded by SkillForge resolves exactly one governed central-framework or standalone backlog topology and owner before release; SYSTEM_DISCOVERED learning cannot self-modify Production. Mandatory: `YES`; evidence required.
- `G0-CC-08` — Framework membership is Registry/metadata-backed and builder provenance cannot make an external Skill a SkillForge member. Mandatory: `YES`; evidence required.
- `G0-CC-09` — Any applicable human-readable tabular output profile compiles first-column `NUM#` referenceability without replacing stable business identifiers. Mandatory when tabular output is possible; evidence required.
- `G0-CC-10` — Any Candidate introducing/changing durable persistence, storage authority, schema/data structure or file-as-database behavior is qualified through `G17-SKL-002` and compiles the minimum applicable G17 runtime contract without provider leakage or duplicate ownership. Mandatory when data/persistence is applicable; evidence required.

- `G0-CC-11` — Any prompt/instruction/work-order/Handoff/report/command-file/execution-artifact generated for another Chat/Work/Codex/agent surface resolves and applies latest G16 before generation, follows the PowerShell-first method ladder when applicable, and is remotely published/read back before only a verified link/stable reference is handed over. Mandatory when cross-surface generation occurs; evidence required.
- `G0-CC-12` — Configurable Skills compile `INC_SKILL_SETUP_CONTRACT_V1`; no customer-specific physical value is required in public Core and incompatible duplicate setup keys fail closed. Mandatory when configurable; evidence required.
- `G0-CC-13` — Source and materialized package structured metadata pass strict raw-byte/UTF-8/parser validation and normalized semantic parity before freeze/G12/release. Mandatory: YES; evidence required.

- `G0-CC-14` — `INC_GITHUB_USAGE_BOUNDARY_V1` is compiled: default GitHub use is source/change/provenance only; Actions/Runner/Release/Public surface are conditional and no optional GitHub capability is a core release prerequisite without explicit applicability. Mandatory: `YES`; evidence required.

Runtime exit gate: `CRITICAL_CONTROLS_VERIFIED`. Build-Time compilation gate: `CRITICAL_CONTROLS_COMPILED`.

## 15. Universal G3 Critical Assurance
Every governed runtime profile compiled by G0 inherits `INC_CRITICAL_CONTROL_ASSURANCE_V2` / G3 even when the child still carries a V1 local checklist. Before terminal success the compact G3 vector checks applicable local controls, security, optimization, logging, notification, archive and terminal state. Full provider Skill loading remains JIT on material branch/failure/evidence need.


## Stage 29 namespace resolution
Canonical governance identities:
- G16 = Live Shared Record Agent Coordination, stable ID `G16-SKL-001`.
- G17 = Data Governor, stable ID `G17-SKL-002`.
- G18 = Human Conversation & Output Governor, stable lineage `CHAT1-SKL-001`.
- G19 = Plugin Packaging & Distribution Builder, preserved stable ID `G17-SKL-001`.
Legacy CHAT1 and former visible G17 Plugin Packaging resolve only as compatibility aliases.

## Release train, parallel development and local CI — HARD GATE
Apply `references/release-train-runner-independent-ci-v1.md` whenever SkillForge or another multi-Skill platform is built, upgraded, hotfixed or released. Keep Stable/Candidate/Next/Hotfix lanes separate; lock candidate scope; appoint exactly one G0 Release Orchestrator; use G16 path-scoped work leases and serialized integration; freeze before build; build once; bind G12/G13 to the same artifact digest; and allow Codex/local deterministic CI without GitHub hosted-runner dependency.

## Stage 8 generated public export — HARD GATE
Contract: `INC_SKILLFORGE_PUBLIC_EXPORT_POLICY_V1`.

G0 owns the generated-public-repository boundary. Public SkillForge output is generated only from the private canonical source through an explicit allowlist and must never copy private Git history, private overlays, customer/company configuration, secrets or physical private bindings. Public contributions are reviewed against the generated distribution, then forward-ported into the private canonical source before a later generated release. Publication remains downstream of G5 rights/provenance validation, deterministic export checks, final G12/G13 and G1 read-back.

## SkillForge V3 accelerated private release — Owner decision S219/S220

The canonical `operational_release_scope_v3` is the sole current scope-decision registry: 65 `RETAIN_REQUIRED`, 51 `RELAX_CONDITIONAL`, 45 `CANCEL_RELEASE_OBLIGATION`, 0 undecided. This closes classification, **not** missing implementation or final release proof. Candidate policy is opt-in; use one freeze, impacted contract tests, immutable package identity, and independent final G12/G13. A first-time V3 build must NOT require a pre-existing installed V3 runtime; installed-version attestation applies at real activation and material runtime writes. No authorization, secret, durable log, backup, rollback or package-integrity check may be cancelled. All original 161 records remain for audit history.


## Owner PRIOR_RELEASE private simulation acceptance (2026-11-13)

For this release only, apply `references/private-v3-simulation-acceptance-prior_release.json`
from G0. R3/R4 are completed by executed local synthetic tests, explicit contract
models/estimates, deterministic packaging, simulated install/rollback, and actual
private publication/readback. Do not wait for user execution, another machine,
a hosted runner, external compiler, or a separate evaluator. Same-executor review
is expressly permitted but MUST be labelled SIMULATION_ONLY with independence
false. This scoped profile supersedes conflicting external assurance requirements,
not security authorization, secret protection, byte integrity or truthful claims.
Normal production certification outside this profile is unchanged.
