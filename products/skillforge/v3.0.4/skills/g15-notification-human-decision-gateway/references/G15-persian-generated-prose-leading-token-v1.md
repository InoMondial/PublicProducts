# G15 Persian Generated-Prose Leading-Token Contract v1

Status: Stage-30 candidate hard gate.
Normative cross-cutting source: `INC_BIDI_SEMANTIC_COLLECTION_LAYOUT_V1`.

## Runtime executor rule
When G15 is invoked independently as the notification/report executor, it MUST enforce Persian-first lexical starts for every generated semantically Persian sentence, heading, list item, report label and Persian table heading.

Generated Persian human-facing text MUST NOT begin with a Latin word, ASCII digit, model/product/version token, Skill ID, acronym or inline code when safe rewriting is possible.

Use Persian lead-ins such as `در G18 ...`, `در مرحله ۳۰ ...`, `مدل GPT-5.6 ...`, `مورد ۱ ...`.

Exact quoted/source text, machine IDs, code, URLs, hashes, filenames/paths and genuinely English blocks are exceptions and remain isolated data/LTR runs.

## Teams rendering
For native Teams HTML:
- Persian generated containers use `lang="fa" dir="rtl"`;
- Persian-generated prose still begins with Persian script so fallback/plain-text clients remain safe;
- do not allow the first item token to decide collection direction;
- visible Persian row-reference label is `ردیف`, while the semantic machine key remains `NUM#`;
- if native list/table rendering is not verified, fall back to Persian-led paragraphs/numbered blocks.

Failure code: `G15_PERSIAN_GENERATED_BLOCK_LTR_PREFIX_PROHIBITED`.
