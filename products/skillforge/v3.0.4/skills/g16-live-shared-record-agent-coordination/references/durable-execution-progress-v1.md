# Durable execution and weighted command reports

Contract: `INC_G16_DURABLE_EXECUTION_PROGRESS_V1`.
Owner: G16. Producers: G0 and any generator of governed executable instructions.
Human rendering: G18 / `CHAT1-SKL-001`. Candidate; independent G12/G13 pending.

## Applicability and authority

Apply the durable-command profile to every governed executable Handoff or work order,
including a single executor. The STAR coordination profile still requires multiple
participants; do not manufacture a worker or a new chat to use this profile.
Retain the existing G16/G18 activation, surface/model recommendations, machine-first
execution, security, owner approvals and governed delivery contracts.

Before execution persist a command envelope with `command_id`, `root_work_unit_id`,
`actor_id`, actual `environment_id`, authority/source identities, `scope_revision`,
complete requirement IDs, a weighted plan, durable journal/projection locations,
current-state revision, report destination and an exact resume point. An unverified
surface is recorded as unverified, not called Windows merely because a terminal exists.

Use one canonical event-derived current-state projection. Historical snapshots are not
current-state authority. Compatibility aliases must be generated and checked against
that projection, not independently edited. A stale mirror or stale conversation summary
cannot reset authorization, progress, source head or resume position. On status queries,
read the current remote revision before answering; a missing final chat message does
not prove that no work happened.

## Bounded execution, including reads and research

Use `scripts/execution_progress.py` as a deterministic pre-action/reducer/report core.
The real orchestrator must call `before_action` before every material operation and
persist the resulting events; merely mentioning this script does not enforce it.
Use `action` events for material reads/discovery/tests and `intent` for mutations.

Default limits are 480 seconds or 12 material actions between checkpoints, 900 seconds
without new verified acceptance evidence, 1500 seconds per work slice, three attempts
per operation identity, two occurrences per identical error signature and six root
no-progress attempts. A checkpoint does not itself earn progress or reset the root
no-progress budget. Splitting/renaming children must preserve attempts, error counters
and the last real evidence time. A repeated verification of the same milestone is not
new evidence. A route that exhausts its budget is blocked until a documented material
change justifies reopening; proceed with independent safe work, not another renamed loop.

A long-running provider job should return a durable job handle and use native status
observation. Before an unbounded host/tool call, checkpoint and verify a timeout or an
authorized runner control. Where cancellation/timer enforcement is unavailable, record
`COOPERATIVE_PRE_ACTION_ONLY` and that limitation. Never claim a prompt can interrupt a
frozen model/tool, guarantee an eight-minute checkpoint while it lacks control, or
self-wake after `Thinking failed`. A deterministic external watchdog is optional only
when actually available and authorized; no timer service, paid dependency or surface
switch is implicitly introduced.

## Write-ahead intent and remote reconciliation

Before a material mutation, write/read back an intent containing operation identity,
exact target/path scope, observed before version/SHA, intended outcome, permission and
owner-decision references, acceptance milestone, expected readback and rollback or
reconciliation rule. Prefer provider idempotency keys and conditional writes.

After a mutation, independently read its remote result and classify `not_applied`,
`applied` or `unknown`. Never automatically repeat an unknown-outcome mutation.
Then verify the actual acceptance criterion and persist its evidence. A successful
HTTP response is not by itself a verified outcome. `VERIFIED` is not yet earned durable
completion; the milestone earns credit only after its checkpoint receipts exist.

Two remote writes are not one transaction. Write the detailed journal/checkpoint
candidate first, read it back, then write the compact projection referring to the same
revision and payload digest and read that back. Commit the receipt event referencing
the prior persisted candidate, so no file must contain its own final hash. Persist that
receipt before another side effect. On interruption between the two writes, reconcile
the highest complete revision and repair the missing projection without replaying the
business operation. Never overwrite a newer unrelated writer's work.

Use verified CAS/ETag/If-Match when available. If the adapter has no atomic concurrency
primitive, allow one explicitly coordinated writer only. A JSON lease field is not a
lock. Checkpoint persistence failure blocks further side effects after bounded retries.
If the detailed report fails while the journal survives, regenerate the report rather
than lose or repeat completed work.

The Python reducer validates consistency; it does not authenticate adapter receipts,
provide a distributed lock, call providers, run a host watchdog or certify G12/G13.
Adapters must resolve real permissions, actor identity, timestamps, source versions and
independent readbacks. Do not fill trusted observations by copying the result that one
wishes to prove. Secrets and raw sensitive errors never enter events; store stable
redacted error codes, operation IDs and governed evidence references only.

## Weighted acceptance, not time spent

Before execution, assign each step a stable ID, title, positive integer `weight_bp`,
requirement IDs and explicit acceptance milestones. All step weights sum to 10000;
all milestone weights inside each step also sum to 10000. A trivial command may have
one row. Ten rows are an example, not a universal fixed count.

Step completion is the sum of weights of `CHECKPOINT_COMMITTED` milestones divided
by 100. Earned percentage points equal step weight times completion divided by 100.
Command completion is the sum of earned contributions; remaining equals 100 minus
completion. Unknown, applied-unverified, blocked and failed work earns no new credit.
Preserve already completed milestone credit on a later failure. Duration, repeated
research, call counts, token consumption and a synthetic fixture are not delivery credit.

On scope changes, create a new plan revision with an explicit old/new requirement and
weight mapping. Retain all original requirements unless the owner explicitly changes
scope; unresolved work must not vanish from the denominator. Carry forward evidence
only after checking unchanged acceptance identities. The core rejects a changed plan
without migration rather than silently reweighting it. Legacy subjective percentages,
including REFERENCE_SCOPE's 43.2 percent snapshot, remain labeled historical estimates until mapped
to acceptance receipts; they are not newly verified acceptance coverage.

## Mandatory report and recovery behavior

After every bounded child, persist a machine report and its human table projection.
After every user-visible execution return, display the table whether the outcome is
complete, partial, failed or blocked. Internal checkpointing must not force routine
user approval during an authorized autonomous parent mission. If the host dies before
it can speak, show the reconstructed report on the next activation before new mutations.

The report includes command/plan revision, state revision, latest observation time,
last durable checkpoint time, step references, titles, weights, verified completion,
earned and remaining contributions, states, remaining milestones, evidence references,
last error location and exact resume position. G16 owns these values; G18 translates
and renders without changing them. Respect an explicit owner request for a table.
Use a small table or multiple short tables on Persian Chat, not raw HTML or a forced
wide layout. Machine IDs remain clean; visible Persian headings begin in Persian.

On resume, read the canonical remote record and source/backlog identities, replay or
verify the checkpoint revision, reconcile pending outcomes and derive the report. Do
not infer state from a cached assistant summary, old preflight file, a UI error banner
or a static percentage. A recovered 100 percent command report is not automatically a
production-release certificate: release-specific hard gates still apply.

## Producer and receiver hooks

G0 and other producers include this contract ID, the weighted plan and journal/report
references in their mandatory governance envelope. Receivers load the compact profile
on activation/resume, pin its source digest and recheck that digest before material
writes. Do not repeatedly reload every governance document for an unchanged call.
G18 consumes the `report` output and never creates another mutable progress authority.
G11 receives material activity/correlation events through its existing logical gateway;
this profile does not introduce another physical database or raw-secret store.

## Verification

Run `python -m unittest discover -s tests -p test_execution_progress.py -v` from the
G16 root. The current tests cover deterministic fixtures and injected state boundaries,
not a crash of the actual Chat host or an independently certified release. Provider
adapter integration and final frozen-candidate G12/G13 remain separate acceptance gates.

Example report command:

```sh
python scripts/execution_progress.py plan.json state.json --markdown
```

For a pre-action decision add `--observations observed.json`; a blocked result exits 2.
