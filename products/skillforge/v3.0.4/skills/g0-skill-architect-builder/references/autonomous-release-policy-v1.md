# Autonomous evidence-based release policy

Contract: `INC_AUTONOMOUS_RELEASE_ACCEPTANCE_V1`.
Profile: `AUTONOMOUS_EVIDENCE_BASED`. Owner: G0. Effective: 2026-11-13.
Authority: direct owner mandate PRIOR_RELEASE, following PRIOR_RELEASE and PRIOR_RELEASE.

## Precedence and applicability
This is the default release policy for the owner's private/internal SkillForge and
its managed Skill releases. It replaces release-only requirements for a separate
person/agent, G12/G13 independence certificate, GitHub Actions/runner/compiler,
user-operated test, native Windows/ChatGPT install, or exhaustive live-provider
end-to-end validation. Those checks are optional assurance, not release blockers.
Historical text prescribing those prerequisites is superseded for this profile.
A third-party certificate is a distinct optional output, never a synonym for release.
Public distribution and externally imposed approval obligations are outside this
private policy; no permission or certification is invented for them.

## Required execution
Run the tests feasible in the current authorized environment: deterministic/static
checks, relevant behavioral and negative tests, safe API/plugin tests where available,
or executable simulation with explicit fixture boundaries. Repair failures and rerun
changed/critical paths. Do not relabel a failed executed test optional to get a PASS.
Retain owner-selected requirement dispositions and exact package/source identities.
Perform a separate quality-review pass; the same executor may perform review and fix.
Use bounded retries; do not create paid services, extra agents, runners or user work
just to satisfy an assurance preference.

## Required release gates
Authorization, known security defects, integrity, dependency closure, rollback,
quality review, scope coverage and all selected executable tests must PASS.
Publish the exact frozen package to the governed private destination and verify
actual remote bytes before claiming RELEASED. Publication/readback is real work,
not a simulated receipt. Bind version, tree/BOM/package digests, logs and report.
Update canonical continuity after readback. The executable decision is
`scripts/autonomous_release.py`, dispatched by `scripts/release_closure_gate.py`
when the manifest uses this profile. Verified owner context comes from the host,
never from package configuration or an untrusted manifest.

## Optional assurance
Record unavailable third-party review, runner, user-assisted testing, native host
install, complete live-provider testing, host visual checks and GitHub-specific
merge/release objects as `NOT_RUN_OPTIONAL` (or `SIMULATED_NOT_LIVE`) with a reason.
Do not wait for them, leave the release as RC, re-open the release, or request user
execution solely because they have not run. Optional means no pending release work.
Report observed results and limits without asserting these checks passed.

## Release versus activation
A final RELEASE has a stable version with no RC, candidate or simulation suffix.
RELEASED means the package passed this policy and was actually published; it does not
mean independently certified, installed on all hosts or guaranteed to contain no bugs.
Real provider writes, secrets, destructive operations and permission checks still
require normal runtime authorization and exact outcomes. Simulation grants no
production permission. Independent readback means a separate read, not a third person.
Changing release acceptance does not disable runtime safeguards or falsify history.

## Propagation and efficiency
G0 compiles this profile into new/changed managed Skills. All packaged Skills consume
it only for release and final status, through a compact reference to this one policy.
Normal low-risk invocation does not load the full release policy. G12 owns test
records, G13 quality assessment, G14 package integrity, G1 publication/readback,
and G16 durable closure. Responsibilities need not be executed by separate actors.
Preserve historical certificates; never relabel them as new independent approval.

## Executable compatibility
Existing strict-mode validators and archived receipts keep their original schemas.
They must not be invoked as unconditional release authorities for this profile.
The current gate dispatch is selected by an explicit release_policy field and a
separate authenticated owner context. Runtime authorization, logs and provider
readbacks are unaffected. Publication traces for this release are persisted in
the verified SharePoint release receipt; no production database write is needed.
