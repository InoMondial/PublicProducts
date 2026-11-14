# INC_G18_PERSIAN_GENERATED_PROSE_LEADING_TOKEN_V1

Status: Stage-30 candidate hard gate.
Owner: G18 / CHAT1-SKL-001.
Normative source: `INC_BIDI_SEMANTIC_COLLECTION_LAYOUT_V1` + `INC_BIDI_LAYOUT_TYPOGRAPHY_V1`.

## Runtime executor rule — HARD GATE
When G18 is invoked as the human-conversation/output executor and the intended natural-language block is Persian/RTL, every assistant-generated natural-language block MUST begin with a Persian/Arabic-script strong character. This is an absolute lexical start rule for generated Persian prose, headings, labels, numbered records and bullets. A leading RLM/LRM/isolate control does NOT satisfy this rule. If exact byte-preserved source/data cannot be rewritten, isolate it as a standalone quoted/code/data block rather than letting it lead a generated Persian prose block.

A generated Persian sentence, heading, structured-record label, bullet/list payload, table title or Persian table header MUST NOT visibly begin with:
- a Latin/English word;
- an ASCII digit;
- a model/product/version token;
- a Skill/Agent ID such as `G18`;
- inline code or acronym.

Rephrase instead, for example:
- `در G18 ...` instead of `G18 ...`;
- `در مرحله ۳۰ ...` instead of `Stage 30 ...`;
- `مدل GPT-5.6 ...` instead of `GPT-5.6 ...`;
- `مورد ۱ ...` instead of `1) ...`;
- `ردیف ۱ — ...` instead of `NUM# 1 — ...` for Persian structured records.

This rule exists because current Chat rendering may apply first-strong direction when no native block-direction control is exposed. Semantic RTL classification remains authoritative, but Persian-first lexical starts are the mandatory portability guard for assistant-generated Persian prose.

Exceptions: byte-preserved quotations/source text, URLs, IDs, hashes, code, filenames/paths, genuinely English blocks, and user-supplied text that must not be rewritten. These are isolated as LTR/data runs rather than used to lead Persian generated prose.

## Persian Chat collection rule
For current Chat Web:
- do not use Markdown bullets as the default Persian collection renderer;
- use Persian-led structured records or short paragraphs;
- visible Persian structured-row reference label is `ردیف` and numbering uses Persian-led forms such as `ردیف ۱`; machine semantic key remains `NUM#`. Do not visibly prefix Persian structured records with `NUM#`;
- Persian table titles and Persian headers begin with Persian script;
- if a Persian Markdown table is used, place the semantic row-reference column source-last for the currently verified renderer so the visible `ردیف` column is expected on the right;
- if current renderer behavior is not visually verified, fall back to structured records.

## Pre-send validation
Block send with `PERSIAN_GENERATED_BLOCK_LTR_PREFIX_PROHIBITED` if any assistant-generated semantically Persian natural-language block visibly begins with Latin/ASCII digit/code/model/ID. Rewrite to a Persian-first lexical start before send. Presentation-layer RLM by itself is insufficient.

This contract is self-contained enough for runtime execution; G18 does not need to recursively invoke G0 or another Skill to obtain these rules.
