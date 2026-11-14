# Durable Priority Feedback Contract

Preferred stable store reference: `INC_G15_PRIORITY_RULE_STORE`.

Key selection:
1. `notification_class`;
2. fallback `source_skill::event_type`;
3. never use sensitive free-text body as the durable key.

Accepted intent:
- absolute: HIGH / MED / LOW and Persian equivalents;
- relative: higher / lower and Persian equivalents.

Rules:
- up-prioritization always allowed;
- down-prioritization cannot violate mandatory HIGH floor;
- persist actor/timestamp/source-message reference when store supports it;
- if durable write/readback is unavailable, parse and acknowledge the request but return `TRACE_PERSISTENCE_DEGRADED`; do not claim cross-session learning.
