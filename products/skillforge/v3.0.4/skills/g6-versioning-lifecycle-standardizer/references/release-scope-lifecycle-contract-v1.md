# Release Scope & Lifecycle Contract

**Contract ID:** `INC_RELEASE_SCOPE_LIFECYCLE_V1`
**Owner:** `G6-Versioning & Lifecycle Standardizer`
**Framework:** `SkillForge`

## 1. Version scopes
Version impact is evaluated separately for:
- framework release;
- individual Skill bytes/contracts;
- registry/schema contract;
- documentation-only artifact;
- backlog-only state;
- runtime/configuration state.

A backlog entry alone does not bump a Skill. A changed contract consumed by a Skill may require that Skill to version even when its prose changes are small.

## 2. Release scope freeze
Before implementation of a target release is finalized:
1. backlog owner presents numbered eligible items;
2. owner selects target items;
3. selected Change IDs form an immutable release-scope snapshot;
4. additions/removals after freeze require an explicit scope-change record and SemVer impact re-evaluation.

## 3. Lifecycle
Minimum governed lifecycle:
`DISCOVER -> QUALIFY -> SELECT -> BUILD -> VALIDATE -> INSTALL/DEPLOY -> SMOKE -> ACTIVATE -> OPERATE -> UPGRADE | ROLLBACK | DEPRECATE -> RETIRE/UNINSTALL`.

Accepted/published bytes are immutable. A correction creates a new version.

## 4. Upgrade compatibility
Before upgrade, record:
- current and target version;
- affected contracts/schemas/registries;
- backward/forward compatibility;
- required migration;
- install coexistence/duplicate risk;
- rollback target and trigger;
- preservation/restore evidence.

Unsupported incompatible transition blocks with `UPGRADE_COMPATIBILITY_FAILED`.

## 5. Rollback
Every material release/upgrade must identify a known-good rollback target unless rollback is technically impossible and explicitly approved. Failed smoke/activation/compatibility/data-integrity gates trigger rollback or a fail-closed blocked state.

## 6. Framework release SemVer
G6 determines the final SkillForge release SemVer only after the accepted change set is frozen and the compatibility surface is known. Do not pre-claim MAJOR/MINOR/PATCH from backlog count alone.
