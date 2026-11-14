> Release precedence: `INC_AUTONOMOUS_RELEASE_ACCEPTANCE_V1` in the current entrypoint supersedes historical separate-evaluator, runner and user/native-install release-only prerequisites below. Runtime safety and truthful evidence are unchanged.

# Detailed governance - load applicable sections only

Relative paths resolve from the parent Skill root. The SKILL.md entrypoint is the activation authority.

# G16 - durable execution and coordination candidate

## Required profiles

Before substantive governed execution, read:

1. `references/durable-execution-progress-v1.md` for every executable Handoff or
   governed command, including single-executor commands.
2. `references/coordination-baseline-v0.1.6.md` for the existing coordination,
   delivery, shared-record, surface/model-advice, artifact and safety requirements.
   This file preserves the complete prior entrypoint bytes. Resolve its relative
   reference paths from the G16 Skill root, not from the references subdirectory.
   Its historical frontmatter is lineage, not another executable authority.

The current entrypoint and governance/manifest version is 0.1.18-candidate. The
baseline's single-agent exclusion applies only to STAR multi-agent coordination;
it does not exempt a single executor from durable command state and reporting.
All prior security, owner-approval, model-selection, execution-surface, machine-route,
remote-artifact, G12/G13 and human-output constraints remain applicable. Do not create
a second agent, change a model, buy a service or claim host capabilities to satisfy
this profile. Platform/system/developer instructions take precedence.

## Execution gate

Every generated execution-ready instruction must carry the original mandatory G16
and CHAT1 activation envelope plus:

```text
- APPLY_DURABLE_EXECUTION_PROGRESS=true
- DURABLE_EXECUTION_CONTRACT=INC_G16_DURABLE_EXECUTION_PROGRESS_V1
- WEIGHTED_PLAN_REQUIRED=true
- WRITE_AHEAD_INTENT_REQUIRED=true
- REPORT_AFTER_EXECUTION_REQUIRED=true
- RESUME_FROM_REMOTE_STATE_ONLY=true
```

Require a stable command/root/actor identity, complete requirement-to-step mapping,
versioned weights and acceptance milestones, durable journal/projection/report
references and an exact resume point. Missing fields make a work order incomplete,
not execution-ready. Pin the applicable profile digest; avoid reloading unchanged
full governance on every operation.

Use `scripts/execution_progress.py` before material actions and for event reduction
and report calculation. Actual adapters must supply verified clock, permission,
single-writer/CAS, remote revision, source digest and read-back observations. The
script is a cooperative consistency gate, not an authenticated provider or a
watchdog that can interrupt a dead host.

Checkpoint by eight minutes or twelve material actions while control is available.
Use a fifteen-minute no-progress circuit and twenty-five-minute slice bound, three
attempts per operation, two identical errors and six root no-progress attempts.
Read/research actions count. Persist counters across child splits and resumes; a new
child name must not reopen an exhausted route. Before a long call, checkpoint and
verify its native timeout/job handle; document unsupported enforcement truthfully.

Persist intent before mutation, reconcile any unknown outcome before retry, verify
acceptance, then commit the checkpoint receipts. Use one canonical event-derived
state; read-only mirrors must agree. Repair a partial journal/projection write
before another side effect. Do not describe separate remote writes as one atomic
transaction. Without provider CAS, allow only one explicitly coordinated writer.

## GitHub coordination boundary
Contract: `INC_GITHUB_USAGE_BOUNDARY_V1`.

GitHub may provide source SHA, branches, pull requests, diffs and durable provenance for coordinated work. It is not the canonical mutable Handoff/work-ledger authority and GitHub Actions/Runner is not a substitute for Chat/Work/Codex semantic execution. A source repository connection does not authorize creating Actions workflows, runners, GitHub Releases or runtime state. Such capabilities require explicit applicability.

## Universal SkillForge feedback intake runtime adapter — ABSOLUTE HARD GATE

Contract: `INC_SKILLFORGE_FEEDBACK_INTAKE_V1`.
Runtime core: `scripts/skillforge_feedback_intake.py`.

For any Skill built or materially upgraded by SkillForge, accept bounded framework-feedback events without recursively loading G0. Preserve `SYSTEM_DISCOVERED` vs `USER_DIRECT`, derive `SYSTEM_EVIDENCE | USER_REQUEST | OWNER_MANDATE`, and keep authority separate from P0-P3 impact/urgency priority.

Before creating a new intake, aggregate by dedupe key. If a prior system finding receives a later owner mandate, preserve both origins/evidence and promote authority to OWNER_MANDATE in the same canonical item. Never downgrade an owner mandate.

If direct canonical write is unavailable, persist/return only `PENDING_CANONICAL_INGESTION`. A runtime may report `CANONICAL_REGISTERED` only after canonical read-back proves Change ID, origin lineage, authority, priority, source Skill/version and dedupe result.

Interaction events should carry feedback-intake receipt references and backlog-relevant decision IDs so G0 can produce `INC_OWNER_CONVERSATION_BACKLOG_COVERAGE_V1` at terminal backlog-maintenance close.

## First-Handoff bootstrap — ABSOLUTE HARD GATE

Profile: `FIRST_HANDOFF_BOOTSTRAP_V1` under `INC_G16_HANDOFF_TRANSACTIONAL_WRITER_V1`.
Core: `scripts/handoff_bootstrap.py`.

A prior Handoff may be continued only when its full Handoff URL is explicitly present in the current Chat/Work/Codex conversation or instruction payload. Project binding, memory, registry lookup, matching project title, bare Handoff ID, prior unrelated surface state or inferred continuity never authorize reuse.

Before substantive governed work:
1. If an explicit Handoff URL is present in the current surface context, resolve that exact URL. If it is missing, fail `G16_BOOTSTRAP_EXPLICIT_HANDOFF_URL_NOT_FOUND`; never silently replace it.
2. If no explicit Handoff URL is present, G16 MUST bootstrap a brand-new canonical Handoff for this Chat/Work/Codex context even when one or more Handoffs already exist for the same project. Existing project-bound Handoffs are ignored for write-continuation authority.
3. Do not ask the user for a Handoff code and do not auto-select an older Handoff by project affinity.
4. Generate the Handoff ID inside G16 as `HOF-<16 uppercase hex>`; callers do not invent/provide the first Handoff ID.
5. Create one internal seed state with `S:0 | M:0` using create-only/CAS or explicit single-writer exclusion. The seed is initialization state and MUST NOT be emitted as the terminal human-visible Handoff reference.
6. Read back the created object and prove exactly one canonical Handoff for the project. Only then invoke the ordinary transactional writer for the accepted external turn, producing the first visible interaction as `S:1 | M:0`.
7. If the same first turn commits project state materially, commit `M:1` through the normal transactional writer and causally bind it to `S:1`.
8. An ambiguous create outcome MUST reconcile the exact generated ID/path before retry. Never generate a second ID until the first outcome is resolved.
9. Provider access/write failure is distinct from missing-Handoff state. Only an actually unavailable/unwritable governed provider may block bootstrap as `G16_HANDOFF_BOOTSTRAP_PROVIDER_WRITE_UNAVAILABLE`.
10. The same rule applies on Chat, Work and Codex. First-Handoff creation is a framework responsibility, not a user relay step. Continuation authority is URL-explicit only.

## Canonical Handoff dual-sequence hard gate

Contract: `INC_G16_HANDOFF_DUAL_SEQUENCE_V1`.

After cutover the canonical Handoff carries two independent counters:
- `S` is the interaction sequence. Allocate it exactly once for every accepted external user turn across Chat, Work or Codex, including read-only questions, approvals, corrections and knowledge-only turns.
- `M` is the material checkpoint sequence. Increment it exactly once for every committed semantic material project checkpoint.

Hard rules:
1. On accepting an external user turn, continue an existing Handoff only from an explicit Handoff URL present in the current surface context. Without such a URL, always execute `FIRST_HANDOFF_BOOTSTRAP_V1` for a brand-new Handoff, regardless of project-bound or discoverable prior Handoffs; then allocate `S_after = S_before + 1` before substantive governed execution. Internal tools, retries, commentary and assistant messages do not allocate another S.
2. Open one interaction event keyed by S and close/update the same event on terminal response. Interrupted work resumes the same S.
3. Increment M only after a material governed project mutation is committed. Every M receipt references the causal S. Non-material turns leave M unchanged.
4. Both counters use canonical single-writer/CAS semantics. Ambiguous provider outcomes require remote reconciliation before retry.
5. The visible reference after cutover is exactly `<handoff_id> | S:<interaction_seq> | M:<material_seq>`.
6. G18 never calculates either counter. A final governed-project response requires the current-turn S receipt; if material work occurred it also requires the committed M receipt.
7. Migration preserves the legacy S value as the starting interaction baseline. M starts at 0 for the new schema epoch unless historical material count is deterministically proven; record a migration receipt and legacy baseline.
8. Cross-surface resume first reads current S, current M and unresolved OPEN/INTERRUPTED interaction events.

Failure codes: `G16_HANDOFF_S_NOT_ADVANCED`, `G16_HANDOFF_S_DUPLICATE`, `G16_HANDOFF_M_NOT_ADVANCED`, `G16_HANDOFF_S_M_CAUSAL_BINDING_INVALID`, `G16_HANDOFF_DUAL_SEQUENCE_READBACK_REQUIRED`.

## Canonical transactional Handoff writer — ABSOLUTE HARD GATE

Contract: `INC_G16_HANDOFF_TRANSACTIONAL_WRITER_V1`.
Reference: `references/handoff-transactional-writer-v1.md`.
Deterministic core: `scripts/handoff_transaction.py`.

This writer is the only semantic authority allowed to advance Handoff S/M state after dual-sequence cutover.

Hard rules:
1. Before substantive work for each newly accepted external user turn, use an existing Handoff only when its explicit URL is present in the current surface context. Otherwise bootstrap exactly one brand-new seed Handoff through `scripts/handoff_bootstrap.py`, verify create/read-back, then read that new canonical Handoff plus provider remote revision and invoke the writer to allocate S internally. Callers MUST NOT supply `next_S`.
2. If the same turn is already OPEN, INTERRUPTED or TRANSFERRED, resume the same S. A retry, tool call, progress message or surface transfer MUST NOT allocate a duplicate S.
3. A material checkpoint may advance M only through the writer, only while an interaction is OPEN, and only from an immutable tool/event ledger proving a material state change. Callers MUST NOT supply `next_M`.
4. Every M receipt MUST bind to the current causal S. A mismatched S/M relation is a hard failure.
5. Every writer mutation requires pre-write canonical readback, remote revision identity and verified CAS/If-Match or explicitly coordinated single-writer exclusion.
6. Every writer mutation requires post-write remote readback. An unchanged/unknown remote revision or ambiguous write outcome MUST be reconciled before retry; never blindly repeat the mutation.
7. Terminal response closes/updates the same interaction event and does not allocate another S or M.
8. Direct mutation of `interaction_seq`, `material_seq` or `visible_ref` outside this writer is prohibited.
9. G18 may render S/M only from a current-turn writer receipt plus post-write readback evidence.

The later cross-surface interaction-ledger work may persist full history, but it MUST consume these writer receipts rather than introduce a second counter authority.

Failure codes include `G16_TX_REMOTE_STATE_STALE`, `G16_TX_SINGLE_WRITER_OR_CAS_REQUIRED`, `G16_TX_OPEN_TURN_ALREADY_EXISTS`, `G16_TX_CAUSAL_S_MISMATCH`, `G16_TX_MATERIAL_EVIDENCE_REQUIRED`, `G16_TX_POSTWRITE_READBACK_REQUIRED`, and `G16_TX_REMOTE_REVISION_NOT_ADVANCED`.

## Canonical Handoff topology and cross-surface interaction ledger — ABSOLUTE HARD GATE

Contracts:
- `INC_G16_HANDOFF_TOPOLOGY_REGISTRY_V1` → `references/handoff-topology-registry-v1.md`
- `INC_CROSS_SURFACE_INTERACTION_LEDGER_V1` → `references/cross-surface-interaction-ledger-v1.md`

Executable cores:
- `scripts/handoff_topology.py`
- `scripts/interaction_ledger.py`

Hard rules:
1. One governed project has exactly one canonical Handoff URL. Checkpoints mutate it in place; per-checkpoint Handoff files are prohibited.
2. Each release has zero or one ACTIVE work ledger. A CLOSED release has no active ledger and exactly one immutable closure report. Multiple ACTIVE releases or duplicate active ledgers fail closed.
3. High-volume interaction history belongs to the active release ledger / G11-G17 structured store. Do not grow the canonical Handoff into an unbounded transcript database.
4. Every S allocated by the transactional writer emits exactly one immutable interaction allocation record. Lifecycle changes append records; they never rewrite history.
5. Interaction lifecycle is `OPEN | INTERRUPTED | COMPLETED | BLOCKED | TRANSFERRED`. Crash/resume and cross-surface transfer continue the same S.
6. Every record is keyed by project, Handoff, release and S; also record surface, conversation/thread reference, timestamp and causal M references.
7. Preserve structured knowledge delta: decisions, approvals/rejections, requirements, evidence refs, open questions and resume point.
8. Hash-chain the append-only ledger. Duplicate replay, duplicate S allocation, broken chain or lifecycle-without-allocation is a hard failure.
9. Apply G8-compatible classification/redaction before append. Secret replication and unnecessary verbatim transcript retention are prohibited.
10. The Handoff stores only a bounded recent index. Authorized resume retrieves only S values newer than the surface's last-seen S.
11. The interaction ledger consumes G16 transactional-writer receipts and MUST NOT become a second authority for S/M allocation.
12. Storage/provider mapping remains G17-owned and semantic logging routes through G11. G16 owns coordination semantics, not physical database schema.

Before promotion, run the topology/ledger regression suite covering duplicate Handoff/ledger detection, immutable closure, concurrent surfaces, crash/resume, transfer, duplicate replay, out-of-order completion, secret blocking and last-seen-S retrieval.

## Runtime version attestation pre-mutation gate — ABSOLUTE HARD GATE

Contract: `INC_SKILLFORGE_RUNTIME_VERSION_ATTESTATION_V1`.
Semantic owner: G0. Runtime mutation enforcement: G16. Version semantics: G6.

Before G16 allocates or commits any material governed project mutation on Chat, Work or Codex:
1. Require a current-context runtime attestation receipt bound to the present surface, runtime instance, account context and session.
2. Require `status=CONFORMING_RUNTIME` and `mutation_allowed=true`.
3. Require independent Handoff provider readback in the same attestation.
4. Reject receipts sourced only from GitHub, Handoff claims, user statements or assistant inference.
5. Re-attest after sign-out/sign-in, account switch, session/runtime replacement, surface transfer, package refresh or digest change.
6. If attestation is missing/mismatched, material M commit is prohibited. Read-only audit may continue only as `NONCONFORMING_RUNTIME_READ_ONLY` and must not allocate a material M.
7. Persist the attestation ID/status and observed/required version summary in the current interaction/checkpoint receipt.
8. An old/uninstalled G16 cannot reuse a stale S/M receipt as evidence of current enforcement.

Failure codes: `RUNTIME_ATTESTATION_REQUIRED`, `RUNTIME_ATTESTATION_MATERIAL_MUTATION_BLOCKED`, `RUNTIME_ATTESTATION_CONTEXT_STALE`, `RUNTIME_ATTESTATION_RUNTIME_PROOF_UNVERIFIED`.

## Mandatory result report

At every execution return, derive the weighted progress table from durable evidence:
step, weight, verified completion, earned contribution, remaining contribution,
state, failure position and resume point. Persist child reports even when the
parent continues autonomously. Render the table on every user-visible result,
including partial, failed and blocked results. After an abrupt host failure, the
next activation reads/reconciles the canonical state and renders the recovered
report before new mutations; a missing final message is not proof of zero work.

G16 owns report semantics; G18 owns localized presentation without recomputing values.

## Mandatory governed project return state

When a conversation has an active canonical Handoff/project-tracking context, every substantive user-visible project return MUST refresh/read canonical state in the current response cycle and provide G18 with the durable project-return payload.

Required fields include current stage, completed stages, current-stage percent, weighted overall percent, next stage/state, `handoff_id`, integer `interaction_seq` (S), integer `material_seq` (M), exact `visible_ref`, verified Handoff URL, updated_at, current work unit, last completed work unit, RESUME_FROM, run status, evidence revision, current-turn S receipt, and when material work occurred the committed M receipt(s).

`visible_ref` MUST equal `<handoff_id> | S:<interaction_seq> | M:<material_seq>` after dual-sequence cutover. A bare URL or S-only footer is insufficient after migration. Read-only/knowledge turns still advance S exactly once and preserve M. Material turns advance S once and M once per committed material checkpoint.

G16 owns all semantic values; G18 renders them without recomputation. If evidence does not support a percentage, expose unknown/unavailable rather than inventing one. Before final output validate the S/M causal binding and current-turn receipt.

## Validation and promotion

Run `python -m unittest discover -s tests -p 'test_*.py' -v`. The transactional-writer regression suite must include duplicate-turn resume, S exactly-once allocation, M internal allocation, causal S/M binding, stale-state/CAS rejection and post-write readback. The bootstrap suite must additionally prove that absent an explicit Handoff URL, existing project bindings and bare Handoff IDs are ignored and a new Handoff is created; it must also cover explicit-URL continuation, explicit missing-URL failure, provider-write distinction, collision handling, post-create readback, first S=1 and first material M=1.
Current local regression PASS is not provider integration, final G12, independent
G13, installation or release certification. Keep those gates and all current-release
backlog requirements open until their own evidence exists. G0 intake correlation:
SF-XCUT-015, SF-XCUT-013 and SF-G16-003.

## Release orchestration and compact Handoff topology — HARD GATE
When SkillForge or another multi-Skill platform is developed while a stable release remains live:
- keep exactly one canonical project Handoff URL as compact pointer/current state/resume authority; semantic checkpoint sequence advances in place and MUST NOT create per-checkpoint Handoff files;
- keep at most one active work ledger per release and one closure report per completed release; high-volume event history belongs to G11/G17 rather than Handoff file sprawl;
- G0 is the Release Orchestrator semantic owner. G16 issues and verifies contributor work leases containing agent/surface ID, owned Skill/path set, base SHA, expiry, dependencies, acceptance criteria and return target;
- overlapping active leases on the same Skill/path fail closed unless G0 serializes them; stale base SHA fails closed before mutation/integration;
- contributors use isolated branches/worktrees and cannot mutate integration/stable directly; accepted changes enter one serialized integration queue;
- source freeze is prohibited while material leases remain active;
- runtime stable release remains pinned while candidate/next/hotfix work proceeds. Do not silently switch an active runtime session to a candidate release.

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
