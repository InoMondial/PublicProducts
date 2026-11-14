# G15 Mandatory Notification Catalog v3.0.0

This catalog defines event classes that MUST produce a G15 notification when they occur inside an active workflow. The listed priority is the default/floor before mandatory-HIGH safety policy and valid learned preferences are applied.

| Event class | Representative events | Default priority | Escalation | Required review evidence |
|---|---|---:|---|---|
| Human decision / authorization | determination requested; blocked waiting for user | HIGH | HIGH when blocking/time-sensitive | exact Teams thread + source link when available |
| Financial transaction | purchase, sale, trade, payment, transfer, refund, transactional commitment | HIGH | mandatory HIGH floor | amount/currency/counterparty + order/source + Teams thread |
| Serious legal / contract | legal approval, contract commitment, material legal consequence | HIGH | double confirmation when serious/high consequence | governing document/source + Teams thread |
| Security / login / destructive action | login authorization, security authorization, data deletion | HIGH | HIGH for high-consequence/destructive action | safe system reference + Teams thread; no secrets |
| Critical failure / outage | crash, blocked/stopped workflow, serious error, outage, data-integrity risk | HIGH | mandatory HIGH floor | error/run/task/source + evidence link |
| Required release/backup failure | required release/package/backup failed and blocks completion | HIGH | HIGH while completion blocked | failed job/run + exact artifact/task link |
| Recoverable/degraded failure | recoverable error, degraded service, contained partial failure | MED | HIGH if it becomes blocking/critical | error/run reference + next step |
| GitHub document/source publication success | document published, canonical file updated, source merged | LOW | MED for major milestone/production review | exact GitHub file/commit/PR link |
| Install package / release success | ZIP verified, tag/Release/Release Asset verified | LOW | MED for production milestone/review; HIGH on blocking failure | exact package/release/asset + hash evidence |
| SharePoint backup/archive success | recovery copy verified, canonical archive stored | LOW | MED if special review required; HIGH on required-backup failure | exact folder/file + verification reference |
| Registry/metadata reconciliation success | artifact/release/project registry reconciled | LOW | MED if discrepancy remains | exact registry file/commit |
| Project lifecycle | stage changed, milestone achieved, production-ready, major scope/deadline/risk change | MED | HIGH if blocked/critical decision required | project/work/task + progress block |
| Major test / validation gate | acceptance gate or validator result | MED | HIGH if failure blocks release; LOW only for routine nonblocking pass | exact test/evidence/report |
| Task/workflow completion | task complete, workflow complete | LOW | MED if follow-up/review/action required | task/Planner/Teams/GitHub as applicable |
| Scheduled/periodic report | daily/weekly/other requested report ready | LOW | MED if action/risk identified | report + summary table + links |
| Audit/validation/sync completion | audit, validation, Planner/Teams/SharePoint/GitHub sync complete | LOW | MED if discrepancy remains | exact run/evidence and affected-object links |
| Evidence bundle ready | support/audit/evidence package ready | LOW | MED if user review required | exact file/folder/commit |
| Priority rule updated | user requests HIGH/MED/LOW or higher/lower for a notification class | MED | mandatory HIGH floor still applies to future messages | rule key + source Teams reply; durable-store evidence when available |

## Mandatory format for each catalog event
Every delivered event notification includes:
1. clear title with priority and canonical category/type;
2. Project Context;
3. concise result/question and necessary supporting details;
4. exact one-click links to relevant Teams/SharePoint/GitHub/Planner objects when available;
5. `PROJECT PROGRESS / پیشرفت پروژه` with project, category, percentage and stage;
6. final `Search Tags / هشتگ‌های جستجو` with English and Persian hashtags.

## Hashtag dimensions
English hashtags cover `#G15`, message type, project, canonical category, priority and event-specific keywords. Persian hashtags mirror the same search dimensions. Use structured safe keywords; never expose credentials, payment/authentication secrets, sensitive body text, private keys or tokens.

## Batching and anti-spam
A mandatory event may not be silently suppressed. Multiple routine LOW successes may be batched only when each underlying event ID and exact link stays directly inspectable. Do not batch-suppress HIGH/MED decisions, failures, action items, or priority-feedback events.
