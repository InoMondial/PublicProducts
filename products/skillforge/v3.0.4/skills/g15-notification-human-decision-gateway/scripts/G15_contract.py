#!/usr/bin/env python3
"""Executable G15 Teams reporting contract gates.

Important distinction:
- pre-send validation inspects the actual HTML payload and rejects raw Markdown/table layout;
- post-send validation inspects normalized connector read-back for semantic presence,
  exact resolved route and links. Connector normalization can legitimately expose
  Markdown-like markers, so those markers alone are not treated as proof of raw-payload
  leakage after read-back.
"""
from __future__ import annotations
import re
from html import unescape
from typing import Any, Mapping
from urllib.parse import unquote
from G15_delivery_policy import (
    CANONICAL_RENDERER_ID,
    CANONICAL_TRANSPORT_CONTENT_FIELD,
    validate_destination_plan,
)

RAW_MARKDOWN_PATTERNS = (
    re.compile(r"(^|\n)\s*#{1,6}\s+"),
    re.compile(r"\*\*[^\n*]+\*\*"),
    re.compile(r"(^|\n)\s*```"),
    re.compile(r"\[[^\]]+\]\(https?://[^)]+\)"),
    re.compile(r"(^|\n)\s*\|.*\|\s*(\n|$)"),
)

MANDATORY_ROOT_MARKERS = (
    "PROJECT PROGRESS / پیشرفت پروژه",
    "Search Tags / هشتگ‌های جستجو",
)


def _plain(html_text: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", str(html_text or ""), flags=re.I)
    text = re.sub(r"</(?:p|li|h1|h2|h3|div|ul|ol|hr)>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return unescape(text)


def _safe_links(req: Mapping[str, Any]) -> list[str]:
    out=[]
    for item in req.get("source_links") or []:
        url = str(item.get("url") if isinstance(item, dict) else item or "")
        if re.match(r"^https?://", url):
            out.append(url)
    return out


def validate_pre_send(req: Mapping[str, Any], plan_result: Mapping[str, Any], rendered: Mapping[str, Any]) -> dict[str, Any]:
    errors=[]
    subject=str(rendered.get("subject") or "")
    body=str(rendered.get("html") or "")
    priority=str(plan_result.get("priority") or "")
    category=str(plan_result.get("message_category") or "")
    mtype=str(plan_result.get("message_type") or "MESSAGE")

    # Destination is an admission gate, not a suggestion.
    errors.extend(validate_destination_plan(plan_result))

    # Only the canonical G15 Teams-native renderer may enter the transport boundary.
    if rendered.get("renderer_id") != CANONICAL_RENDERER_ID:
        errors.append("CANONICAL_G15_RENDERER_REQUIRED")
    if rendered.get("transport_content_field") != CANONICAL_TRANSPORT_CONTENT_FIELD:
        errors.append("HTML_CONTENT_FIELD_REQUIRED")

    for token in ("[G15]", f"[{priority}]", f"[{category}]"):
        if token not in subject:
            errors.append("SUBJECT_CONTRACT_MISSING:"+token)
    if not body:
        errors.append("HTML_PAYLOAD_REQUIRED")
    if "<table" in body.lower() or "</table" in body.lower():
        errors.append("HTML_TABLE_LAYOUT_PROHIBITED")
    plain=_plain(body)
    for pattern in RAW_MARKDOWN_PATTERNS:
        if pattern.search(plain):
            errors.append("RAW_MARKDOWN_LAYOUT_PROHIBITED")
            break
    for marker in MANDATORY_ROOT_MARKERS:
        if marker not in plain:
            errors.append("MANDATORY_BLOCK_MISSING:"+marker)
    if "Search Tags / هشتگ‌های جستجو" in plain:
        after=plain.split("Search Tags / هشتگ‌های جستجو",1)[1].strip()
        if after and not all(line.lstrip().startswith("#") for line in after.splitlines() if line.strip()):
            errors.append("SEARCH_TAGS_NOT_FINAL")

    if mtype in {"MESSAGE","REPORT","FAILURE"}:
        if "Project Context" not in plain and "زمینه پروژه" not in plain:
            errors.append("PROJECT_CONTEXT_BLOCK_REQUIRED")
        if "Next Step" not in plain and "قدم بعدی" not in plain:
            errors.append("NEXT_STEP_BLOCK_REQUIRED")
    if mtype == "REPORT" and not str(req.get("outcome") or req.get("body") or "").strip():
        errors.append("OUTCOME_REQUIRED")
    for url in _safe_links(req):
        if url not in body:
            errors.append("EXACT_LINK_MISSING:"+url)
    return {"status":"PASS" if not errors else "FAIL", "errors":errors}


def _route_blob(readback: Mapping[str, Any]) -> str:
    return unquote(" ".join(str(readback.get(k) or "") for k in ("web_link","display_url","url")))


def validate_post_send_readback(
    readback: Mapping[str, Any], *, expected_subject: str, expected_team_id: str | None = None,
    expected_channel_id: str | None = None, required_links: list[str] | None = None,
) -> dict[str, Any]:
    """Validate connector read-back semantically and require exact resolved route evidence."""
    errors=[]
    content=str(readback.get("content") or "")
    title=str(readback.get("title") or readback.get("display_title") or "")
    if expected_subject and title != expected_subject:
        errors.append("READBACK_SUBJECT_MISMATCH")

    route_blob = _route_blob(readback)
    actual_team = str(readback.get("team_id") or "")
    actual_channel = str(readback.get("channel_id") or "")
    if expected_team_id and actual_team != expected_team_id and expected_team_id not in route_blob:
        errors.append("READBACK_TEAM_MISMATCH")
    if expected_channel_id and actual_channel != expected_channel_id and expected_channel_id not in route_blob:
        errors.append("READBACK_CHANNEL_MISMATCH")

    for marker in MANDATORY_ROOT_MARKERS:
        if marker not in content:
            errors.append("READBACK_MANDATORY_BLOCK_MISSING:"+marker)
    for url in required_links or []:
        if url and url not in content and url not in str(readback.get("web_link") or ""):
            errors.append("READBACK_LINK_MISSING:"+url)
    if not (readback.get("web_link") or readback.get("display_url")):
        errors.append("READBACK_THREAD_LINK_MISSING")
    return {"status":"PASS" if not errors else "FAIL", "errors":errors}


def delivery_state(send_accepted: bool, pre_send: Mapping[str, Any], readback: Mapping[str, Any] | None) -> str:
    if pre_send.get("status") != "PASS":
        return "RENDER_CONTRACT_FAILED"
    if not send_accepted:
        return "SEND_FAILED"
    if not readback or readback.get("status") != "PASS":
        return "RENDER_VALIDATION_FAILED"
    return "SENT_COMPLETE"
