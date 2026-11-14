# G0 v3 Build Pipeline

1. Qualify artifact.
2. Select Complexity Profile and Functional Role independently.
3. Resolve authoritative sources and REUSE → ADAPT → COMPOSE → NEW.
4. Resolve naming/namespace and preserve Stable ID/history.
5. Build a Build-Time applicability matrix for every governance capability.
6. Build a Runtime applicability/propagation matrix for every governance capability.
7. Selectively load only applicable rules/contracts.
8. Patch/build Candidate.
8A. For every configurable Skill, compile `INC_SKILL_SETUP_CONTRACT_V1`; expose every external/configurable parameter by stable semantic setup ID and keep actual customer physical values outside public Core.
8B. Run `scripts/skill_structure_setup_gate.py` on source structured metadata before freeze and on the clean materialized package after packaging; strict UTF-8/parser failure, literal structural escape artifacts, duplicate critical keys or normalized semantic drift fail closed.
9. Compile minimum Runtime Governance Profile.
10. Execute deterministic/static checks.
11. Execute proportional BT tests.
12. Execute proportional RT propagation tests/simulations.
13. Enforce S4, approval and integrity gates.
14. Package evidence into Validator Handoff.
15. Independent Validator/G13 evaluates.
16. If PASS_CANDIDATE, route managed publication through G1.
17. Remote-read/reconcile publication before claiming completion.
18. Emit only proportional logging/notification events.

No downstream Skill recursively loads the entire governance stack.

## Mandatory exhaustive pairwise gate
Before G12 entry at every source/release freeze, apply `INC_SKILLFORGE_EXHAUSTIVE_PAIRWISE_GATE_V1` using `scripts/skillforge_pairwise_gate.py`.

- resolve the exact frozen G0-G18 runtime member set from BOM/namespace authority;
- generate exactly 342 directed non-self edges / 171 unordered pairs for the current 19-member scope;
- fail closed on omission, duplication, stale identity/version/path, unresolved applicable edge or missing evidence;
- keep CONTENT_COPYING prohibited and use stable references/digests rather than peer implementation copies;
- run the matrix through runner-independent local CI in release-ready mode;
- bind matrix/member-set SHA-256 to the candidate and require G12 then independent G13 to certify the same digests;
- regenerate after any post-freeze identity/artifact change.

A complete matrix whose edges are still BLOCKED is structurally valid evidence of implementation, but it is not release-ready.

## Universal feedback intake and owner requirement coverage
For every Skill built or materially upgraded by SkillForge, compile `INC_SKILLFORGE_FEEDBACK_INTAKE_V1` as a compact runtime adapter regardless of framework membership. SkillForge-framework findings route to the unified SkillForge backlog; child product/domain findings remain in the child's resolved backlog.

Preserve origin and authority separately from numerical priority. Run Deduplicate → Correlate → Aggregate → Qualify before record creation. Direct canonical write unavailable means a truthful pending-intake receipt, never a fabricated registration success.

Before closing a SkillForge backlog-maintenance interaction, derive `decision_delta` and run `scripts/backlog_coverage_gate.py`. A completeness claim requires zero unmapped backlog-relevant decisions, verified post-write canonical SHA and canonical/private backlog parity. Owner mandates retain OWNER_MANDATE authority through dedupe, aggregation and supersession.

## Mandatory end-of-version rebuild and carry-forward gates

After step 17 and before release closure, apply
`references/skillforge-release-rebuild-carry-forward-gate-v1.md`
(`INC_SKILLFORGE_RELEASE_REBUILD_CARRY_FORWARD_GATE_V1`) as a hard gate.

The gate must:

1. enumerate every prior SkillForge-built framework member and external/descendant
   Skill from the Registry, lineage records, prior BOMs/manifests and known
   sources; distinguish canonical Skills from aliases, backlog-only entries and
   unconfirmed provenance;
2. compare the new SkillForge version with the prior version and produce the
   affected descendant set;
3. ask the owner for an explicit current-release decision
   (`REBUILD_ALL_ELIGIBLE`, `REBUILD_SELECTED` or `NO_REBUILD_NOW`) before
   any descendant rebuild; never infer consent from package approval, a waiver or
   silence;
4. route every approved rebuild through G0 and record its independent Skill
   version, stable lineage, artifact digest and applicable G12/G13 evidence;
5. construct a complete previous-to-new `carry_forward_manifest` for every
   unchanged requirement, contract, test, reference, script, asset, dependency,
   backlog/fix-register record and generated-Skill row; missing, duplicate,
   stale or `UNRESOLVED` rows fail closed;
6. bind the inventory digest and carry-forward digest to the BOM, release report,
   G12 input and independent G13 input.

The release report and final weighted table must distinguish
`FRAMEWORK_PACKAGE_COMPLETE`, `CARRY_FORWARD_COMPLETE`,
`DESCENDANT_REBUILD_COMPLETE` and
`DESCENDANT_REBUILD_DEFERRED_OWNER_DECISION`. A SkillForge package can be
complete while ecosystem descendant regeneration is pending, but it must not
claim ecosystem-wide 100 percent. This gate is executor-neutral and does not
require GitHub Actions or a hosted runner.

## Executable previous-version carry-forward completeness

The release rebuild/carry-forward gate delegates completeness enforcement to `INC_SKILLFORGE_CARRY_FORWARD_MANIFEST_V1`.

Before G12 entry:

1. materialize the full previous accepted package snapshot using the pinned lineage authority in `references/previous-release-carry-forward-source-v2.1.0.json`;
2. materialize the current release-candidate snapshot at source freeze;
3. include requirements, contracts, tests, scripts, references, assets, dependencies, negative tests, backlog/fix-register records, generated-Skill inventory and component identity/version artifacts;
4. generate and validate `carry_forward_manifest` with `scripts/carry_forward_gate.py --release-ready`;
5. require zero missing, duplicate, stale, unclassified or UNRESOLVED rows;
6. bind previous snapshot, current snapshot and manifest SHA-256 values into the release candidate;
7. require G12 and independent G13 to certify the same three digests.

File-count equality is not carry-forward proof. Any post-certification source change invalidates the bound evidence and reopens affected validation.

## REFERENCE_SCOPE Stage30 release-transition interlock

For the owner-selected FINAL v5 mission, apply
`references/release-closure-gate-v1.md` and execute
`scripts/release_closure_gate.py` before G12 entry, G13 entry, publication,
deployment and terminal closure. The gate complements rather than replaces G1,
G6, G8, G12, G13, G14, G16 and provider permissions.

Keep implementation/self-test readiness separate from final independent
certification. Compile the complete live-backlog ledger; never count a captured
requirement as implemented. The current owner approval must be independently
resolved from its source and bound to this mission and its latest approval gate.

Use the scoped FINAL v5 proportional test profile: retain completeness,
adversarial and lifecycle coverage without mandatory repeated heavy suites.
Source/package/backlog/BOM and ledger identities are frozen together; changed
identity after certification requires affected revalidation, not a silent rebuild.
The implementation actor cannot issue its own independent G12/G13 approval.

This is an unreleased candidate interlock. Its unit-test PASS and metadata
presence do not establish final SkillForge release readiness.

## Mandatory durable-command compilation

When a build emits an executable Handoff, command or inter-agent work order, compile
`INC_G16_DURABLE_EXECUTION_PROGRESS_V1` from canonical G16, including for one executor.
Do not merely attach a prose reminder. Generate a stable command/root/actor identity,
complete requirement IDs, versioned weighted steps and acceptance milestones, durable
journal/projection/report references, bounded action/retry counters and exact resume
position. Validate the plan before marking the instruction execution-ready.

The receiving executor must use G16's pre-action gate, write-ahead intent and remote
outcome reconciliation, then checkpoint and report from durable evidence. Include
`REPORT_AFTER_EXECUTION_REQUIRED=true` in the mandatory governance envelope. Every
user-visible complete/partial/blocked/failed return renders the weighted table through
G18; an abrupt host failure defers that rendering to the first resumed activation.
G16 owns semantics and G18 presentation. Preserve original project scope, release gates
and owner-only decisions. Missing fields, stale plan/state or a missing mandatory
report block acceptance. Do not duplicate G16's entire implementation into child Skills.

## Stage 2 setup/structure gate
`INC_SKILL_SETUP_CONTRACT_V1` is owned by G7 and compiled by G0. `INC_SKILL_SOURCE_PACKAGE_STRUCTURAL_VALIDATION_V1` is mandatory before candidate freeze and after package materialization. G12/G13 later certify the same evidence on the final frozen release artifact; Stage 2 self-tests do not self-certify final release.


## Mandatory publicization phase


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

Compile exact per-file review, external owner parameters, archive recursion, current destination observations and full remote surface evidence before selecting public distribution. PRIVATE release receipts cannot satisfy this phase.
