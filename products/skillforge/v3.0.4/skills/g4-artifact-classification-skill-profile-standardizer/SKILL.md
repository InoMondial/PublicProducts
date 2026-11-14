---
name: g4-artifact-classification-skill-profile-standardizer
description: Classify artifact type, sensitivity, lifecycle, complexity and minimum
  governance profile without conflating complexity with runtime resource class.
metadata:
  stable_id: O6-SKL-004
  visible_id: G4
  display_name: G4-Artifact Classification & Skill Profile Standardizer
  version: 3.1.2
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

# G4-Artifact Classification & Skill Profile Standardizer v3.1.2 - Released
## Purpose
Determine what an artifact is, how sensitive/critical it is, which lifecycle/complexity profile applies, and the minimum governance modules required.

## Build-Time
Classify independently: artifact type, lifecycle, sensitivity/security class, complexity `LITE|FULL|CRITICAL`, produced-file status, runtime applicability and required governance modules. Complexity is not Resource Class; G9 owns runtime resource routing. Conservative elevation is allowed for unresolved material risk, but not arbitrary overclassification.

Use the smallest sufficient module set. Build-Time always records why a module applies or is N/A. Runtime is OFF by default unless the artifact's actual activity can materially change classification.

## Runtime
Reclassify only on material change such as new sensitive data, destructive capability, new external write, substantially larger scope, or newly discovered critical dependency. Micro-steps do not trigger full reclassification.

## Integration
G0 compiles profile; G8 supplies security floors; G9 consumes independent classification; G12 derives test profile; G13 evaluates quality; G1/G14 consume artifact type and preservation/packaging implications.

## Gates
`DPGA_COMPLETE`, `GOVERNANCE_PROPAGATION_COMPLETE`, `CLASSIFICATION_PROFILE_COMPILED`.

## Critical Control Checklist — Runtime Exit Gate
Immediately after the governed activity and before terminal success, evaluate every applicable control below. Record `PASS | FAIL | N/A`; mandatory `FAIL` blocks `SUCCESS_VERIFIED`; `N/A` requires a reason; evidence-required PASS requires a stable evidence reference.

Ordinary low-risk execution performs this compact self exit check. Release/publication, destructive or irreversible work, high-consequence security/legal/financial/data-integrity actions, explicit certification, conflicting evidence, or a previously failed control also require an independent G12/G13 double-check.

- `G4-CC-01` — Artifact type, lifecycle, sensitivity/security, complexity and resource class are not conflated. Mandatory: `YES`. Evidence required: `NO`.
- `G4-CC-02` — Only the minimum sufficient governance module set is compiled with explicit applicability/N/A rationale. Mandatory: `YES`. Evidence required: `YES`.
- `G4-CC-03` — Runtime reclassification occurs only on a material classification change. Mandatory: `YES`. Evidence required: `NO`.
- `G4-CC-04` — Unresolved material risk is not underclassified for convenience or resource savings. Mandatory: `YES`. Evidence required: `NO`.

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

Privacy responsibility: Treat owner inventories and operational metadata as private unless specifically approved.

## Private installation and user-specific parameterization — SkillForge 3.0.4
The distributable contains no owner-specific service IDs, credential values, site/folder URLs, tenant IDs, or private evidence. Use `config/setup-service-catalog.json` and `setup/CHATGPT_FIRST_RUN.md` for the setup plan. Resolve configuration through a user-authorized private external profile, pinned by exact SHA-256; validate current connector identity/permissions/readback for every real action. Missing bindings must produce a read-only/configuration-needed result, never invented values or silent mutation. G20 is a separate setup-runtime candidate; this is not a claim of automatic ChatGPT plugin execution. Public feedback remains OFF until a particular sanitized payload and destination receive explicit owner permission.
Relevant optional service families: `LOCAL_ONLY`.
