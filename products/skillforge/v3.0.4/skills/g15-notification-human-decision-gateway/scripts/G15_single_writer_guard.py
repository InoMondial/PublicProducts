#!/usr/bin/env python3
"""Static guard against direct governed Teams notification writes outside G15.

The guard intentionally scans executable/config source, not historical docs/evidence.
It does not ban Teams generally. It blocks a producer that owns a direct Teams write
while also coupling to a governed G15 production destination OR emitting the governed
INC_NOTIFICATION_EVENT_V1 semantic contract. That closes the bypass where a producer
could emit the semantic event and still independently send a flat/wrong-route message.
"""
from __future__ import annotations
import pathlib, re, sys

G15_ROOT = pathlib.PurePosixPath("skills/router/g15-notification-human-decision-gateway")
EXCLUDED_PARTS = {"archives","evidence","docs","documentation","deploy","dist","node_modules","__pycache__",".git"}
SOURCE_SUFFIXES = {".py",".ps1",".sh",".js",".ts",".yml",".yaml",".json"}
WRITE_PATTERNS = (
    re.compile(r"\bsend_channel_message\b"),
    re.compile(r"\breply_to_channel_message\b"),
    re.compile(r"\breply_to_message\b"),
    re.compile(r"graph\.microsoft\.com.+/messages", re.I),
)
PRODUCTION_ROUTE_PATTERNS = (
    re.compile(r"INC_G15_PRIORITY_(?:HIGH|MED|LOW)_CHANNEL"),
    re.compile(r"Agent Notification(?: - (?:High|Med|Low) Priority)?", re.I),
)
SEMANTIC_EVENT_PATTERN = re.compile(r"INC_NOTIFICATION_EVENT_V1")


def is_exempt(rel: pathlib.PurePosixPath) -> bool:
    if tuple(rel.parts[:len(G15_ROOT.parts)]) == G15_ROOT.parts:
        return True
    return any(part in EXCLUDED_PARTS for part in rel.parts)


def scan_text(rel: pathlib.PurePosixPath, text: str) -> list[str]:
    if is_exempt(rel) or rel.suffix.lower() not in SOURCE_SUFFIXES:
        return []
    has_write=any(p.search(text) for p in WRITE_PATTERNS)
    has_prod=any(p.search(text) for p in PRODUCTION_ROUTE_PATTERNS)
    has_event=bool(SEMANTIC_EVENT_PATTERN.search(text))
    if has_write and (has_prod or has_event):
        return [f"DIRECT_G15_PRODUCTION_WRITE_BYPASS:{rel.as_posix()}"]
    return []


def scan_repo(root: pathlib.Path) -> list[str]:
    findings=[]
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel=path.relative_to(root)
        try:
            text=path.read_text(encoding="utf-8",errors="ignore")
        except Exception:
            continue
        findings.extend(scan_text(pathlib.PurePosixPath(rel.as_posix()), text))
    return findings


def producer_contract_ok(text: str) -> bool:
    """A producer may emit the governed semantic event without owning Teams transport."""
    return bool(SEMANTIC_EVENT_PATTERN.search(str(text or "")))


def main(argv=None):
    argv=list(argv or sys.argv[1:])
    root=pathlib.Path(argv[0] if argv else pathlib.Path(__file__).resolve().parents[4]).resolve()
    findings=scan_repo(root)
    if findings:
        print("\n".join(findings))
        return 1
    print("G15_SINGLE_WRITER_GUARD: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
