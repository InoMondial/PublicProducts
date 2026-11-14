# G8 Post-Deploy Secret Migration Runbook v1

Contract: `INC_G8_SECRET_MIGRATION_V1`  
Backlog: `SF-G8-003`  
Execution timing: **POST_DEPLOY_OWNER_GATED**

## Safety boundary

This runbook never authorizes predeploy migration. Do not read or place raw secret values in Chat, prompts, Handoffs, GitHub, ordinary SharePoint documents, spreadsheets, normal database rows, or ordinary logs. Resolve or inject secret material only inside an approved trusted provider/tool boundary for the single authorized operation.

Do not retire or delete the legacy authority automatically. Destructive retirement requires separate explicit owner approval after observation and recovery evidence.

## Required activation gates

Before any real secret mutation, verify all gates from `INC_G8_SECRET_MIGRATION_V1`: certified SkillForge deployed, `SF-G8-002` PASS, final G12 PASS, independent G13 PASS, namespace/ownership blockers resolved, target Azure environment owner-confirmed, GOOD recoverable backup, rollback manifest, complete live-consumer inventory, and explicit owner execution approval.

Any missing gate is `BLOCKED_G8_SECRET_MIGRATION_ACTIVATION`.

## Preparation workflow

1. Freeze one migration unit only; do not batch unrelated secret classes.
2. Re-read live consumers and current source authority.
3. Resolve the destination through the stable G8 `secret_ref`; keep tenant/subscription/vault identifiers in trusted environment/registry configuration, not child Skill logic.
4. Verify GOOD backup and rollback target.
5. Verify target provider/identity route with synthetic or metadata-only proof first.
6. Record only non-secret manifest/evidence fields.

## Class-specific decision rules

### G17 root key

Use `INC_G17_KEY_LIFECYCLE_V1` and `INC_G17_MIGRATION_ROLLBACK_V1`. Keep the current source recoverable/read-only through observation. Switch consumers through the logical G8 binding only after target verification and rollback proof. Never destroy an old key version while live data or retained backups depend on it.

### Hatchable bootstrap credential

Re-evaluate OIDC/Workload Identity Federation first. If unavailable, evaluate certificate-based confidential-client authentication. Retain a client secret only as `BOOTSTRAP_EXTERNAL_WORKLOAD_CREDENTIAL` when federation is unavailable and certificate authentication is unsupported or operationally unsuitable. Hatchable native secure storage must not become a general second secret store.

### Other machine secrets

Re-inventory first. Migrate one owner-approved class at a time. Blanket account-wide migration is prohibited.

## Cutover workflow

1. Verify all activation gates again immediately before mutation.
2. Create/verify the target behind the logical `secret_ref` inside the trusted provider boundary.
3. Verify least privilege and expected denial paths.
4. Rewire only the approved consumers to the logical binding.
5. Reconcile non-secret metadata, version, fingerprint/hash-equivalent evidence, and consumer health.
6. Enter the owner-approved observation window with the old source read-only or recoverable.
7. On any rollback trigger, revert the binding/consumer route and verify operation on the prior authority.
8. After observation, request separate owner approval before destructive legacy retirement.

## Rollback triggers

Rollback on target unavailability, authorization/security regression, `secret_ref` resolution failure, consumer regression, unexplained integrity/fingerprint mismatch, or owner abort. Follow `INC_G17_MIGRATION_ROLLBACK_V1` for provider-switch rollback mechanics.

## Evidence

Persist only metadata: migration unit ID, logical `secret_ref`, safe source/target refs, credential mode, non-secret version/fingerprint, approval refs, operation outcome, rollback state, actor ref, and UTC timestamps. Run leak scanning before terminal success.

## Terminal states

- `BLOCKED_G8_SECRET_MIGRATION_ACTIVATION` — one or more activation gates missing.
- `READY_FOR_POSTDEPLOY_OWNER_GATED_MIGRATION` — all non-secret gates pass; readiness only.
- `OBSERVATION` — cutover completed, prior authority retained.
- `ROLLED_BACK` — prior authority restored and verified.
- `COMPLETE_PENDING_LEGACY_RETIREMENT` — migration verified but destructive retirement not yet approved.
- `COMPLETE` — observation passed and any approved retirement completed with evidence.
