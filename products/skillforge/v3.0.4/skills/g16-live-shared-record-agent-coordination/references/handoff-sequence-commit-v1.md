# G16 canonical Handoff sequence commit v1

Contract: `INC_G16_HANDOFF_SEQUENCE_COMMIT_V1`.

`continuity_seq` is the semantic Handoff commit counter. It is independent from provider file-version numbering. It increments exactly once for each successfully committed material Handoff checkpoint and does not increment for read-only refreshes.

Material checkpoint examples: Skill/policy changes; governed artifact publication; execution/work-unit changes; blocker/owner-gate changes; durable progress changes; cross-surface dispatch/result; any state future surfaces must know.

Required write receipt fields:
- `handoff_checkpoint_mode`
- `material_project_change_detected`
- `handoff_seq_before`
- `handoff_seq_after`
- `remote_revision_before`
- `remote_revision_after`
- `handoff_write_receipt_id`
- `post_write_readback_verified`

Invariants:
1. `READ_ONLY_REFRESH`: material change is false; seq before == seq after == current continuity sequence; current-cycle canonical read-back is verified.
2. `MATERIAL_WRITE_COMMITTED`: material change is true; seq after == seq before + 1; current continuity sequence == seq after; remote revision after differs from before; write receipt exists; post-write read-back is verified.
3. Unknown write outcome is reconciled before retry; never pre-increment twice.
4. One material checkpoint creates one semantic increment, regardless of provider-internal version numbering.
5. A provider revision advance with unchanged semantic sequence on a material write is nonconformant.
