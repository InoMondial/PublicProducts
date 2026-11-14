# Cross-surface interaction ledger v1

Contract: `INC_CROSS_SURFACE_INTERACTION_LEDGER_V1`.
Cross-cutting owner: G0. Runtime coordinator: G16. Storage/logging authority: G11/G17.

## Purpose

Persist complete conversational continuity without bloating the canonical Handoff.

## Event model

- Every S allocated by the G16 transactional writer has exactly one immutable `ALLOCATED` record.
- Lifecycle transitions are appended as immutable records using `OPEN`, `INTERRUPTED`, `COMPLETED`, `BLOCKED`, or `TRANSFERRED`.
- Every record includes project ID, Handoff ID, release ID, S, surface, conversation/thread reference, timestamp and causal M references.
- Structured knowledge delta fields include decisions, approvals/rejections, requirements, evidence refs, open questions and resume point.
- Records are hash chained. Duplicate replay and duplicate S allocation fail closed.
- Secret replication is prohibited. Classification/redaction is required before append.
- Handoff holds only a bounded recent index; the full append-only ledger is routed through the active release ledger/G11-G17 store.
- Authorized resume retrieves only latest projections newer than `last_seen_S`; it does not require reading the full source conversation.

Executable core: `scripts/interaction_ledger.py`.
