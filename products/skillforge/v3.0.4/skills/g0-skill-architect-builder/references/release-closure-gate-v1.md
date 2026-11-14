> Current release authority: autonomous-release-policy-v1.md. Historical strict-mode requirements below do not make external evaluators, runners or user/native installation prerequisites of the active autonomous profile.

# G0 Release Closure Gate v1

Contract: `INC_G0_RELEASE_CLOSURE_GATE_V1`.
Owner: G0. Scope: the owner-selected REFERENCE_SCOPE Stage30 FINAL v5 release integration.
Status: unreleased candidate implementation; not independent certification.
Backlog correlation: SF-XCUT-020, SF-XCUT-015 and the REFERENCE_SCOPE-C154 preflight approval/freeze findings.

## Authority and boundaries

The current owner decision authorizes bounded implementation, not destructive actions,
paid upgrades, production-secret migration, self-certification or premature release.
The current conversation's explicit approval gate wins over an older autonomy prompt.
An assistant checkpoint cannot establish a human decision. Keep the approval's source
reference, mission and gate identity; never rehabilitate an invalidated approval.

Use `scripts/release_closure_gate.py` at every release transition below. This script is
read-only and cannot authorize or perform a mutation. It verifies consistency against
separately supplied trusted adapter observations. It does not authenticate provider
receipts, discover permissions, activate validators or establish their independence.
The orchestrator must obtain those facts through the real owner message, authorized
provider read-back and a genuinely independent evaluation actor. Never populate the
trusted context by copying claims from the manifest or asking the implementation model
to declare itself independent. A passing synthetic fixture is never live release proof.

## Readiness is not certification

For every exact current canonical backlog record, preserve its full-record SHA-256 and
map exactly one evidence-backed readiness disposition:

- `IMPLEMENTED_SELF_TESTED` or `ALREADY_SATISFIED_SELF_TESTED`: implementation evidence
  and actual self-test references exist; G12/G13 remain subsequent gates.
- `HISTORICAL_EVIDENCE_ONLY`: only when the canonical source record is historical.
- `SUPERSEDED_WITH_SUCCESSOR_EVIDENCE`: only when the source record is superseded and a
  stable successor reference exists.
- `POSTDEPLOY_REQUIRED`: only for IDs explicitly selected for post-deployment review;
  the review implementation/contract is self-tested now and its result is required at close.
- `POSTDEPLOY_OWNER_GATED`: only for the explicitly selected non-release-blocking live
  operation, with its current-release contract/tooling self-tested and live mutation not executed.

Any missing, duplicate, extra, changed, blocked or unqualified record blocks the relevant
release transition. Do not hard-code 103 or any other count. The record ledger is a
release-evidence projection, not another backlog and not permission to rewrite terminal history.
Canonical backlog statuses are not automatically changed by this script.

This separation removes the circular condition in which G12 could not begin until an
item already carried final G12/G13 certification. Self-tested readiness permits only
entry to G12, never publication. Final terminal dispositions require the real evaluations.


## Mandatory prior-generated-Skill and carry-forward proof

Before `prepare_g12`, the orchestrator must run
`INC_SKILLFORGE_RELEASE_REBUILD_CARRY_FORWARD_GATE_V1` and provide both
machine-readable projections:

- `prior_generated_skill_inventory` plus its impact/delta digest;
- `carry_forward_manifest` plus its previous-to-new completeness digest.

The inventory must include framework members, external descendants, aliases,
backlog-only entries and any unconfirmed builder provenance. Before any
descendant rebuild begins, the trusted context must contain an explicit
current-release owner decision of `REBUILD_ALL_ELIGIBLE`,
`REBUILD_SELECTED` or `NO_REBUILD_NOW`. Package-release approval, silence
and a simulation waiver are not substitutes.

The carry-forward manifest must have exactly one classified row for every item
from the previous release requirements/BOM/manifest/contracts/tests/references/
assets/dependencies/backlog/fix-register and generated-Skill set. Missing,
duplicate, stale or `UNRESOLVED` rows block `prepare_g12`. The same
inventory and carry-forward digests must flow into G12, independent G13 and the
final release evidence. This gate separates framework-package completion from
ecosystem-descendant completion and does not require a hosted GitHub runner.

## Exact candidate and transition order

The frozen identity includes the source commit, raw-byte Git backlog blob SHA,
package SHA-256, BOM SHA-256 and the entire readiness ledger. Every certificate and
external receipt must bind the same computed candidate digest. The trusted observation
must match the candidate. The observed required local execution evidence names must
exactly match the verified local-execution policy. GitHub Actions, hosted runners and
remote CI are not required evidence sources for SkillForge; absent or failed local
execution evidence is not success.

1. `prepare_g12`: approval, complete readiness ledger, exact freeze and required local execution pass.
   No G12/G13 receipt is required at this entry point.
2. `prepare_g13`: the same conditions plus verified independent G12 PASS.
3. `publish`: add verified G13 PASS after G12 from a distinct eligible independent actor.
4. `deploy`: add verified publication/read-back of the certified package after G13.
5. `close`: add verified deployment and required-surface installation in order, rollback
   reference, post-deployment review results and final Handoff read-back.

A post-certification rebuild must be byte-identical. Any material source, backlog,
package, BOM or ledger change invalidates the bound evidence; run proportional affected
checks and obtain the applicable fresh independent evaluation. Re-read live authority
immediately before mutation. This consistency checker does not supply a distributed lock,
atomic compare-and-swap or permission to bypass a changed remote version.

Keep SF-G8-003's real-secret migration separately owner-gated after deployment. The
script exposes no action for migration, rotation or deletion of real secrets.

## Proportional testing for this mission

The owner-selected FINAL v5 profile governs this REFERENCE_SCOPE release: targeted deterministic
checks after each bounded change, completeness/adversarial/lifecycle coverage in one
consolidated review, then one fresh final G12 and genuinely independent G13. Repeat
only for failures or material changes. Earlier mandatory multi-cycle wording does not
cause redundant full suites for this mission. This is a scoped reconciliation, not a
waiver of security/integrity/independence and not a global change to unrelated releases.

## Local execution policy

GitHub Actions and GitHub-hosted runners are optional integrations and MUST NOT block
SkillForge testing, packaging, installation smoke or release-readiness evidence. Run the
applicable deterministic checks through a verified local Codex executor. Use
`projects/skill-ecosystem-vnext/plugins/skillforge-private/runbooks/LOCAL_CODEX_WINDOWS_EXECUTION_AND_REPORT.md`
when Windows PowerShell, local files or an install smoke are required. The generated,
append-only local report supplies the evidence reference and SHA-256 required by this gate.

## Invocation and input handling

Python 3 and PyYAML are required. Use the actual canonical backlog bytes, not excerpts.
The manifest holds mission, implementation actor, approval ID, frozen candidate,
readiness ledger and certificate references. Trusted context is separately assembled
from verified observations and contains the approval gate, verified owner decisions,
observed candidate, CI policy/results, independent certificates and external receipts.

```sh
python scripts/release_closure_gate.py --stage prepare_g12 \
  --backlog references/skillforge-unified-backlog.yaml \
  --manifest /governed-transient/release-manifest.json \
  --trusted-context /governed-transient/verified-adapter-context.json
```

Keep raw secrets, tokens, cookies and credentials out of both inputs. Preserve only safe
logical identities and stable evidence references. Duplicate YAML/JSON keys and invalid
inputs fail closed. Exit 0 means `CONSISTENCY_PASS` for that transition only; exit 2 means
`BLOCKED`. Neither result is itself a provider authorization or a G12/G13 certificate.

Run `python -m unittest discover -s tests -p test_release_closure_gate.py -v` for the
synthetic unit regression. Obtain full final-candidate tests and independent certification
separately before release; no test fixture is suitable as a production manifest/context.
