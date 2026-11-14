# G15 Notification & Human Decision Gateway v4.3.1 — Validation Status

Date: 2026-08-18  
Stable ID: `G15-SKL-001`  
Technical name: `g15-notification-human-decision-gateway`  
Build classification: `FULL / ROUTER / S4 / T4`  
Lifecycle: `Candidate`

## Current result
**MANDATORY ROUTING + CANONICAL TEAMS REPORT STYLE: SOURCE/RUNTIME ENFORCEMENT VERIFIED**  
**VERSION AUTHORITY: v4.3.1 PATCH — accepted v4.3.0 bytes remain immutable**  
**IMMUTABLE v4.3.1 RELEASE / G1-G01 PRESERVATION / INSTALL-TIME PLATFORM GATE: OPEN**

The owner supplied production evidence showing two classes of bypass: a flat/plain Usage report that did not follow the G15 report information architecture, and notification traffic whose destination was selected outside the mandatory priority-channel policy. v4.3.1 converts those previously declarative requirements into executable admission and completion gates.

## Mandatory routing controls
Unless the user explicitly requests another destination, final G15 priority determines the only legal default production route:
- HIGH → `INC_G15_PRIORITY_HIGH_CHANNEL`;
- MED → `INC_G15_PRIORITY_MED_CHANNEL`;
- LOW → `INC_G15_PRIORITY_LOW_CHANNEL`.

A producer, Work, Agent, Skill, scheduler, project or prompt cannot authorize its own destination override. A noncanonical route requires an attributable explicit user request supplied to G15 as out-of-band runtime authorization. `test_mode=true` alone cannot send production traffic to the test channel; `INC_G15_TEST_CHANNEL` is reserved for genuine transport/integration/acceptance tests.

## Mandatory rendering controls
Every governed Teams REPORT/MESSAGE/completion/failure/audit/status payload must pass the canonical renderer contract before send:
- renderer ID `G15_TEAMS_NATIVE_V1`;
- transport content field `html_content`;
- semantic G15 subject identity;
- outcome-first result;
- Project Context;
- scan-friendly categorized details;
- Quick Links when applicable;
- explicit Next Step;
- Project Progress;
- final bilingual Search Tags;
- no flat/plain-text, Markdown-layout, table-layout or producer-owned ad-hoc fallback.

Post-send completion also requires read-back of the expected resolved Team/channel/container when runtime identities are known. Missing or mismatching route evidence blocks `SENT_COMPLETE`.

## Deterministic validation
Latest v4.3.1 validation on PR #158:
- Python 3.12 compile: PASS;
- source contract validator: PASS;
- historical-compatible regression: **87/87 PASS**;
- v4.3.1 mandatory route/style regression: **15/15 PASS**;
- historical v4.3 compatibility entrypoint: **15/15 PASS**;
- repository single-writer guard: PASS;
- independent single-writer workflow: PASS.

Two historical expectations are deliberately superseded and therefore excluded from compatibility counting: the obsolete v3 HTML-table report layout and the old behavior where `test_mode=true` alone automatically selected the test channel.

## v4.3.1 regression coverage
The v4.3.1 suite proves:
- LOW/MED/HIGH default destination mapping;
- producer self-override rejection;
- explicit-user override authorization and required reason;
- test-channel isolation;
- canonical renderer identity and `html_content` requirement;
- rejection of a flat Usage-monitoring report matching the observed failure class;
- pre-send rejection of route tampering;
- post-send failure when actual Team/channel evidence is absent or mismatched;
- post-send PASS when exact route evidence is present;
- single-writer rejection when a producer both emits `INC_NOTIFICATION_EVENT_V1` and directly writes Teams.

## Package gate
The v4.3.1 candidate package must be rebuilt after the final source freeze. Acceptance requires exact deploy metadata, deterministic ZIP, full source validator, clean extraction, extracted compile, extracted full validator, 87/87 historical-compatible tests and 15/15 mandatory route/style tests. The package is not promoted until those exact-byte gates are closed.

## Live Teams boundary
Historical live Teams send/read-back and exact-thread behavior from v4.3.0 remains valid transport evidence, but v4.3.1 requires a fresh acceptance message for the new mandatory route/style behavior before final release closure. The acceptance transport belongs in `INC_G15_TEST_CHANNEL`; production priority channels are not used for test traffic.

## Remaining promotion gates
1. rebuild and remotely reconcile the exact v4.3.1 install ZIP after this source freeze;
2. merge authoritative v4.3.1 source/package to `main`;
3. create/verify immutable tag + GitHub Release Asset `artifact/G15-SKL-001/v4.3.1` with remote byte read-back;
4. execute applicable G1/G01 high-value SharePoint preservation and retention proof;
5. perform a fresh live Teams acceptance/read-back for the observed Usage-report failure class;
6. keep ChatGPT install/platform scan as a separate install-time gate and never claim it without actual platform evidence.

## Promotion statement
`V4.3.1_ROUTE_STYLE_ENFORCEMENT_VERIFIED — READY_FOR_FINAL_PACKAGE_REBUILD`
