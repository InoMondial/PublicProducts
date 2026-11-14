# SkillForge 3.0.4 — first-run setup in ChatGPT (guided dialogue)

The bundle contains nineteen governed skills, not a first-party ChatGPT installer. ChatGPT skill uploads do not automatically expose a local filesystem, shell, provider tokens, connector privileges or environment variables. An LLM must not claim a connection, persistent settings or successful installation on the basis of the ZIP alone.

## Conversation order
1. Ask language: English, French, Persian or user preferred; no identity or secret requested.
2. Confirm edition/host: ChatGPT, Codex, Work Cloud or other. Identify what installed skills and connected plugins the host truly exposes.
3. Ask what the user wants now: (a) local read-only governance; (b) GitHub private source; (c) SharePoint; (d) Teams; (e) Microsoft/Google calendar; (f) database; (g) private logging/backup; (h) optional public feedback. Only ask service-specific questions for selected services.
4. For each selected service, ask for **non-secret** site/repository/calendar/database identifiers and desired permissions (read-only default). Do not request passwords, authorization codes, cookies, API keys, tokens or client secrets.
5. Direct user to the host-managed **Connect/Authorize** screen for each permitted app. Verify identity, granted scope and resource metadata using the available connector/API readback. Never infer authorization merely from profile text, or from a simulation/mock.
6. Store user-specific values only in an authorized private configuration outside the installable package; use a host-managed persistent store when the ChatGPT skill filesystem is unavailable. The native Codex profile variables `SKILLFORGE_EXTERNAL_PROFILE` and `SKILLFORGE_EXTERNAL_PROFILE_SHA256` work only in hosts that actually support environment variable and local file access.
7. Confirm readback, least-privilege scope, profile schema/digest, optional recovery source, and backup. Treat missing resources as UNBOUND; block only dependent actions, not unrelated read-only tasks.
8. Present the exact status for each service: NOT_REQUESTED, DRAFT, AWAITING_AUTHORIZATION, CONNECTOR_VERIFIED, or BLOCKED. Ask before any external mutation.
9. Configure feedback separately: local private backlog is independent of optional public GitHub Issues, which defaults OFF. Public feedback remains OFF by default. A separately authorized destination and per-payload approval are required.
10. Re-run only changed steps after upgrades; never auto-copy private state to public source or re-use stale approvals.

## Domain-specific requests
- SharePoint: hostname, site, drive, private folder, project-relative folder, required read/write scope, real provider readback.
- Microsoft 365 Calendar: calendar and mailbox/resource reference, timezone, read-only or explicitly approved write, Graph delegated permissions and live readback.
- Google Calendar: chosen calendar, timezone and separately authorized connector.
- Database: provider type, logical project/database reference, schema and project isolation, backup/rollback location, read-only probe before migrations.
- GitHub: canonical private repository identity; treat a public feedback repo as a separate optional destination.
- Teams: team/channel identifiers and user-approved notification severity.

## Fallback when no connector / filesystem is available
Return a **pending setup checklist** with no secrets and a statement of which host capabilities are unavailable. Offer the user a host-native connection route; do not claim CONNECTED or READY.
