#!/usr/bin/env python3
"""Deterministic G15 owner-reply discovery/filtering contract.

Scheduling is external. The central Scheduler/Dispatcher supplies recent Teams
messages/replies plus the durable ledger. This module does no network I/O.
"""
from __future__ import annotations
from datetime import datetime, timezone
import json
from typing import Any, Iterable, Mapping

TERMINAL_REPLY_STATES = {
    "COMPLETED", "NO_ACTION_REQUIRED", "DEFERRED", "CANCELLED", "BLOCKED",
    "IGNORED_SYSTEM_OUTBOUND", "DUPLICATE",
}


def _as_set(values: Iterable[str] | None) -> set[str]:
    return {str(x) for x in (values or []) if str(x)}


def _message_id(msg: Mapping[str, Any]) -> str:
    return str(msg.get("message_id") or msg.get("id") or "")


def _parent_id(msg: Mapping[str, Any]) -> str:
    return str(msg.get("parent_message_id") or msg.get("replyToId") or msg.get("reply_to_id") or "")


def _author_id(msg: Mapping[str, Any]) -> str:
    return str(
        msg.get("author_id") or msg.get("from_user_id") or msg.get("reply_author_id")
        or ((msg.get("from") or {}).get("user") or {}).get("id") or ""
    )


def _author_name(msg: Mapping[str, Any]) -> str:
    return str(msg.get("author_name") or msg.get("reply_author_name") or "")


def is_channel_reply(msg: Mapping[str, Any]) -> bool:
    kind = str(msg.get("container_type") or "").lower()
    return bool(_parent_id(msg)) and (not kind or kind == "channel_reply")


def is_owner(msg: Mapping[str, Any], owner_id: str | None = None, owner_name: str | None = None) -> bool:
    """Names are discovery hints, never authority to execute an owner's reply."""
    return isinstance(owner_id, str) and bool(owner_id.strip()) and _author_id(msg) == owner_id


def reply_eligibility(
    msg: Mapping[str, Any], *, owner_id: str | None = None, owner_name: str | None = None,
    outbound_message_ids: Iterable[str] | None = None,
    processed_reply_ids: Iterable[str] | None = None,
    managed_parent_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    mid = _message_id(msg)
    parent = _parent_id(msg)
    if not mid:
        return {"eligible": False, "state": "INVALID_MESSAGE_ID"}
    if not is_channel_reply(msg):
        return {"eligible": False, "state": "NOT_CHANNEL_REPLY", "message_id": mid}
    if mid in _as_set(outbound_message_ids):
        return {"eligible": False, "state": "IGNORED_SYSTEM_OUTBOUND", "message_id": mid, "parent_message_id": parent}
    if mid in _as_set(processed_reply_ids):
        return {"eligible": False, "state": "DUPLICATE", "message_id": mid, "parent_message_id": parent}
    if not is_owner(msg, owner_id=owner_id, owner_name=owner_name):
        return {"eligible": False, "state": "NON_OWNER_REPLY", "message_id": mid, "parent_message_id": parent}
    managed = _as_set(managed_parent_ids)
    if not managed or parent not in managed:
        return {"eligible": False, "state": "PARENT_NOT_G15_MANAGED", "message_id": mid, "parent_message_id": parent}
    return {"eligible": True, "state": "FILTERED_ELIGIBLE", "message_id": mid, "parent_message_id": parent}


def build_compact_reply_event(msg: Mapping[str, Any], monitor_cursor: str | None = None) -> dict[str, Any]:
    """Minimal payload passed across the deterministic→semantic boundary."""
    return {
        "reply_message_id": _message_id(msg),
        "reply_text": str(msg.get("content") or msg.get("reply_text") or ""),
        "reply_author_id": _author_id(msg) or None,
        "reply_author_name": _author_name(msg) or None,
        "reply_created_at": msg.get("created_at") or msg.get("createdDateTime"),
        "parent_message_id": _parent_id(msg),
        "team_id": msg.get("team_id"),
        "channel_id": msg.get("channel_id"),
        "reply_web_url": msg.get("web_link") or msg.get("display_url") or msg.get("webUrl"),
        "monitor_cursor": monitor_cursor,
    }


def reconcile_tick(
    messages: Iterable[Mapping[str, Any]], *, owner_id: str | None = None, owner_name: str | None = None,
    outbound_message_ids: Iterable[str] | None = None,
    processed_reply_ids: Iterable[str] | None = None,
    managed_parent_ids: Iterable[str] | None = None,
    monitor_cursor: str | None = None,
) -> dict[str, Any]:
    """At-least-once discovery with deterministic de-dup before AI."""
    eligible, ignored = [], []
    unique, fingerprints, conflicting = {}, {}, set()
    for msg in messages:
        if not isinstance(msg, Mapping):
            ignored.append({"eligible": False, "state": "INVALID_MESSAGE"})
            continue
        mid = _message_id(msg)
        try:
            fingerprint = json.dumps(dict(msg), sort_keys=True, separators=(",", ":"), allow_nan=False)
        except (ValueError, TypeError):
            ignored.append({"eligible": False, "state": "INVALID_MESSAGE"})
            continue
        if mid in fingerprints:
            if fingerprints[mid] != fingerprint:
                conflicting.add(mid)
            else:
                ignored.append({"eligible": False, "state": "DUPLICATE", "message_id": mid})
        else:
            fingerprints[mid], unique[mid] = fingerprint, msg
    # Reconcile the entire bounded tick before emitting executable replies.
    for mid in conflicting:
        unique.pop(mid, None)
        ignored.append({"eligible": False, "state": "CONFLICTING_MESSAGE_ID", "message_id": mid})
    for msg in unique.values():
        result = reply_eligibility(
            msg, owner_id=owner_id, owner_name=owner_name,
            outbound_message_ids=outbound_message_ids,
            processed_reply_ids=processed_reply_ids,
            managed_parent_ids=managed_parent_ids,
        )
        if result["eligible"]:
            eligible.append(build_compact_reply_event(msg, monitor_cursor))
        else:
            ignored.append(result)
    eligible.sort(key=lambda x: (str(x.get("reply_created_at") or ""), x["reply_message_id"]))
    return {
        "status": "REPLY_MONITOR_CONFLICT" if conflicting else "REPLY_MONITOR_PASS",
        "eligible_owner_replies": eligible,
        "ignored": ignored,
        "eligible_count": len(eligible),
        "ignored_count": len(ignored),
    }


def record_outbound(ledger: dict[str, Any], message_id: str, *, parent_message_id: str | None = None, kind: str = "ACK") -> dict[str, Any]:
    """Record every G15 Teams write, even when the delegated author is the owner."""
    if not message_id:
        raise ValueError("OUTBOUND_MESSAGE_ID_REQUIRED")
    out = dict(ledger or {})
    outbound = dict(out.get("outbound") or {})
    outbound[str(message_id)] = {
        "kind": kind,
        "parent_message_id": parent_message_id,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    out["outbound"] = outbound
    return out


def record_reply_state(ledger: dict[str, Any], reply_message_id: str, state: str, **extra: Any) -> dict[str, Any]:
    if not reply_message_id:
        raise ValueError("REPLY_MESSAGE_ID_REQUIRED")
    out = dict(ledger or {})
    replies = dict(out.get("replies") or {})
    replies[str(reply_message_id)] = {
        **dict(replies.get(str(reply_message_id)) or {}),
        "state": str(state),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        **{k: v for k, v in extra.items() if v is not None},
    }
    out["replies"] = replies
    return out


def processed_ids_from_ledger(ledger: Mapping[str, Any] | None) -> set[str]:
    return set((ledger or {}).get("replies") or {})


def outbound_ids_from_ledger(ledger: Mapping[str, Any] | None) -> set[str]:
    return set((ledger or {}).get("outbound") or {})
