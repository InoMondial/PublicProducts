#!/usr/bin/env python3
"""Mandatory G15 destination and rendering policy.

This module makes the two owner requirements executable:
1) governed Teams notifications use the canonical LOW/MED/HIGH destinations by default;
2) a different Teams destination is allowed only when the user explicitly requested it.

The authorization bit for a destination override is intentionally an out-of-band runtime
argument, not a producer-controlled field inside INC_NOTIFICATION_EVENT_V1. A producer may
request an override locator, but cannot self-authorize it.
"""
from __future__ import annotations
from typing import Any, Mapping

DEFAULT_DESTINATION_REFS = {
    "HIGH": "INC_G15_PRIORITY_HIGH_CHANNEL",
    "MED": "INC_G15_PRIORITY_MED_CHANNEL",
    "LOW": "INC_G15_PRIORITY_LOW_CHANNEL",
    "TEST": "INC_G15_TEST_CHANNEL",
}

DEFAULT_DESTINATION_HINTS = {
    "HIGH": "Example Team / PARAM_HIGH_CHANNEL_NAME",
    "MED": "Example Team / PARAM_MED_CHANNEL_NAME",
    "LOW": "Example Team / PARAM_LOW_CHANNEL_NAME",
    "TEST": "PARAM_TEST_CHANNEL_NAME",
}

CANONICAL_RENDERER_ID = "G15_TEAMS_NATIVE_V1"
CANONICAL_TRANSPORT_CONTENT_FIELD = "html_content"


def _text(value: Any) -> str:
    return str(value or "").strip()


def is_explicit_transport_test(req: Mapping[str, Any]) -> bool:
    """True only for a genuine transport/integration/acceptance test event."""
    if req.get("test_mode") is not True:
        return False
    if req.get("transport_test") is True:
        return True
    category = _text(req.get("message_category")).upper()
    event = _text(req.get("event_type")).casefold()
    notification_class = _text(req.get("notification_class")).casefold()
    return (
        category == "TEST_VALIDATION"
        or event in {"transport_test", "integration_test", "acceptance_test", "live_acceptance_test"}
        or any(token in notification_class for token in ("transport-test", "integration-test", "acceptance-test"))
    )


def resolve_destination(
    req: Mapping[str, Any],
    priority: str,
    *,
    explicit_destination_authorized: bool = False,
) -> dict[str, Any]:
    """Resolve the only admissible delivery destination for this event.

    Precedence:
      1. user-explicit destination override, but only with out-of-band authorization;
      2. genuine transport test -> TEST channel;
      3. canonical priority route -> HIGH/MED/LOW channel.
    """
    priority = _text(priority).upper()
    if priority not in {"LOW", "MED", "HIGH"}:
        raise ValueError("INVALID_PRIORITY")

    override_ref = _text(req.get("destination_override_ref"))
    override_name = _text(req.get("destination_override_display_name"))
    override_reason = _text(req.get("destination_override_reason"))
    has_override_request = bool(override_ref or override_name or override_reason)

    if has_override_request:
        if explicit_destination_authorized is not True:
            raise ValueError("DESTINATION_OVERRIDE_NOT_AUTHORIZED")
        if not override_ref:
            raise ValueError("DESTINATION_OVERRIDE_REF_REQUIRED")
        if not override_reason:
            raise ValueError("DESTINATION_OVERRIDE_REASON_REQUIRED")
        return {
            "destination_ref": override_ref,
            "destination_display_hint": override_name or override_ref,
            "destination_policy": "USER_EXPLICIT_OVERRIDE",
            "destination_override_authorized": True,
            "destination_override_reason": override_reason,
        }

    if req.get("test_mode") is True:
        if not is_explicit_transport_test(req):
            raise ValueError("TEST_ROUTE_NOT_AUTHORIZED_FOR_PRODUCTION_EVENT")
        return {
            "destination_ref": DEFAULT_DESTINATION_REFS["TEST"],
            "destination_display_hint": DEFAULT_DESTINATION_HINTS["TEST"],
            "destination_policy": "TEST_ONLY",
            "destination_override_authorized": False,
        }

    return {
        "destination_ref": DEFAULT_DESTINATION_REFS[priority],
        "destination_display_hint": DEFAULT_DESTINATION_HINTS[priority],
        "destination_policy": "DEFAULT_PRIORITY_ROUTE",
        "destination_override_authorized": False,
    }


def validate_destination_plan(plan_result: Mapping[str, Any]) -> list[str]:
    """Reject route drift before transport even if a custom caller bypassed the router helper."""
    errors: list[str] = []
    priority = _text(plan_result.get("priority")).upper()
    policy = _text(plan_result.get("destination_policy"))
    dest = _text(plan_result.get("destination_ref"))

    if policy == "DEFAULT_PRIORITY_ROUTE":
        expected = DEFAULT_DESTINATION_REFS.get(priority)
        if not expected or dest != expected:
            errors.append("DEFAULT_PRIORITY_ROUTE_MISMATCH")
    elif policy == "TEST_ONLY":
        if dest != DEFAULT_DESTINATION_REFS["TEST"]:
            errors.append("TEST_ROUTE_MISMATCH")
    elif policy == "USER_EXPLICIT_OVERRIDE":
        if plan_result.get("destination_override_authorized") is not True:
            errors.append("DESTINATION_OVERRIDE_NOT_AUTHORIZED")
        if not dest:
            errors.append("DESTINATION_OVERRIDE_REF_REQUIRED")
    else:
        errors.append("DESTINATION_POLICY_REQUIRED")
    return errors


def canonical_render_metadata() -> dict[str, str]:
    return {
        "renderer_id": CANONICAL_RENDERER_ID,
        "transport_content_field": CANONICAL_TRANSPORT_CONTENT_FIELD,
    }
