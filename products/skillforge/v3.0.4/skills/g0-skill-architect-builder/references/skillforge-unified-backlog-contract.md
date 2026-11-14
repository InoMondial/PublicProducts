# SkillForge Unified Backlog Contract v1 — Compatibility Alias

**Legacy Contract ID:** `INC_SKILLFORGE_UNIFIED_BACKLOG_CONTRACT_V1`  
**Current normative contract:** `INC_SKILLFORGE_UNIFIED_BACKLOG_CONTRACT_V2`  
**Generic governing contract:** `INC_GOVERNED_SKILL_BACKLOG_CONTRACT_V1`  
**Canonical owner:** `G0-Skill Architect / Builder`

This file is retained so existing backlog records/packages that still reference `INC_SKILLFORGE_UNIFIED_BACKLOG_CONTRACT_V1` do not break during the next-release transition.

For all new Build/Maintenance work, V1 resolves forward to:

`references/skillforge-unified-backlog-contract-v2.md`

The active backlog remains:

`references/skillforge-unified-backlog.yaml`

## Compatibility rule

- Existing V1 references remain readable and are not treated as missing dependencies.
- New or materially upgraded SkillForge contracts must reference V2.
- V2 adds the approved governed-learning/backlog-topology model: `USER_DIRECT | SYSTEM_DISCOVERED`, ITIL-aligned record types, owner-numbered release review, deduplication/aggregation and the generic central-vs-standalone backlog contract.
- This compatibility alias is not a second backlog and must not be edited as an independent active requirement source.
- Final package/version migration and any retirement of the V1 alias are governed by G6/G10/G14/G1 in later release stages.
