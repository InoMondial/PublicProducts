# live-shared-record-agent-coordination protocol v0.1.0

## 1. Canonical topology

The protocol uses a star topology:

```text
              Worker A
                 |
Worker B ---- Manager ---- Worker C
                 |
               User
```

The manager is the only global coordinator. It may work itself and may dispatch multiple independent work units concurrently.

## 2. Required session fields

Each coordination session has:
- `coordination_session_id`
- `project_ref`
- `record_ref`
- `manager_actor_id`
- `record_provider`
- `record_version`
- `started_at`
- `timeout_at`
- `status`

## 3. Event schema

Every immutable event must contain at least:

```json
{
  "event_id": "EVT-...",
  "timestamp": "ISO-8601",
  "coordination_session_id": "COORD-...",
  "project_ref": "PRJ-...",
  "actor_id": "agent-or-user-id",
  "environment_id": "host-or-vm-or-cloud-id",
  "session_type": "host-local|guest-vmconnect|guest-rdp|cloud|other",
  "parent_event_id": "EVT-...|null",
  "turn_token": "TURN-...",
  "coordination_manager": "actor-id",
  "work_unit_id": "WU-...",
  "action_owner": "actor-id|null",
  "listeners": ["actor-id"],
  "status": "READY|EXECUTING|RESULT|WAITING_FOR_AGENT|WAITING_FOR_USER|BLOCKED|COMPLETE|CANCELLED",
  "action": "short machine action",
  "input_summary": "bounded summary",
  "result_summary": "bounded summary|null",
  "waiting_for": "actor/event/evidence|null",
  "next_expected_evidence": "bounded evidence contract|null",
  "resource_scope": ["resource/ref"],
  "parallel_safe": false,
  "safety_scope": "bounded safety limits",
  "lease_expires_at": "ISO-8601|null",
  "record_version_seen": "provider version/etag|null",
  "governance_refs": ["G16", "CHAT1-SKL-001"],
  "conversation_output_target": "G18",
  "access_route_used": "CONNECTED_TOOL|SURFACE_NATIVE_BROWSER|EXTERNAL_BROWSER|NONE",
  "access_route_reason": "bounded reason",
  "recommended_execution_profile": {
    "contract": "INC_G16_EXECUTION_PROFILE_RECOMMENDATION_V1",
    "availability_state": "VERIFIED|UNVERIFIED",
    "model": "exact host-exposed model name",
    "reasoning_effort": "exact host-exposed effort label",
    "minimum_floor": true,
    "factor_levels_0_4": {
      "semantic_complexity": 0,
      "ambiguity_novelty": 0,
      "reasoning_depth": 0,
      "change_blast_radius": 0,
      "tool_orchestration": 0,
      "context_dependency_load": 0,
      "verification_burden": 0,
      "consequence_irreversibility": 0,
      "long_horizon_recovery": 0,
      "surface_brittleness": 0
    },
    "score_0_100": 0,
    "complexity_class": "ROUTINE|STANDARD|COMPLEX|CRITICAL|FRONTIER",
    "confidence": "LOW|MEDIUM|HIGH",
    "why_not_lower": "bounded reason",
    "why_not_higher": "bounded reason",
    "escalation_triggers": []
  }
}
```

Optional fields may add evidence/artifact refs, error codes, retry metadata and user decision refs. Secret material is forbidden.

## 4. State machine

```text
READY
  -> EXECUTING
  -> RESULT
  -> READY                 (manager selects next work)
  -> WAITING_FOR_AGENT
  -> WAITING_FOR_USER
  -> BLOCKED
  -> COMPLETE
  -> CANCELLED
```

Worker state:
- READY: eligible for assignment.
- EXECUTING: owns one work unit under a valid lease.
- RESULT: immutable result/evidence appended.
- LISTENING is represented as READY or WAITING_FOR_AGENT with no active work-unit lease.

Manager state:
- always remains coordination authority until explicit transfer/cancel/complete.
- may enter WAITING_FOR_USER while workers remain READY/WAITING.
- may execute its own work unit.

## 5. Turn and lease rules

- `turn_token` scopes one coordination decision cycle.
- A worker execution requires `work_unit_id`, `action_owner`, `lease_expires_at`, `resource_scope`.
- Only one active owner per work unit.
- Parallel work units are allowed only when the manager marks all as `parallel_safe=true` and resource scopes are disjoint or otherwise proven non-conflicting.
- Lease expiry never authorizes automatic duplicate execution. The manager/observer first appends a status-check event.
- Ownership changes require an explicit manager event.

## 6. Anti-deadlock

If the configured poll interval produces six consecutive checks with no relevant event (default example: 6 × 30 seconds):
1. append `ANTI_DEADLOCK_QUERY`;
2. ask the current owner whether it is executing or waiting;
3. preserve current ownership;
4. do not start a duplicate worker;
5. escalate to manager/user only after the defined response timeout.

## 7. Live waiting

Preferred transport order:
1. event stream / webhook / thread event;
2. long-poll;
3. delta polling;
4. full-record polling only as declared degradation.

Delta cursor:
```json
{
  "last_seen_event_id": "EVT-...",
  "record_version": "etag-or-version",
  "byte_offset": 12345
}
```

If provider lacks byte-range/delta APIs, record `DELTA_UNAVAILABLE`; never claim low-cost polling.

Default live wait timeout: 30 minutes. On timeout append `WAIT_TIMEOUT`, preserve last known ownership/evidence, and stop gracefully.

## 8. Optimistic concurrency

For replace-only file providers:
1. read record and version/ETag;
2. parse only unseen events where possible;
3. construct one new event;
4. write with atomic conditional version match;
5. on conflict, re-read latest, verify event_id not already present, then retry bounded times;
6. read back and verify exact event.

Without provider-level atomic conditional write, concurrent record writers are unsafe. In that mode the manager must serialize record writes or block parallel record-writing.

## 9. Human-in-the-loop

Manager may:
- append `USER_INPUT_REQUIRED`;
- keep workers READY/WAITING;
- return to user without cancelling the team;
- append `USER_DECISION` after response;
- resume/assign new work.

Workers never ask the user independently unless manager delegates that specific role.

## 10. Wake-up limitation

A shared record is state, not necessarily transport. If a target surface cannot receive an event/push/webhook, the skill must say the agent cannot be awakened automatically. The user must activate/resume that agent. Once activated, it resumes from the shared record without the user relaying task content.

## 11. Evidence isolation

A result is accepted only when:
- `environment_id` matches target;
- `session_type` matches target;
- evidence was produced in that target session.

Example: VMConnect camera success does not prove RDP Meet success.

## 12. Example — parallel manager delegation

```json
{"event_id":"EVT-100","actor_id":"manager","work_unit_id":"WU-A","action_owner":"codex-host","status":"READY","resource_scope":["host/repo-A"],"parallel_safe":true}
{"event_id":"EVT-101","actor_id":"manager","work_unit_id":"WU-B","action_owner":"work-cloud","status":"READY","resource_scope":["cloud/test-B"],"parallel_safe":true}
{"event_id":"EVT-102","actor_id":"codex-host","work_unit_id":"WU-A","action_owner":"codex-host","status":"RESULT","result_summary":"completed host-side test"}
{"event_id":"EVT-103","actor_id":"work-cloud","work_unit_id":"WU-B","action_owner":"work-cloud","status":"RESULT","result_summary":"completed cloud-side test"}
{"event_id":"EVT-104","actor_id":"manager","work_unit_id":"WU-SYNTH","action_owner":"manager","status":"EXECUTING","action":"synthesize"}
```

## 13. Provider adapter minimum contract

```text
RECORD_RESOLVE
RECORD_READ_HEAD
RECORD_READ_DELTA
RECORD_APPEND_EVENT
RECORD_CONDITIONAL_REPLACE
RECORD_WAIT
RECORD_READBACK_VERIFY
RECORD_HEALTH
```

Provider capability flags:
- atomic_append
- conditional_write
- etag_or_version
- delta_read
- range_read
- event_wait
- webhook_or_push

The runtime must adapt honestly to missing capabilities.


## 14. Connector/browser routing

Mandatory routing order for Work/Codex/agent execution:
1. already-connected native plugin/connector/tool;
2. current surface internal/cloud browser;
3. external/local browser such as Chrome only as last resort.

A connected SharePoint/GitHub/other connector MUST be used instead of reopening the same service in a site when the connector can complete the action. If the needed site/account differs from the connected identity or the connector lacks the required capability, the surface-native browser is the next route. External browser fallback requires an explicit reason in `access_route_reason`.

Every executable inter-agent work order must carry `governance_refs: [G16, CHAT1-SKL-001]`. The accepted future human-output namespace is G18; G17 remains Data Governor.


## 15. Minimum execution-profile recommendation

Every execution-ready inter-agent work order must contain `recommended_execution_profile` conforming to `INC_G16_EXECUTION_PROFILE_RECOMMENDATION_V1`. The manager resolves the actual model/effort inventory exposed by the target surface, computes the lowest sufficient profile, records the complete factor vector plus score, and records the recommendation before delegation. Missing profile metadata makes the work order non-execution-ready.

The profile is a capability floor. If actual execution is below the floor, append `BELOW_RECOMMENDED_FLOOR_RISK`. If a stronger profile is used, record it as above-floor without claiming material gain unless an escalation trigger justifies it. Availability that cannot be verified is `UNVERIFIED`; model names or effort labels must never be fabricated.


## 16. Human dispatch notice and terminology

The umbrella for Chat, Work and Codex is `execution_surface`; an `execution_agent` is the actor operating on a surface. For every human-facing cross-surface work order, render a one- or two-sentence dispatch notice with target surface/agent, delegated action and current state. Do not duplicate the full work order in the notice.

Recommended machine fields when a human dispatch exists:
```json
{
  "human_dispatch_notice": {
    "target_surface": "Chat|Work|Codex|other_verified",
    "target_agent_role": "bounded role or null",
    "action_summary": "one bounded sentence",
    "status": "ABOUT_TO_EXECUTE|EXECUTING|COMPLETED|PARTIAL|BLOCKED"
  }
}
```
