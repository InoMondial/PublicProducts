# Capability Boundaries — G15 v3.0.0

## Default operational surface
`DECISION_REQUEST` uses a normal Microsoft Teams post plus same-thread replies. This path is the live-certified baseline from v2.4 and remains the v3 default.

## Native Microsoft Teams Approvals
Use only when the runtime explicitly exposes a real Microsoft Approvals capability. Required evidence includes native approval ID/status, approver, timestamps, decision, comment, and correlation to G15 IDs. A plain text post is not a Native Approval.

## Response-capable Adaptive Cards
Use only when the runtime explicitly exposes a response-capable Teams Adaptive Card action. Capture structured response, responder, timestamp, optional comment, and correlation. A static card or plain text post is not a response-capable Adaptive Card.

## Capability gap
If a requested advanced surface is unavailable, return:
- `INTERACTIVE_CAPABILITY_REQUIRED`
- blocker `NATIVE_MICROSOFT_TEAMS_APPROVALS_REQUIRED`, or
- blocker `TEAMS_ADAPTIVE_CARD_WAIT_FOR_RESPONSE_REQUIRED`.

Do not silently downgrade governed authorization to free-text.
