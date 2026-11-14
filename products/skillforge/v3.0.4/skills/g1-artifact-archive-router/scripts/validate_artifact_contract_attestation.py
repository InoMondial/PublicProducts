#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path

EXPECTED = "INC_REMOTE_ARTIFACT_DELIVERY_V2"
HISTORICAL = "INC_REMOTE_ARTIFACT_DELIVERY_V1"
FAILURE = "ARTIFACT_CONTRACT_ATTESTATION_FAILED"

def read(path):
    return path.read_text(encoding="utf-8")

def extract(pattern, text, label):
    m = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if not m:
        raise ValueError("MISSING_METADATA:" + label)
    return m.group(1).strip().strip("'\"")

def refs(skill_dir, role):
    skill = read(skill_dir / "SKILL.md")
    gov = read(skill_dir / "GOVERNANCE.yaml")
    manifest = json.loads(read(skill_dir / "MANIFEST.json"))
    if role == "G1":
        return {
            "SKILL": extract(r"^\s*remote_artifact_delivery_contract_ref:\s*([^\s#]+)", skill, "G1.SKILL"),
            "GOVERNANCE": extract(r"remote_artifact_delivery:\s*\n\s*contract_ref:\s*([^\s#]+)", gov, "G1.GOVERNANCE"),
            "MANIFEST": manifest["contracts"]["remote_artifact_delivery"],
        }
    return {
        "SKILL": extract(r"^\s*artifact_egress_contract_ref:\s*([^\s#]+)", skill, "G18.SKILL"),
        "GOVERNANCE": extract(r"artifact_egress:\s*\n\s*contract_ref:\s*([^\s#]+)", gov, "G18.GOVERNANCE"),
        "MANIFEST": manifest["artifact_delivery_contract_ref"],
    }

def discover_repo_root(script_path):
    for parent in script_path.resolve().parents:
        if (parent / "skills/router/g1-artifact-archive-router").is_dir():
            return parent
    return None

def validate_scope(name, g1, g18, matrix_path, errors):
    try:
        matrix = json.loads(read(matrix_path))
    except Exception as e:
        errors.append(f"{name}:MATRIX_INVALID:{type(e).__name__}")
        return
    if matrix.get("active_contract") != EXPECTED:
        errors.append(f"{name}:MATRIX_ACTIVE_CONTRACT_MISMATCH")
    lineage = matrix.get("historical_lineage", [])
    if not any(x.get("contract") == HISTORICAL and x.get("status") == "HISTORICAL_NON_EXECUTABLE" for x in lineage if isinstance(x, dict)):
        errors.append(f"{name}:V1_HISTORY_LINEAGE_MISSING")
    for role, directory in (("G1", g1), ("G18", g18)):
        try:
            observed = refs(directory, role)
        except Exception as e:
            errors.append(f"{name}:{role}:READ_FAILED:{e}")
            continue
        for surface, value in observed.items():
            if value != EXPECTED:
                errors.append(f"{name}:{role}:{surface}:{value}")
        participant = matrix.get("participants", {}).get(role, {})
        if participant.get("expected_active_ref") != EXPECTED:
            errors.append(f"{name}:{role}:MATRIX_PARTICIPANT_MISMATCH")

def compare_files(canonical_dir, package_dir, rels, label, errors):
    for rel in rels:
        a = canonical_dir / rel
        b = package_dir / rel
        if not a.is_file() or not b.is_file():
            errors.append(f"{label}:{rel}:MISSING")
            continue
        if a.read_bytes() != b.read_bytes():
            errors.append(f"{label}:{rel}:CANONICAL_PRIVATE_DRIFT")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path)
    ap.add_argument("--package-root", type=Path)
    ap.add_argument("--mode", choices=("startup", "package"), default="startup")
    args = ap.parse_args()

    repo = args.repo_root.resolve() if args.repo_root else discover_repo_root(Path(__file__))
    package_root = args.package_root.resolve() if args.package_root else (repo / "plugins/inomondial-skillforge-private" if repo else None)
    errors = []

    canonical_available = bool(repo and (repo / "skills/router/g1-artifact-archive-router").is_dir())
    package_available = bool(package_root and (package_root / "skills/g1-artifact-archive-router").is_dir())

    if canonical_available:
        validate_scope(
            "CANONICAL",
            repo / "skills/router/g1-artifact-archive-router",
            repo / "skills/router/g18-human-conversation-output-governor",
            repo / "skills/router/g1-artifact-archive-router/references/artifact-delivery-contract-compatibility-v2.json",
            errors,
        )
    if package_available:
        validate_scope(
            "PRIVATE",
            package_root / "skills/g1-artifact-archive-router",
            package_root / "skills/g18-human-conversation-output-governor",
            package_root / "skills/g1-artifact-archive-router/references/artifact-delivery-contract-compatibility-v2.json",
            errors,
        )

    if not canonical_available and not package_available:
        errors.append("NO_ATTESTABLE_SCOPE")

    if args.mode == "package":
        if not canonical_available or not package_available:
            errors.append("PACKAGE_MODE_REQUIRES_CANONICAL_AND_PRIVATE")
        else:
            g1_rels = [
                "SKILL.md", "GOVERNANCE.yaml", "MANIFEST.json",
                "references/artifact-delivery-contract-compatibility-v2.json",
                "scripts/validate_artifact_contract_attestation.py",
            ]
            g18_rels = ["SKILL.md", "GOVERNANCE.yaml", "MANIFEST.json"]
            compare_files(repo / "skills/router/g1-artifact-archive-router", package_root / "skills/g1-artifact-archive-router", g1_rels, "G1", errors)
            compare_files(repo / "skills/router/g18-human-conversation-output-governor", package_root / "skills/g18-human-conversation-output-governor", g18_rels, "G18", errors)
            # Tests are source evidence, not installable runtime content.
            source_private = repo / "plugins/inomondial-skillforge-private/skills/g1-artifact-archive-router"
            compare_files(repo / "skills/router/g1-artifact-archive-router", source_private,
                          ["tests/test_artifact_contract_attestation_v2.py"], "G1_SOURCE_TEST", errors)

    if errors:
        print(FAILURE)
        for e in errors:
            print(e)
        return 1
    print("ARTIFACT_CONTRACT_ATTESTATION_PASS")
    print("active_contract=" + EXPECTED)
    print("mode=" + args.mode)
    return 0

if __name__ == "__main__":
    sys.exit(main())
