#!/usr/bin/env python3
"""Produce a checked, deterministic SkillForge public source distribution."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import zipfile

sys.dont_write_bytecode = True
PRODUCT = Path(__file__).resolve().parents[1]
ROOT = PRODUCT / "v3.0.4"
VERSION = "3.0.4-public.1"
ARCHIVE_ROOT = f"SkillForge-{VERSION}"
OUTPUT = Path(os.environ.get("SKILLFORGE_PUBLIC_DIST", str(PRODUCT / "dist"))).resolve()
ZIP_NAME = f"SkillForge-{VERSION}-SOURCE.zip"
LEGAL = ("LICENSE", "NOTICE", "THIRD_PARTY_NOTICES", "TRADEMARKS", "RIGHTS_PROFILE.yaml", "SECURITY.md")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def pretty(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def main() -> int:
    assert ROOT.is_dir(), "PUBLIC_SOURCE_DIRECTORY_MISSING"
    assert all((ROOT / name).is_file() for name in LEGAL), "MANDATORY_LEGAL_SURFACE_MISSING"
    pub = json.loads((ROOT / "RELEASE_POLICY.json").read_text(encoding="utf-8"))
    prov = json.loads((ROOT / "PROVENANCE.json").read_text(encoding="utf-8"))
    assert pub.get("public_publication_authorized") is True and pub.get("channel") == "PUBLIC_SOURCE_AVAILABLE", "PUBLIC_POLICY_MISMATCH"
    assert prov.get("public_release_authorized") is True and prov.get("private_history_embedded") is False, "PROVENANCE_NOT_PUBLIC"
    assert "public_publication_authorized: true" in (ROOT / "RIGHTS_PROFILE.yaml").read_text(encoding="utf-8"), "RIGHTS_PUBLICATION_UNAUTHORIZED"
    spec_path = ROOT / "skills/g8-security-privacy-permission-standardizer/scripts/public_boundary.py"
    assert spec_path.is_file(), "G8_PRIVACY_GATE_MISSING"
    spec = importlib.util.spec_from_file_location("sf_public_boundary", spec_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    policy = {"approved_emails": ["Info@inomondial.com"], "max_files": 5000, "max_expanded_bytes": 64000000}
    scanner = module.Scanner(policy)
    inspection = scanner.scan(ROOT)
    assert inspection["status"] == "STATIC_SCAN_PASS" and not inspection["findings"], "PUBLIC_SOURCE_SCAN_FAILED"
    files = sorted(p for p in ROOT.rglob("*") if p.is_file())
    assert len(files) == 422, f"SOURCE_FILE_COUNT_DRIFT:{len(files)}"
    skill_count = sum(p.name == "SKILL.md" for p in files)
    assert skill_count == 19, f"CORE_SKILL_COUNT_DRIFT:{skill_count}"
    assert not any(p.name == "PACKAGE_MANIFEST.json" and p.parent == ROOT for p in files), "PRIVATE_FROZEN_MANIFEST_MUST_NOT_SHIP"
    checked_python = 0
    records = []
    for p in files:
        rel = p.relative_to(ROOT).as_posix()
        raw = p.read_bytes()
        assert not p.is_symlink() and not any(x in rel.lower() for x in ("private-evidence", "owner-state", ".git/")), "FORBIDDEN_PATH"
        if p.suffix == ".py":
            compile(raw, rel, "exec")
            checked_python += 1
        records.append({"path": rel, "sha256": sha(raw), "bytes": len(raw)})
    OUTPUT.mkdir(parents=True, exist_ok=True)
    zip_path = OUTPUT / ZIP_NAME
    manifest = {"schema_version": "1.0", "product": "skillforge", "version": VERSION,
                "core_version": "3.0.4", "repository": "InoMondial/PublicProducts",
                "source_path": "products/skillforge/v3.0.4", "file_count": len(records),
                "skill_count": skill_count, "feedback_default": "OFF", "files": records,
                "source_tree_digest": inspection["tree_digest"]}
    with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as zf:
        for p in files:
            rel = p.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(f"{ARCHIVE_ROOT}/{rel}", (2026, 11, 14, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, p.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        info = zipfile.ZipInfo(f"{ARCHIVE_ROOT}/PUBLIC_EXPORT_MANIFEST.json", (2026, 11, 14, 0, 0, 0))
        info.create_system = 3
        info.external_attr = 0o100644 << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(info, pretty(manifest), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(zip_path) as zf:
        assert zf.testzip() is None, "ZIP_CRC_ERROR"
        for row in records:
            assert sha(zf.read(f"{ARCHIVE_ROOT}/{row['path']}")) == row["sha256"], "ZIP_SOURCE_HASH_MISMATCH"
        assert len(zf.namelist()) == len(records) + 1, "ZIP_MEMBER_COUNT_DRIFT"
    zip_inspection = module.Scanner(policy).scan(zip_path)
    assert zip_inspection["status"] == "STATIC_SCAN_PASS" and not zip_inspection["findings"], "PUBLIC_ZIP_PRIVACY_SCAN_FAILED"
    zip_hash = sha(zip_path.read_bytes())
    (OUTPUT / "SHA256SUMS.txt").write_text(f"{zip_hash}  {ZIP_NAME}\n", encoding="utf-8")
    result = {"status": "PASS_PUBLIC_ARCHIVE_READY", "version": VERSION, "zip_file": ZIP_NAME,
              "zip_bytes": zip_path.stat().st_size, "zip_sha256": zip_hash,
              "source_files": len(records), "source_skills": skill_count,
              "source_static_scan": inspection["status"], "source_scan_units": inspection["unit_count"],
              "archive_static_scan": zip_inspection["status"], "archive_scan_units": zip_inspection["unit_count"],
              "python_syntax_files_checked": checked_python,
              "source_tree_digest": inspection["tree_digest"],
              "native_installation_verified": False, "external_service_access_verified": False,
              "license": "SOURCE_AVAILABLE_NOT_OSI_OPEN_SOURCE", "public_feedback": "OFF"}
    (OUTPUT / "PUBLIC_RELEASE_VALIDATION.json").write_bytes(pretty(result))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
