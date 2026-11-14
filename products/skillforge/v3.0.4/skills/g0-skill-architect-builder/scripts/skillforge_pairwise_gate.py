#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

EXPECTED_VISIBLE_IDS = [f"G{i}" for i in range(19)]
ALLOWED_DISPOSITIONS = {"PASS", "N/A", "FAIL", "BLOCKED"}
REQUIRED_DIMENSIONS = (
    "BUILD_TIME_COMPATIBILITY",
    "RUNTIME_COMPATIBILITY",
    "CONTRACT_PROPAGATION",
    "EVIDENCE",
    "CONTENT_COPYING",
)
PENDING_PREFIX = "pairwise://pending/"
CONTRACT_ID = "INC_SKILLFORGE_EXHAUSTIVE_PAIRWISE_GATE_V1"

def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")

def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()

def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def normalize_members(doc: dict[str, Any]) -> list[dict[str, str]]:
    members = doc.get("members")
    if not isinstance(members, list):
        raise ValueError("MEMBERS_REQUIRED")
    if len(members) != 19:
        raise ValueError(f"MEMBER_COUNT_NOT_19:{len(members)}")
    normalized = []
    seen_visible, seen_stable = set(), set()
    for raw in members:
        if not isinstance(raw, dict):
            raise ValueError("INVALID_MEMBER_RECORD")
        row = {
            "visible_id": str(raw.get("visible_id", "")).strip(),
            "stable_id": str(raw.get("stable_id", "")).strip(),
            "version": str(raw.get("version", "")).strip(),
            "runtime_package_path": str(raw.get("runtime_package_path", "")).strip(),
        }
        if not all(row.values()):
            raise ValueError(f"INCOMPLETE_MEMBER:{row.get('visible_id') or 'UNKNOWN'}")
        if row["visible_id"] in seen_visible:
            raise ValueError(f"DUPLICATE_VISIBLE_ID:{row['visible_id']}")
        if row["stable_id"] in seen_stable:
            raise ValueError(f"DUPLICATE_STABLE_ID:{row['stable_id']}")
        seen_visible.add(row["visible_id"]); seen_stable.add(row["stable_id"]); normalized.append(row)
    if sorted(seen_visible, key=lambda x: int(x[1:])) != EXPECTED_VISIBLE_IDS:
        raise ValueError("VISIBLE_ID_SET_NOT_G0_G18")
    return sorted(normalized, key=lambda x: int(x["visible_id"][1:]))

def member_set_hash(members: list[dict[str, str]]) -> str:
    return sha256(members)

def _default_edge(source: dict[str, str], target: dict[str, str]) -> dict[str, Any]:
    key = f"{source['visible_id']}->{target['visible_id']}"
    return {
        "edge_id": key,
        "source": copy.deepcopy(source),
        "target": copy.deepcopy(target),
        "disposition": "BLOCKED",
        "reason": "PAIRWISE_BEHAVIORAL_EVIDENCE_PENDING_FINAL_FREEZE",
        "evidence_refs": [f"{PENDING_PREFIX}{source['visible_id']}/{target['visible_id']}"],
        "dimensions": {
            "BUILD_TIME_COMPATIBILITY": "BLOCKED",
            "RUNTIME_COMPATIBILITY": "BLOCKED",
            "CONTRACT_PROPAGATION": "BLOCKED",
            "EVIDENCE": "BLOCKED",
            "CONTENT_COPYING": "PROHIBITED",
        },
    }

def _apply_evidence(edge: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(edge)
    disposition = evidence.get("disposition")
    if disposition not in ALLOWED_DISPOSITIONS:
        raise ValueError(f"INVALID_DISPOSITION:{out['edge_id']}:{disposition}")
    out["disposition"] = disposition
    out["reason"] = str(evidence.get("reason", "")).strip()
    refs = evidence.get("evidence_refs")
    if not isinstance(refs, list) or not refs or not all(isinstance(x, str) and x.strip() for x in refs):
        raise ValueError(f"EVIDENCE_REFS_REQUIRED:{out['edge_id']}")
    out["evidence_refs"] = refs
    dims = evidence.get("dimensions")
    if not isinstance(dims, dict):
        raise ValueError(f"DIMENSIONS_REQUIRED:{out['edge_id']}")
    out["dimensions"] = {name: dims.get(name) for name in REQUIRED_DIMENSIONS}
    return out

def generate_matrix(member_doc: dict[str, Any], evidence_doc: dict[str, Any] | None = None) -> dict[str, Any]:
    members = normalize_members(member_doc)
    evidence_edges = {}
    if evidence_doc is not None:
        raw = evidence_doc.get("edges", {})
        if not isinstance(raw, dict):
            raise ValueError("EVIDENCE_EDGE_MAP_REQUIRED")
        evidence_edges = raw
    edges, used_evidence = [], set()
    for source in members:
        for target in members:
            if source["visible_id"] == target["visible_id"]:
                continue
            edge = _default_edge(source, target)
            if edge["edge_id"] in evidence_edges:
                edge = _apply_evidence(edge, evidence_edges[edge["edge_id"]]); used_evidence.add(edge["edge_id"])
            edges.append(edge)
    unknown = sorted(set(evidence_edges) - used_evidence)
    if unknown:
        raise ValueError("UNKNOWN_EVIDENCE_EDGES:" + ",".join(unknown))
    matrix = {
        "schema_version": "1.0",
        "contract_id": CONTRACT_ID,
        "runtime_scope": member_doc.get("runtime_scope", "G0-G18_WITH_ONE_CANONICAL_G17"),
        "freeze_id": member_doc.get("freeze_id", "UNFROZEN_CANDIDATE"),
        "member_set_sha256": member_set_hash(members),
        "member_count": len(members),
        "directed_relationship_count": len(edges),
        "unique_unordered_pair_count": len(members) * (len(members) - 1) // 2,
        "members": members,
        "edges": edges,
    }
    matrix["summary"] = summarize(matrix)
    matrix["matrix_sha256"] = sha256({k: v for k, v in matrix.items() if k != "matrix_sha256"})
    return matrix

def summarize(matrix: dict[str, Any]) -> dict[str, Any]:
    counts = {k: 0 for k in sorted(ALLOWED_DISPOSITIONS)}
    for edge in matrix.get("edges", []):
        d = edge.get("disposition")
        if d in counts: counts[d] += 1
    unresolved = counts["FAIL"] + counts["BLOCKED"]
    return {"disposition_counts": counts, "unresolved_edge_count": unresolved, "release_ready": unresolved == 0, "content_copying_policy": "PROHIBITED_ON_ALL_EDGES"}

def validate_matrix(matrix: dict[str, Any], member_doc: dict[str, Any], release_ready: bool = False) -> list[str]:
    errors = []
    try:
        members = normalize_members(member_doc)
    except Exception as exc:
        return [str(exc)]
    if matrix.get("contract_id") != CONTRACT_ID: errors.append("CONTRACT_ID_MISMATCH")
    if matrix.get("member_count") != 19: errors.append("MEMBER_COUNT_NOT_19")
    if matrix.get("member_set_sha256") != member_set_hash(members): errors.append("MEMBER_SET_HASH_MISMATCH")
    if matrix.get("members") != members: errors.append("MATRIX_MEMBER_SET_STALE")
    edges = matrix.get("edges")
    if not isinstance(edges, list): return errors + ["EDGES_REQUIRED"]
    if len(edges) != 342: errors.append(f"DIRECTED_RELATIONSHIP_COUNT_INVALID:{len(edges)}")
    if matrix.get("directed_relationship_count") != 342: errors.append("DIRECTED_RELATIONSHIP_SUMMARY_INVALID")
    if matrix.get("unique_unordered_pair_count") != 171: errors.append("UNORDERED_PAIR_COUNT_INVALID")
    lookup = {m["visible_id"]: m for m in members}
    seen, unordered = set(), set()
    for edge in edges:
        if not isinstance(edge, dict): errors.append("INVALID_EDGE_RECORD"); continue
        edge_id = edge.get("edge_id"); source = edge.get("source") or {}; target = edge.get("target") or {}
        s, t = source.get("visible_id"), target.get("visible_id")
        if not isinstance(edge_id, str) or edge_id != f"{s}->{t}": errors.append(f"EDGE_ID_MISMATCH:{edge_id}"); continue
        if edge_id in seen: errors.append(f"DUPLICATE_EDGE:{edge_id}")
        seen.add(edge_id)
        if s == t: errors.append(f"SELF_EDGE_PROHIBITED:{edge_id}")
        if s not in lookup or t not in lookup: errors.append(f"UNKNOWN_MEMBER_EDGE:{edge_id}"); continue
        if source != lookup[s]: errors.append(f"STALE_SOURCE_IDENTITY:{edge_id}")
        if target != lookup[t]: errors.append(f"STALE_TARGET_IDENTITY:{edge_id}")
        unordered.add(tuple(sorted((s, t), key=lambda x: int(x[1:]))))
        disposition = edge.get("disposition")
        if disposition not in ALLOWED_DISPOSITIONS: errors.append(f"INVALID_DISPOSITION:{edge_id}")
        if not isinstance(edge.get("reason"), str) or not edge.get("reason", "").strip(): errors.append(f"EDGE_REASON_REQUIRED:{edge_id}")
        refs = edge.get("evidence_refs")
        if not isinstance(refs, list) or not refs or not all(isinstance(x, str) and x.strip() for x in refs): errors.append(f"EDGE_EVIDENCE_REF_REQUIRED:{edge_id}")
        dims = edge.get("dimensions")
        if not isinstance(dims, dict) or set(dims) != set(REQUIRED_DIMENSIONS): errors.append(f"EDGE_DIMENSIONS_INVALID:{edge_id}"); continue
        if dims.get("CONTENT_COPYING") != "PROHIBITED": errors.append(f"CONTENT_COPYING_NOT_PROHIBITED:{edge_id}")
        if disposition in {"PASS", "N/A"}:
            if any(str(x).startswith(PENDING_PREFIX) for x in refs): errors.append(f"RESOLVED_EDGE_USES_PENDING_EVIDENCE:{edge_id}")
            for name in REQUIRED_DIMENSIONS[:-1]:
                if dims.get(name) != disposition: errors.append(f"DIMENSION_DISPOSITION_MISMATCH:{edge_id}:{name}")
        elif disposition in {"FAIL", "BLOCKED"} and dims.get("EVIDENCE") not in {"FAIL", "BLOCKED"}:
            errors.append(f"UNRESOLVED_EVIDENCE_DIMENSION_INVALID:{edge_id}")
    if len(seen) != 342: errors.append(f"UNIQUE_DIRECTED_EDGE_COUNT_INVALID:{len(seen)}")
    if len(unordered) != 171: errors.append(f"UNIQUE_UNORDERED_EDGE_COUNT_INVALID:{len(unordered)}")
    expected_ids = {f"{a['visible_id']}->{b['visible_id']}" for a in members for b in members if a != b}
    if expected_ids - seen: errors.append(f"MISSING_EDGE_COUNT:{len(expected_ids - seen)}")
    if seen - expected_ids: errors.append(f"EXTRA_EDGE_COUNT:{len(seen - expected_ids)}")
    if matrix.get("summary") != summarize(matrix): errors.append("SUMMARY_MISMATCH")
    if matrix.get("matrix_sha256") != sha256({k: v for k, v in matrix.items() if k != "matrix_sha256"}): errors.append("MATRIX_DIGEST_MISMATCH")
    if release_ready and not summarize(matrix)["release_ready"]: errors.append("PAIRWISE_MATRIX_NOT_RELEASE_READY")
    return errors

def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    gen = sub.add_parser("generate"); gen.add_argument("--members", type=Path, required=True); gen.add_argument("--evidence", type=Path); gen.add_argument("--out", type=Path, required=True)
    val = sub.add_parser("validate"); val.add_argument("--members", type=Path, required=True); val.add_argument("--matrix", type=Path, required=True); val.add_argument("--release-ready", action="store_true")
    args = ap.parse_args()
    try:
        members = _load(args.members)
        if args.cmd == "generate":
            matrix = generate_matrix(members, _load(args.evidence) if args.evidence else None)
            args.out.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({"result":"PASS","member_count":matrix["member_count"],"directed_relationship_count":matrix["directed_relationship_count"],"unique_unordered_pair_count":matrix["unique_unordered_pair_count"],"matrix_sha256":matrix["matrix_sha256"],"release_ready":matrix["summary"]["release_ready"]}, sort_keys=True)); return 0
        matrix = _load(args.matrix); errors = validate_matrix(matrix, members, args.release_ready)
        if errors: print(json.dumps({"result":"FAIL","errors":errors}, sort_keys=True)); return 1
        print(json.dumps({"result":"PASS","member_count":matrix["member_count"],"directed_relationship_count":matrix["directed_relationship_count"],"unique_unordered_pair_count":matrix["unique_unordered_pair_count"],"matrix_sha256":matrix["matrix_sha256"],"release_ready":matrix["summary"]["release_ready"]}, sort_keys=True)); return 0
    except Exception as exc:
        print(json.dumps({"result":"FAIL","errors":[type(exc).__name__+":"+str(exc)]}, sort_keys=True)); return 2

if __name__ == "__main__":
    raise SystemExit(main())
