#!/usr/bin/env python3
import json
import re
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from G15_core import *
from G15_core import _decision_category, _event_type
from G15_reply import *
from G15_render import *
from G15_render import _financial_support_complete, _supporting_details
from G15_contract import validate_pre_send
from G15_delivery_policy import resolve_destination, canonical_render_metadata


def _attach_validated_render(req, result, rendered):
    if not isinstance(rendered, dict) or rendered.get("status") not in (None,"READY"):
        result.update(status=(rendered or {}).get("status","RENDER_CONTRACT_FAILED"), errors=(rendered or {}).get("errors",["RENDER_FAILED"]))
        return result
    rendered = dict(rendered)
    rendered.update(canonical_render_metadata())
    check=validate_pre_send(req,result,rendered)
    result["render_contract"] = check
    if check["status"] != "PASS":
        result.update(status="RENDER_CONTRACT_FAILED", errors=check["errors"])
        return result
    result["rendered"] = rendered
    return result


def plan(req, learned_priority=None, native_approval_available=False, adaptive_card_available=False, explicit_destination_authorized=False):
    if not isinstance(req, dict):
        return {"status":"INVALID_REQUEST","errors":["REQUEST_NOT_OBJECT"]}
    if not str(req.get("title") or "").strip() or not str(req.get("body") or "").strip():
        return {"status":"INVALID_REQUEST","errors":["TITLE_AND_BODY_REQUIRED"]}

    message_type = str(req.get("message_type") or "MESSAGE").upper()
    if message_type not in MESSAGE_TYPES:
        return {"status":"INVALID_INTERACTION","errors":["INVALID_MESSAGE_TYPE"]}

    try:
        priority, reason = classify_priority(req, learned_priority)
        project = resolve_project_context(req, priority, message_type)
        destination = resolve_destination(
            req, priority, explicit_destination_authorized=explicit_destination_authorized
        )
    except ValueError as exc:
        return {"status":str(exc),"errors":[str(exc)]}

    mandatory = mandatory_event_policy(req)
    result = {
        "status":"READY","version":VERSION,"skill_id":SKILL_ID,
        "dispatch_id":stable_dispatch_id(req),"notification_class":req.get("notification_class"),
        "message_type":message_type,"priority":priority,"priority_reason":reason,
        "interaction_surface":interaction_surface(message_type),"errors":[],
        "must_notify":bool(mandatory.get("must_notify")),
        "mandatory_event_class":mandatory.get("event_class"),
        "event_type":mandatory.get("event_type") or _event_type(req) or None,
        "transport_owner":"G15_SINGLE_WRITER",
        "producer_contract":"INC_NOTIFICATION_EVENT_V1",
    }
    result.update(project)
    result.update(destination)

    try:
        tags_en, tags_fa, tag_warnings = build_search_tags(req, result)
    except ValueError as exc:
        return {**result,"status":str(exc),"errors":[str(exc)]}
    result["search_tags_en"] = tags_en
    result["search_tags_fa"] = tags_fa
    result["warnings"] = list(dict.fromkeys((result.get("metadata_warnings") or []) + tag_warnings))

    if message_type == "APPROVAL" and not native_approval_available:
        result.update(status="INTERACTIVE_CAPABILITY_REQUIRED", blocker="NATIVE_MICROSOFT_TEAMS_APPROVALS_REQUIRED")
        return result
    if message_type in ADAPTIVE_CARD_TYPES and not adaptive_card_available:
        result.update(status="INTERACTIVE_CAPABILITY_REQUIRED", blocker="TEAMS_ADAPTIVE_CARD_WAIT_FOR_RESPONSE_REQUIRED")
        return result

    if message_type == "DECISION_REQUEST":
        category = _decision_category(req)
        if category not in DECISION_CATEGORIES:
            result.update(status="INVALID_INTERACTION", errors=["VALID_DECISION_CATEGORY_REQUIRED"])
            return result
        priority, reason = classify_priority(req, learned_priority)
        try:
            destination = resolve_destination(
                req, priority, explicit_destination_authorized=explicit_destination_authorized
            )
        except ValueError as exc:
            result.update(status=str(exc), errors=[str(exc)])
            return result
        result.update(priority=priority, priority_reason=reason)
        result.update(destination)
        if not str(req.get("question_fa") or "").strip():
            result.update(status="INVALID_INTERACTION", errors=["PERSIAN_QUESTION_REQUIRED"])
            return result
        try:
            options = normalize_options(req)
            did = make_decision_id(req.get("decision_id"))
        except ValueError as exc:
            result.update(status="INVALID_INTERACTION", errors=[str(exc)])
            return result
        if category in FINANCIAL_CATEGORIES and not _financial_support_complete(req):
            result.update(status="DECISION_SUPPORT_REQUIRED", errors=["FINANCIAL_SUPPORT_CONTEXT_AND_LOCATOR_REQUIRED"])
            return result
        support_chars = sum(len(k)+len(v) for k,v in _supporting_details(req))
        if support_chars > 4000 and not re.match(r"^https?://", str(req.get("attachment_or_support_file_url") or "")):
            result.update(status="SUPPORT_FILE_REQUIRED", errors=["LARGE_SUPPORT_DETAILS_REQUIRE_ONE_CLICK_SUPPORT_FILE"])
            return result
        result.update(
            decision_id=did,
            decision_category=category, decision_icon=WAITING_ICON, decision_options=options,
            control_codes=CONTROL_CODES, bilingual_order=["en","fa"],
            double_confirmation_required=requires_double_confirmation(req),
            reply_mode="SINGLE_SHORT_CODE_PLUS_OPTIONAL_COMMENT",
        )
        result["message_category"] = category
        try:
            result["search_tags_en"], result["search_tags_fa"], more_warnings = build_search_tags(req, result)
            result["warnings"] = list(dict.fromkeys(result.get("warnings",[]) + more_warnings))
        except ValueError as exc:
            result.update(status=str(exc), errors=[str(exc)])
            return result
        return _attach_validated_render(req,result,render_decision(req, result))

    if message_type == "REPORT":
        try:
            result["report_id"] = make_report_id(req.get("report_id"))
        except ValueError as exc:
            result.update(status="REPORT_INCOMPLETE", errors=[str(exc)])
            return result
        return _attach_validated_render(req,result,render_report(req, result))

    if message_type in {"MESSAGE","FAILURE"}:
        return _attach_validated_render(req,result,render_message(req, result))

    return result


def main():
    try:
        req = json.load(sys.stdin)
    except Exception:
        print(json.dumps({"status":"INVALID_REQUEST","errors":["INVALID_JSON"]}))
        return 2
    result = plan(req)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in {
        "READY","INTERACTIVE_CAPABILITY_REQUIRED","REPORT_LINK_REQUIRED","REPORT_INCOMPLETE",
        "DECISION_SUPPORT_REQUIRED","SUPPORT_FILE_REQUIRED","PROJECT_CONTEXT_REQUIRED",
        "PROJECT_PROGRESS_REQUIRED","PROJECT_PROGRESS_RANGE","SEARCH_KEYWORDS_REQUIRED",
        "UNSAFE_SEARCH_KEYWORD","INVALID_MESSAGE_CATEGORY","RENDER_CONTRACT_FAILED",
        "DESTINATION_OVERRIDE_NOT_AUTHORIZED","DESTINATION_OVERRIDE_REF_REQUIRED",
        "DESTINATION_OVERRIDE_REASON_REQUIRED","TEST_ROUTE_NOT_AUTHORIZED_FOR_PRODUCTION_EVENT"
    } else 1


if __name__ == "__main__":
    raise SystemExit(main())
