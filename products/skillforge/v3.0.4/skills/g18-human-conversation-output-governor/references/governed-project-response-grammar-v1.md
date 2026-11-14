# Governed project response grammar v1

Contract: `INC_G18_GOVERNED_PROJECT_RESPONSE_GRAMMAR_V1`.

This contract is the canonical reconciliation for SF-G18-006, SF-G18-008, SF-G18-010 and SF-G18-011. It supersedes any active wording that describes governed-project final output as absolute TABLE_ONLY.

## Canonical envelope

A substantive governed-project final response is:

`DIRECTIONAL_SEGMENT_TITLE + NUMBERED_TABLE_TITLE + TABLE ... + NUMBERED_CONTROL_TABLE + NUMBERED_FOUR_ROW_SUMMARY_TABLE + ABSOLUTE_FINAL_HANDOFF_ALIAS`.

Ordinary prose, bullets, numbered lists, Markdown H1-H6 headings and free-standing links outside tables remain prohibited. Structural directional segment titles, numbered table titles and the single terminal Handoff alias are the only non-table exceptions.

## Directional segment title

Persian/RTL source:
`<RLM><SEMANTIC_ICON> **<RTL_SEGMENT_TITLE>**`

English/LTR source:
`<SEMANTIC_ICON> **<LTR_SEGMENT_TITLE>**`

For multi-table segments, the segment title precedes the first numbered table-title/table block. For a segment containing exactly one table, its numbered table title may also serve as the segment title.

## Numbered table title

Every human-visible table has exactly one title immediately above it.

Persian/RTL source:
`<RLM><SEMANTIC_ICON> **جدول <ASCII_INTEGER> — <RTL_TITLE>**`

English/LTR source:
`<SEMANTIC_ICON> **Table <ASCII_INTEGER> — <LTR_TITLE>**`

The icon is presentation/navigation metadata outside the lexical title prefix. Therefore the lexical title still begins with `جدول N` or `Table N`.

Table numbering:
- starts at 1 in every assistant final response;
- increases contiguously with no gaps or duplicates;
- resets to 1 in the next assistant final response;
- is independent from row numbering.

Human cross-reference grammar:
- Persian: `جدول N، ردیف M`
- English: `Table N, Row M`

Optional durable internal cross-turn reference:
`<handoff_id>|S:<interaction_seq>|T:<table_serial>|R:<row_serial>`.
The internal durable form never replaces the simple visible human label.

## Row-reference preservation

Every table keeps the existing mandatory row-reference column. Persian Chat retains the owner-confirmed source-first `ردیف` serializer so the row-reference column renders on the right. Codex retains its separate source-last profile. This contract does not collapse surface-specific table serializers.

## Terminal Handoff is always on

Every substantive governed-project final response terminates with exactly one clickable canonical Handoff alias even under READ_ONLY, BACKLOG_ONLY, NO_MUTATION or NO_DIRECT_ACTION scope. Rendering the already-verified Handoff state is a read/display obligation and does not mutate S or M.

After dual-sequence cutover:
`<RLM>[<LRI><handoff_id> | S:<interaction_seq> | M:<material_seq><PDI>](<verified-url>)`

Before cutover, legacy S-only form remains supported. G18 never invents counters. If current canonical state cannot be verified, fail closed with `PROJECT_HANDOFF_STATE_UNAVAILABLE`; never substitute stale sequence data.

## Terminal tables

The penultimate table is the detailed G16/Handoff control table and exposes at least Handoff ID, Interaction S, Material M, visible reference, updated-at, run status, current/last work units, resume point and evidence revision.

The final table contains exactly four semantic rows: current stage + completed stages, current-stage percent, weighted overall percent, and next stage + state.

Both terminal tables participate in the same per-response table serial sequence.

## Validators

- `scripts/project_response_grammar.py` — shared deterministic grammar.
- `scripts/validate_project_segments.py` — title/table-body validation.
- `scripts/validate_project_chat_footer.py` — full terminal control/summary/Handoff validation.
- `scripts/validate_table_conformance.py` — row-reference/direction/alignment validation.

Failure codes include:
`PROJECT_RESPONSE_NON_TABLE_CONTENT`,
`PROJECT_TABLE_TITLE_MISSING`,
`PROJECT_TABLE_SERIAL_MISSING`,
`PROJECT_TABLE_SERIAL_DUPLICATE`,
`PROJECT_TABLE_SERIAL_GAP`,
`PROJECT_TABLE_SERIAL_LANGUAGE_PREFIX_INVALID`,
`PROJECT_TABLE_TITLE_NOT_ADJACENT`,
`PROJECT_TABLE_TITLE_GRAMMAR_CONFLICT`,
`PROJECT_TABLE_TITLE_LEXICAL_SERIAL_PREFIX_INVALID`,
`PROJECT_TERMINAL_HANDOFF_FOOTER_MISSING`,
`PROJECT_HANDOFF_RENDER_SUPPRESSED_BY_NO_MUTATION`,
`PROJECT_HANDOFF_STATE_UNAVAILABLE`,
`PROJECT_HANDOFF_FOOTER_NOT_ABSOLUTE_FINAL`,
`PROJECT_HANDOFF_FOOTER_SEQUENCE_FABRICATED`.
