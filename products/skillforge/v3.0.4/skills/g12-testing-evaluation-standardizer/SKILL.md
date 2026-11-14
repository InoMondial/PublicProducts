---
name: g12-testing-evaluation-standardizer
description: Proportional Build-Time and Runtime testing governance using deterministic-first
  evaluation, bounded retries and risk-based evaluator depth.
metadata:
  stable_id: O6-SKL-012
  visible_id: G12
  display_name: G12-Testing & Evaluation Standardizer
  version: 3.4.3
  domain: governance
  functional_role: QUALITY
  lifecycle: production
  strictness: S4
  global_assurance_contract_ref: INC_CRITICAL_CONTROL_ASSURANCE_V2
  global_assurance_skill_ref: G3
---

## Current release policy (PRIOR_RELEASE)
For release/build/promotion decisions, use `INC_AUTONOMOUS_RELEASE_ACCEPTANCE_V1`
at `../g0-skill-architect-builder/references/autonomous-release-policy-v1.md`. Available local/API/plugin/simulation tests are required;
unavailable third-party/runner/user/native-host assurance is optional and nonblocking.
This supersedes conflicting release-only clauses below or in detailed references.
Security, authorization, integrity and truthful runtime evidence remain mandatory.

# G12-Testing & Evaluation Standardizer v3.4.3 - Released
## Purpose
Require sufficient evidence for correctness without running heavy evaluators or repeated tests on simple paths.

## Build-Time
Every managed artifact gets an explicit test profile and deterministic/static checks appropriate to its class. Test only changed and critical behavior first; expand coverage on failure, high risk or certification requirements. A test marked N/A requires a reason.

Testing dimensions remain independent from artifact complexity, security class and Resource Class. Security/approval/integrity gates cannot be reduced to save resources.

## Runtime
Runtime tests execute only where behavior materially depends on live state, external systems, critical branching, destructive effects or explicit acceptance requirements. Routine deterministic/read-only paths do not invoke full evaluators.

Retries are bounded. Stop on success or no-progress. One evaluator is default; a second independent evaluator is used only for material risk, conflicting evidence, prior failure or explicit certification policy.

## Integration
G4 classifies risk; G9 budgets test/evaluator resources; G13 consumes evidence for SQS; G1 requires package/publication reconciliation; G15 reports material gate failure; G11 records compact test outcomes.

## Gates
`DPGA_COMPLETE`, `GOVERNANCE_PROPAGATION_COMPLETE`, `TEST_PROFILE_COMPLETE`.

## Critical Control Checklist — Runtime Exit Gate
Immediately after the governed activity and before terminal success, evaluate every applicable control below. Record `PASS | FAIL | N/A`; mandatory `FAIL` blocks `SUCCESS_VERIFIED`; `N/A` requires a reason; evidence-required PASS requires a stable evidence reference.

Ordinary low-risk execution performs this compact self exit check. Release/publication, destructive or irreversible work, high-consequence security/legal/financial/data-integrity actions, explicit certification, conflicting evidence, or a previously failed control also require an independent G12/G13 double-check.

- `G12-CC-01` — A proportional test profile exists and changed/critical behavior is covered. Mandatory: `YES`. Evidence required: `YES`.
- `G12-CC-02` — Deterministic/static checks run before heavier live/evaluator tests. Mandatory: `YES`. Evidence required: `YES`.
- `G12-CC-03` — Runtime/live testing is invoked only when behavior materially depends on live state/risk/acceptance. Mandatory: `YES`. Evidence required: `NO`.
- `G12-CC-04` — Retries are bounded and a second independent evaluator is used only when risk/conflict/certification requires it. Mandatory: `YES`. Evidence required: `YES`.

Runtime exit gate: `CRITICAL_CONTROLS_VERIFIED`. Build-Time compilation gate: `CRITICAL_CONTROLS_COMPILED`.
## G3 Global-Assurance Negative Tests
Build/certification testing must prove that local-control failure, unresolved G8 security, missing G9 optimization check, missing required G11 log, required G15 notification missing/misrouted/badly rendered, and required G1 publication/recovery gate failure cannot produce terminal success. Ordinary micro-runtime does not rerun the full negative suite; it executes the compact G3 exit vector.

## Mandatory G16 cross-surface generation gate
Contract: `INC_G16_CROSS_SURFACE_EXECUTION_DELIVERY_V1`.

When this Skill generates a prompt, instruction, work order, Handoff, report, command file, execution artifact, or operational file intended for another Chat/Work/Codex/agent surface, it MUST resolve/apply latest G16 before generation. No G16 => `BLOCKED_G16_NOT_APPLIED`.

Administrative/infrastructure execution MUST follow: PowerShell -> official API -> official CLI -> structured browser/connected tool -> visual UI. On Windows Codex with verified direct terminal capability, PowerShell 7 is the mandatory first candidate. Lower-priority fallback requires an approved reason code.

Generated cross-surface artifacts MUST be persisted to governed GitHub/SharePoint under G1/G17 placement, verified by remote read-back, and transferred only by verified remote link or stable reference. Direct local/sandbox file delivery, direct cross-surface attachment, or inline full-file delivery as a substitute for governed publication is prohibited. Secrets/MFA/credentials never enter prompts, Handoffs, logs, or generated handoff artifacts.

## Frozen-artifact and runner-independent CI validation — HARD GATE
Accept deterministic CI evidence from any approved executor, including local Codex, when it conforms to the repository pipeline attestation contract. Do not require GitHub Actions, a GitHub hosted runner, a self-hosted runner, a Workflow Run ID, a required status check or a Workflow Artifact unless an explicitly applicable GitHub automation profile requires that specific surface. After source freeze, validate exactly the frozen artifact digest produced by G19; any source/artifact digest change invalidates the affected validation and requires rerun. Verify scope lock, active-lease closure, release manifest, package integrity and promotion eligibility.

## GitHub test proportionality
Contract: `INC_GITHUB_USAGE_BOUNDARY_V1`.

GitHub-provider infrastructure tests are conditional. Runner availability, Actions job startup, status checks, workflow artifacts, GitHub Release objects and public repository surfaces are tested only when that capability is explicitly in the acceptance scope. Provider-neutral structural, security, digest, package, carry-forward, pairwise and semantic tests remain applicable independent of GitHub Actions.

## Publicization/export black-box validation — HARD GATE
Contract: `INC_SKILLFORGE_PUBLIC_RELEASE_ACCEPTANCE_V1` at `references/public-release-acceptance-v1.yaml`.

For a distribution whose selected visibility is explicitly `PUBLIC`, G12 binds validation to the exact frozen canonical source identity and deterministic exported tree. For `PRIVATE`, `INTERNAL` or ordinary SkillForge core release, this public-export gate is `N/A_WITH_REASON` and MUST NOT emit `REQUIRED_PUBLIC_SURFACE_MISSING`. Pre-release evidence must prove required legal surfaces, zero denied/private paths, zero secret/private-identifier findings, resolved component rights profiles, deterministic rebuild and canonical-private lineage. Unresolved ownership/license conflict, missing required attribution, private-history/private-overlay leakage or exported-tree readback mismatch is release-blocking.

Tests that genuinely require owner/cross-surface/external activation solely for assurance may remain `POST_RELEASE_ASSURANCE_PENDING` under the owner-approved deferral policy, but they are not converted to PASS. Genuine security, integrity, approval and publication/readback hard gates remain blocking. Any material export/package rebuild invalidates affected prior certification.

## SkillForge V3 private-release proportional evaluation

Under an explicit `PRIVATE_V3_RISK_PROPORTIONAL` candidate, evaluate changed critical paths and impacted interface edges rather than blanket unchanged/historical edge matrices. Require deterministic syntax/package checks, negative tests for security/data-integrity/authorization changes, exact active-contract carry-forward and a single independent G12 plus separately independent G13 certificate bound to the same final `impact_scope_sha256` and package digest. Fail closed on unknown high risk, missing verified input or stale source, never on optional absent services or unrelated user-assisted post-release exercises. This opt-in amendment does not waive production approval or independently required security gates.


## Owner PRIOR_RELEASE private simulation acceptance (2026-11-13)

For this release only, apply `../g0-skill-architect-builder/references/private-v3-simulation-acceptance-prior_release.json`
from G0. R3/R4 are completed by executed local synthetic tests, explicit contract
models/estimates, deterministic packaging, simulated install/rollback, and actual
private publication/readback. Do not wait for user execution, another machine,
a hosted runner, external compiler, or a separate evaluator. Same-executor review
is expressly permitted but MUST be labelled SIMULATION_ONLY with independence
false. This scoped profile supersedes conflicting external assurance requirements,
not security authorization, secret protection, byte integrity or truthful claims.
Normal production certification outside this profile is unchanged.


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

Privacy responsibility: Require complete semantic and byte coverage, not just legal-file presence or hashes.

## Private installation and user-specific parameterization — SkillForge 3.0.4
The distributable contains no owner-specific service IDs, credential values, site/folder URLs, tenant IDs, or private evidence. Use `config/setup-service-catalog.json` and `setup/CHATGPT_FIRST_RUN.md` for the setup plan. Resolve configuration through a user-authorized private external profile, pinned by exact SHA-256; validate current connector identity/permissions/readback for every real action. Missing bindings must produce a read-only/configuration-needed result, never invented values or silent mutation. G20 is a separate setup-runtime candidate; this is not a claim of automatic ChatGPT plugin execution. Public feedback remains OFF until a particular sanitized payload and destination receive explicit owner permission.
Relevant optional service families: `LOCAL_ONLY`.
