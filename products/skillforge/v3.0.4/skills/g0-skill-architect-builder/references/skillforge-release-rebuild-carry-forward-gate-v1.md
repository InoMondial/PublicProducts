# SkillForge Release Rebuild and Carry-Forward Gate v1

Contract: `INC_SKILLFORGE_RELEASE_REBUILD_CARRY_FORWARD_GATE_V1`
Owner: G0 / SkillForge
Status: next-release mandatory candidate hard gate
Correlated backlog: SF-XCUT-037, SF-XCUT-038, SF-XCUT-035

## Purpose

Every new SkillForge version must prove two separate facts before it claims
ecosystem completeness:

1. every previously SkillForge-built Skill was inventoried, impact-assessed and
   either rebuilt under an explicit owner decision or explicitly deferred; and
2. every unchanged requirement, contract, test, reference, dependency, stable
   identity and release artifact from the previous version was carried forward,
   revalidated, or retired with an owner-approved reason.

A package can be complete as a SkillForge framework package while descendant
rebuilds remain pending. The release report must never collapse those states into
one percentage.

## Scope and trigger

Run this gate at:

- the end of every SkillForge version build;
- source freeze and release-candidate freeze;
- before G12 entry, G13 entry, publication, deployment and terminal closure;
- after any post-certification material source, backlog, BOM or package change.

The current v2.1.0 package remains immutable. This gate is a next-release source
change and does not silently rebuild, deploy or mutate v2.1.0.

## Gate A — prior generated-Skill inventory and owner consent

### A1. Construct the inventory

G0 resolves the authoritative Registry, generation-lineage records, all prior
package BOMs and manifests, release reports, external Skill sources and known
descendant records into one machine-readable
`prior_generated_skill_inventory`.

Each row contains at least:

- `stable_id`, `visible_id`, canonical path and aliases;
- framework membership and `builder_framework_ref`;
- current independent Skill version and artifact/source digest;
- source repository/ref and last verified rebuild evidence;
- classification: `IN_SCOPE_MEMBER`, `EXTERNAL_DESCENDANT`,
  `LEGACY_ALIAS`, `BACKLOG_ONLY` or `UNCONFIRMED`;
- the new-version contract delta, affected/not-affected result and proposed
  rebuild disposition.

The inventory includes framework members and external descendants. A legacy alias
is linked to its canonical Skill and is not counted as a second rebuild target.
An entry missing builder provenance is not silently excluded; it is
`UNCONFIRMED` until classified.

### A2. Compute impact

Compare the previous and new SkillForge contracts, runtime governance,
packaging/installation rules, security/output rules, dependency bindings and
cross-Skill matrix. Record the exact affected descendant set. The absence of a
known affected descendant is evidence only when the inventory and delta are
complete.

### A3. Ask the owner before any rebuild

Before rebuilding a descendant, G0 presents the inventory summary, affected set,
versions, expected work and risks and asks one explicit release-bound question:

- `REBUILD_ALL_ELIGIBLE` — rebuild every classified eligible prior Skill;
- `REBUILD_SELECTED` — rebuild only the owner-selected entries;
- `NO_REBUILD_NOW` — rebuild none and record the reason and deferred set.

The decision is bound to the current SkillForge version, source freeze, inventory
digest and approving owner message. General package approval, a simulation
waiver, a previous conversation or silence is not consent.

### A4. Execute and close the decision

For an approved rebuild, route the entire build through G0, preserve stable IDs,
aliases and lineage, select the latest corrected independent Skill version, and
run deterministic self-tests plus applicable G12 and independent G13 evidence.
Record the new source/artifact digest and deployment state.

For `NO_REBUILD_NOW`, the release may report the framework package separately
only when the owner decision and impact/deferment statement are present. It must
report descendant rebuild state as `DEFERRED_OWNER_DECISION`, not
`COMPLETE`; if a changed contract affects a deployed descendant, the affected
descendant remains a release blocker for ecosystem-wide completion.

## Gate B — previous-version carry-forward completeness

### Executable completeness binding

Gate B is enforced by `INC_SKILLFORGE_CARRY_FORWARD_MANIFEST_V1` in `references/carry-forward-manifest-v1.md`, generated/validated by `scripts/carry_forward_gate.py` and bound to release certification by `scripts/carry_forward_release_binding.py`.

The previous package lineage for the current release family is pinned by `references/previous-release-carry-forward-source-v2.1.0.json`. This lineage anchor does not replace the final full previous-version snapshot.

Before G12 entry the local runner MUST validate the final previous/current snapshots and carry-forward manifest in release-ready mode with zero unresolved rows. The release candidate, G12 certificate and independent G13 certificate MUST bind the same previous snapshot, current snapshot and carry-forward manifest digests.



### B1. Freeze the previous-version set

Before the new source freeze, snapshot the previous manifest, BOM, stable IDs,
per-Skill versions, requirements ledger, contracts, tests, scripts, references,
assets, dependency bindings, negative tests, backlog/fix-register records,
generated-Skill inventory and release evidence.

### B2. Produce the carry-forward manifest

Create a deterministic `carry_forward_manifest` with exactly one row per
previous-version item and one of these dispositions:

- `UNCHANGED_CARRIED_FORWARD`;
- `MODIFIED_REVALIDATE`;
- `RETIRED_WITH_REASON`;
- `NEW`;
- `UNRESOLVED`.

Every unchanged item must be present in the new package or referenced through an
explicit immutable inherited contract. Stable IDs, aliases, lineage and
applicable tests remain resolvable after file moves, package major-version
changes or added Skills.

`UNRESOLVED`, missing, duplicate, stale or unclassified rows fail closed.
File-count equality or a matching top-level package hash is not sufficient.

A modified row names its affected tests and proportional G12/G13 scope. A retired
row names the owner-approved reason and successor or historical reference.
Migration is not omission.

### B3. Reconcile and bind

Reconcile the carry-forward manifest against the unified backlog, per-Skill
fix registers, BOM, release manifest, package digest and release report.
Hash the manifest and bind the same digest to G12 input, independent G13 input
and final release evidence. A post-certification material change invalidates
the bound evidence and requires affected revalidation.

## Release-state outputs

G0 must emit separate states:

- `FRAMEWORK_PACKAGE_COMPLETE`;
- `CARRY_FORWARD_COMPLETE`;
- `DESCENDANT_REBUILD_COMPLETE` or
  `DESCENDANT_REBUILD_DEFERRED_OWNER_DECISION`;
- `ECOSYSTEM_RELEASE_COMPLETE` only when the applicable states and independent
  gates are complete.

The weighted table always lists the prior generated-Skill inventory at its end.
An empty or unavailable list is a finding, not permission to omit the section.

## Runner policy

This gate is executor-neutral. The inventory, delta, carry-forward manifest and
hash checks may run through the verified local deterministic Codex/Windows path.
GitHub Actions and a hosted runner are not required and must not be treated as a
release dependency. Provider/live mutations remain separately owner-gated.

## Minimum negative tests

- owner decision absent -> no descendant rebuild starts;
- an unconfirmed prior Skill -> ecosystem-wide completion fails closed;
- an unchanged prior requirement omitted from the new manifest -> carry-forward
  fails closed;
- a legacy alias counted as a second canonical Skill -> inventory fails;
- a post-certification source change with old digest -> G12/G13 evidence invalid;
- explicit `NO_REBUILD_NOW` -> framework package may be reported independently,
  but descendant completion remains deferred.
