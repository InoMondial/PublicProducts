from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = ROOT / "deploy"
VERSION = "4.4.2"
FILENAME = f"G11-Serial011-Skill-Logging_Traceability_Standardizer_Ver{VERSION}_2026-08-16.zip"
ZIP_PATH = DEPLOY / FILENAME
STAMP = (2026, 8, 16, 0, 0, 0)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def canonical_files() -> list[Path]:
    out: list[Path] = []
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT)
        if rel.parts[0] in {"deploy", "tests"}:
            continue
        if "__pycache__" in rel.parts or p.suffix == ".pyc":
            continue
        out.append(p)
    return sorted(out, key=lambda x: x.relative_to(ROOT).as_posix())


def build_zip(files: list[Path]) -> None:
    DEPLOY.mkdir(exist_ok=True)
    for old in DEPLOY.glob("*.zip"):
        if old.name != FILENAME:
            old.unlink()
    tmp = ZIP_PATH.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in files:
            rel = p.relative_to(ROOT).as_posix()
            zi = zipfile.ZipInfo(rel, STAMP)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            z.writestr(zi, p.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    tmp.replace(ZIP_PATH)
    with zipfile.ZipFile(ZIP_PATH) as z:
        bad = z.testzip()
        if bad:
            raise RuntimeError(f"ZIP integrity failure: {bad}")
        expected = [p.relative_to(ROOT).as_posix() for p in files]
        if z.namelist() != expected:
            raise RuntimeError("ZIP canonical file list mismatch")
        for p, rel in zip(files, expected):
            if z.read(rel) != p.read_bytes():
                raise RuntimeError(f"normalized equivalence mismatch: {rel}")


def replace_field(text: str, key: str, value: str) -> str:
    pat = rf"(?m)^({re.escape(key)}:\s*).*$"
    if not re.search(pat, text):
        raise RuntimeError(f"missing PACKAGE field: {key}")
    return re.sub(pat, lambda m: m.group(1) + value, text)


def update_metadata() -> dict:
    data = ZIP_PATH.read_bytes()
    evidence = {
        "version": VERSION,
        "filename": FILENAME,
        "size": len(data),
        "sha256": sha256_bytes(data),
        "git_blob_sha": git_blob_sha(data),
        "zip_integrity": "PASS",
        "normalized_equivalence": "PASS",
        "declared_tests": 32,
        "caller_interface": "INC_G11_CALLER_INTERFACE_V1",
        "writer_route": "INC_G11_C7_WRITE_ROUTE_V1",
        "writer_envelope": "INC_G11_LOG_ENVELOPE_V1",
    }
    pkg = DEPLOY / "PACKAGE.yaml"
    text = pkg.read_text(encoding="utf-8")
    for key, value in [
        ("version", VERSION),
        ("filename", FILENAME),
        ("sha256", evidence["sha256"]),
        ("size", str(evidence["size"])),
        ("git_blob_sha", evidence["git_blob_sha"]),
        ("release_asset_status", "PENDING_POST_MERGE_FINALIZATION"),
    ]:
        text = replace_field(text, key, value)
    pkg.write_text(text, encoding="utf-8")
    (DEPLOY / "SHA256SUMS.txt").write_text(f"{evidence['sha256']}  {FILENAME}\n", encoding="utf-8")
    (DEPLOY / "BUILD-EVIDENCE.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    return evidence


def main() -> int:
    files = canonical_files()
    build_zip(files)
    evidence = update_metadata()
    print(f"PASS G11 v{VERSION} deterministic candidate build")
    print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
