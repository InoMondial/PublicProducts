# G16 canonical Handoff topology registry v1

Contract: `INC_G16_HANDOFF_TOPOLOGY_REGISTRY_V1`.

## Bootstrap cardinality

`FIRST_HANDOFF_BOOTSTRAP_V1` is conversation/surface-context scoped, not project-binding scoped. A new Chat/Work/Codex context without an explicit Handoff URL creates its own canonical Handoff even if other Handoffs already exist for the same broader project. Existing Handoffs may be continued only by explicit URL. Topology uniqueness therefore applies per governed Handoff context/continuity identity, not as permission to auto-select one project-wide Handoff.

## Hard topology

- Exactly one canonical Handoff URL exists for one governed project.
- Checkpoints mutate the canonical Handoff in place; per-checkpoint Handoff files are prohibited.
- Each release has zero or one active work ledger.
- A project has at most one ACTIVE release at a time.
- A CLOSED release has no active ledger and exactly one immutable closure report.
- High-volume history is stored through G11/G17-backed structured storage, not by creating extra Handoff files.
- Duplicate canonical Handoff, duplicate active ledger, stale release identity or duplicate closure state fails closed.

Executable validator: `scripts/handoff_topology.py`.
