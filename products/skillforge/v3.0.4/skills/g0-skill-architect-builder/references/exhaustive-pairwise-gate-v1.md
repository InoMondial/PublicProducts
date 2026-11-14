# INC_SKILLFORGE_EXHAUSTIVE_PAIRWISE_GATE_V1

This is a P0 fail-closed SkillForge release gate owned by G0.

At build/source freeze/release-candidate freeze, resolve the exact runtime member set from the frozen BOM/namespace registry and generate every directed non-self relationship. For N members the matrix MUST contain N*(N-1) directed edges and N*(N-1)/2 unordered pairs. The current G0-G18 scope is 19 members, 342 directed edges and 171 unordered pairs.

Every edge MUST identify the frozen source/target identities and classify BUILD_TIME_COMPATIBILITY, RUNTIME_COMPATIBILITY, CONTRACT_PROPAGATION and EVIDENCE. CONTENT_COPYING is always PROHIBITED. Each edge disposition is PASS, N/A, FAIL or BLOCKED with a reason and evidence reference. Missing/duplicate/unknown/stale edges, stale member identity/version/path, missing evidence or unresolved P0/P1 edge MUST block release.

The matrix generator/validator is `scripts/skillforge_pairwise_gate.py`. The local runner-independent CI MUST validate the frozen matrix with release-ready mode. Hosted CI is optional and cannot change the decision.

Before G12 entry, the release manifest MUST bind `pairwise_gate_required=true`, the exact pairwise matrix SHA-256 and the member-set SHA-256. Trusted read-back MUST prove 19/342/171, PASS and release_ready=true. G12 and independent G13 certificates MUST echo the same matrix and member-set digests. Any post-freeze identity/artifact change invalidates the matrix and reopens validation.

The matrix is conformance evidence only. Never copy peer Skill prompts, internal instructions, schemas, tests, references or implementation into the matrix or another Skill. Use stable contract IDs, version pins, digests and evidence references. Final matrix/BOM/release evidence is persisted through governed G1/SharePoint routes at freeze.
