# G15 Reply Monitoring & Closed-Loop Runtime Architecture Decision

**Decision date:** 2026-08-17  
**Status:** DECIDED — CURRENT-PHASE BASELINE  
**Scope:** G15-SKL-001 / Teams owner-reply monitoring, acknowledgment, action routing and follow-up  
**Implementation owner:** central Scheduler/Dispatcher runtime + G15  
**Timer ownership:** external to G15; G15 MUST NOT create a dedicated timer

## 1. Why this document exists
This ADR preserves the architectural decisions made while validating the G15 Teams reporting and decision/reply experience. Future work on the central timer, Dispatcher, Microsoft Graph, Power Automate, Azure Functions or another event bridge MUST consult this document before changing the reply-monitoring design.

The immediate objective is simple: among many Teams notifications, detect only meaningful new replies authored by the owner, resolve the exact parent post, interpret the reply in context, and close the loop in the same Teams thread.

## 2. Live behavior proven during design
The manual pilot in `Example Team → PARAM_TEST_CHANNEL_NAME` proved the core non-event pipeline:

`owner reply → detect reply → resolve exact parent post → read parent context → interpret reply → post same-thread acknowledgment`

Observed owner test replies were correctly correlated to three different parent posts and each received a context-aware response in its original thread. This proves parent correlation and same-thread response behavior; it does **not** prove autonomous event delivery into ChatGPT/Dispatcher.

## 3. Options considered

### Option A — Existing central timer / reconciliation sweep
**Decision: SELECTED FOR CURRENT PHASE.**

Use the already-planned central Scheduler/Dispatcher timer. No dedicated G15 timer and no new G15-specific Power Automate flow is created.

On each central tick, the runtime checks G15-managed Teams channels for new candidate replies since the last cursor/watermark, applies cheap deterministic filtering, and sends only eligible owner replies into G15/AI processing.

Advantages:
- no additional scheduler or Power Automate dependency;
- reuses the central runtime architecture;
- predictable recovery and idempotency;
- AI receives only relevant replies, not every channel message.

Trade-off:
- acknowledgment latency is bounded by the timer cadence rather than true real time.

### Option B — Microsoft Graph Change Notifications + lightweight webhook receiver
**Decision: PREFERRED FUTURE REAL-TIME UPGRADE; NOT IMPLEMENTED NOW.**

Microsoft Graph supports low-latency change notifications for channel messages and replies by subscribing to `/teams/{team-id}/channels/{channel-id}/messages`. A webhook/receiver can filter events before any AI invocation.

Important: the Graph subscription itself can emit channel message/reply events; it is the lightweight receiver/bridge that MUST filter to owner replies before forwarding anything to G15/AI. Do not claim Graph performs an owner-only server-side sender filter unless that capability is separately proven.

A real-time upgrade should use:
`Teams → Graph Change Notification → lightweight receiver → owner/reply/idempotency filter → G15 → same-thread Teams response`

The central timer remains valuable as subscription-renewal/recovery/reconciliation infrastructure.

Primary Microsoft references:
- [Microsoft Graph — Get change notifications for messages in Teams channels and chats](https://learn.microsoft.com/en-us/graph/teams-changenotifications-chatmessage)
- [Microsoft Graph — Change notifications for Microsoft Teams resources](https://learn.microsoft.com/en-us/graph/teams-change-notification-in-microsoft-teams-overview)
- [Microsoft Graph — Reduce missing change notifications and removed subscriptions](https://learn.microsoft.com/en-us/graph/change-notifications-lifecycle-events)
- [Microsoft Teams connector — trigger behavior and root-message limitation](https://learn.microsoft.com/en-us/connectors/teams/)

### Option C — New Power Automate flow dedicated to G15 reply monitoring
**Decision: NOT SELECTED.**

Do not add another G15-specific Power Automate timer/flow while the central timer already exists. If Power Automate is later used as a shared platform bridge, that is a separate platform decision and must not silently create a second scheduling architecture for G15.

The legacy Teams trigger `When a new channel message is added` is unsuitable for reply monitoring because Microsoft documents that it fires only for root channel messages, not replies. A newer Teams trigger exists for a specified chat/channel, but reply behavior must be tenant-live-tested before it can replace the selected baseline.

### Option D — Microsoft Graph + Azure Event Hubs
**Decision: DEFERRED.**

This is a valid high-throughput delivery option but is unnecessarily heavy for the current G15 scale. Reconsider only if webhook throughput, reliability or enterprise event-stream requirements justify it.

## 4. Selected current architecture

### 4.1 Scheduler contract
G15 does not own scheduling. The central Scheduler/Dispatcher invokes a reply-monitoring job on each existing timer tick.

The timer cadence is a platform setting. G15 MUST work correctly at any supported cadence. A shorter cadence improves response latency; the architecture must not hard-code a separate G15 schedule.

### 4.2 Channel scope
The monitor reads only channels registered as G15-managed destinations/test surfaces. Current design includes the production HIGH/MED/LOW notification channels and explicitly registered test channels. Channel IDs come from the destination registry, not hard-coded skill prose.

### 4.3 Candidate filtering before AI
The monitoring layer MUST perform deterministic filtering before invoking G15/AI:

1. message is a channel **reply**, not a root post;
2. created/updated after the stored cursor or not yet present in the reply ledger;
3. author identity matches the configured owner identity;
4. message ID is not a G15/system-generated outbound message;
5. parent thread is G15-managed or otherwise explicitly eligible;
6. message is not already terminally processed.

Only after these gates pass is parent context loaded and the reply submitted to semantic interpretation.

### 4.4 Critical delegated-identity safeguard
In the current Teams connector, messages written by automation can appear under the same signed-in Microsoft user identity as the human owner. **Author-name/user-ID filtering alone is therefore insufficient and can create a reply loop.**

G15/Dispatcher MUST maintain an outbound-message ledger. Every message/reply created by G15 is recorded by returned Teams `message_id` and correlation ID. A candidate reply is treated as human-owner input only when:
- author matches owner; **and**
- its message ID is not in the system outbound ledger; **and**
- it is not otherwise marked/correlated as a G15-generated acknowledgment/progress/result message.

If a future bot/service identity is used, identity separation becomes an additional guard, not a replacement for idempotency.

## 5. Minimal reply event passed to G15
The monitor should pass compact metadata first, not entire channel history:

- `reply_message_id`
- `reply_text`
- `reply_author_id`
- `reply_created_at`
- `parent_message_id`
- `team_id`
- `channel_id`
- `reply_web_url`
- `monitor_cursor`

G15 then loads only the exact parent/thread context required to resolve project, category, priority, dispatch/decision/task correlation and execution state.

## 6. Intent classes
Every meaningful owner reply is classified into one or more of:

- vote / option selection;
- question;
- instruction/action request;
- comment/feedback;
- priority feedback;
- change of mind / superseding decision;
- cancel;
- defer;
- re-ask;
- acknowledgment-only/free text.

Multiple intents in one reply are preserved separately; e.g. `2 lower the priority for this report class` contains both a choice and priority feedback.

## 7. Mandatory same-thread closed loop
For every meaningful owner reply, G15 MUST post a response in the same root Teams thread.

Minimum acknowledgment contract:
1. **What I understood** — selected option/question/instruction/comment/priority request;
2. **Current state** — what changed or did not change;
3. **What happens next** — action, routing, wait state, blocker or no-op.

If execution is needed, the thread continues as:

`Owner Reply → Parsed Acknowledgment → Action Routed/Started → meaningful Progress update(s) when needed → Final Result + evidence/links`

A generic `Thanks`/`Received` alone is insufficient when a semantic result is available.

If the owner changes a valid pre-lock decision, G15 explicitly records the prior choice as superseded. If an irreversible action is already locked/executed, the later reply is a new instruction and MUST NOT be represented as reversing completed external work.

## 8. State and idempotency
Use `reply_message_id` as the primary idempotency key.

Recommended state progression:

`NEW → FILTERED_ELIGIBLE → PARSED → ACKNOWLEDGED → ACTION_ROUTED → COMPLETED`

Alternative terminal states:

`IGNORED_SYSTEM_OUTBOUND | DUPLICATE | NO_ACTION_REQUIRED | DEFERRED | CANCELLED | BLOCKED | FAILED`

The next timer tick MUST skip replies already at an appropriate terminal/acknowledged state unless a retry/reconciliation rule explicitly applies.

## 9. Cursor / reconciliation design
Maintain a per-channel high-water mark plus the reply ledger. Do not depend on a timestamp alone because delayed delivery/edit/retry scenarios can otherwise be missed.

A safe sweep uses an overlap window and deduplicates by message ID. This provides at-least-once discovery with exactly-once semantic processing as the target behavior.

## 10. Real-time upgrade path
When real-time response becomes a priority, implement Option B without changing the G15 semantic contract:

`Graph event → receiver → same deterministic owner/reply/system-ledger filters → G15`

The event path is the performance path; the existing timer remains the reliability/reconciliation path.

Graph subscriptions require lifecycle/renewal handling. The timer/Dispatcher is the natural location for subscription renewal and missed-event reconciliation if this upgrade is adopted.

## 11. Failure/degraded states
Required explicit states include:

- `REPLY_MONITOR_DEGRADED`
- `REPLY_AUTOMATION_UNAVAILABLE`
- `PARENT_CONTEXT_UNRESOLVED`
- `OWNER_IDENTITY_UNRESOLVED`
- `OUTBOUND_LEDGER_UNAVAILABLE`
- `REPLY_ACK_FAILED`
- `ACTION_ROUTING_FAILED`

G15 must not silently claim immediate or automatic processing when the monitoring bridge is unavailable.

## 12. Decisions frozen by this ADR
1. No new G15-specific Power Automate timer is created for reply monitoring in the current phase.
2. Existing central timer/Dispatcher is the selected current runtime path.
3. Only eligible new owner replies reach semantic G15/AI processing.
4. Parent context is loaded just-in-time after deterministic filtering.
5. Every meaningful owner reply closes the loop in the same Teams thread.
6. G15 outbound message IDs are ledgered to prevent loops when automation posts under the owner's delegated identity.
7. Microsoft Graph Change Notifications + lightweight webhook receiver is the preferred future real-time upgrade.
8. The timer remains the reconciliation/reliability path even after a future event-driven upgrade.

## 13. Revisit triggers
Re-open this ADR only when one of these occurs:
- central Scheduler/Dispatcher implementation changes materially;
- a supported inbound event bridge becomes available directly to the target AI runtime;
- Microsoft Teams/Graph trigger semantics materially change;
- message volume or latency requirements justify Event Hubs;
- a distinct bot/service identity replaces delegated owner-posting;
- owner explicitly changes the latency or interaction requirement.
