---
name: g13-skill-quality-sqs-evaluator
description: Evidence-based Skill Quality Score evaluator with hard-gate overrides,
  Build-Time/Runtime separation and explicit overbuilding/underexecution penalties.
metadata:
  stable_id: O6-SKL-013
  visible_id: G13
  display_name: G13-Skill Quality & SQS Evaluator
  version: 3.3.3
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

# G13-Skill Quality & SQS Evaluator v3.3.3 - Released
## Purpose
Provide an independent, evidence-based Skill Quality Score (SQS) without allowing a numeric score to override hard governance failures.

## Decision bands
- `SQS >= 90`: approve only if all hard gates pass.
- `85–89`: conditional approval with explicit remediation.
- `<85`: reject/remediate.
Any unresolved security, integrity, approval, dependency, canonical deploy, release obligation or DPGA hard-gate failure overrides the score.

## Evaluation dimensions
Assess requirement coverage, semantic correctness, BT/RT separation, runtime efficiency, dependency hygiene, test adequacy, security/privacy, logging/notification integration, structure/metadata, naming/versioning/IP, deployment/preservation and evidence traceability.

Penalize both underexecution and overbuilding: missing required behavior is a defect; unnecessary modules, recursive governance loading, redundant evaluators, unjustified files or excessive context are also quality defects.

G13 cannot self-approve its own changes and must distinguish deterministic/static evidence, simulated runtime evidence and live external verification.

## GitHub overbuilding check
Apply `INC_GITHUB_USAGE_BOUNDARY_V1`. Treat unnecessary GitHub Actions workflows, runner dependencies, required status checks, GitHub Release/Asset obligations, public-repository requirements or GitHub runtime calls as overbuilding when no explicit applicability exists. Their absence cannot reduce SQS when the selected profile is `SOURCE_COORDINATION_ONLY`; conversely, an explicitly required GitHub capability must have appropriate evidence and cannot be silently skipped.

## Runtime
Runtime evaluation is conditional on material acceptance, regression, release or explicit audit; it is not loaded for every ordinary invocation.

## Gates
`DPGA_COMPLETE`, `GOVERNANCE_PROPAGATION_COMPLETE`, `SQS_EVIDENCE_COMPLETE`.

## Critical Control Checklist — Runtime Exit Gate
Immediately after the governed activity and before terminal success, evaluate every applicable control below. Record `PASS | FAIL | N/A`; mandatory `FAIL` blocks `SUCCESS_VERIFIED`; `N/A` requires a reason; evidence-required PASS requires a stable evidence reference.

Ordinary low-risk execution performs this compact self exit check. Release/publication, destructive or irreversible work, high-consequence security/legal/financial/data-integrity actions, explicit certification, conflicting evidence, or a previously failed control also require an independent G12/G13 double-check.

- `G13-CC-01` — No SQS score overrides an unresolved security, integrity, approval, dependency, deploy, release or DPGA hard gate. Mandatory: `YES`. Evidence required: `YES`.
- `G13-CC-02` — Static, simulated and live-external evidence are distinguished truthfully. Mandatory: `YES`. Evidence required: `YES`.
- `G13-CC-03` — Both missing required behavior and unnecessary overbuilding/runtime overhead are scored as quality defects. Mandatory: `YES`. Evidence required: `NO`.
- `G13-CC-04` — Evaluator does not self-approve its own governed change when independent validation is required. Mandatory: `YES`. Evidence required: `YES`.

Runtime exit gate: `CRITICAL_CONTROLS_VERIFIED`. Build-Time compilation gate: `CRITICAL_CONTROLS_COMPILED`.
## G3 Global-Assurance Hard Gate
`GLOBAL_CRITICAL_CONTROLS_VERIFIED` is non-overridable by SQS. Evaluate the compact vector `local | security | optimization | logging | notification | archive`. Missing required controls, silent omission, or missing required evidence blocks approval regardless of numeric score. Avoidable repeated model/tool calls, excessive context, noisy notifications and verbose unnecessary logs are also quality defects.

## Mandatory G16 cross-surface generation gate
Contract: `INC_G16_CROSS_SURFACE_EXECUTION_DELIVERY_V1`.

When this Skill generates a prompt, instruction, work order, Handoff, report, command file, execution artifact, or operational file intended for another Chat/Work/Codex/agent surface, it MUST resolve/apply latest G16 before generation. No G16 => `BLOCKED_G16_NOT_APPLIED`.

Administrative/infrastructure execution MUST follow: PowerShell -> official API -> official CLI -> structured browser/connected tool -> visual UI. On Windows Codex with verified direct terminal capability, PowerShell 7 is the mandatory first candidate. Lower-priority fallback requires an approved reason code.

Generated cross-surface artifacts MUST be persisted to governed GitHub/SharePoint under G1/G17 placement, verified by remote read-back, and transferred only by verified remote link or stable reference. Direct local/sandbox file delivery, direct cross-surface attachment, or inline full-file delivery as a substitute for governed publication is prohibited. Secrets/MFA/credentials never enter prompts, Handoffs, logs, or generated handoff artifacts.

## Independent frozen-artifact certification — HARD GATE
Certify evidence for the exact artifact digest already validated by G12. Do not accept a rebuilt artifact under the same release identity. Confirm executor-neutral CI attestation integrity, build-once provenance, scope-lock/lease evidence and that promotion will use the same certified digest. Independence remains mandatory even when CI execution occurred locally in Codex.

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

Privacy responsibility: A quality score cannot compensate for a failed privacy or unknown-surface gate.

## Private installation and user-specific parameterization — SkillForge 3.0.4
The distributable contains no owner-specific service IDs, credential values, site/folder URLs, tenant IDs, or private evidence. Use `config/setup-service-catalog.json` and `setup/CHATGPT_FIRST_RUN.md` for the setup plan. Resolve configuration through a user-authorized private external profile, pinned by exact SHA-256; validate current connector identity/permissions/readback for every real action. Missing bindings must produce a read-only/configuration-needed result, never invented values or silent mutation. G20 is a separate setup-runtime candidate; this is not a claim of automatic ChatGPT plugin execution. Public feedback remains OFF until a particular sanitized payload and destination receive explicit owner permission.
Relevant optional service families: `LOCAL_ONLY`.
