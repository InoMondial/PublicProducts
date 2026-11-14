# INC_OWNER_CONVERSATION_BACKLOG_COVERAGE_V1

This P0 fail-closed contract is owned by G0 and consumes the interaction/event semantics owned by G16.

For every governed SkillForge maintenance interaction, derive a machine-readable `decision_delta` containing owner mandates, explicit backlog-registration requests, accepted system recommendations, discovered defects, unresolved questions and supersession/duplicate decisions. Each backlog-relevant decision receives a stable `decision_id` and preserves origin plus authority lineage from `INC_SKILLFORGE_FEEDBACK_INTAKE_V1`.

Before the terminal backlog-maintenance response, reconcile every backlog-relevant decision to exactly one disposition:

- `NEW_CHANGE_ID`
- `EXISTING_CHANGE_ID_AGGREGATED`
- `SUPERSEDED_WITH_REFERENCE`
- `DUPLICATE_WITH_REFERENCE`
- `EXPLICITLY_NOT_BACKLOG_WITH_OWNER_REASON`

Any missing mapping, duplicate mapping, missing Change-ID/reference, lost OWNER_MANDATE authority or ownerless non-backlog disposition is `UNMAPPED` and blocks a completeness claim.

The canonical `backlog_coverage_receipt` includes interaction S when available, all mappings, canonical backlog SHA before/after, exact canonical/private mirror parity, mapped Change IDs, `unmapped_count` and a receipt digest. A PASS requires `unmapped_count=0`, mirror parity and a verified post-write canonical SHA.

When the owner explicitly requires that every necessary item be registered, the coverage input must include the current interaction and unresolved accepted requirements from the active interaction ledger. Concurrent writers refresh the canonical backlog before mutation and reconcile equivalent writes before retry.

G18 may state that all necessary/agreed backlog items are registered only when a current `INC_OWNER_CONVERSATION_BACKLOG_COVERAGE_V1` receipt is PASS with `unmapped_count=0`. Conversation confidence, assistant memory or an unverified local copy is insufficient.

G12 tests missed-requirement detection, duplicate aggregation, concurrent-writer reconciliation, cross-chat accepted recommendations and owner-authority preservation. Independent G13 certifies the same receipt/evidence digest.
