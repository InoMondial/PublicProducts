# INC_SKILLFORGE_CARRY_FORWARD_MANIFEST_V1

This P0 fail-closed contract implements the previous-version carry-forward completeness requirement owned by G0 with G6 lifecycle semantics and G12/G13 certification.

## Freeze inputs

Before G12 entry, materialize two immutable snapshots:

1. previous accepted SkillForge package/release;
2. current release-candidate freeze.

Each snapshot contains one stable item row for every applicable:
- requirement;
- contract;
- positive test;
- script;
- reference;
- asset;
- dependency binding;
- negative test;
- unified-backlog/fix-register record;
- generated-Skill inventory record;
- Skill component identity/version artifact.

Every row contains `item_id`, `category`, `stable_ref`, `source_ref` and `content_sha256`. File counts alone are never sufficient.

## Deterministic projection

Run `scripts/carry_forward_gate.py` to create exactly one row per unioned item identity using only:

- `UNCHANGED_CARRIED_FORWARD`
- `MODIFIED_REVALIDATE`
- `RETIRED_WITH_REASON`
- `NEW`
- `UNRESOLVED`

An unchanged row must preserve stable reference and content digest. A modified row requires affected tests plus explicit proportional G12 and independent G13 scopes; changed stable identity also requires `lineage_ref`. Retirement requires explicit owner approval, reason, and successor or historical reference. Missing prior items without an approved retirement become `UNRESOLVED`.

Duplicate IDs, missing rows, stale digests, invalid dispositions, unresolved rows, missing modified-test scope, or unapproved retirement fail closed.

## Release binding

The manifest records:
- previous snapshot SHA-256;
- current snapshot SHA-256;
- carry-forward manifest SHA-256.

The release candidate binds all three digests. `scripts/carry_forward_release_binding.py` requires verified release-ready evidence with zero unresolved rows before G12 entry. G12 and independent G13 certificates must echo the same three digests. Any post-certification current-snapshot change invalidates the evidence and requires affected revalidation.

The final release report cannot claim 100% carry-forward or ecosystem completion while the manifest is incomplete, unresolved, stale, or digest-mismatched.
