# G15 v3.0.0 — 14-Gate Governance Compliance Map

The Master Bible v2.2.1 defines 12 canonical Governance Standards. The canonical Skill Architect/Builder gateway precedes them and the independent Validator/Evaluator gate follows them. For this release these form the 14 build/promotion gates below. They are applied by the Builder/Orchestrator; G15 does not recursively invoke governance Skills at runtime.

| # | Gate | Applicability | v3 evidence |
|---:|---|---|---|
| 1 | Skill Architect / Builder (`O6-SKL-003`) | BUILD | Existing G15 qualified as a reusable Skill; ADAPT/MIGRATE selected; FULL + ROUTER selected independently; v2.4 capability preserved then v3 package migration applied. |
| 2 | Artifact Classification & Skill Profile | BUILD | `artifact_type=skill`, `complexity_profile=FULL`, `functional_role=ROUTER`; runtime risk does not auto-map to resource class. |
| 3 | Corporate IP & Copyright | BUILD + PACKAGE | Proprietary ownership/contact and `G15-NOTICE.md`; no third-party source code bundled. |
| 4 | Artifact Naming | BUILD + RELEASE | Stable ID `G15-SKL-001`; Agent-Skills-compatible technical name; G15-prefixed managed files where possible; `SKILL.md` reserved exception. |
| 5 | Versioning & Lifecycle | BUILD + RELEASE | SemVer major `3.0.0` because install identity/package layout changed; v2 history retained; platform scan state remains separate. |
| 6 | Skill Structure & Metadata | BUILD | Agent Skills `SKILL.md`, progressive references/scripts/assets/schemas, metadata, explicit contracts, no giant monolithic runtime context. |
| 7 | Security, Privacy & Permission | BUILD + RUNTIME | S4; secret/credential prohibition; high-consequence double confirmation; truthful capability claims; G15 never executes irreversible governed action itself. |
| 8 | Token & Context Efficiency | BUILD + RUNTIME | Deterministic fast path; `runtime_resource_routing_applicable=false`; JIT references; no full governance/schema load; compact outputs/telemetry. |
| 9 | Dependency & Stable Reference | BUILD + RUNTIME | Logical refs for Teams/stores; no tenant/channel/list IDs or secrets in package; typed edges; no recursive governance or runtime cycles. |
| 10 | Logging & Traceability | RUNTIME | Minimum semantic envelope only to `INC_LOG_STORE`; canonical IDs + exact deep links; no parallel log schema or full prompt/CoT logging. |
| 11 | Testing & Evaluation | BUILD | T4 package/regression/security/decision/report/capability tests; clean extracted-ZIP rerun required. |
| 12 | Skill Quality / SQS | BUILD + PROMOTION | Hard-gate review + deterministic precheck in `references/G15-sqs-precheck.md`; canonical/platform evaluator remains authoritative. |
| 13 | Artifact Output & Packaging | BUILD + RELEASE | Single installable ZIP, one technical root, manifest/SHA, no build cache/deploy/dist inside ZIP, source/deployment separated. |
| 14 | Independent Validator / Evaluator | PROMOTION | Separate `scripts/G15_validate.py` plus clean extracted-package test/validation pass; ChatGPT performs an additional platform scan at upload. |

## Build-time vs runtime applicability
- Build-time governance is applicable to this major migration and packaging release.
- Runtime resource routing is **NOT_APPLICABLE** because the core G15 classifier/parser path is deterministic and fixed. This avoids optimizer overhead.
- Runtime security, stable references, logging, decision rules, traceability, and capability gates remain applicable.
- Native Approval / Adaptive Card provider-specific behavior loads only when the corresponding optional capability is actually requested and exposed.

## Core architecture decisions preserved
- Small composable Skill > giant Skill.
- Work/Agent owns macro orchestration; Router owns micro-routing.
- Source and deployment are separate.
- Rule/state separation is mandatory.
- Stable references resolve dynamic environment state outside the Skill package.
- Build-time and runtime applicability are resolved independently.
- Runtime generic best-practice web discovery is OFF by default.
- `INC_LOG_STORE` is the canonical telemetry target.
