# Host connector verification protocol (private setup)

This contract is intentionally provider-neutral. The offline wizard does NOT
call Graph, GitHub, SharePoint, Teams, Google Calendar or databases. A trusted
host must execute connector operations using user-authorized credentials that
remain in the provider's native secure store; no raw tokens in SkillForge.

## Step gates

1. Select only requested services and the target account/tenant.
2. Identify the host's actual connected app/plugin, granted operations and
   current resource scope. Do not rely on an inferred or cached login.
3. Request least-privileged **read-only** probe first, scoped to a known
   repository/site/calendar/project; report a normalized resource type/id
   and observation time without copying provider personal records.
4. Bind an alias only after the provider readback proves resource identity,
   permission and scope. Store private non-secret references outside the
   distributed ZIP. Any provider proof must be fresh for a sensitive write.
5. Separate mutation permissions by type (read/write/share/delete/notify/
   publish). No inferred authorization from successful read access.
6. Repeat verification after token refresh, account change, host restart,
   edition change, migration or detected permission drift.
7. Before any production write require G8/host approval, G16 write-ahead
   intent and remote readback. A simulated success is never a live binding.

## Minimum per-service evidence

| Service | Readback check | Sensitive operations requiring separate approval |
| :--- | :--- | :--- |
| GitHub private | Repository full name, repository ID, visibility and granted permission | Writing/merging, release, sharing/publication |
| SharePoint | Site, drive and folder IDs, visibility and selected file permissions | Upload/delete/share, confidentiality-label changes |
| Teams | Selected team/channel identity, membership/permission | Notifications/messages to a channel |
| M365 Calendar | Calendar ID/owner and delegated Graph scope | Create/update/delete calendar events |
| Google Calendar | Calendar ID and granted scope | Event change, attendee invitation |
| Database | Logical resource/project isolation, read-only probe | DDL/DML/migrations/backup cutover |
| Logging/backup | Canonical private target, storage permissions, retention class | Data deletion, key migration, destructive restore |
| Public feedback | Public repo identity, exact sanitized payload, per-issue consent | Public GitHub Issue submission (currently DISABLED due to withdrawal) |

A ChatGPT Skill ZIP alone cannot grant the host filesystem/connector API.
Missing APIs or readback evidence means `AWAITING_AUTHORIZATION`, not READY.
