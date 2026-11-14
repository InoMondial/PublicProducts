---
name: g16-live-shared-record-agent-coordination
description: Govern durable execution and progress reporting for executable Handoffs
  and inter-agent work orders, including one executor; coordinate multiple Chat, Work,
  Codex or other verified surfaces using one manager, append-only shared evidence,
  bounded retries and safe resume.
metadata:
  stable_id: G16-SKL-001
  visible_id: G16
  display_name: G16-Live Shared Record Agent Coordination
  version: 0.1.21
  lifecycle: production
  framework_id: INC_SKILLFORGE
  framework_membership: MEMBER
  governance_owner: INOMondial Inc.
  legacy_aliases:
  - G16-Conversation Continuity & Handoff
  human_output_governor_ref: CHAT1-SKL-001
  human_output_target_visible_id: G18
  skillforge_feedback_intake_ref: INC_SKILLFORGE_FEEDBACK_INTAKE_V1
  owner_backlog_coverage_ref: INC_OWNER_CONVERSATION_BACKLOG_COVERAGE_V1
---

## Current release policy (PRIOR_RELEASE)
For release/build/promotion decisions, use `INC_AUTONOMOUS_RELEASE_ACCEPTANCE_V1`
at `../g0-skill-architect-builder/references/autonomous-release-policy-v1.md`. Available local/API/plugin/simulation tests are required;
unavailable third-party/runner/user/native-host assurance is optional and nonblocking.
This supersedes conflicting release-only clauses below or in detailed references.
Security, authorization, integrity and truthful runtime evidence remain mandatory.


# g16-live-shared-record-agent-coordination - compact activity router

## Authority and evidence boundary
This entrypoint remains the sole activation authority. Read only the sections required
for the present operation in `references/detailed-governance.md`; that file preserves
the full normative contract, not a second executable Skill. Resolve every relative
path inside it from this Skill directory, not the references directory. System and
host instructions take precedence. Do not treat repository source, local fixtures,
profile configuration or historical PASS labels as authenticated live evidence.
A fresh review by the same executor is not independent G12/G13 certification.
Do not widen scope, create services, change credentials or invent telemetry.

## Activation
Use for executable commands, durable progress and cross-surface continuation, including
single-executor work. Ordinary conversation does not activate multi-agent orchestration.
An existing Handoff is continued only from its explicit full URL in current context.
Without one, use first-Handoff bootstrap; never select a prior record by guessed affinity.

## Minimum runtime
Before executable work read `references/durable-execution-progress-v1.md` and the
applicable sections of `references/coordination-baseline-v0.1.6.md`. Use
`scripts/execution_progress.py` for requirement mapping, weights, intent and receipts.
Persist intent before a material action; reconcile unknown outcomes; checkpoint while
control is available. Do not claim a timer can interrupt an unresponsive host.

## Handoff transaction
Use `scripts/handoff_transaction.py` as the sole S/M allocation authority. A new accepted
external user turn allocates S once. A committed semantic change allocates M once and
binds it to that S. Interrupted/transferred copies of the same turn reopen that interaction
without allocating another S. Replayed no-op state may legitimately retain its revision.
Require current remote readback and CAS or explicit single-writer coordination; do not
invent either. Bootstrap `first_interaction(..., observation=...)` requires the real host
observation, including revision, readback digest and write exclusion; it cannot manufacture
those flags. The helper validates consistency, not provider authenticity.

## Coordination and report
Path leases reject exact and parent-child overlap, expired leases, stale source and
unknown scope. Ledger appends verify the existing hash chain and identity before adding
an event. Secret keys are rejected; delta reads are bounded and return detached copies.
Use one canonical Handoff and bounded recent index; full history belongs to G11/G17.
Load detailed coordination/ledger/topology sections only when those features apply.
Before final rendering provide G18 with verified stage/percent/next-state and current
S/M receipts. Never calculate progress without acceptance evidence. Never claim live
installation or independent release certification from local tests. Real activation
requires current runtime/host authorization; profile validity alone grants nothing.


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

Privacy responsibility: Bind consent and observations to the current actor, target, artifact and interaction.

## Private installation and user-specific parameterization — SkillForge 3.0.4
The distributable contains no owner-specific service IDs, credential values, site/folder URLs, tenant IDs, or private evidence. Use `config/setup-service-catalog.json` and `setup/CHATGPT_FIRST_RUN.md` for the setup plan. Resolve configuration through a user-authorized private external profile, pinned by exact SHA-256; validate current connector identity/permissions/readback for every real action. Missing bindings must produce a read-only/configuration-needed result, never invented values or silent mutation. G20 is a separate setup-runtime candidate; this is not a claim of automatic ChatGPT plugin execution. Public feedback remains OFF until a particular sanitized payload and destination receive explicit owner permission.
Relevant optional service families: `SHAREPOINT`, `GITHUB_PRIVATE`, `LOGGING`.
