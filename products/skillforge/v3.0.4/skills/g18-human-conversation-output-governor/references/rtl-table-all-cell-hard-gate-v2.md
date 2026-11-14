# RTL table all-cell hard gate v2

Contract: `INC_G18_RTL_TABLE_ALL_CELL_HARD_GATE_V2`.

This contract supersedes v1 for runtime use.

For every human-facing semantically RTL Markdown table on Chat:

1. Every header and every non-row-reference body cell starts in source with exactly one U+200F RIGHT-TO-LEFT MARK (RLM), immediately followed by a visible word in the table language's RTL script. The invisible RLM never satisfies the lexical rule by itself.
2. The `ردیف` cell is the only numeric-first exception and retains the separate exact row-reference form: one leading U+200F RLM followed immediately by the bare ASCII integer.
3. Every embedded opposite-direction visible technical run containing ASCII letters or digits is isolated as one semantic unit with exactly one U+2066 LEFT-TO-RIGHT ISOLATE (LRI) before the run and exactly one U+2069 POP DIRECTIONAL ISOLATE (PDI) after it. The isolate pair is presentation-only.
4. Compound technical references are isolated as ONE unit, not fragmented. Example semantic run: `HOF-... | S:125` is one LRI/PDI-isolated run so `|`, `:`, hyphens and digits keep their intended visual order. Because `|` is also a Markdown table delimiter, every literal visible pipe inside a table cell MUST be escaped in source as `\|`; the rendered cell still shows `|`.
5. Bare ASCII letters or digits outside an LRI/PDI pair are prohibited in non-row-reference RTL Chat table cells. This includes model names, versions, percentages written with ASCII digits, IDs, statuses, filenames and validator/error codes. Prefix with an RTL label and isolate only the technical value, for example: `مرجع: <LRI>HOF-... | S:125<PDI>`.
6. Markdown inline-code/backtick styling is prohibited inside human-facing RTL Chat table cells. It is not a BiDi isolation mechanism and previously produced unstable pills/neutral-boundary behavior. Use LRI/PDI isolation instead.
7. Do not wrap isolated technical runs in guillemets, ASCII quotes or parentheses merely for presentation. Neutral wrapper punctuation adjacent to an opposite-direction run is prohibited because it can re-enter surrounding RTL ordering. Use an RTL label plus colon followed directly by the isolated run.
8. Raw visible URLs are prohibited. Markdown link destinations may remain in source only when the visible link label itself satisfies this contract.
9. U+200E LRM, U+2067 RLI, U+2068 FSI, NBSP and any extra U+200F RLM are prohibited in Chat RTL table text cells. LRI/PDI are permitted ONLY as balanced, non-nested embedded LTR-run isolators after the required RTL-word-first start.
10. Every RTL table column is right aligned with `---:`. The `ردیف` column is the LAST source column and its values are sequential bare ASCII integers starting at 1. Header/body column counts match exactly.

The validator `scripts/validate_table_conformance.py` is fail-closed. It must reject:
- bare embedded ASCII alphanumeric runs outside LRI/PDI;
- unbalanced or nested isolate pairs;
- RTL-script content inside an LRI/PDI technical run;
- neutral wrappers immediately surrounding an isolated technical run;
- inline-code/backtick tokens in RTL table cells;
- raw visible URLs;
- any unescaped literal `|` inside an LRI/PDI technical run in a table cell;
- the previously established row-reference, alignment, numbering or lexical-start failures.
