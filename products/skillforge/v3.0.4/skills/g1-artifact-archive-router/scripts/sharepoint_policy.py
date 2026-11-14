#!/usr/bin/env python3
"""G1 SharePoint authority resolver and policy gates (v4.3.0)."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Mapping, Sequence

AUTHORIZED_ROOT = None  # host-supplied approved external authority required
PHYSICAL_OWNER = "G1_ARTIFACT_ARCHIVE_ROUTER"
CALLER_PATH_KEYS = {
    "sharepoint_path", "sharepoint_destination", "destination_path",
    "physical_destination", "target_folder", "parent_folder_path",
}
ALLOWED_NAMESPACES = {"Ecosystem", "Projects", "Shared", "_Control"}
NESTED_BINARY_EXCEPTIONS = {"RELEASE_BUNDLE", "SELF_CONTAINED_DISASTER_RECOVERY"}
PROJECT_CLASSIFICATION_ROUTES = {
    "RELEASE_BUNDLE": ("Release",),
    "DOCUMENTATION_RELEASE": ("Documentation",),
    "EVIDENCE": ("Evidence",),
    "RECOVERY_EVIDENCE": ("Evidence", "Recovery-Snapshots"),
    "SELF_CONTAINED_DISASTER_RECOVERY": ("Evidence", "Recovery-Snapshots"),
    "PROJECT_HISTORY": ("Evidence", "Project-History"),
    "CANDIDATE_FREEZE_EVIDENCE": ("Evidence", "Project-History"),
    "RECERTIFICATION_EVIDENCE": ("Evidence", "Project-History"),
    "ACCEPTANCE_EVIDENCE": ("Evidence", "Project-History"),
    "PHASE_DOCUMENTATION_EVIDENCE": ("Evidence", "Project-History"),
}

@dataclass(frozen=True)
class PolicyFailure(Exception):
    code: str
    detail: str = ""
    def __str__(self) -> str:
        return self.code + (f": {self.detail}" if self.detail else "")


def _fail(code: str, detail: str = "") -> None:
    raise PolicyFailure(code, detail)


def validate_registry(registry: Mapping[str, Any], *, expected_root: str | None = None) -> dict[str, Any]:
    if registry.get("schema") != "INC_SHAREPOINT_BACKUP_REGISTRY_V1":
        _fail("CANONICAL_BACKUP_AUTHORITY_CONFLICT", "unsupported registry schema")
    if not expected_root or registry.get("authorized_root") != expected_root:
        _fail("BACKUP_DESTINATION_POLICY_VIOLATION", "authorized root mismatch")
    auth = registry.get("authority") or {}
    if auth.get("physical_destination_owner") != PHYSICAL_OWNER:
        _fail("CANONICAL_BACKUP_AUTHORITY_CONFLICT", "physical resolver owner mismatch")
    if auth.get("caller_destination_override") != "FORBIDDEN":
        _fail("CANONICAL_BACKUP_AUTHORITY_CONFLICT", "caller override must be forbidden")
    if set(auth.get("allowed_namespaces") or []) != ALLOWED_NAMESPACES:
        _fail("CANONICAL_BACKUP_AUTHORITY_CONFLICT", "namespace set mismatch")
    return {"ok": True, "status": "REGISTRY_AUTHORITY_VERIFIED"}


def reject_caller_physical_destination(request: Mapping[str, Any]) -> None:
    bad = sorted(k for k in CALLER_PATH_KEYS if request.get(k) not in (None, "", []))
    if bad:
        _fail("CALLER_SHAREPOINT_DESTINATION_OVERRIDE_FORBIDDEN", ",".join(bad))


def _safe_segment(value: Any, label: str) -> str:
    s = str(value or "").strip()
    if not s or s in {".", ".."} or "/" in s or "\\" in s:
        _fail("BACKUP_DESTINATION_POLICY_VIOLATION", f"invalid {label}")
    return s


def resolve_destination(request: Mapping[str, Any], registry: Mapping[str, Any], *, expected_root: str | None = None) -> dict[str, Any]:
    validate_registry(registry, expected_root=expected_root)
    reject_caller_physical_destination(request)
    scope = str(request.get("scope") or "").upper()
    if scope == "SKILL":
        name = _safe_segment(request.get("canonical_name"), "canonical_name")
        relative = PurePosixPath("Ecosystem", "Skills", name)
    elif scope == "PROJECT":
        project = _safe_segment(request.get("project"), "project")
        classification = str(request.get("classification") or "").upper()
        route = PROJECT_CLASSIFICATION_ROUTES.get(classification)
        if not route:
            _fail("CANONICAL_BACKUP_AUTHORITY_CONFLICT", f"unmapped project classification {classification or '<missing>'}")
        relative = PurePosixPath("Projects", project, *route)
    elif scope == "SHARED":
        topic = _safe_segment(request.get("topic"), "topic")
        relative = PurePosixPath("Shared", topic)
    else:
        _fail("CANONICAL_BACKUP_AUTHORITY_CONFLICT", f"unsupported scope {scope or '<missing>'}")
    if relative.parts[0] not in ALLOWED_NAMESPACES:
        _fail("BACKUP_DESTINATION_POLICY_VIOLATION", "namespace outside authority")
    return {
        "ok": True,
        "status": "SHAREPOINT_DESTINATION_RESOLVED",
        "physical_owner": PHYSICAL_OWNER,
        "authorized_root": expected_root,
        "relative_path": relative.as_posix(),
        "full_path": f"{expected_root}/{relative.as_posix()}",
    }


def validate_nested_managed_artifacts(nested_managed: Sequence[Mapping[str, Any]] | None, classification: str) -> dict[str, Any]:
    nested = list(nested_managed or [])
    cls = str(classification or "").upper()
    if nested and cls not in NESTED_BINARY_EXCEPTIONS:
        _fail("NESTED_MANAGED_ARTIFACT_DUPLICATION", f"{len(nested)} managed binary artifact(s)")
    return {"ok": True, "status": "NESTED_ARTIFACT_POLICY_PASS", "exception_used": bool(nested), "classification": cls}


def reconcile_authority(github: Mapping[str, Any], sharepoint: Mapping[str, Any]) -> dict[str, Any]:
    lineages = int(sharepoint.get("canonical_lineage_count", 1))
    if lineages != 1:
        _fail("CANONICAL_BACKUP_AUTHORITY_CONFLICT", f"canonical_lineage_count={lineages}")
    gv, sv = str(github.get("version") or ""), str(sharepoint.get("version") or "")
    if not gv or gv != sv:
        _fail("VERSION_AUTHORITY_DRIFT", f"github={gv or '<missing>'};sharepoint={sv or '<missing>'}")
    gh, sh = github.get("sha256"), sharepoint.get("installable_sha256") or sharepoint.get("sha256")
    if gh and sh and gh != sh:
        _fail("VERSION_AUTHORITY_DRIFT", "version equal but SHA-256 differs")
    return {"ok": True, "status": "VERSION_AUTHORITY_RECONCILED", "version": gv}


def publication_disposition(existing: Mapping[str, Any] | None, incoming: Mapping[str, Any]) -> dict[str, Any]:
    if not existing:
        return {"ok": True, "status": "PUBLISH_REQUIRED"}
    if existing.get("version") == incoming.get("version"):
        if existing.get("sha256") == incoming.get("sha256"):
            return {"ok": True, "status": "ALREADY_PUBLISHED"}
        _fail("VERSION_IMMUTABILITY_CONFLICT", "same version has different SHA-256")
    return {"ok": True, "status": "PUBLISH_REQUIRED"}


def destructive_cleanup_gate(evidence: Mapping[str, Any]) -> dict[str, Any]:
    required = ("inventory_snapshot", "dry_run_map", "rollback_evidence", "remote_readback")
    missing = [k for k in required if evidence.get(k) != "PASS"]
    if missing:
        _fail("DESTRUCTIVE_CLEANUP_EVIDENCE_REQUIRED", ",".join(missing))
    return {"ok": True, "status": "DESTRUCTIVE_CLEANUP_EVIDENCE_VERIFIED"}


def dual_destination_outcome(github_ok: bool, sharepoint_ok: bool, github_readback: bool, sharepoint_readback: bool) -> dict[str, Any]:
    g = bool(github_ok and github_readback)
    s = bool(sharepoint_ok and sharepoint_readback)
    if g and s:
        return {"ok": True, "status": "SUCCESS_VERIFIED"}
    if g or s:
        return {"ok": False, "status": "PARTIAL", "github_verified": g, "sharepoint_verified": s}
    return {"ok": False, "status": "FAILED", "github_verified": g, "sharepoint_verified": s}
