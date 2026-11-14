> Current release authority: autonomous-release-policy-v1.md. Historical strict-mode requirements below do not make external evaluators, runners or user/native installation prerequisites of the active autonomous profile.

# SkillForge Release Train and Runner-Independent CI Contract v1

## Four lanes
Stable is immutable live; Candidate is current selected release; Next accepts continuous backlog intake; Hotfix is restricted to critical production/security/data-loss/release-blocking repair.

## Scope lock
Backlog intake never closes. Candidate scope locks explicitly. Ordinary late intake routes to Next. Hotfix admission records owner/orchestrator decision and invalidates affected validation.

## Multi-agent integration
G0 is the single Release Orchestrator. G16 issues path-scoped leases from a base SHA. Contributors work on isolated branches/worktrees. Same-path overlap, stale base, direct integration/stable mutation and freeze with active material leases fail closed. Integration is serialized.

## Build once / promote same artifact
Freeze source and release manifest; G19 builds one artifact digest. G12 validates that digest and G13 certifies the same digest. Promotion changes an atomic active-release pointer; post-certification rebuild under the same release identity is prohibited. Rollback re-points to a prior immutable certified artifact.

## Runner-independent CI
The repository owns one versioned deterministic pipeline contract. Codex/local machine execution is a first-class executor. GitHub Actions is optional. Each run emits source SHA, pipeline version, commands, results, evidence and artifact digest.

## GitHub boundary
The release train consumes `INC_GITHUB_USAGE_BOUNDARY_V1`. GitHub is the default source/change/provenance plane, not a mandatory execution plane. Actions, hosted/self-hosted Runner, required status checks, Workflow Artifacts and GitHub Release/Asset are conditional adapters. Core SkillForge release evidence remains executor-neutral and provider-neutral; an optional GitHub adapter failure blocks only that adapter or explicitly selected distribution target.

## Runtime separation
Runtime sessions pin to an active release_id and digest. Candidate/Next changes cannot mutate the live artifact mid-session. Hotfixes forward-merge into Candidate/Next after deployment.
## Exhaustive pairwise release gate
Every SkillForge freeze uses `INC_SKILLFORGE_EXHAUSTIVE_PAIRWISE_GATE_V1`. The local runner receives both the frozen member-set document and frozen matrix, validates exact 19/342/171 coverage in release-ready mode, and fails on any missing/stale/blocked edge. Hosted CI remains optional. G12/G13 must certify the same matrix/member-set digests.
## Previous-version carry-forward hard gate
Every release-candidate local runner invocation receives the frozen previous snapshot, current snapshot and `INC_SKILLFORGE_CARRY_FORWARD_MANIFEST_V1` manifest. It validates zero unresolved rows and exact manifest/snapshot digests in release-ready mode before G12 entry. G12 and independent G13 certify the same three digests. Missing inputs or post-freeze drift fail closed.

