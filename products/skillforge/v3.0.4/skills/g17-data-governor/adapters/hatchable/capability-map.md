# Hatchable Adapter Capability Map — REFERENCE_SCOPE Design Baseline

Status: DESIGN BASELINE, not canonical production release.

## Directly verified
- PostgreSQL-backed database access.
- Schema inspection.
- Parameterized SQL read/write.
- Multi-statement transactional batch through db.transaction.
- API functions and function logs.
- Deployment inspection.
- Internal scheduler/cron.
- Project storage.
- External HTTP egress via fetch.
- Web Crypto AES-GCM path.
- Full logical custom export function.
- Microsoft Graph network reachability (401 Bearer challenge without credential proves route reachability).

## Provider/runtime ceilings observed in the 2026-09-15 measurement report
- concurrent executions/account: 5
- requests/sec/app: 100
- response/request: 25 MB
- files/app: 5,000
- DB tables/app: 50

Account-wide Free usage cards observed:
- Storage: 1.0 GB
- Function invocations: 100,000/month
- Function CPU: 600 min/month
- Function runtime: 1,500 min/month
- Database time: 120 min/month
- Bandwidth: 5.0 GB/month
- Email: 750/month; 25/day observed

## Direct-plugin parity
DIRECT/PARTIAL:
- project
- schema
- SQL
- functions
- logs
- deployments
- cron jobs

BROWSER-ONLY in current evidence:
- cumulative Storage usage card
- function call/CPU/runtime usage history
- database-time cumulative/history
- bandwidth cumulative/history
- email usage/billing
- browser Activity time filters

## Architecture constraints
- one Hatchable project only for REFERENCE_SCOPE default shared DB;
- no consumer Skill calls Hatchable-specific API directly;
- schema changes through governed migrations;
- provider-specific monitoring/backup/scheduler logic stays in this adapter;
- no autonomous paid upgrade;
- no fabricated quota formula.
