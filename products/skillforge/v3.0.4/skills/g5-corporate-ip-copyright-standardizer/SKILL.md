---
name: g5-corporate-ip-copyright-standardizer
description: Govern ownership, provenance, licensing, copyright notice, attribution
  and third-party rights for managed artifacts.
metadata:
  stable_id: O6-SKL-005
  visible_id: G5
  display_name: G5-Corporate IP & Copyright Standardizer
  version: 3.2.2
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

# G5-Corporate IP & Copyright Standardizer v3.2.2 - Released
## Purpose
Preserve truthful ownership/provenance/licensing while applying corporate copyright/NOTICE requirements to INOMondial-created artifacts.

## Build-Time
Identify ownership basis and provenance before adding corporate claims. Preserve third-party copyrights, licenses, notices and attribution; never convert external evidence into corporate-owned content by renaming/repackaging. New proprietary corporate artifacts carry the approved INOMondial notice unless a different approved license applies. Open-source or mixed-license artifacts must retain compatible license/attribution evidence.

Do not claim exclusive ownership of user-provided, public-domain, licensed third-party or unknown-provenance material. Unknown material provenance creates a gate rather than a fabricated assertion.

## Runtime
Apply only when runtime creates, modifies for distribution, republishes, licenses or packages an IP-relevant artifact. Pure analysis carries the compiled IP profile only.

## Public distribution rights profiles — HARD GATE
Contract: `INC_SKILLFORGE_PUBLIC_LICENSE_PROVENANCE_V1` at `references/public-license-provenance-v1.yaml`.

SkillForge Core defaults to corporate proprietary/all-rights-reserved unless an explicit verified license applies. Community/public source distribution uses the approved source-available rights profile and MUST NOT be described as OSI open source. True open-source treatment is component-specific only after ownership, third-party rights and license compatibility are verified.

Generated Skills and public exports require a rights profile. Do not claim blanket INOMondial ownership over user-provided, customer-owned, public-domain, third-party or otherwise externally owned inputs. Canadian moral-rights handling remains separate from economic-rights assignment: an assignment alone is not treated as a moral-rights waiver. Contribution policy uses DCO only for true inbound=outbound open source; source-available/commercial models requiring relicensing need an appropriate CLA/assignment/relicensing grant.

Public/export release surfaces must preserve applicable LICENSE/rights terms, NOTICE, THIRD_PARTY_NOTICES, TRADEMARKS, CONTRIBUTING and SECURITY material. Trademark registration, TM or registered-symbol claims require verified approval. Public release remains blocked on unresolved provenance/license conflicts and release-time rights revalidation.

## Integration
G2 naming must not destroy provenance. G14 packaging preserves notices. G1 publication may not drop license/NOTICE files. G8 prevents disclosure of protected/confidential material. G11 logs material rights/provenance decisions by references, not copied content.

## Gates
`DPGA_COMPLETE`, `GOVERNANCE_PROPAGATION_COMPLETE`, `IP_PROVENANCE_VERIFIED`.

## Failure states
`PROVENANCE_UNKNOWN | LICENSE_CONFLICT | ATTRIBUTION_REQUIRED | OWNERSHIP_CLAIM_UNSUPPORTED | SUCCESS_VERIFIED`.

## Critical Control Checklist — Runtime Exit Gate
Immediately after the governed activity and before terminal success, evaluate every applicable control below. Record `PASS | FAIL | N/A`; mandatory `FAIL` blocks `SUCCESS_VERIFIED`; `N/A` requires a reason; evidence-required PASS requires a stable evidence reference.

Ordinary low-risk execution performs this compact self exit check. Release/publication, destructive or irreversible work, high-consequence security/legal/financial/data-integrity actions, explicit certification, conflicting evidence, or a previously failed control also require an independent G12/G13 double-check.

- `G5-CC-01` — Ownership/provenance basis is verified before a corporate IP claim is applied. Mandatory: `YES`. Evidence required: `YES`.
- `G5-CC-02` — Third-party copyright/license/attribution is preserved during rename, package and publication. Mandatory: `YES`. Evidence required: `NO`.
- `G5-CC-03` — Exclusive ownership is never claimed for external/public-domain/licensed/unknown material without support. Mandatory: `YES`. Evidence required: `NO`.
- `G5-CC-04` — Required NOTICE/license evidence survives packaging and G1 publication. Mandatory: `YES`. Evidence required: `YES`.

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

Privacy responsibility: Bind approved identity fields and licensing to exact owner disclosure consent.

## Private installation and user-specific parameterization — SkillForge 3.0.4
The distributable contains no owner-specific service IDs, credential values, site/folder URLs, tenant IDs, or private evidence. Use `config/setup-service-catalog.json` and `setup/CHATGPT_FIRST_RUN.md` for the setup plan. Resolve configuration through a user-authorized private external profile, pinned by exact SHA-256; validate current connector identity/permissions/readback for every real action. Missing bindings must produce a read-only/configuration-needed result, never invented values or silent mutation. G20 is a separate setup-runtime candidate; this is not a claim of automatic ChatGPT plugin execution. Public feedback remains OFF until a particular sanitized payload and destination receive explicit owner permission.
Relevant optional service families: `LOCAL_ONLY`.
