# INC_SKILLFORGE_DESCENDANT_BUILD_GATE_V1

Status: Stage-30 candidate hard gate.
Owner: G0 / SkillForge.

## Purpose
Prevent any Skill created or materially governed by SkillForge from creating a new Skill outside the SkillForge build gateway.

## Hard gate
If a SkillForge-built Skill participates in the creation, generation, scaffolding, synthesis, cloning, splitting, merging, or material redesign of another artifact that qualifies as a Skill, it MUST first route that new Skill through G0 / SkillForge.

The producer Skill MUST NOT directly author or publish a new Skill as an independent builder.

Required pre-build check:
1. classify the target artifact;
2. if target qualifies as Skill, verify `builder_framework_ref=INC_SKILLFORGE` or an active G0/SkillForge build transaction;
3. if not verified, stop before Skill generation and emit `BLOCKED_SKILLFORGE_BUILD_GATE_REQUIRED`;
4. hand off the requested Skill definition, requirements, source inputs, constraints and evidence to G0;
5. resume only after G0 returns an execution-ready Candidate/build context.

This rule applies whether the resulting Skill is a SkillForge MEMBER, CANDIDATE_MEMBER, or EXTERNAL. Framework membership of the child is independent from mandatory builder provenance.

## Non-Skill interactions
This gate does not block ordinary runtime interaction with already-existing Skills, agents, tools, prompts, files, APIs, or services. It applies only when a new Skill is being created or an existing Skill is materially rebuilt as a new Candidate.

## Propagation
G0 MUST compile this gate into every Skill it builds. The child carries a minimum local guard and stable reference; it MUST NOT recursively load the entire G0 stack during ordinary runtime.

## Failure code
`BLOCKED_SKILLFORGE_BUILD_GATE_REQUIRED`

## Required tests
- SkillForge-built Skill attempts direct child-Skill creation -> BLOCK.
- Same Skill routes child creation to G0 -> PASS.
- Child is EXTERNAL but built through G0 -> PASS.
- Ordinary interaction with an existing non-Skill tool -> N/A/PASS.
- Existing Skill invocation with no creation/rebuild -> N/A/PASS.
