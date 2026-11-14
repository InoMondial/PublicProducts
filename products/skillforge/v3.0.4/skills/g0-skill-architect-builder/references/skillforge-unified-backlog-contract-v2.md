# SkillForge Unified Backlog Contract v2

**Contract ID:** `INC_SKILLFORGE_UNIFIED_BACKLOG_CONTRACT_V2`  
**Canonical owner:** `G0-Skill Architect / Builder`  
**Canonical backlog:** `references/skillforge-unified-backlog.yaml`  
**Generic backlog contract:** `INC_GOVERNED_SKILL_BACKLOG_CONTRACT_V1`  
**Framework:** `SkillForge`

## Purpose

SkillForge has exactly one active next-version backlog. This contract is the SkillForge-specific instance of `INC_GOVERNED_SKILL_BACKLOG_CONTRACT_V1`.

SkillForge child Governance Skills must not maintain competing active next-version backlogs. Historical issue threads, prior per-Skill backlog files, design notes, handoffs and external change requests remain evidence/source references only after migration.

## Membership boundary

Only Registry/metadata-resolved SkillForge `MEMBER` or governed `CANDIDATE_MEMBER` work may be treated as SkillForge framework backlog scope. An external Skill built by SkillForge does not become a SkillForge member or use this central backlog merely because `builder_framework_ref=INC_SKILLFORGE`.

## Intake

New intake follows `INC_GOVERNED_SKILL_BACKLOG_CONTRACT_V1` and must include:

- discovered phase/context;
- ITIL-aligned `record_type`: `INCIDENT | PROBLEM | CHANGE_REQUEST | IMPROVEMENT`;
- observed condition/problem and proposed change;
- impact, urgency and priority;
- affected Skill(s), evidence/source references, confidence/occurrence where applicable;
- testable acceptance criteria.

SYSTEM_DISCOVERED is governed learning only. It may create/update backlog state but may not self-modify Production behavior or publish a release.

### Authority and registration truth

Every SkillForge framework intake also follows `INC_SKILLFORGE_FEEDBACK_INTAKE_V1`. Preserve origin separately from numerical P0-P3 priority. `SYSTEM_DISCOVERED` normally carries `SYSTEM_EVIDENCE`; `USER_DIRECT` carries `USER_REQUEST` or `OWNER_MANDATE` when explicitly owner-mandated. At the same numerical priority, review precedence is OWNER_MANDATE > USER_REQUEST > SYSTEM_EVIDENCE; origin alone never automatically raises severity.

If an owner mandate matches an existing system-discovered item, aggregate into the same Change ID, preserve both origin/evidence histories and promote authority to OWNER_MANDATE. A child runtime without authorized canonical write returns/persists `PENDING_CANONICAL_INGESTION`; it cannot claim canonical registration without successful write/read-back.

Before a terminal claim that all agreed/necessary items are registered, require a PASS `INC_OWNER_CONVERSATION_BACKLOG_COVERAGE_V1` receipt with zero unmapped requirements, post-write canonical backlog SHA and exact canonical/private parity.

## Deduplication

G0 performs `Deduplicate -> Correlate -> Aggregate -> Qualify`. Repeated equivalent findings update occurrence/evidence on one record rather than generating spam duplicates. Conflicts remain visible and blocked for owner decision.

## Release review

Before SkillForge release scope freeze, G0 presents open/accepted items to the owner in a priority-ordered table with first column `NUM#` and at minimum: date, Change ID, priority, type, origin, affected Skill, short observed condition/problem, proposed change and blocked/deferred state. The owner selects row numbers for the target release.

Unselected items remain open/deferred; they are never deleted merely because they were not selected.

## Source of truth

`references/skillforge-unified-backlog.yaml` is the only active SkillForge next-version backlog. Child packages carry only stable references. GitHub issues/comments and former per-Skill backlogs are historical/migrated sources.

## Current hard gates

- unresolved framework/backlog ownership -> block;
- false SkillForge membership -> block;
- critical current defect -> current failure path still applies; backlog capture is not enough;
- missing exact external Change Request source -> affected implementation remains source-gated unless owner authorizes a documented substitute;
- stage advance requires three simulations;
- release requires G12/G13 validation and G14/G1 packaging/publication gates.

## Critical control

`G0-CC-06 — UNIFIED_BACKLOG_CAPTURED` remains the SkillForge-specific intake gate.

`G0-CC-07 — BACKLOG_TOPOLOGY_RESOLVED` ensures any Skill built/upgraded by SkillForge has a central-framework or standalone backlog topology before release.
