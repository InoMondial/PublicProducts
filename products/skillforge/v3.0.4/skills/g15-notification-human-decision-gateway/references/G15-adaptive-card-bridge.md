# G15 Adaptive Card Bridge Contract

**Current status:** OPTIONAL / FUTURE RICHER SURFACE — NOT THE CURRENT MANDATORY REPORT TRANSPORT.

The owner accepted the native Teams post/thread framework as the current frozen baseline on 2026-08-17. Adaptive Cards remain a candidate upgrade for stronger typography, RTL containers and interactive controls, but MUST NOT be treated as available or mandatory until a response-capable provider/bridge is implemented and live-certified in the target tenant.

Use an Adaptive Card only when a real Microsoft Teams provider is available for the required interaction mode.

Potential uses:
- `ACKNOWLEDGMENT`;
- `CHOICE`;
- `QUICK_CONFIRM`;
- `FORM`;
- richer report rendering when certified.

Required when used:
- visible actionable control(s) when interaction is claimed;
- structured response capture;
- responder and timestamp;
- optional comment/input capture;
- G15 dispatch/decision correlation and idempotency;
- update/close behavior when supported;
- preservation of the canonical G15 reporting information/traceability contract;
- same-thread or otherwise exact conversation correlation;
- no false claim that a static card or plain text message captured a structured response.

If the required interactive provider is unavailable, return an explicit capability state such as `INTERACTIVE_CAPABILITY_REQUIRED / TEAMS_ADAPTIVE_CARD_WAIT_FOR_RESPONSE_REQUIRED` and use the current native Teams thread-reply baseline when that baseline satisfies the workflow.

See:
- `G15-teams-reporting-standard.md`
- `G15-report-visual-standard.md`
- `G15-decision-reply-standard.md`
