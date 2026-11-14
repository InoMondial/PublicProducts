# G15 Canonical Teams Reporting & Reply Standard

**Status:** OWNER-FROZEN FOR CURRENT PHASE  
**Decision date:** 2026-08-17  
**Applies to:** all G15-governed Teams notification/report/decision producers  
**Normative keywords:** MUST, MUST NOT, SHOULD, MAY

This is the canonical Stage-2 standard for the currently accepted Teams framework. Implementation/enforcement changes in the G15 runtime follow in the next engineering stage.

## 1. Core rule
Every producer that needs to notify the owner through the governed Teams notification system MUST produce a G15-compatible event and MUST use the same information/reply framework. Producers MUST NOT invent independent production notification layouts or direct-write behaviors that bypass G15 governance once single-writer enforcement is implemented.

## 2. Mandatory root-post structure
An ordinary root notification/report MUST contain, in this order where applicable:

1. semantic icon + meaningful title;
2. visible priority + canonical category;
3. outcome-first status/result sentence;
4. Project Context;
5. concise categorized details/findings;
6. scan-friendly summary blocks/labeled rows when needed;
7. Quick Links to exact inspectable evidence objects when available;
8. explicit Next Step / owner action / `No action required`;
9. `PROJECT PROGRESS / پیشرفت پروژه`;
10. `Search Tags / هشتگ‌های جستجو` as the final root-post block.

Long evidence MUST be linked rather than pasted when it harms scanability.

## 3. Current accepted visual surface
The current mandatory baseline is a native Teams channel post/thread. Teams host limitations on custom font sizing and Persian RTL are accepted for the current phase.

MUST:
- use target-native formatted content (`html_content` or verified equivalent) when formatting is required;
- keep English and Persian blocks visibly separated;
- use native headings/bold/spacing/bullets for hierarchy;
- use clickable native links;
- preserve the frozen information architecture even when Teams normalizes heading sizes.

MUST NOT:
- send raw Markdown layout through plain-text production messages;
- expose `##`, `**`, fenced code, Markdown-link syntax or pipe-table markup;
- depend on unsupported CSS/JavaScript/custom font-size styling;
- claim pixel-perfect RTL/font control when the Teams client did not render it.

Adaptive Cards are a future optional richer surface, not the current mandatory baseline.

## 4. Report-type applicability

| Type | Typical use | Default priority | Additional mandatory content |
|---|---|---|---|
| `DECISION_REQUEST` | vote, approval, controlled choice | HIGH/MED by consequence | options, reply rules, Decision ID, closed-loop reply behavior |
| `FAILURE_CRITICAL` | crash, blocker, outage, serious risk | HIGH | impact, blocker, recovery/next action, exact evidence |
| `FAILURE_DEGRADED` | contained/recoverable failure | MED | affected scope, workaround/recovery, next action |
| `RELEASE_COMPLETION` | successful package/release/deployment completion | LOW normally; MED if owner review/action required | exact release/artifact/hash/evidence links |
| `PUBLICATION_COMPLETION` | GitHub/SharePoint/source publication success | LOW normally | exact object/commit/file links |
| `PHASE_COMPLETION` | ordinary phase/milestone closure | LOW normally; MED if owner gate/action required | phase outcome, progress, next gate |
| `VALIDATION_RESULT` | meaningful test/acceptance result | MED for major gate; LOW for routine nonblocking pass | scope, result, failed controls if any, evidence |
| `AUDIT_SYNC_RESULT` | audit/sync/reconciliation completion | LOW normally | affected systems, discrepancy status, evidence |
| `PRIORITY_RULE_UPDATE` | owner changes notification priority behavior | MED | interpreted rule/scope, safety floor, persistence status |
| `STATUS_REPORT` | scheduled/periodic report | LOW normally | period/scope, key changes, next action if any |

Mandatory safety floors in the notification catalog override defaults.

## 5. Priority rules
HIGH MUST be used for blockers, crashes, serious operational/security/legal/financial/data-integrity risks and failures that block required release/archive/backup/preservation.

MED MUST be used for important nonblocking review/action, meaningful degraded contained state, or owner gate when LOW would understate required attention.

LOW SHOULD be used for verified routine success, ordinary publication/archive/backup/validation/sync completion and ordinary phase closure with no blocking owner action.

A successful production release is not HIGH merely because it is production. Escalation requires an actual risk/blocker/mandatory review reason.

Durable owner feedback may adjust future priority within the rules of `G15-priority-feedback-contract.md`; mandatory HIGH floors cannot be lowered.

## 6. Mandatory vs conditional blocks
Always required for ordinary reports:
- meaningful title;
- priority/category;
- outcome/status;
- project context;
- next step or no-action statement;
- project progress;
- final bilingual search tags.

Conditionally required:
- Quick Links when evidence objects exist;
- impact/consequence when failure/risk/action affects the owner;
- decision options/controls/Decision ID for decisions;
- financial/legal/security context for governed high-consequence decisions;
- exact error/run/task reference for failures;
- hash/package/release evidence for release/package reports;
- priority-rule scope/persistence status for priority feedback.

## 7. Summary block semantics
When a summary matrix would help, render it in Teams as labeled blocks/rows rather than a Markdown table. Semantic fields are:
- Item;
- Summary;
- Impact / Consequence;
- Recommended Next Step;
- Open / exact link.

Short reports MAY omit fields that add no value.

## 8. Project context and progress
The producer MUST resolve, without fabrication:
- project name or stable project ID;
- current stage/milestone;
- progress percentage `0..100` when the project uses percentage tracking;
- canonical message category.

If required context cannot be resolved during an ordinary notification, completion is degraded/incomplete. HIGH emergency delivery may use `UNKNOWN` only with an explicit degraded-state indication.

## 9. Quick Links and traceability
Use exact canonical links whenever available. Prefer exact Teams thread, SharePoint file/folder, GitHub file/commit/PR/release/workflow run and Planner task links over generic home/repository links.

If the root Teams URL exists only after send, same-thread enrichment MAY be used to add the canonical thread link. The send is not fully trace-complete until required link/readback checks pass.

## 10. Search Tags
Bilingual safe hashtags are mandatory as the final root-post block. They identify at least skill/message type/project/category/priority plus event keywords. Secrets and sensitive free text are prohibited.

## 11. Decision and owner-reply behavior — HARD GATE
Every meaningful owner reply MUST close the feedback loop in the same root Teams thread.

Minimum acknowledgment:
- **What I understood**;
- **Current state**;
- **What happens next**.

For action-triggering replies:
`Owner Reply → Parsed Acknowledgment → Action Routed/Started → meaningful Progress update(s) when needed → Final Result + evidence/links`

Questions are answered in-thread when possible. Vote/choice replies state the selected option. Changes of mind state which previous choice was superseded when still pre-lock. Priority feedback states the interpreted rule/scope and persistence result.

See `G15-decision-reply-standard.md`.

## 12. Reply-monitoring architecture
Current selected discovery path: existing central Scheduler/Dispatcher timer. G15 creates no dedicated timer and no new G15-specific Power Automate timer flow.

The monitor performs cheap deterministic filtering before AI, loads only the exact parent context just in time, and excludes G15/system-generated outbound messages using an outbound-message ledger/idempotency controls.

Preferred future real-time upgrade: Microsoft Graph Change Notifications + lightweight receiver/filter. The existing timer remains the reconciliation/reliability path.

See `G15-reply-monitoring-runtime-architecture-decision.md`.

## 13. Post-send / post-reply validation gates
A root report cannot become `SENT_COMPLETE` until applicable checks pass:
- correct channel/route;
- correct title/priority/category;
- mandatory blocks present;
- exact required links present;
- no raw Markdown leakage;
- required content not truncated;
- root Search Tags block is final;
- remote readback performed.

A processed owner reply cannot become closed until applicable checks pass:
- exact parent correlation;
- reply not system-generated/duplicate;
- parsed intent retained;
- same-thread acknowledgment written;
- acknowledgment result/readback trace captured when available;
- action/result state accurately represented.

## 14. Machine-enforcement targets for Stage 3
The next G15 implementation stage MUST make these rules executable:
- single-writer/direct-send bypass detection;
- report schema/block validation;
- target-native renderer enforcement;
- no-Markdown-leak validation;
- post-send readback gate;
- owner-reply filter;
- parent-thread correlation;
- same-thread acknowledgment gate;
- outbound-ledger loop prevention;
- reply idempotency;
- timer reconciliation;
- priority feedback persistence/degraded handling;
- regression fixtures based on previously bad real Teams messages.

## 15. Related normative references
- `G15-report-visual-standard.md`
- `G15-decision-reply-standard.md`
- `G15-reply-monitoring-runtime-architecture-decision.md`
- `G15-mandatory-notification-catalog-v3.md`
- `G15-priority-feedback-contract.md`
- `G15-adaptive-card-bridge.md`
- `G15-logging-contract.md`

## 16. Freeze rule
This standard is the owner-approved current baseline. Producers and the next G15 implementation MUST target it. A future richer Teams surface may replace the visual transport only after live validation and explicit standard revision; the semantic, traceability and closed-loop reply guarantees remain mandatory unless explicitly changed.
