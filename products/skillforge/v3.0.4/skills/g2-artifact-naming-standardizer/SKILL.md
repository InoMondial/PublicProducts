---
name: g2-artifact-naming-standardizer
description: Canonical naming governance for managed artifacts, files, Skills, versions,
  evidence and deployment packages, including truthful framework display identity.
metadata:
  stable_id: O6-SKL-002
  visible_id: G2
  display_name: G2-Artifact Naming Standardizer
  version: 3.2.2
  domain: governance
  functional_role: NORMAL
  lifecycle: production
  strictness: S3
  governance_owner: INOMondial Inc.
  builder_framework_ref: INC_SKILLFORGE
  framework_id: INC_SKILLFORGE
  framework_name: SkillForge
  framework_membership: MEMBER
  framework_registry_ref: INC_SKILL_NAMESPACE_REGISTRY
  framework_membership_contract_ref: INC_SKILL_FRAMEWORK_MEMBERSHIP_V1
---

## Current release policy (PRIOR_RELEASE)
For release/build/promotion decisions, use `INC_AUTONOMOUS_RELEASE_ACCEPTANCE_V1`
at `../g0-skill-architect-builder/references/autonomous-release-policy-v1.md`. Available local/API/plugin/simulation tests are required;
unavailable third-party/runner/user/native-host assurance is optional and nonblocking.
This supersedes conflicting release-only clauses below or in detailed references.
Security, authorization, integrity and truthful runtime evidence remain mandatory.

# G2-Artifact Naming Standardizer v3.2.2 - Released
## Purpose
Compile deterministic, collision-safe names and truthful visible framework identity for managed artifacts without renaming third-party evidence, inventing framework membership or violating platform-reserved filenames.

G2 is a canonical SkillForge Governance Skill because that membership resolves from `INC_SKILL_NAMESPACE_REGISTRY`. The word `Skill`, repository location, builder provenance or naming similarity is never sufficient to make another Skill a SkillForge member.

## Build-Time rules
- Preserve Stable ID as identity; visible labels and filenames may evolve.
- Resolve serials and canonical names from authoritative registries; never invent a serial when registry authority exists.
- Resolve framework membership from `INC_SKILL_NAMESPACE_REGISTRY` / `INC_SKILL_FRAMEWORK_MEMBERSHIP_V1`; never from name/substrings or repository path.
- `MEMBER` may use the canonical framework title on suitable human-facing surfaces; for this framework the canonical title is `SkillForge`.
- `CANDIDATE_MEMBER` may be described as a SkillForge Candidate only when candidate state is explicitly governed; it must not claim canonical MEMBER.
- `EXTERNAL` relative to SkillForge must not inherit SkillForge member branding merely because SkillForge built, tested or packaged it. `builder_framework_ref: INC_SKILLFORGE` is provenance, not membership.
- Platform-reserved filenames such as `SKILL.md`, `MANIFEST.json`, `NOTICE.md`, `GOVERNANCE.yaml` and required deploy metadata override cosmetic naming preferences.
- Generated deliverables use deterministic artifact-type, semantic-name, version and date conventions appropriate to their class.
- Third-party/source evidence keeps its original filename unless an explicit governed copy is required; provenance must remain intact.
- Detect case-insensitive/path collisions before publication. Resolve deterministically when policy permits; otherwise return a concise collision gate.

## SkillForge display rule
For a Registry-backed SkillForge MEMBER, G2 permits/compiles visible `SkillForge` identity where the surface benefits from framework context, including Skill human documentation, governed package/release metadata and ecosystem reports. Do not replace or obscure the registered G-number/display identity.

Examples:
- `G2-Artifact Naming Standardizer — SkillForge` is valid contextual display wording.
- An external `PFA1-...` Skill built using SkillForge may record builder provenance but must not be renamed to imply that PFA is a SkillForge Governance member.
- A not-yet-canonical G16 continuity Candidate must not be labeled canonical MEMBER until Registry acceptance.

## Runtime
Runtime naming applies only when the activity actually creates, renames, versions, labels or packages an output. Pure read/analyze paths carry only the compiled naming/profile reference.

## Cross-cutting propagation
G0 compiles applicability and membership resolution; G7 owns machine-readable membership metadata; G4 supplies artifact class; G6 supplies lifecycle/version; G1 consumes the final canonical name for publication; G14 packages without changing naming truth; G11 logs only material naming/version events.

## DPGA gates
`DPGA_COMPLETE`, `GOVERNANCE_PROPAGATION_COMPLETE`, `NAMING_PROFILE_COMPILED`, `FRAMEWORK_DISPLAY_IDENTITY_VALID`.

## Failure states
`NAMING_CONFLICT | REGISTRY_SERIAL_REQUIRED | RESERVED_FILENAME_VIOLATION | PROVENANCE_NAME_PROTECTED | FRAMEWORK_MEMBERSHIP_MISLABEL | SUCCESS_VERIFIED`.

## Critical Control Checklist — Runtime Exit Gate
Immediately after the governed activity and before terminal success, evaluate every applicable control below. Record `PASS | FAIL | N/A`; mandatory `FAIL` blocks `SUCCESS_VERIFIED`; `N/A` requires a reason; evidence-required PASS requires a stable evidence reference.

Ordinary low-risk execution performs this compact self exit check. Release/publication, destructive or irreversible work, high-consequence security/legal/financial/data-integrity actions, explicit certification, conflicting evidence, or a previously failed control also require an independent G12/G13 double-check.

- `G2-CC-01` — Stable ID/history is preserved while visible names and filenames evolve. Mandatory: `YES`. Evidence required: `NO`.
- `G2-CC-02` — Serial/canonical name is resolved from authoritative naming state when available; it is not invented. Mandatory: `YES`. Evidence required: `YES`.
- `G2-CC-03` — Reserved platform filenames and third-party provenance filenames are preserved. Mandatory: `YES`. Evidence required: `NO`.
- `G2-CC-04` — Case/path collision checks pass before publication. Mandatory: `YES`. Evidence required: `YES`.
- `G2-CC-05` — SkillForge framework display is used only for Registry/metadata-resolved MEMBER/CANDIDATE contexts and cannot cause an EXTERNAL Skill to self-identify as a SkillForge member. Mandatory: `YES` when framework identity is displayed. Evidence required: `YES`.

Runtime exit gate: `CRITICAL_CONTROLS_VERIFIED`. Build-Time compilation gate: `CRITICAL_CONTROLS_COMPILED`.

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

Privacy responsibility: Inspect public filenames, labels and identifiers for owner information.

## Private installation and user-specific parameterization — SkillForge 3.0.4
The distributable contains no owner-specific service IDs, credential values, site/folder URLs, tenant IDs, or private evidence. Use `config/setup-service-catalog.json` and `setup/CHATGPT_FIRST_RUN.md` for the setup plan. Resolve configuration through a user-authorized private external profile, pinned by exact SHA-256; validate current connector identity/permissions/readback for every real action. Missing bindings must produce a read-only/configuration-needed result, never invented values or silent mutation. G20 is a separate setup-runtime candidate; this is not a claim of automatic ChatGPT plugin execution. Public feedback remains OFF until a particular sanitized payload and destination receive explicit owner permission.
Relevant optional service families: `LOCAL_ONLY`.
