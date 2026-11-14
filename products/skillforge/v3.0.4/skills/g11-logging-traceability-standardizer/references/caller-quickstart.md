# G11 Caller Quick Start — v4.4.2

Use this page from any Skill, Agent, Chat or Work that needs to log. Do not load the physical SharePoint schema.

## Normal call
Provide G11 only:

```yaml
producer_ref: <module or stable skill ref>
activity_id: <stable activity/run/correlation id>
status: SUCCEEDED
summary: <one concise factual outcome>
is_test: false
```

Defaults are `profile=LIGHT` and `verification=ASYNC`.

G11 handles redaction, IDs, typed semantics, writer-envelope compilation, queue transport and the physical `INC_LOG_STORE` mapping.

## Add records only when real
- Event: always one minimum outcome.
- Action: meaningful action/state transition only.
- Metric: actual measured/observed value only.
- Error: actual error/degradation only.
- Approval: actual approval state only.

Do not manufacture records just to populate every List.

## When durable verification is mandatory
Set:

```yaml
verification: REQUIRED
```

G11 owns the verification attempt. The caller does not poll SharePoint, wait for the hourly recurrence or implement a parallel read-back path.

Only `G11_PERSISTED_VERIFIED` permits a durable-persistence PASS claim. Queue acceptance is not durable persistence.

## Caller must never
- direct-write `INC_LOG_STORE` Lists;
- know/submit physical List or column names;
- build `INC_G11_LOG_ENVELOPE_V1` itself;
- poll `write-queue`;
- wait for an hourly tick;
- log each click/tool call;
- include raw prompts, full responses, hidden reasoning, secrets or unnecessary sensitive PII.

## Examples

### LIGHT success
```yaml
producer_ref: G15
activity_id: G15-REPORT-20260816-001
status: SUCCEEDED
summary: Priority report delivered and verified.
is_test: false
```

### STANDARD material action + metric
```yaml
producer_ref: C6
activity_id: C6-SYNC-20260816-001
status: SUCCEEDED
summary: Planner synchronization completed.
is_test: false
profile: STANDARD
verification: REQUIRED
semantic_facts:
  action:
    action_type: SYNC
    action_summary: Planner task state synchronized.
  metric:
    metric_name: records_changed
    metric_value: 4
    metric_unit: records
```

### Real failure
```yaml
producer_ref: G1
activity_id: G1-ARCHIVE-20260816-001
status: PARTIAL_FAILURE
summary: Archive publication completed but remote hash read-back failed.
is_test: false
verification: REQUIRED
semantic_facts:
  error:
    severity: HIGH
    message_code: REMOTE_HASH_READBACK_FAILED
    message_summary: Release asset hash could not be verified.
```
