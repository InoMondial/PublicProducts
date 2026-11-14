# G15 Teams Report Visual & Information Standard — Stage-30 BiDi Candidate

**Decision date:** 2026-09-16  
**Status:** CANDIDATE — independent G12/G13 validation required  
**Scope:** all G15-governed Teams reports/notifications and mixed Persian/English owner-facing output

This standard supersedes the prior acceptance of imperfect Persian RTL as a permanent condition. It adopts `INC_BIDI_LAYOUT_TYPOGRAPHY_V1`.

## 1. Core layout rule — HARD GATE
Each visible semantic block is directional independently.

- Persian/Arabic-script first-strong block: RTL + right alignment.
- English/Latin first-strong block: LTR + left alignment.
- Unknown/dynamic block: first-strong / auto direction semantics.
- One message may contain both RTL/right-aligned and LTR/left-aligned blocks.
- Never force the whole bilingual message into one base direction.
- Keep logical character order; never reverse text visually.

Inline opposite-direction text must be directionally isolated so punctuation, numbers and neighboring runs do not spill across boundaries.

Machine identifiers, URLs, hashes, paths, IDs and code remain byte-clean LTR and must not contain persisted BiDi controls.

## 2. Teams rendering route — HARD GATE
Preferred certified route when the available transport supports it: **Adaptive Card schema 1.5+**.

For a Persian card/container:
- `rtl: true`;
- Persian `TextBlock` / `RichTextBlock` uses `horizontalAlignment: right`;
- Persian text starts the block whenever semantically possible.

For an English block/container:
- `rtl: false` when independently scoped;
- `horizontalAlignment: left`;
- English text starts the block.

Bilingual content is split into separate semantic blocks rather than alternating scripts repeatedly inside one paragraph.

If Adaptive Cards are unavailable on the active write transport, native Teams HTML is allowed only under the HTML fallback contract below.

## 3. Native Teams HTML fallback — HARD GATE
When `html_content` is the available transport:
- Persian semantic block uses `lang="fa"` and `dir="rtl"` where Teams preserves these attributes;
- English semantic block uses `lang="en"` and `dir="ltr"`;
- blocks are separated structurally;
- do not rely on unsupported CSS, JavaScript, Markdown tables or custom fonts;
- do not expose raw HTML source to the user;
- Persian-first block must not begin with a Latin technical token solely for decoration/status; put that token on its own LTR line or after Persian wording.

If live Teams rendering strips/ignores the required direction semantics and produces materially unreadable Persian, this fallback is **not certified**. G15 must return `TEAMS_BIDI_LAYOUT_NOT_CERTIFIED` rather than silently accepting malformed output.

## 4. Inline BiDi isolation
When inline mixed text is unavoidable:
- use direction-isolating markup when the renderer supports it;
- otherwise use presentation-layer Unicode isolates LRI/RLI/FSI closed by PDI;
- use FSI for runtime text with unknown direction;
- do not use LRO/RLO direction overrides for ordinary prose;
- never persist invisible controls inside canonical IDs/URLs/code/database values.

## 5. Information architecture
Every ordinary report follows this order where applicable:
1. meaningful title;
2. visible priority/category;
3. outcome-first status/result;
4. project context;
5. concise findings/details;
6. scan-friendly labeled blocks;
7. exact quick links;
8. explicit next step or no-action statement;
9. project progress;
10. final bilingual search tags.

Do not turn the body into one prose wall.

## 6. Typography and hierarchy
Teams controls final font rendering; G15 controls structure, direction and alignment where the surface exposes them.

Required:
- strongest available native title/subject;
- short paragraphs/lists;
- critical state near the top;
- Persian blocks right-aligned when supported;
- English blocks left-aligned;
- no dense mixed-script paragraph when it can be split into two blocks.

Do not claim a specific pixel/font size unless verified by the Teams host.

## 7. Tables and summaries
Markdown tables are prohibited in visible Teams reports.

Use labeled rows/blocks. If a richer Adaptive Card table is used, table/cell direction and horizontal alignment must be explicit and live-tested.

Long evidence belongs behind exact links.

## 8. Project context and progress
Resolve without fabrication:
- project name/stable ID;
- current stage/milestone;
- progress percentage when tracked;
- canonical message category.

If required context cannot be resolved, normal completion is degraded/incomplete.

## 9. Search tags
Final root-post block contains safe searchable English and Persian tags. Keep each language in its own directional block. Never place credentials, tokens, account/card numbers or secrets in tags.

## 10. Deep links
Use exact canonical links when available. Generic home/repository links do not substitute for a more exact object.

## 11. Post-send acceptance gate — HARD GATE
`SENT_COMPLETE` requires:
- correct route/channel;
- mandatory semantic blocks present;
- no Markdown/raw-HTML leakage;
- no required truncation;
- exact links when applicable;
- remote read-back;
- direction/alignment contract preserved for representative Persian and English blocks;
- live visual verification for release certification.

Source read-back alone is not sufficient evidence for visual BiDi correctness.

## 12. Mandatory Stage-30 live regression
Before this G15 upgrade can be certified:
1. send a Persian-only test block to the governed Teams test channel;
2. send an English-only block;
3. send a Persian-first mixed sentence with one English term;
4. send an English-first mixed sentence with one Persian phrase;
5. test numbers, punctuation, URL and version boundaries;
6. test multiline Persian + English blocks;
7. test the real current G15 report template;
8. capture/read the actual rendered result on Teams Web/Desktop;
9. compare against `INC_BIDI_LAYOUT_TYPOGRAPHY_V1`;
10. require G12 independent PASS before promotion.

Any visibly left-aligned Persian block or right-aligned English block that should be independently scoped is a failure unless the host exposes no alignment control and a certified alternative renderer is selected.

## 13. Failure codes
- `UTF8_RTL_RENDERING_FAILED`
- `TEAMS_BIDI_LAYOUT_NOT_CERTIFIED`
- `TEAMS_PERSIAN_BLOCK_ALIGNMENT_FAILED`
- `TEAMS_ENGLISH_BLOCK_ALIGNMENT_FAILED`
- `TEAMS_MIXED_BIDI_ISOLATION_FAILED`
- `TEAMS_ADAPTIVE_CARD_RTL_REQUIRED_BUT_UNAVAILABLE`

## 14. Normative references
- `INC_BIDI_LAYOUT_TYPOGRAPHY_V1`
- W3C International bidirectional text guidance
- Unicode Bidirectional Algorithm isolation controls
- Microsoft Adaptive Cards 1.5 `rtl`
- Microsoft Adaptive Cards `horizontalAlignment`
- `G15-teams-reporting-standard.md`
- `G15-adaptive-card-bridge.md`

## 15. Freeze rule
The prior statement that imperfect Persian RTL is an accepted permanent limitation is superseded for the Stage-30 candidate. A renderer is certified only after actual visual validation on the target Teams client. Semantic routing/traceability/reply guarantees remain unchanged.
