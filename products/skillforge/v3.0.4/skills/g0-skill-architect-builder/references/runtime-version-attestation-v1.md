# SkillForge runtime version attestation v1

Contract: `INC_SKILLFORGE_RUNTIME_VERSION_ATTESTATION_V1`.

## Purpose

Before any material governed project mutation on Chat, Work or Codex, independently prove the active installed SkillForge package, G16 and G18 from runtime evidence and reconcile them with the project release manifest/minimum governance profile.

GitHub source, Handoff claims, user claims or assistant inference are not runtime installation evidence.

## Required proof channels

1. Runtime channel: host/package/plugin metadata from the current runtime instance and current account/session context.
2. Handoff channel: independent provider readback of the current canonical Handoff revision.

The two channels must be independently proven.

## Material gate

Material work requires:
- current surface identity;
- runtime instance, account-context and session fingerprints;
- installed SkillForge version and package SHA-256;
- installed G16 version/digest;
- installed G18 version/digest;
- verified runtime proof source/ref/timestamp;
- required minimum versions and allowed package/component digests from the release manifest/profile;
- independent Handoff readback revision.

Any mismatch or unprovable evidence blocks mutation with `RUNTIME_ATTESTATION_MATERIAL_MUTATION_BLOCKED`.

## Read-only exception

A read-only audit may continue as `NONCONFORMING_RUNTIME_READ_ONLY`. It must expose the mismatch and must not claim that G16/G18 hard gates are actively enforced.

## Cross-account and cross-chat safety

An attestation is bound to surface + runtime instance + account-context fingerprint + session fingerprint. Sign-out/sign-in, another account, another chat runtime or another surface requires a fresh attestation. Reusing a prior receipt is prohibited.

## Persistence

Persist the attestation receipt identifier, observed versions/digests, required profile, status and mismatch list in the Handoff/checkpoint receipt. Do not persist secrets or raw credentials.

Executable validator: `scripts/runtime_version_attestation.py`.
Deterministic tests: `tests/test_runtime_version_attestation.py`.
