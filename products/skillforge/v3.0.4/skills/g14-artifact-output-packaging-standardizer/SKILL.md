---
name: g14-artifact-output-packaging-standardizer
description: Output and packaging governance for file-producing activities, including
  format validation, final bundle rules and canonical Skill deploy handoff.
metadata:
  stable_id: O6-SKL-014
  visible_id: G14
  display_name: G14-Artifact Output & Packaging Standardizer
  version: 3.3.2
  domain: governance
  functional_role: NORMAL
  lifecycle: production
  strictness: S3
---

## Current release policy (PRIOR_RELEASE)
For release/build/promotion decisions, use `INC_AUTONOMOUS_RELEASE_ACCEPTANCE_V1`
at `../g0-skill-architect-builder/references/autonomous-release-policy-v1.md`. Available local/API/plugin/simulation tests are required;
unavailable third-party/runner/user/native-host assurance is optional and nonblocking.
This supersedes conflicting release-only clauses below or in detailed references.
Security, authorization, integrity and truthful runtime evidence remain mandatory.

# G14-Artifact Output & Packaging Standardizer v3.3.2 - Released
## Purpose
Produce the smallest complete, validated deliverable set for activities that create files or packages.

## Build-Time
If `produces_file=false`, G14 is normally N/A. For file-producing paths, compile expected format, naming, version, ownership/NOTICE, package contents, validation method, archive/preservation class and delivery location.

Use G2 naming, G6 versioning and G5 IP rules. PDF/Office outputs must open successfully and receive layout/structure validation appropriate to the format. Large evidence/log sets are referenced rather than embedded.

Default delivery is one final file when sufficient; use a ZIP only when multiple required files form one installable/recovery/submission unit. Do not create decorative duplicate formats unless requested or required.

For managed Skills, G14 hands the validated package to G1; it does not redefine or bypass the mandatory canonical sibling `deploy/` ZIP, metadata, release and preservation gates.

### ChatGPT managed-Skill install ZIP size gate
For a ZIP intended to be uploaded/installed as a ChatGPT Skill, G14 owns the final serialized-package size gate. The governing operational constraint is owner-observed from real ChatGPT installation behavior; it is not represented as an independently documented OpenAI product limit unless official documentation is available for the transaction.

- Hard maximum: `SKILL_INSTALL_ZIP_MAX_EXCLUSIVE_BYTES = 25_000_000`.
- Required condition: `final_zip_size_bytes < 25_000_000`.
- Preparation target: `<= 24_000_000` bytes when practical, to leave transport/UI margin.
- Measure the **final serialized ZIP bytes**, after deterministic build; source-folder or uncompressed size is not acceptable evidence.
- Record exact byte size and SHA-256 in package validation evidence.

If the final ZIP is at or above the hard maximum, do not deliver or hand it to G1 as installable. Perform package slimming in this order: remove backups/history and stale temp/cache/test outputs from the install ZIP; remove duplicate or redundant evidence/docs not needed at runtime; externalize large optional/reference assets to canonical GitHub/SharePoint references with hashes where compatible; optimize compressible assets without semantic loss; then rebuild deterministically and rerun manifest/hash, clean-extract and size validation. Nested archives or disguised payloads must not be used to evade the size gate. Runtime-required functionality must not be removed merely to make the ZIP smaller.

If the package cannot be reduced below the hard maximum without losing required functionality, fail `SKILL_INSTALL_ZIP_TOO_LARGE`, stop installable publication, and require redesign/splitting plus G0 requalification when scope or architecture changes. Normative policy: `references/chatgpt-skill-install-zip-limit.yaml`.

## GitHub-independent packaging
Apply `INC_GITHUB_USAGE_BOUNDARY_V1`. Package construction, clean extraction, manifest/hash validation and installable readiness MUST be executable independently of GitHub Actions/Runner. GitHub Release/Asset packaging is an optional downstream distribution surface unless an explicit profile selects it. Public-export packaging activates only for an explicitly public distribution.

## Runtime
Runtime packaging runs only when the current activity actually produces or materially changes a deliverable. Pure analysis has no packaging runtime load.

## Integration
G2/G5/G6 provide naming/IP/version truth; G12 validates outputs; G13 scores completeness/overpackaging; G1 publishes/preserves; G11 stores stable artifact refs.

## Gates
`DPGA_COMPLETE`, `GOVERNANCE_PROPAGATION_COMPLETE`, `OUTPUT_PACKAGE_VALID`.

## Critical Control Checklist — Runtime Exit Gate
Immediately after the governed activity and before terminal success, evaluate every applicable control below. Record `PASS | FAIL | N/A`; mandatory `FAIL` blocks `SUCCESS_VERIFIED`; `N/A` requires a reason; evidence-required PASS requires a stable evidence reference.

Ordinary low-risk execution performs this compact self exit check. Release/publication, destructive or irreversible work, high-consequence security/legal/financial/data-integrity actions, explicit certification, conflicting evidence, or a previously failed control also require an independent G12/G13 double-check.

- `G14-CC-01` — Packaging runtime is active only when the activity actually creates or materially changes a deliverable. Mandatory: `YES`. Evidence required: `NO`.
- `G14-CC-02` — Produced file/package opens or validates structurally with the format-appropriate check. Mandatory: `YES`. Evidence required: `YES`.
- `G14-CC-03` — The delivered artifact set is the smallest complete set; duplicate/decorative formats are not added without need. Mandatory: `YES`. Evidence required: `YES`.
- `G14-CC-04` — Managed Skill package is handed to G1 canonical deploy/release/preservation gates and never bypasses them. Mandatory: `YES`. Evidence required: `YES`.
- `G14-CC-05` — A ChatGPT managed-Skill install ZIP is measured after final serialization and is strictly below `25_000_000` bytes; oversize packages are slimmed/rebuilt/revalidated or fail `SKILL_INSTALL_ZIP_TOO_LARGE`. Mandatory: `YES` when applicable. Evidence required: `YES`.

Runtime exit gate: `CRITICAL_CONTROLS_VERIFIED`. Build-Time compilation gate: `CRITICAL_CONTROLS_COMPILED`.

## Mandatory G16 cross-surface generation gate
Contract: `INC_G16_CROSS_SURFACE_EXECUTION_DELIVERY_V1`.

When this Skill generates a prompt, instruction, work order, Handoff, report, command file, execution artifact, or operational file intended for another Chat/Work/Codex/agent surface, it MUST resolve/apply latest G16 before generation. No G16 => `BLOCKED_G16_NOT_APPLIED`.

Administrative/infrastructure execution MUST follow: PowerShell -> official API -> official CLI -> structured browser/connected tool -> visual UI. On Windows Codex with verified direct terminal capability, PowerShell 7 is the mandatory first candidate. Lower-priority fallback requires an approved reason code.

Generated cross-surface artifacts MUST be persisted to governed GitHub/SharePoint under G1/G17 placement, verified by remote read-back, and transferred only by verified remote link or stable reference. Direct local/sandbox file delivery, direct cross-surface attachment, or inline full-file delivery as a substitute for governed publication is prohibited. Secrets/MFA/credentials never enter prompts, Handoffs, logs, or generated handoff artifacts.


## Public distribution package boundary — HARD GATE
For a generated public SkillForge distribution, G14 consumes `INC_SKILLFORGE_PUBLIC_EXPORT_POLICY_V1`, `INC_SKILLFORGE_PUBLIC_LICENSE_PROVENANCE_V1` and `INC_SKILLFORGE_PUBLIC_RELEASE_ACCEPTANCE_V1`. Packaging must preserve the exact required legal/provenance surfaces, bind the exported tree digest and reject a package missing NOTICE/third-party attribution/rights profile or containing private history/overlay material. G14 does not decide legal ownership and cannot override G5 or final G12/G13.


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

Privacy responsibility: Inspect final archives recursively, including names/comments/extra metadata.

## Private installation and user-specific parameterization — SkillForge 3.0.4
The distributable contains no owner-specific service IDs, credential values, site/folder URLs, tenant IDs, or private evidence. Use `config/setup-service-catalog.json` and `setup/CHATGPT_FIRST_RUN.md` for the setup plan. Resolve configuration through a user-authorized private external profile, pinned by exact SHA-256; validate current connector identity/permissions/readback for every real action. Missing bindings must produce a read-only/configuration-needed result, never invented values or silent mutation. G20 is a separate setup-runtime candidate; this is not a claim of automatic ChatGPT plugin execution. Public feedback remains OFF until a particular sanitized payload and destination receive explicit owner permission.
Relevant optional service families: `BACKUP`.
