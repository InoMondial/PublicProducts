# INC_BIDI_LAYOUT_TYPOGRAPHY_V1

Status: Stage-30 candidate cross-cutting standard
Owner: SkillForge / G18 with surface adapters in G15 and DocForge
Scope: all human-facing Persian/Arabic-script or mixed RTL/LTR output produced by SkillForge-managed Skills, Chat/Work/Codex responses, Teams notifications, and formal documents.

## 1. Design basis
This standard follows Unicode Bidirectional Algorithm (UAX #9) and W3C Internationalization guidance.

Hard principles:
- base direction belongs to each semantic block/paragraph, not to an arbitrary whole message;
- semantic direction MUST be decided before serialization and MUST NOT be inferred only from the first visible token when generated prose already has a known intended language;
- use logical text order; never reverse source text to simulate RTL;
- isolate opposite-direction inline runs instead of allowing directional spillover;
- prefer format-native direction metadata on capable surfaces;
- use Unicode presentation controls only at the final presentation layer where markup is unavailable;
- never insert BiDi controls into machine identifiers, URLs, hashes, paths, code, database values, canonical source IDs or protocol payloads.

Normative external basis:
- Unicode UAX #9 rules P2/P3 explain that first-strong behavior determines paragraph level when no higher-level protocol supplies it;
- UAX #9 HL1 permits a higher-level protocol to set paragraph direction from context/semantics instead of blindly using first-strong;
- W3C recommends LRI/RLI/FSI with PDI for opposite-direction inline runs and RLM/LRM when a strong directional mark is needed;
- HTML-capable surfaces should use structural `dir` metadata rather than visual reversal.

## 2. Semantic block direction — HARD GATE
Every visible block is classified BEFORE rendering as exactly one of:

### SEMANTIC_RTL
Use when the natural-language sentence/paragraph is Persian or another RTL language, even when its first visible token is:
- a number;
- an acronym or Skill ID such as `G18`;
- an English product/model name;
- a version token;
- inline code;
- a list number or bullet marker.

Examples that remain SEMANTIC_RTL:
- `G18 اکنون نسخه جدید را اجرا می‌کند.`
- `Stage 30 اکنون در مرحله اعتبارسنجی است.`
- `1) این مرحله هنوز کامل نشده است.`

Rendering intent: RTL base direction + right/start alignment where the target surface exposes alignment control.

### SEMANTIC_LTR
Use when the natural-language block is genuinely English/LTR, even if a Persian translation or phrase appears inside it.

Rendering intent: LTR base direction + left/start alignment where supported.

### AUTO_UNKNOWN
Use only for genuinely unknown/dynamic/user-supplied text whose intended language is not known before render. In this state first-strong/`dir=auto` semantics are appropriate.

Generated assistant prose MUST NOT use AUTO_UNKNOWN merely because the first token is Latin or numeric.

## 3. Plain-text / Markdown base-direction seeding — HARD GATE
When the surface does not expose reliable block-level `dir`/alignment metadata:

For SEMANTIC_RTL blocks:
- inject U+200F RIGHT-TO-LEFT MARK (RLM) at the final presentation layer before the first visible content character;
- for Markdown list/bullet syntax, place the presentation RLM after the syntactic marker and before the visible payload when that parser preserves it;
- do not store the RLM inside canonical data, IDs, code, filenames, URLs, logs or machine-readable source fields.

For SEMANTIC_LTR blocks:
- use the natural LTR base direction;
- if an RTL token would otherwise become the first strong character and no block direction metadata exists, presentation-layer U+200E LEFT-TO-RIGHT MARK (LRM) MAY be used.

This presentation-layer seeding exists specifically to prevent a Persian sentence that begins with `G18`, `Stage 30`, a number or similar LTR/neutral token from being misclassified by a first-strong renderer.

## 4. Inline isolation — HARD GATE
When an inline run has a different direction from the surrounding block:
- markup-capable surface: use an isolating element/semantic container with explicit direction or `dir=auto`/`bdi` equivalent;
- plain-text surface: use LRI U+2066, RLI U+2067, or FSI U+2068, closed by PDI U+2069, at the final presentation layer only;
- punctuation that semantically belongs to the isolated run stays inside the isolate;
- prefer FSI for runtime text whose direction is not known in advance.

Prohibited for ordinary prose:
- LRO/RLO directional overrides;
- manual visual reversal;
- persistent insertion of invisible BiDi controls into machine identifiers or canonical source text.

## 5. Persian bilingual wording
For Persian human-facing output:
- Persian-first wording is preferred: `اعتبارسنج (Validator)` rather than `Validator (اعتبارسنج)`, unless the block itself is intentionally English/LTR;
- a SEMANTIC_RTL sentence may begin visibly with an English technical token only when needed; its block direction remains RTL via the surface adapter/presentation seeding rule;
- avoid repeated direction switching inside one sentence;
- long English/code tokens move to their own LTR block/line when practical;
- mixed-direction arrow chains on a Persian line are prohibited; represent sequences vertically as steps.

## 6. Tables and structured data
A table is allowed only when the target renderer has a proven direction/alignment contract for that exact surface.

If not proven:
- use numbered structured blocks instead of forcing a multi-column table;
- preserve semantic row referenceability (`NUM#`) without sacrificing readability;
- never use raw HTML in a surface that may display it literally.

## 7. Surface adapters
### Chat
- assistant-authored raw HTML presentation is prohibited;
- Persian Chat defaults to semantic paragraphs/structured blocks, not multi-column tables;
- classify every block as SEMANTIC_RTL, SEMANTIC_LTR or AUTO_UNKNOWN before serialization;
- SEMANTIC_RTL blocks that begin visibly with Latin/numbers receive presentation-layer RTL base-direction seeding when no native block direction control exists;
- embedded LTR runs are isolated where needed;
- do not claim pixel-perfect alignment if the Chat host does not expose explicit alignment control.

### Work / Codex
- surface-specific renderer behavior must be independently verified;
- do not copy Chat column-order assumptions;
- apply the same semantic block classification and inline-isolation rules.

### Microsoft Teams / G15
Current direct ChatGPT Teams connector capability must be treated separately from generic Teams platform capabilities.

When current transport is native Teams HTML:
- Persian semantic blocks use explicit `lang="fa"` and `dir="rtl"` on the nearest preserved block/container;
- English semantic blocks use `lang="en"` and `dir="ltr"`;
- bilingual content is split into distinct semantic blocks where practical;
- do not rely on unsupported CSS or Markdown;
- post-send read-back is mandatory and visual owner acceptance is required before renderer certification.

Adaptive Card is optional, capability-gated, not assumed available or free merely because Teams supports the schema:
- use only after the actual configured transport exposes a supported card-send path and license/tenant capability is verified;
- when available, schema 1.5+ may use `rtl: true` for Persian card/container content;
- Teams support or Microsoft documentation alone does not prove availability through the current G15 transport.

### DocForge / documents
For DOCX/PDF/HTML/document outputs:
- paragraph direction and paragraph alignment are independent properties and both must be set;
- SEMANTIC_RTL paragraph: RTL + right/start alignment;
- SEMANTIC_LTR paragraph: LTR + left/start alignment;
- a Persian paragraph that starts visibly with an English token remains RTL/right-aligned because semantic direction overrides first-visible-token heuristics;
- mixed inline runs are isolated without changing logical character order;
- tables use format-native bidi/table controls rather than reversed source order;
- generated documents must pass visual/rendered-page inspection, not only source-level checks.

## 8. Validation — HARD GATE
A Persian/mixed-language output cannot be marked PASS using source-text inspection alone.

Required layers:
1. semantic block classification validation;
2. serializer/native direction configuration validation;
3. remote read-back;
4. visual verification on the actual target surface for release certification;
5. mixed RTL/LTR regression fixtures.

Minimum regression cases:
- Persian-only paragraph;
- English-only paragraph inside a Persian response;
- Persian sentence visibly beginning with `G18`;
- Persian sentence visibly beginning with `Stage 30`;
- Persian sentence visibly beginning with a number;
- Persian-first sentence with one English term;
- English-first genuine English sentence with one Persian phrase;
- bullets where payload is Persian but first visible token is Latin;
- numbers and punctuation at boundaries;
- URL/path/hash beside Persian text;
- multiline Persian + English blocks;
- process/step sequence;
- Teams native HTML post;
- Teams Adaptive Card only when the actual transport exposes it;
- formal document paragraph/table.

## 9. Release gate
Any Skill/framework that emits Persian or mixed-direction human-facing text MUST compile this contract or a stricter compatible surface adapter. G12 independently validates representative live surfaces; G13 certifies release quality. A surface that has not been visually tested remains `NOT_CERTIFIED_FOR_BIDI_LAYOUT`.
