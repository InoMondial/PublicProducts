# Governed Skill Backlog & Controlled Learning Contract

**Contract ID:** `INC_GOVERNED_SKILL_BACKLOG_CONTRACT_V1`  
**Builder owner:** `G0-Skill Architect / Builder`  
**Metadata compiler:** `G7-Skill Structure & Metadata Standardizer`  
**Framework:** `SkillForge` build governance

## 1. Purpose

Every Skill built or materially upgraded by SkillForge must leave Build-Time with exactly one resolved next-version backlog topology. This contract applies whether the resulting Skill is a SkillForge member, belongs to another governed framework, or is standalone.

Being built by SkillForge does **not** make an external Skill a SkillForge framework member. Builder provenance and framework membership are separate metadata facts.

## 2. Mandatory backlog topology

Exactly one topology is required:

- `CENTRAL_FRAMEWORK_BACKLOG` — for a governed multi-Skill framework/collection that has one root/gate Skill. The root/gate owns the one active backlog; child Skills may submit intake but must not maintain competing active next-version backlogs.
- `STANDALONE_SKILL_BACKLOG` — for an independent Skill. The Skill owns one canonical backlog for itself.

If multiple Skills form one governed collection but no root/gate/backlog owner can be resolved, release is blocked with `BACKLOG_OWNER_UNRESOLVED` until G0/owner resolves the architecture.

## 3. Mandatory backlog metadata

Every governed Skill records or resolves:

```yaml
builder_framework_ref: INC_SKILLFORGE
backlog_topology: CENTRAL_FRAMEWORK_BACKLOG | STANDALONE_SKILL_BACKLOG
next_version_backlog_ref: <stable backlog id>
backlog_owner_ref: <root/gate Skill or standalone Skill>
backlog_contract_ref: INC_GOVERNED_SKILL_BACKLOG_CONTRACT_V1
```

A framework child carries a stable reference only; it does not copy the mutable central backlog into its package.

## 4. Intake origin and controlled learning


- `USER_DIRECT` — the user/owner explicitly requested the change.
- `SYSTEM_DISCOVERED` — a Skill, Agent, Work, Codex task, test, release process or runtime execution detected a material future improvement/defect.

For `SYSTEM_DISCOVERED`, also record discovery context where available:
`BUILD_TIME | RUNTIME | TEST | RELEASE | OPERATIONS | OTHER`.

System discovery is **governed learning**, not autonomous Production mutation. A SYSTEM_DISCOVERED item may create/update a backlog candidate with evidence and confidence, but it must never silently modify or publish Production Skill behavior.

## 5. ITIL-aligned record types

Minimum supported types:

- `INCIDENT` — an observed interruption, failure or degraded/unexpected service behavior requiring restoration/containment.
- `PROBLEM` — an identified/potential underlying cause, recurring pattern or structural weakness that can cause one or more incidents.
- `CHANGE_REQUEST` — a proposed Request for Change to modify a Skill/framework/product behavior, contract or implementation.
- `IMPROVEMENT` — a continual-improvement opportunity where no current Incident/Problem is required.

Related records may form chains such as:
`INCIDENT -> PROBLEM -> CHANGE_REQUEST`.

## 6. Required item fields

```yaml
change_id: <stable id>
created_at: <ISO-8601>
discovered_phase: BUILD_TIME | RUNTIME | TEST | RELEASE | OPERATIONS | OTHER | N/A
record_type: INCIDENT | PROBLEM | CHANGE_REQUEST | IMPROVEMENT
title: <short title>
observed_condition: <what happened/was discovered>
proposed_change: <desired future state>
affected_skills: []
impact: CRITICAL | HIGH | MEDIUM | LOW
urgency: CRITICAL | HIGH | MEDIUM | LOW
priority: P0 | P1 | P2 | P3
priority_override_reason: <required when authorized override changes suggested priority>
source_refs: []
evidence_refs: []
confidence: HIGH | MEDIUM | LOW | N/A
occurrence_count: <integer >=1 when known>
status: CAPTURED | QUALIFIED | ACCEPTED | SELECTED | IMPLEMENTING | BLOCKED | VERIFIED | RELEASED | DEFERRED | REJECTED | SUPERSEDED | HISTORICAL
target_release: <release id | TBD>
related_records: []
```

## 7. Priority

Impact and urgency determine a suggested priority using the governed priority matrix. G0/backlog owner may override when authorized, but must record `priority_override_reason`. Priority is not a substitute for type, evidence, or owner approval.

## 8. Deduplication and learning hygiene

Before creating a new record, the backlog owner performs:

`Deduplicate -> Correlate -> Aggregate -> Qualify`

Repeated observations of the same underlying condition normally update one record by increasing `occurrence_count` and appending evidence rather than creating spam duplicates.

Conflicting requirements are retained with source evidence and blocked for owner decision; they are never silently merged.

## 9. Release selection gate

Before scope freeze for any new Skill/framework version, the backlog owner must present all applicable open/accepted items to the owner in a human-readable table that:

- has first column `NUM#`;
- is priority ordered;
- includes item date, Change ID, priority, type, origin, affected Skill/framework, short observed condition/problem, and proposed change;
- clearly identifies blocked/source-gated/deferred items.

The owner selects item numbers for the target release. Selected items become the frozen release scope. Unselected items remain open/deferred; they are not deleted.

## 10. Failure and safety rules

- Backlog capture never substitutes for handling a current safety/security/data-integrity/correctness failure.
- No direct backlog write capability -> return/persist truthful intake for the resolved backlog owner; do not fabricate successful registration.
- No backlog topology/owner -> release blocked.
- SYSTEM_DISCOVERED alone -> no Production self-modification or release.
- Child framework Skill competing backlog -> reject and route intake to central root/gate backlog.

## 11. Validation

G12/G13 must test at least:

1. central framework child cannot establish competing backlog;
2. standalone Skill cannot release without its own canonical backlog;
3. USER_DIRECT and SYSTEM_DISCOVERED remain distinguishable;
4. runtime-discovered improvement becomes backlog intake without Production mutation;
5. recurring equivalent findings aggregate deterministically;
6. owner release-selection table is numbered and includes required fields;
7. unselected backlog items survive scope freeze.
