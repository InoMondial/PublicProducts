# G16 governed project chat return state v2

Contract: `INC_G16_GOVERNED_PROJECT_CHAT_RETURN_V2`.
Counter authority: `INC_G16_HANDOFF_TRANSACTIONAL_WRITER_V1`.

Trigger whenever the conversation has active canonical project tracking/Handoff context. Every substantive user-visible project return must use current-cycle canonical state and writer receipts.

Required keys:
- `current_stage`, `completed_stages`, `current_stage_percent`, `weighted_overall_percent`
- `next_stage`, `next_state`
- `handoff_id`, `interaction_seq`, `material_seq`, `visible_ref`
- `handoff_url`, `handoff_updated_at`
- `run_status`, `current_work_unit`, `last_completed_work_unit`, `resume_from`
- `evidence_revision`, `evidence_timestamp`
- `current_turn_S_receipt`
- `material_M_receipts` (empty for non-material turns)
- `post_write_readback_verified`

Hard invariants:
1. `visible_ref` equals `<handoff_id> | S:<interaction_seq> | M:<material_seq>`.
2. The current-turn S receipt comes from `INC_G16_HANDOFF_TRANSACTIONAL_WRITER_V1` and its S equals `interaction_seq`.
3. The caller never calculates or repairs S or M.
4. A non-material turn has no new M receipt and preserves M.
5. Every material M receipt has the same current causal S and the terminal receipt M equals `material_seq`.
6. Post-write canonical readback is required before G18 renders the footer.
7. OPEN/INTERRUPTED/TRANSFERRED resume uses the same S for the same turn identity.
8. Percentages remain evidence-backed or null/unknown.
9. G18 renders this payload without recomputation.

Legacy `continuity_seq` and S-only visible references are historical fields and are not executable authority after dual-sequence cutover.
