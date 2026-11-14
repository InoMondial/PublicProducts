# Upgrading a private SkillForge installation from 3.0.3 to 3.0.4

- Keep the exact 3.0.3 owner-parameter sidecar and previous backups in the
  authorized private destination. Do not add those files to GitHub Public.
- A non-destructive converter at `setup/migrate_private_profile.py` maps every
  previously declared parameter into the new catalog and adds new service
  parameters as `null`; it never discards existing values or grants authority.
- The resulting owner file MUST be outside the installable, with tight access
  restrictions, and remains `REVALIDATION_REQUIRED` until the host verifies each
  selected service. Its old `BOUND` strings are downgraded, not blindly reused.
- Review current private account/tenant identity and allowlist desired repositories,
  SharePoint site/folders, Teams channels, calendar(s), database(s), key refs and
  backup roots. Do not enter passwords or client secrets in the assistant chat.
- If the host genuinely supports environment variables, configure
  `SKILLFORGE_EXTERNAL_PROFILE` to the **approved private** profile path and
  `SKILLFORGE_EXTERNAL_PROFILE_SHA256` to its exact file digest. The profile
  must use `state: BOUND` only after trusted connector validation and approval.
- In ChatGPT, do not assume local environment variables are available; complete
  guided onboarding through connected apps and a permissioned private store.
- The G20 setup router remains a separate candidate. The shipped setup helper
  is an offline planner, validator and feedback-preview guard, not a background
  agent or a magical account-authorization service.
- If a required service is unavailable, affected mutating actions remain blocked;
  unrelated local/read-only governance continues.
- No new public release or automatic public-feedback posting is authorized.
