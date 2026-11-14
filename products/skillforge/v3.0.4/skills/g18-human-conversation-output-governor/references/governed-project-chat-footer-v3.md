# Governed project chat footer v3

Contract: `INC_G18_GOVERNED_PROJECT_CHAT_FOOTER_V3`.

This contract supersedes v2 for runtime use. It is superseded for runtime use by `INC_G18_GOVERNED_PROJECT_CHAT_FOOTER_V4` in `governed-project-chat-footer-v4.md`.

Trigger when the conversation has active G16 project tracking and a canonical Handoff context. Every substantive final response uses a table-only body followed by exactly one absolute-final clickable Handoff alias. Tool-progress commentary is not a final response.

Mandatory terminal order:
1. Any substantive content tables.
2. Detailed G16/Handoff control table with at least: handoff ID, continuity sequence, visible reference, Handoff updated-at, run status, current work unit, last completed work unit, resume point and evidence revision.
3. Final four-row project-summary table containing current stage/completed stages, current-stage percent, weighted overall percent, next stage/state.
4. Absolute-final Markdown link whose visible text is ONLY the canonical Handoff reference and whose destination is the verified Handoff URL.

Exact Chat source form for the final line:
`<RLM>[<LRI><handoff_id> | S:<continuity_seq><PDI>](<verified-url>)`

Human-visible result: only `<handoff_id> | S:<continuity_seq>` is visible and clickable. The words `هندزآف`, `لینک`, `URL`, or the raw URL MUST NOT be visible in the footer. Nothing may follow this link.

The final alias must match the current-cycle G16 payload and the control-table Handoff ID/sequence. A bare URL, a labeled footer such as `هندزآف: ...`, or a visible raw URL is nonconformant. Unsupported percentages remain explicit RTL-first unknown/unavailable values and are never invented.
