# G15 Minimum Logging Contract

Canonical telemetry target: `INC_LOG_STORE`.

Emit minimum semantic deltas only. Do not load or reproduce the full physical log schema in routine runtime context.

Recommended fields when available:
- `skill_id`: `G15-SKL-001`
- `skill_version`
- `dispatch_id`
- `decision_id` or `report_id`
- `notification_class`
- `decision_category`
- `priority`
- `status`
- `response_code`
- `source_work_ref`
- `teams_thread_ref`
- `source_evidence_ref`
- `created_at`, `responded_at`, `closed_at`
- `measurement_status`: `MEASURED | PARTIAL | UNAVAILABLE`

Never log hidden chain-of-thought, full prompts/responses by default, passwords, OTPs, PINs, CVV, full card numbers, private keys, or access/refresh tokens.

Large support artifacts are referenced by stable ID/link instead of embedded.
