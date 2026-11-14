# G17 Data Governor — Encryption & Key Management Standard

Status: REFERENCE_SCOPE STAGE-18 DESIGN/IMPLEMENTATION BASELINE. Owner acceptance, G12/G13 and final release gates remain required.

## 1. Security objective
For S3/S4 protected payloads, a raw Hatchable database, Hatchable logical backup, accidental database publication, or ordinary provider-side database access must reveal only ciphertext plus explicitly allowed low-sensitivity routing metadata.

The database provider must not receive the G17 ROOT_KEK or derived DEKs.

## 2. Cryptographic baseline
- AEAD: AES-256-GCM.
- Root key: 256-bit cryptographically random ROOT_KEK stored outside Hatchable.
- KDF: HKDF-SHA-256.
- HKDF protocol salt: SHA-256("INC-G17-HKDF-v1") (public protocol constant).
- HKDF info: canonical UTF-8 JSON containing protocol, project_ref, domain_ref, purpose, key_version.
- Derived key: 32 bytes.
- IV/nonce: 12 random bytes per encryption; reuse with the same derived key is forbidden.
- Authentication tag: 16 bytes, included in AES-GCM ciphertext.
- AAD: canonical UTF-8 JSON binding project_ref, domain_ref, entity/table, stable row_ref, field/purpose, key_version and alg_version.
- DB storage: ciphertext/IV as bytea; key_version and alg_version as non-secret metadata.

## 3. Key hierarchy
ROOT_KEK_vN
  -> HKDF-SHA-256(scope context)
  -> scoped DEK

Scope context separates at least:
- project_ref
- domain_ref
- purpose/field
- key_version

Derived DEKs are ephemeral and are never persisted.

## 4. Trusted crypto boundary
Encrypt/decrypt happens in deterministic code outside LLM reasoning.

Approved logical flow:
1. G17 resolves authorization, project scope, classification and exact requested fields.
2. Trusted runtime retrieves the required ROOT_KEK version from approved external custody without printing key bytes.
3. Deterministic crypto code derives the scoped DEK.
4. Encrypt/decrypt executes in code.
5. Only minimum necessary plaintext is returned to the consuming operation/model.
6. Key bytes, DEKs and ciphertext are never copied into chat text, prompts, Handoff, G11, Teams, GitHub or ordinary business records.

The LLM must never perform cryptography by reasoning over key/ciphertext text.

## 5. Write path
Plaintext S3/S4 field
  -> canonical scope/AAD
  -> external ROOT_KEK retrieval
  -> HKDF scoped DEK
  -> random 12-byte IV
  -> AES-256-GCM
  -> provider adapter receives ciphertext + IV + version metadata only

## 6. Read path
Bounded DB query
  -> ciphertext + IV + version metadata + reproducible AAD inputs
  -> external ROOT_KEK retrieval
  -> scoped DEK derivation
  -> AES-GCM authenticate/decrypt
  -> minimum necessary plaintext
  -> consumer/model only if business task needs plaintext

Tag/AAD/key mismatch fails closed and emits a redacted G11 security event.

## 7. Search/index behavior for encrypted fields
- Do not use deterministic AES encryption by default.
- Do not store a plaintext duplicate solely to make an encrypted field searchable.
- For explicitly approved equality search, G17 may generate a blind index using HMAC-SHA-256 under a separately derived INDEX purpose key.
- A blind index leaks equality/frequency patterns; it therefore requires explicit threat/utility review.
- Range, fuzzy and full-text search over protected fields require a separate approved design; do not silently weaken encryption.

## 8. Algorithm agility
Each envelope stores alg_version and key_version.
V1 remains AES-256-GCM because it is widely standardized, high-performance, portable and already verified in this environment.

Future candidates may include AES-GCM-SIV, XChaCha20-Poly1305 or another reviewed AEAD if platform support/security needs justify migration. No cipher is described as "unbreakable".

## 9. Private custody parameters

Resolve ROOT_KEK_SECRET_REF from an external private profile through the approved
secret provider. Never embed a key file path or effective principals in a Skill.
Custody/ACL observations are private evidence, not release content.

## 10. Rotation policy
Routine target:
- rotate ROOT_KEK at least every 12 months unless an owner-approved risk assessment sets a different cryptoperiod.

Immediate rotation triggers:
- suspected/confirmed key exposure;
- unexpected permission expansion;
- compromise of the trusted crypto boundary;
- material cryptographic defect affecting key safety;
- material operator/access change requiring rekey.

Routine rotation:
1. create ROOT_KEK_vN+1;
2. register metadata/fingerprint without exposing bytes;
3. mark new key ACTIVE;
4. old key becomes DECRYPT_ONLY;
5. new/updated records use the new key version;
6. re-encrypt old data by governed batch/opportunistic migration as required;
7. retain old key while any governed live data or retained backup still needs it.

Compromise rotation:
- stop affected writes;
- create new key;
- identify affected scope;
- re-encrypt as soon as safely possible;
- old key becomes COMPROMISED/REVOKED after dependencies are removed;
- log incident without key material.

## 11. Recovery

Require verified recoverable key custody with independently authorized custodians,
versioned references, revocation and break-glass audit. Store all physical custody
locations and current access observations privately outside this package.

## 12. Backup semantics
Field-level provider-blind encryption is mandatory for S3/S4 before data reaches Hatchable.

Therefore Hatchable logical backups can safely contain:
- ciphertext for S3/S4;
- explicitly allowed S1/S2/plain routing metadata;
- schema/version metadata.

The REFERENCE_SCOPE v1 design does NOT require Hatchable itself to whole-file encrypt the backup, because doing so with ROOT_KEK would violate provider-blind key separation. SharePoint backup transfer remains Stage 19. Whole-file application encryption may be added later only through an external trusted crypto service/KMS without giving ROOT_KEK to Hatchable.

## 13. Performance validation

Benchmark representative synthetic records under the selected host. Store real
operational measurements in private evidence; unknown measurements stay unknown.
