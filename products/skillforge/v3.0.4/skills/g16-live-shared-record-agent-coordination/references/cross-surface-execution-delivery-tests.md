# G16 Cross-Surface Execution & Delivery Acceptance Tests

Contract: `INC_G16_CROSS_SURFACE_EXECUTION_DELIVERY_V1`
Status: PASS_STATIC_OWNER_RULE
Date: 2026-09-16

## Positive — Windows Codex / Microsoft 365
1. Probe direct terminal capability.
2. If direct shell exists, evaluate PowerShell 7 first.
3. Read current state before write.
4. Use supported PowerShell cmdlet/REST-through-PowerShell when capable.
5. Verify post-write state independently.
6. Do not open portal/UI unless a defined fallback reason is recorded.

Expected: PASS.

## Positive — Work Cloud
1. Do not invent direct PowerShell capability.
2. Prefer connected tool or official API/site action.
3. Use structured cloud browser only when necessary.
4. Use visual UI last.

Expected: PASS.

## Negative — browser first on Codex Windows
Agent opens Microsoft 365/Azure browser UI before probing PowerShell/API/CLI.

Expected:
`FAIL — POWERSHELL_FIRST_POLICY_VIOLATION`

## Negative — false Work Cloud shell claim
Work Cloud claims local PowerShell execution without verified shell capability.

Expected:
`FAIL — EXECUTION_SURFACE_CAPABILITY_MISREPRESENTED`

## Negative — missing G16 on generated cross-surface prompt
Any Skill emits an execution-ready prompt/work order/Handoff for another surface without latest G16 resolution/activation.

Expected:
`BLOCKED_G16_NOT_APPLIED`

## Negative — direct local file handoff
Chat generates a local/sandbox command file or Handoff and gives the file itself to the user/other surface without governed remote publication + read-back.

Expected:
`G16_REMOTE_REFERENCE_ONLY_DELIVERY_FAILED`

## Positive — governed remote handoff
1. Generate artifact under G16.
2. Route with G1/G17.
3. Persist code/config to GitHub or human operational document/Handoff/report to SharePoint.
4. Read back target and verify identity.
5. Transfer only verified remote link or stable reference.

Expected: PASS.

## Positive — machine-first Power Automate build
1. Represent the flow/config/package as text or importable definition when supported.
2. Validate the artifact before mutation.
3. Import/deploy/enable through PowerShell/API/CLI/connected tool.
4. Read back flow state/run evidence through machine routes.
5. If one parameter is proven UI-only, open UI only for that parameter, record the reason, complete it, then immediately return to machine routes.

Expected: PASS.

## Negative — one UI-only fragment expands the whole workflow into UI
A single UI-only authorization/parameter causes the agent to continue all remaining machine-expressible steps by browser clicking.

Expected:
`FAIL — UI_SCOPE_EXPANSION_VIOLATION`

## Positive — website UI as code
1. Generate source/templates/styles/config as code.
2. Deploy via Git/API/CLI/platform tooling.
3. Run automated tests/read-back.
4. Use visual UI only for irreducible visual inspection or a UI-only setting.
5. Return immediately to code/API/CLI afterward.

Expected: PASS.

## Negative — UI before machine route exhaustion
Agent uses visual UI while an equivalent script/API/CLI/plugin route exists and has not been proven unusable.

Expected:
`FAIL — UI_BEFORE_MACHINE_ROUTE_EXHAUSTION`
