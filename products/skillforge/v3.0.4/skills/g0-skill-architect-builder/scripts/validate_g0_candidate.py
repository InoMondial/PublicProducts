#!/usr/bin/env python3
from pathlib import Path
import argparse
import yaml, sys, re, json

parser = argparse.ArgumentParser(description="G0 source checks with optional release-transition interlock")
parser.add_argument("--release-stage", choices=("prepare_g12", "prepare_g13", "publish", "deploy", "close"))
parser.add_argument("--release-manifest", type=Path)
parser.add_argument("--trusted-context", type=Path)
args = parser.parse_args()
if (args.release_manifest or args.trusted_context) and not args.release_stage:
    parser.error("--release-stage is required with release evidence inputs")
if args.release_stage and not (args.release_manifest and args.trusted_context):
    parser.error("a release stage requires both evidence inputs")

root = Path(__file__).resolve().parents[1]
errors=[]
required=["SKILL.md","GOVERNANCE.yaml","NOTICE.md","CHANGELOG.md",
          "references/build-pipeline.md","references/dpga-contract.md",
          "references/governance-propagation-matrix.yaml",
          "references/runtime-profile-template.yaml",
          "references/validator-handoff-template.yaml",
          "tests/test-cases.yaml","tests/eval-rubric.yaml",
          "references/release-closure-gate-v1.md", "scripts/release_closure_gate.py",
          "tests/test_release_closure_gate.py",
          "references/exhaustive-pairwise-gate-v1.md",
          "references/pairwise-runtime-member-set-REFERENCE_SCOPE.json",
          "scripts/skillforge_pairwise_gate.py", "scripts/pairwise_release_binding.py",
          "tests/test_skillforge_pairwise_gate.py", "tests/test_pairwise_release_binding.py",
          "references/skillforge-feedback-intake-v1.yaml",
          "references/owner-conversation-backlog-coverage-v1.md",
          "scripts/backlog_coverage_gate.py", "tests/test_backlog_coverage_gate.py",
          "references/carry-forward-manifest-v1.md",
          "references/previous-release-carry-forward-source-v2.1.0.json",
          "scripts/carry_forward_gate.py", "scripts/carry_forward_release_binding.py",
          "tests/test_carry_forward_gate.py", "tests/test_carry_forward_release_binding.py"]
for rel in required:
    if not (root/rel).exists(): errors.append(f"missing:{rel}")
# Missing files must produce a controlled failure rather than an unhandled read.
if errors:
    print("FAIL")
    for e in errors: print(e)
    sys.exit(1)
for rel in ["GOVERNANCE.yaml","references/governance-propagation-matrix.yaml",
            "references/runtime-profile-template.yaml","references/validator-handoff-template.yaml",
            "tests/test-cases.yaml","tests/eval-rubric.yaml"]:
    try:
        yaml.safe_load((root/rel).read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"yaml:{rel}:{type(e).__name__}")
if errors:
    print("FAIL")
    for e in errors: print(e)
    sys.exit(1)
skill=(root/"SKILL.md").read_text(encoding="utf-8")
for token in ["G0-Skill Architect / Builder","O6-SKL-003","DPGA_COMPLETE",
              "GOVERNANCE_PROPAGATION_COMPLETE","INC_G15_TEST_CHANNEL",
              "INC_G15_PRIORITY_LOW_CHANNEL","INC_LOG_STORE","EFFICIENT",
              "INC_SKILLFORGE_FEEDBACK_INTAKE_V1","INC_OWNER_CONVERSATION_BACKLOG_COVERAGE_V1",
              "INC_SKILLFORGE_CARRY_FORWARD_MANIFEST_V1"]:
    if token not in skill: errors.append(f"skill-token:{token}")
m=yaml.safe_load((root/"references/governance-propagation-matrix.yaml").read_text())
ids={x["id"] for x in m["capabilities"]}
expected={"G1","G2","G4","G5","G6","G7","G8","G9","G10","G11","G12","G13","G14","G15"}
if ids != expected: errors.append(f"capability-set:{sorted(ids)}")
tests=yaml.safe_load((root/"tests/test-cases.yaml").read_text())["tests"]
test_ids={t["id"] for t in tests}
for c in m["capabilities"]:
    if c.get("rt_test") and c["rt_test"] not in test_ids:
        errors.append(f"missing-rt-test:{c['id']}:{c['rt_test']}")
try:
    from skillforge_pairwise_gate import generate_matrix, validate_matrix
    member_doc=json.loads((root/"references/pairwise-runtime-member-set-REFERENCE_SCOPE.json").read_text(encoding="utf-8"))
    seed=generate_matrix(member_doc)
    pair_errors=validate_matrix(seed, member_doc, False)
    if pair_errors:
        errors.extend("pairwise:" + code for code in pair_errors)
    if seed.get("member_count") != 19 or seed.get("directed_relationship_count") != 342 or seed.get("unique_unordered_pair_count") != 171:
        errors.append("pairwise:COUNT_INVARIANT_FAILED")
except Exception as e:
    errors.append("pairwise:INPUT_INVALID:" + type(e).__name__)
if args.release_stage:
    try:
        from release_closure_gate import load_backlog, load_json, evaluate
        backlog, raw = load_backlog(root/"references/skillforge-unified-backlog.yaml")
        decision = evaluate(args.release_stage, backlog, raw,
                            load_json(args.release_manifest), load_json(args.trusted_context))
        if not decision["allowed"]:
            errors.extend("release:" + code for code in decision["errors"])
    except Exception as e:
        errors.append("release:INPUT_INVALID:" + type(e).__name__)
if errors:
    print("FAIL")
    for e in errors: print(e)
    sys.exit(1)
print(f"PASS files={len(required)} tests={len(tests)} capabilities={len(ids)}")
print("RELEASE_TRANSITION_CONSISTENCY_PASS" if args.release_stage else "SOURCE_CHECK_ONLY_NOT_RELEASE_CERTIFICATION")
