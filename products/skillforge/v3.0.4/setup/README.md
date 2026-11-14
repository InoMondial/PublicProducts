# Post-install setup: G20 contract companion (3.0.4)

This package contains a working **offline setup plan and parameter-schema validator** (Python script `setup/onboarding.py`) and a guided ChatGPT conversational procedure. The G20 setup skill is a separate candidate in the private SkillForge repository; its existence does NOT imply automatic installation/activation with the 19 governance skills.

Run from the extracted plugin root:

```sh
python3 setup/onboarding.py catalog
python3 setup/onboarding.py plan --host CODEX --services SHAREPOINT,MICROSOFT_CALENDAR
python3 setup/onboarding.py draft --host CODEX --services SHAREPOINT --output /secure/path/skillforge-owner-draft.json
python3 setup/onboarding.py check --file /secure/path/skillforge-owner-profile.json --sha256 <verified-file-hash>
```

`draft` writes **only a non-operational DRAFT** (0600 file permission where supported); it cannot certify real connector access. `check` only verifies schema, digest, path and non-secret configuration; it cannot independently authenticate a user or grant a host permission. Runtime must separately execute connector readback with user authorization.

For ChatGPT without host-side filesystem, follow `CHATGPT_FIRST_RUN.md` instead of pretending an environment variable works.

Feedback: `python3 setup/onboarding.py feedback-check --file /secure/path/proposal.json` performs *offline, no-post* payload checks. Actual public GitHub Issue mutation is never available from the setup script and requires separate user permission and a connected tool, after public repository reauthorization.

Security: no source/ZIP is permission to write to GitHub, SharePoint, calendar, database, Teams or a public issue. No raw machine secrets in an external profile, prompt, log or package.
