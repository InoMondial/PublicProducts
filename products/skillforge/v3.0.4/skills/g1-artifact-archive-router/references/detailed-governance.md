> Release precedence: `INC_AUTONOMOUS_RELEASE_ACCEPTANCE_V1` in the current entrypoint supersedes historical separate-evaluator, runner and user/native-install release-only prerequisites below. Runtime safety and truthful evidence are unchanged.

# Detailed governance - load applicable sections only

Relative paths resolve from the parent Skill root. The SKILL.md entrypoint is the activation authority.

# G1-Artifact Archive Router v5.1.2 — SkillForge Candidate

## 1. Purpose and authority
G1 is the mandatory owner of governed artifact egress, GitHub publication, remote-only file/document persistence and link delivery, binary integrity, P0/P1 SharePoint preservation, artifact lineage, cross-system evidence, recovery assurance and transaction closure.

GitHub `main` is authoritative for durable normative/source artifacts **except document-class binaries**. Durable document-class human/business artifacts are canonically stored in governed SharePoint only; GitHub may hold their source/generator code and lightweight SharePoint pointer/provenance metadata, never the document bytes in current normative/runtime paths. SharePoint is also used according to governed preservation/runtime/transitional/recovery policy. **Windows/local/sandbox paths are not governed artifact storage destinations and are never final delivery.** A technically required transient transport buffer is non-authoritative plumbing only and must be bounded and reconciled/removed after verified remote persistence when the tool surface permits it.

G1 is a Registry-backed SkillForge Governance Skill. G0 decides applicability; G6 owns SemVer/lifecycle; G8 security/privacy; G10 stable references; G11 logging semantics; G12/G13 validation/evaluation; G14 package construction; G15 notification/human-decision delivery. Those owners must not duplicate G1 physical routing.

## 2. Universal remote artifact delivery — HARD GATE
Use `INC_REMOTE_ARTIFACT_DELIVERY_V2`.

### 2.0 Artifact-delivery contract attestation — ABSOLUTE HARD GATE
The only active executable artifact-delivery contract is `INC_REMOTE_ARTIFACT_DELIVERY_V2`. Its V1 predecessor is migration history only and MUST NOT be advertised as current authority by G1 or G18.

Before the first governed artifact mutation/delivery in a runtime activation, resolve the G1/G18 compatibility matrix `references/artifact-delivery-contract-compatibility-v2.json` and run `scripts/validate_artifact_contract_attestation.py --mode startup`. Before package build/promotion, run the same validator in `--mode package` against canonical source plus the private-package mirror. Any missing participant, V1/V2 mismatch, canonical/package drift, or matrix mismatch fails closed as `ARTIFACT_CONTRACT_ATTESTATION_FAILED`.

The startup/package attestation is metadata/version integrity evidence; it does not replace G1 write/read-back, G12 validation, or independent G13 certification.

For every generated document/file/artifact requested or materially produced by Chat, Work, Agent, Codex or Skill:

`generated artifact -> G1 class route -> [document-class: SharePoint-only | other governed artifact: GitHub and/or SharePoint] -> remote write -> remote read-back -> verified canonical link -> user`

The following are prohibited as terminal completion:
- persistence on the user's Windows filesystem;
- local/sandbox-only artifact delivery;
- inline-only Chat/Agent delivery when a file/document artifact is the requested output;
- manual-user-upload fallback used to evade remote persistence;
- an upload response without required remote read-back/link verification.

Chat/Agent may summarize or quote a small portion, but the requested artifact itself must be remotely persisted and linked.

Failure states include `WINDOWS_ARTIFACT_DESTINATION_FORBIDDEN`, `LOCAL_ONLY_DELIVERY_FORBIDDEN`, `INLINE_ONLY_ARTIFACT_DELIVERY_FORBIDDEN`, `REMOTE_ARTIFACT_PERSISTENCE_REQUIRED`, and `REMOTE_ARTIFACT_DELIVERY_BLOCKED`.

## 2.1 Machine-readable route before visual UI — HARD GATE
Contract: `INC_MACHINE_ROUTE_BEFORE_VISUAL_UI_V1`.

For SharePoint/OneDrive/Excel/Teams/GitHub/database or other governed file/data resources, G1 MUST NOT open or manipulate the visual browser/UI merely to read, inspect, parse, update or move data while a machine-readable route is available.

Required route order for connected cloud file/data resources:
1. installed native connector/plugin/action or exact file/data API;
2. direct mounted/local file access when the exact governed file is already available to the active surface;
3. official provider API/SDK;
4. official CLI or PowerShell when appropriate to the target and host;
5. structured browser/DOM automation;
6. visual UI/Computer Use.

On Windows Codex for Microsoft 365/Azure administration with verified terminal capability, PowerShell 7 is the first candidate before browser/UI. For ordinary file/data retrieval, a working connector/API/direct-file route outranks opening Excel/SharePoint/Teams/GitHub in the browser.

Visual UI is allowed only with a factual reason code from `INC_MACHINE_ROUTE_BEFORE_VISUAL_UI_V1`, after higher-priority attempts/outcomes are recorded. UI remains valid for rendering/visual-acceptance checks, interactive consent/authentication that genuinely requires UI, or when all higher structured routes are unavailable/unsupported/failed with evidence.

Failure code: `VISUAL_UI_SELECTED_BEFORE_MACHINE_ROUTE_EXHAUSTION`.

## 2.2 Document-class SharePoint-only storage — HARD GATE
Contract: `INC_G1_DOCUMENT_CLASS_STORAGE_V1` at `references/document-class-storage-contract-v1.yaml`.

Durable human/business document binaries, including DOC/DOCX, XLS/XLSX/XLSM, PDF, PPT/PPTX and equivalent semantic document/report binaries, MUST use governed SharePoint as the only canonical storage authority.

For these document-class binaries:
- current normative/runtime GitHub storage is prohibited;
- GitHub may store source/generator code and lightweight SharePoint pointer/provenance metadata only;
- pointer metadata MUST reference the SharePoint object and provenance and MUST NOT embed document bytes/base64/inline file payloads;
- SharePoint write, remote read-back, size/hash/content-identity verification and verified SharePoint link are mandatory before success;
- historical Git evidence is preserved; history rewrite/force-purge requires a separate explicit owner-approved destructive migration.

Software/installable packages, source code and generator code remain governed by their own G1/G14 routes and are not reclassified as document-class merely because they are binary.

Failure states include `G1_DOCUMENT_CLASS_GITHUB_STORAGE_FORBIDDEN`, `G1_DOCUMENT_POINTER_SHAREPOINT_REF_REQUIRED`, `G1_DOCUMENT_POINTER_PROVENANCE_REQUIRED` and `G1_DOCUMENT_POINTER_EMBEDDED_BYTES_FORBIDDEN`.

## 3. Temporary artifacts are remote too
Temporary, draft, ad-hoc and disposable files do not receive a local exemption. They go to a governed remote `Temporary` namespace/folder resolved by G1 and carry lifecycle/cleanup metadata. Minimum temporary record: `artifact_id`, `transaction_id`, classification, creation time, cleanup/review policy, canonical remote link and read-back status.

A connector-required local/sandbox buffer may exist only as transient transport state. It is not a user artifact, authority, archive, backup or completion evidence.

Missing temporary lifecycle metadata fails `TEMPORARY_REMOTE_LIFECYCLE_MISSING`.

## 4. Project artifact egress
For every project-bound execution, 100% of durable generated/modified artifacts must be accounted before terminal success. Producer responsibilities are project resolution, complete delta discovery, Artifact Ledger registration, classification and handoff. G1 owns canonical routing, remote publication/preservation, read-back and reconciliation.

Durable includes final/user-deliverable/reusable/source/deployment/recovery/evidence/audit files of any relevant extension. Document-class binaries such as DOCX/PDF/XLSX/PPTX route SharePoint-only under `INC_G1_DOCUMENT_CLASS_STORAGE_V1`; code/JSON/YAML/XML/scripts/generator sources and software/installable packages follow their applicable governed GitHub/SharePoint routes. Every managed Skill publication requires its current installable ZIP.

A durable-looking artifact in temp/cache is `REVIEW` unless a valid exclusion exists. `UNACCOUNTED=0` is mandatory. Failures include `NEEDS_PROJECT_BINDING` and `ARCHIVE_COMPLETENESS_FAILED`.

## 5. Deterministic GitHub routing and binary publication
Resolve repository paths from governed routing/taxonomy registries; arbitrary fallback is prohibited. Metadata/README/manifest never substitutes for the actual artifact.

Binary publication uses binary-safe transport. Verify canonical remote path, filename, size and fresh SHA-256 read-back; ZIPs reopen cleanly. Document-class Office/PDF artifacts are published to SharePoint only and require exact byte preservation plus SharePoint read-back. GitHub publication of their document bytes is prohibited; GitHub pointer/provenance records are allowed. Fail closed on transport/read-back/hash mismatch.

Repository package and GitHub Release/Release Asset are distinct distribution surfaces. Core accepted-release identity is provider-neutral and is established by the governed release manifest, source/package identity, required G12/G13 certification and governed remote read-back. A GitHub tag/Release/Asset is required only when an explicit distribution profile or user requirement selects that channel; otherwise it is `N/A_WITH_REASON` and cannot block core Skill release. Canonical source, sibling `deploy/`, current installable ZIP and registry reconciliation remain required where applicable.

For ChatGPT managed-Skill install ZIPs, G1 remains the publication guard. Require fresh G14 evidence for the exact final ZIP proving `final_zip_size_bytes < 25_000_000` and matching filename/hash. Missing/oversize evidence fails `INSTALLABLE_PACKAGE_SIZE_LIMIT_EXCEEDED`; return to G14 before publication.

## GitHub publication boundary
Apply `INC_GITHUB_USAGE_BOUNDARY_V1`. GitHub remains authoritative for applicable versioned source/config/governance, but GitHub Actions and Runner are never implicit publication prerequisites. GitHub Release, tag and Release Asset are optional distribution-channel obligations unless explicitly selected. Failure of an optional GitHub distribution surface must be reported against that surface only and MUST NOT downgrade a separately certified and remotely reconciled core release.

## 6. Canonical SharePoint authority
Every G1-managed SharePoint write descends from the exact governed root defined by `INC_SHAREPOINT_BACKUP_REGISTRY_V1`. Authorized namespaces remain `Ecosystem`, `Projects`, `Shared` and G1 control-plane `_Control`.

Callers supply semantic identity/classification, never arbitrary physical destination. Non-empty caller destination/path overrides fail `CALLER_SHAREPOINT_DESTINATION_OVERRIDE_FORBIDDEN` before mutation.

Canonical durable resolution remains:
- managed Skill -> `Ecosystem/Skills/<canonical-skill-name>`;
- project Release -> `Projects/<project>/Release`;
- project Documentation -> `Projects/<project>/Documentation`; document-class binaries under this semantic route are SharePoint-only canonical artifacts;
- project Evidence/history/recovery -> `Projects/<project>/Evidence/...`;
- shared durable artifact -> `Shared/<topic>/...`.

Temporary remote placement is also resolved by G1 beneath an authorized governed namespace and never by arbitrary caller path. Verify Site/Drive/root identity before mutation and ancestry after writes/moves.

## 7. Canonical lineage, preservation and version authority
Each managed Skill has exactly one canonical SharePoint lineage. Competing lineages fail `CANONICAL_BACKUP_AUTHORITY_CONFLICT`.

Managed Skill binaries nested in unrelated project/recovery artifacts are forbidden by default. Only explicit governed bundle/DR exceptions are allowed and never create second authority.

GitHub/SharePoint version identity must reconcile. Same version+same SHA is idempotent; same version+different SHA fails immutability. Canonical Skill SharePoint retention is one Current plus maximum one Previous under Archive unless a separately governed retention contract says otherwise.

Never delete the only known-good copy before replacement is remotely verified. Destructive rotation/move/delete requires inventory/dry-run/rollback/read-back and concurrency freshness evidence.

## 8. Backlinks and cross-system evidence
SharePoint-backed artifacts must be bidirectionally navigable. For document-class binaries, GitHub stores pointer/provenance metadata only: SharePoint link/stable ID, read-back identity/hash/size and lineage; it never embeds the document bytes. GitHub evidence records SharePoint link/stable ID/read-back/retention; SharePoint lineage records GitHub canonical path/commit/release provenance. Evidence is bound to the active transaction and must be fresh.

Maintain an acyclic lineage from Producer Output -> Artifact Ledger -> GitHub artifact/commit -> optional Release -> optional SharePoint -> optional external evidence. Required dangling/missing/cyclic nodes fail `LINEAGE_GRAPH_INVALID`.

## 9. Security, capability, idempotency and concurrency
Before publication scan for credentials/private keys/unsafe secrets and sensitive transfer hazards. G8 floors cannot be bypassed.

Preflight required capabilities before mutation. Missing mandatory capability fails before partial mutation when possible.

Every operation has transaction identity/idempotency key. Exact content already at canonical path is a verified no-op. Artifact Ledger transitions are append-only/hash chained. Canonical lineage mutations require safe concurrency/lock semantics appropriate to the surface.

## 10. Recovery assurance
A recovery package is not proven by upload alone. Verify manifest/payload hashes, provenance and, when required, restore extraction and restored-byte verification. Progression remains `BACKUP_CREATED -> BACKUP_HASH_VERIFIED -> BACKUP_RESTORE_TESTED -> RESTORED_PAYLOAD_HASH_VERIFIED -> RECOVERY_PROVEN`.

## 11. Transaction closure and branch lifecycle
A pushed branch/open PR is not completion. Reconcile current authoritative `main`; require all intended changes committed/pushed/merged as applicable, final `main` read-back, required Release artifacts, and zero current-transaction residue.

Only residue proven to belong to the current transaction may be auto-cleaned. Historical branch residue is separately governed; never weaken repository protection merely to force cleanup.

## 12. Completion semantics
For document-class binaries, `SUCCESS_VERIFIED` requires SharePoint write/read-back/identity verification plus a verified SharePoint link; a GitHub binary write is forbidden and cannot be part of success. If both GitHub and SharePoint are required for a non-document artifact, `SUCCESS_VERIFIED` requires both remote writes and both read-backs. One verified/one failed is `PARTIAL`; neither verified is `FAILED`.

For every user-deliverable artifact, terminal success additionally requires a verified canonical remote link. A local path or inline body is not the deliverable.

## 13. Critical controls
Existing G1 controls remain in force. Add:
- `G1-CC-11` — exact-final ChatGPT install ZIP G14 evidence proves `<25,000,000` bytes before publication.
- `G1-CC-12` — generated user-deliverable document/artifact is remotely persisted/read back and delivered by verified link; Windows/local/inline-only completion is prohibited.
- `G1-CC-13` — temporary generated artifacts use governed remote Temporary placement plus cleanup/lifecycle metadata; local temporary classification is not an exemption.
- `G1-CC-14` — governed file/data work uses machine-readable routes before visual UI; UI fallback requires an admissible reason and prior-route evidence.
- `G1-CC-15` — durable document-class binaries use SharePoint-only canonical storage; current normative/runtime GitHub document-byte storage is forbidden. Evidence required: `YES`.
- `G1-CC-16` — any GitHub record for a document-class artifact is pointer/provenance only, contains a verified SharePoint ref, and embeds no document bytes. Evidence required: `YES`.

Mandatory FAIL overrides any score.

## 14. Required tests
In addition to existing routing/binary/SharePoint/security/idempotency/recovery/branch/size cases, test at least:
1. Windows path requested as final artifact destination -> BLOCK;
2. sandbox/local-only final file -> BLOCK;
3. file requested but only inline Chat body returned -> BLOCK;
4. temporary artifact written locally as authority -> BLOCK;
5. remote Temporary + cleanup metadata + read-back link -> PASS;
6. connector transient buffer followed by verified remote persistence and no local-authority claim -> PASS;
7. wrong/unverified remote link -> BLOCK;
8. existing `<25MB` boundary regression remains PASS/BLOCK as specified;
9. SharePoint/Excel read with working connector/API/direct-file route but visual UI selected first -> BLOCK;
10. visual-only acceptance after structured data work -> PASS;
11. durable DOCX/XLSX/PDF/PPTX sent to GitHub as binary -> BLOCK;
12. durable document written to SharePoint + read-back/hash + verified link -> PASS;
13. GitHub pointer with SharePoint ref/provenance and no document bytes -> PASS;
14. GitHub pointer with embedded/base64 document payload -> BLOCK.

Before final release, repeat verification on the same immutable candidate/package according to G12/G13/G14/G1 release policy.

## 15. Stop condition
Stop only when all applicable artifact egress, remote persistence/link, security, lineage, publication/preservation and transaction-closure gates are verified, or when the exact blocked/partial state is recorded. No local-only, Windows-only, inline-only, arbitrary SharePoint fallback, fake link, manifest-only success or unsupported completion claim is allowed.

## Mandatory G16 cross-surface generation gate
Contract: `INC_G16_CROSS_SURFACE_EXECUTION_DELIVERY_V1`.

When this Skill generates a prompt, instruction, work order, Handoff, report, command file, execution artifact, or operational file intended for another Chat/Work/Codex/agent surface, it MUST resolve/apply latest G16 before generation. No G16 => `BLOCKED_G16_NOT_APPLIED`.

Administrative/infrastructure execution MUST follow: PowerShell -> official API -> official CLI -> structured browser/connected tool -> visual UI. On Windows Codex with verified direct terminal capability, PowerShell 7 is the mandatory first candidate. Lower-priority fallback requires an approved reason code.

Generated cross-surface artifacts MUST follow the G1 class route: durable document-class binaries persist to governed SharePoint only; other governed artifacts use their applicable GitHub/SharePoint route. All require remote read-back and verified link or stable reference. Direct local/sandbox file delivery, direct cross-surface attachment, or inline full-file delivery as a substitute for governed publication is prohibited. Secrets/MFA/credentials never enter prompts, Handoffs, logs, or generated handoff artifacts.

## Release coordination storage boundary — HARD GATE
For SkillForge release coordination, route live mutable Handoff/work-ledger records to governed SharePoint and keep source/backlog/specification/release manifests in GitHub. Do not create one SharePoint file per checkpoint; preserve one canonical Handoff and one active ledger per release. Document/binary/media delivery continues to follow the SharePoint governed destination rules. High-volume operational event history is not a document-routing workload and belongs to G11/G17 structured stores.
