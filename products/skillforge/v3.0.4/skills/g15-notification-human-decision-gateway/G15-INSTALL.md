# G15 v4.3.1 — Installation

## Governed package
Install only the exact current ZIP from the canonical `deploy/` folder or its byte-identical immutable GitHub Release asset after release closure.

## Expected identity
- Technical Skill name: `g15-notification-human-decision-gateway`
- Display name: `G15-Notification_Human_Decision_Gateway`
- Stable ID: `G15-SKL-001`
- Version: `4.3.1`
- Lifecycle: `candidate` until governed promotion closes.

## Mandatory runtime behavior
- Default production destination is derived from the final G15 priority: HIGH/MED/LOW map only to their canonical G15 priority-channel references.
- A different destination is legal only when the user explicitly requested it and G15 receives attributable out-of-band authorization for the override.
- Producers cannot self-authorize destination overrides.
- `INC_G15_TEST_CHANNEL` is restricted to genuine transport/integration/acceptance tests.
- Ordinary governed Teams messages require canonical renderer `G15_TEAMS_NATIVE_V1` and `html_content`; flat/plain/Markdown/ad-hoc fallback is prohibited.
- Missing/mismatching resolved route or render evidence blocks `SENT_COMPLETE`.

## Package shape
The ZIP contains exactly one top-level directory named `g15-notification-human-decision-gateway/`, with `SKILL.md` at its root. It must not contain `deploy/`, `dist/`, `evidence/`, `__pycache__/`, credentials, tenant IDs, or generated `.pyc` files.

## ChatGPT product boundary
Use the Skill upload/install surface currently exposed by the user's ChatGPT plan/workspace at installation time. Product UI availability must be re-checked against current official OpenAI guidance rather than hard-coded into this package.

## Microsoft runtime boundary
The default controlled decision path is a normal Teams post plus same-thread replies. Native Approvals and response-capable Adaptive Cards remain optional capability-gated enhancements. Current owner-reply discovery is externally scheduled by the central Scheduler/Dispatcher timer; G15 does not create its own timer.
