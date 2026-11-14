# G18 rendering of G16 execution reports

Runtime reference: `INC_G16_DURABLE_EXECUTION_PROGRESS_V1`.
Semantic/state owner: G16. Presentation owner: G18 / `CHAT1-SKL-001`.
Scope: the result of a governed executable command/Handoff, not ordinary conversation.

Consume the deterministic G16 machine report and verified checkpoint references.
Do not recompute weights, manufacture percentages, treat an old summary as current,
or infer zero progress from `Thinking failed` or a missing final response.

Render a compact table after every user-visible execution return: completed, partial,
blocked or failed. On recovery from abrupt host failure, render the current remote
checkpoint report before new mutations. Internal child reports must be persisted,
but they need not interrupt the autonomous parent with routine approval requests.
A dead process cannot be required to render; the next activated executor owns recovery.

Minimum table semantics: row reference, step, weight, verified completion, remaining
weighted contribution and state. Include earned contribution when it aids review.
Show command/plan revision, checkpoint time, failure location, outstanding steps and
precise resume point in the table or immediately adjacent compact text. Bind evidence
references to the relevant rows. Keep original machine IDs and numerical values clean.

For this owner's explicit table request, use a narrow Markdown table in Persian Chat;
long evidence/IDs may be adjacent short text rather than extra wide columns. Do not
emit raw HTML or claim rightmost-column geometry without verified rendering. Persian
headings and natural-language cells start in Persian. NUM# remains the machine row
key; a localized visible row header is permitted by the current Persian profile.

The baseline four-record project overview is not a cap on the number of executable
command steps. Do not truncate a ten-step command into four rows or drop requirements.
Avoid duplicating the same progress facts in a second overview. Other G18 safety,
BiDi, citation, source authority, confidentiality and final-Handoff rules remain intact.
Exactly one verified Handoff link remains at the absolute end.

Missing report, stale checkpoint, inconsistent totals or unsupported earned credit
is `EXECUTION_RESULT_REPORT_INVALID`, not successful command completion. A report
showing 100 percent for a bounded subcommand never implies 100 percent for SkillForge
or supersedes independent G12/G13, CI, deployment, installation or owner-only gates.
