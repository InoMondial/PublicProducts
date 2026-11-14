# Governed project chat footer v4

Contract: `INC_G18_GOVERNED_PROJECT_CHAT_FOOTER_V4`.

Runtime presentation grammar is now `INC_G18_GOVERNED_PROJECT_RESPONSE_GRAMMAR_V1` in `governed-project-response-grammar-v1.md`. Any older v3/v4 wording that implied an absolute TABLE_ONLY body is superseded by the canonical grammar.

Mandatory rules:
1. Structural directional segment titles and numbered table titles are allowed non-table structure; ordinary prose/bullets remain prohibited.
2. Every human-visible table participates in the per-response `جدول N` / `Table N` sequence.
3. The last two tables before the Handoff alias are the detailed G16/Handoff control table and the exact four-row project summary table.
4. Every substantive governed-project final response terminates with exactly one clickable canonical Handoff alias. This remains mandatory for READ_ONLY, BACKLOG_ONLY, NO_MUTATION and NO_DIRECT_ACTION scopes.
5. Footer rendering itself never mutates Handoff state and never increments S or M.
6. After dual-sequence cutover, render only `<handoff_id> | S:<interaction_seq> | M:<material_seq>` from current G16/provider-verified state. Before cutover, legacy S-only form remains supported.
7. Material turns require the current S receipt plus matching committed M receipt(s). Read-only turns still require current verified state and preserve M.
8. Missing/unverified current Handoff state fails closed with `PROJECT_HANDOFF_STATE_UNAVAILABLE`; stale/invented sequence rendering is prohibited.
9. Nothing may follow the terminal Handoff alias.

Exact dual-sequence Chat source:
`<RLM>[<LRI><handoff_id> | S:<interaction_seq> | M:<material_seq><PDI>](<verified-url>)`.

Validator: `scripts/validate_project_chat_footer.py --g16-state <current-project-return.json>`.
