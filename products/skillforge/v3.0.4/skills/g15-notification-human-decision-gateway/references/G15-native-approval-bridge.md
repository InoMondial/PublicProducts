# Native Approval Bridge Contract

Optional advanced surface. Use only when a Microsoft Teams Approvals / Microsoft Approvals provider is actually available.

Required:
- one G15 dispatch/decision ID maps to one Approval object;
- preserve Approval ID, approver(s), decision, status, timestamps, native comment;
- idempotency prevents duplicate Approval creation;
- exact Teams/Approval link is retained when available;
- upstream workflow receives the result;
- G15 itself does not execute purchase/payment/trade/delete/deploy/login actions;
- do not claim native Approval success when only a normal message was sent.

If unavailable: `INTERACTIVE_CAPABILITY_REQUIRED / NATIVE_MICROSOFT_TEAMS_APPROVALS_REQUIRED`.
