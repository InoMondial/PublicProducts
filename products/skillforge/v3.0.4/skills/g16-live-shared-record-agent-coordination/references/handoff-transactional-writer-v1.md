# G16 transactional dual-sequence Handoff writer v1

Contract: `INC_G16_HANDOFF_TRANSACTIONAL_WRITER_V1`.

## Authority

This is the only permitted semantic writer for Handoff counters after dual-sequence cutover.
Callers MUST NOT calculate, supply or directly mutate next S or next M.

The deterministic core is `scripts/handoff_transaction.py`. Provider adapters own real remote reads, CAS/If-Match or verified single-writer exclusion, writes and post-write readback.

## Operations

1. `ALLOCATE_INTERACTION`: before substantive work for a newly accepted external user turn, read canonical state and remote revision, verify CAS/single-writer ownership, compute S+1 internally and open exactly one interaction event for that S.
2. `RESUME_INTERACTION`: if the same turn_id is OPEN/INTERRUPTED/TRANSFERRED, reuse the same S. Do not allocate another S.
3. `COMMIT_MATERIAL`: require an immutable tool/event ledger proving material change; compute M+1 internally; bind that M to the current open S.
4. `CLOSE_INTERACTION`: terminal response closes/updates the same interaction event and never increments S or M.
5. Every mutation is followed by independent provider readback. A receipt without changed remote revision and verified readback is not committed.

## Hard gates

- Direct semantic mutation of `interaction_seq`, `material_seq` or `visible_ref` outside this writer is prohibited.
- Caller-supplied `next_S` or `next_M` is prohibited.
- Every user turn has exactly one S receipt.
- Every material checkpoint has exactly one M receipt causally bound to the current S.
- A non-material turn increments S once and does not increment M.
- Unknown/ambiguous provider outcome MUST be reconciled remotely before retry; never retry blind.
- The full append-only cross-surface interaction ledger is implemented by the later dedicated ledger backlog item; this writer already requires the per-turn interaction identity/receipt needed by that ledger.

## Failure semantics

At minimum: `G16_TX_REMOTE_STATE_STALE`, `G16_TX_SINGLE_WRITER_OR_CAS_REQUIRED`, `G16_TX_OPEN_TURN_ALREADY_EXISTS`, `G16_TX_CAUSAL_S_MISMATCH`, `G16_TX_MATERIAL_EVIDENCE_REQUIRED`, `G16_TX_POSTWRITE_READBACK_REQUIRED`, `G16_TX_REMOTE_REVISION_NOT_ADVANCED`.


## First-Handoff bootstrap

Profile: `FIRST_HANDOFF_BOOTSTRAP_V1`. Core: `scripts/handoff_bootstrap.py`.

When no explicit Handoff URL is supplied in the current Chat/Work/Codex context, G16 MUST create a brand-new canonical Handoff for that context. Existing project-bound Handoffs, registry matches, memory, bare IDs or inferred continuity do not authorize reuse.

The adapter MUST:
1. resolve zero existing canonical Handoffs;
2. generate the Handoff ID inside G16;
3. create one seed state at S=0/M=0 using create-only/CAS or verified single-writer exclusion;
4. post-create read back the exact state and prove canonical Handoff count equals one;
5. invoke `ALLOCATE_INTERACTION` on that read-back state so the first external turn becomes S=1/M=0;
6. invoke normal `COMMIT_MATERIAL` if the first turn commits material state, producing M=1 causally bound to S=1.

S=0/M=0 is internal initialization and is never the final human-visible reference. An explicitly supplied Handoff URL is the only continuation authority. If that URL cannot be resolved, it is not auto-replaced. Without an explicit URL, even one or many discoverable prior Handoffs are ignored and a new Handoff is created. An ambiguous create is reconciled against the same generated ID before retry; creating a second ID first is prohibited. Provider write unavailability is a separate blocker from absence of a prior Handoff.
