# G15 Decision & Owner-Reply Standard — Stage-2 Frozen Baseline

**Decision date:** 2026-08-17  
**Status:** FROZEN FOR CURRENT PHASE

## 1. Decision visual identity
- Waiting icon: `⏳`
- Title: `⏳ [G15][<PRIORITY>][<CATEGORY>] <clear question>`
- Decision ID: `G15-DQ-<UUIDv4>` for production decisions; deterministic test IDs are allowed only on explicit test surfaces.
- Language order: English first, Persian second for decision requests.

## 2. Reply codes
- 1–3 characters.
- Default two primary options.
- Genuine multi-choice: numbered `1..9`.
- Controls: `[X]` cancel, `[D]` defer, `[R]` re-ask.
- Optional text after the code is preserved as operator comment/instruction.
- Persian/Arabic numerals `۰..۹` / `٠..٩` are normalized to ASCII reply codes.

## 3. Every meaningful owner reply closes the loop — HARD REQUIREMENT
Every meaningful owner reply to a G15-governed Teams thread MUST receive a new response in the **same root Teams thread** after the reply is processed.

Minimum acknowledgment content:
1. **What I understood** — selected option, question, instruction, comment and/or priority feedback;
2. **Current state** — what changed, what did not change, or what is waiting;
3. **What happens next** — action, routing, clarification, blocker, no-op or expected follow-up.

A generic `Thanks`, `Received`, or silent state change is insufficient when a semantic result is available.

If the owner's reply is a question, answer it in the same thread when the answer is available. If the reply requests an action, acknowledge the interpreted action and then report meaningful progress/final outcome in the same thread.

## 4. Closed-loop execution sequence
For replies that trigger work, the preferred sequence is:

`Owner Reply → Parsed Acknowledgment → Action Routed/Started → meaningful Progress update(s) if needed → Final Result + evidence/links`

Do not create a new channel root post merely to report the result of a reply-triggered action unless a separate mandatory notification event independently requires one.

## 5. Reply intent parsing
A reply may contain one or more independent intents:
- vote/option selection;
- free-text comment;
- question;
- instruction/action request;
- priority feedback;
- change of mind;
- cancel;
- defer;
- re-ask;
- acknowledgment-only/free text.

Parse and preserve all applicable intents. Example: `2 lower the priority for these reports` contains both option 2 and a priority-feedback instruction.

## 6. Mutable decision
Latest valid pre-lock reply supersedes earlier choices. Preserve the full history. Lock immediately before irreversible execution.

When a valid pre-lock reply changes the decision, the same-thread acknowledgment MUST state that the earlier choice was superseded and identify the current choice.

A later post-lock reply is a new instruction; never pretend it reversed a completed external action.

## 7. Double confirmation
Require a second same-thread confirmation when:
- serious/material legal consequence applies;
- `high_consequence=true`;
- amount > 50 in the declared currency;
- material financial threshold is ambiguous and safe resolution is unavailable.

Second-stage codes: `[Y]`, `[N]`, plus `[X]`, `[D]`, `[R]`. Reuse the same decision ID.

During the second-confirmation stage, a new valid primary option code is accepted as a pre-lock change of mind; it supersedes the prior option and still requires Y/N final confirmation.

## 8. Financial detail
Include all available safe decision context: item/instrument/service, side, quantity, unit price, total/currency, fees/taxes, reference codes, platform, safe counterparty/account alias, analysis/recommendation, risks, deadline, source URL and support links.

Never expose credentials, OTPs, PINs, CVV, full card numbers, private keys, access/refresh tokens or recovery secrets.

Financial categories themselves imply the mandatory HIGH floor even when redundant producer flags are missing. For a material financial category, missing/invalid amount or missing currency uses the conservative second-confirmation path.

## 9. Owner-reply monitoring runtime
The decision/reply standard does not create its own timer. Runtime reply discovery follows `G15-reply-monitoring-runtime-architecture-decision.md`.

Current selected path:
- existing central Scheduler/Dispatcher timer;
- deterministic owner/reply/idempotency filtering before AI;
- just-in-time exact parent context loading;
- same-thread acknowledgment and result closure.

Preferred future real-time path:
- Microsoft Graph Change Notifications + lightweight receiver/filter;
- existing timer retained for renewal/reconciliation/recovery.

No new G15-specific Power Automate timer is required by this standard.

## 10. Delegated identity / loop prevention
When G15 writes to Teams using the same delegated Microsoft identity as the human owner, author identity alone cannot distinguish human replies from system-generated replies.

Every G15 outbound Teams message/reply MUST therefore be ledgered by returned message ID/correlation ID. Owner-input processing MUST exclude known G15 outbound IDs and duplicates before semantic interpretation.

## 11. Reply processing states
Recommended states:

`NEW → FILTERED_ELIGIBLE → PARSED → ACKNOWLEDGED → ACTION_ROUTED → COMPLETED`

Alternative terminal/degraded states include:

`IGNORED_SYSTEM_OUTBOUND | DUPLICATE | NO_ACTION_REQUIRED | DEFERRED | CANCELLED | BLOCKED | FAILED | REPLY_ACK_FAILED`

## 12. Truthful automation state
If autonomous reply monitoring is unavailable, do not imply that a reply was processed immediately. Record/return an explicit degraded state such as `REPLY_MONITOR_DEGRADED` or `REPLY_AUTOMATION_UNAVAILABLE`.

## 13. Persian and option presentation
`question_fa` and every Persian option label are mandatory for `DECISION_REQUEST`; do not duplicate English text as a fake Persian translation.

Persian and English blocks should remain visually separated. Current native Teams post limitations on precise RTL/font sizing are accepted under the frozen visual baseline; do not claim stronger rendering than the client actually provides.
