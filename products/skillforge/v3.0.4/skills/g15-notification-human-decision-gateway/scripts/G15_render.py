#!/usr/bin/env python3
import html
import re
from urllib.parse import urlsplit, unquote, parse_qsl
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from G15_core import SKILL_ID, VERSION, WAITING_ICON, FINANCIAL_CATEGORIES, GENERIC_REPORT_TITLES, _now, _decision_category

PERSIAN_RE = re.compile(r"[\u0600-\u06FF]")
BIDI_CONTROL_RE = re.compile(r"[\u061C\u200E\u200F\u202A-\u202E\u2066-\u2069]")
RENDERER_ID = "G15_TEAMS_NATIVE_V1"
UTF8_ENCODING = "utf-8"


def _contains_persian(value):
    return bool(PERSIAN_RE.search(str(value or "")))


def _machine_clean(value, field="machine_identifier"):
    text = str(value or "")
    if BIDI_CONTROL_RE.search(text):
        raise ValueError(f"BIDI_CONTROL_FORBIDDEN_IN_{field.upper()}")
    return text


def _lang_dir(text, explicit_lang=None):
    lang = (explicit_lang or "").lower().strip()
    if lang == "fa" or (not lang and _contains_persian(text)):
        return "fa", "rtl"
    return "en", "ltr"


def _container(inner, text_for_detection="", explicit_lang=None):
    lang, direction = _lang_dir(text_for_detection, explicit_lang)
    return f'<div lang="{lang}" dir="{direction}">{inner}</div>'


def _render_result(subject, body, status="READY", **extra):
    result = {
        "status": status,
        "subject": subject,
        "html": body,
        "encoding": UTF8_ENCODING,
        "renderer_id": RENDERER_ID,
    }
    result.update(extra)
    return result


def _safe_url(value):
    if not isinstance(value, str) or not value:
        return False
    decoded = unquote(value)
    if any(ord(c) <= 32 or ord(c) == 127 for c in decoded) or BIDI_CONTROL_RE.search(decoded):
        return False
    try:
        u = urlsplit(value)
        if u.scheme != "https" or not u.hostname or u.username or u.password or "\\" in value:
            return False
        _ = u.port
        secret_keys = {"sig", "signature", "token", "access_token", "refresh_token", "api_key", "key", "client_secret", "password"}
        return not any(k.casefold() in secret_keys for k, _ in parse_qsl(u.query))
    except (ValueError, TypeError):
        return False


def _safe_links(links):
    out=[]
    for item in links or []:
        if isinstance(item, dict):
            label, url = str(item.get("label") or "Open"), str(item.get("url") or "")
        else:
            label, url = "Open", str(item)
        url = _machine_clean(url, "url")
        if _safe_url(url):
            out.append({"label":label,"url":url})
    return out


def _supporting_details(req):
    value = req.get("supporting_details")
    if value is None:
        return []
    if isinstance(value, dict):
        return [(str(k), str(v)) for k,v in value.items() if v is not None and str(v).strip()]
    if isinstance(value, list):
        rows=[]
        for item in value:
            if isinstance(item, dict):
                label = str(item.get("label") or item.get("key") or "Detail")
                val = item.get("value", item.get("text", ""))
                if str(val).strip(): rows.append((label,str(val)))
            elif str(item).strip():
                rows.append(("Detail",str(item)))
        return rows
    if str(value).strip():
        return [("Details",str(value))]
    return []


def _financial_support_complete(req):
    if _decision_category(req) not in FINANCIAL_CATEGORIES:
        return True
    details = {k.casefold(): v for k,v in _supporting_details(req)}
    links = _safe_links(req.get("source_links"))
    has_context = bool(details)
    has_locator = bool(links) or any(k in details for k in {
        "platform","site","broker","store","counterparty","seller","buyer","vendor","merchant"
    })
    return has_context and has_locator


def _links_html(links, heading="Quick Links / پیوندهای سریع"):
    safe = _safe_links(links)
    if not safe:
        return ""
    items = "".join(
        f'<li><a href="{html.escape(x["url"], quote=True)}">{html.escape(x["label"])}</a></li>' for x in safe
    )
    inner = f"<h3>🔗 {html.escape(heading)}</h3><ul>{items}</ul>"
    return _container(inner, heading)


def _project_context_html(plan_result):
    pid = _machine_clean(plan_result.get("project_id") or "—", "project_id")
    name = plan_result.get("project_name") or "UNKNOWN"
    category = _machine_clean(plan_result.get("message_category") or "GENERAL_NOTIFICATION", "message_category")
    priority = _machine_clean(plan_result.get("priority") or "MED", "priority")
    inner = (
        '<h3>📌 Project Context / زمینه پروژه</h3><ul>'
        f'<li><b>Project / پروژه:</b> {html.escape(str(name))} ({html.escape(str(pid))})</li>'
        f'<li><b>Priority / اولویت:</b> {html.escape(str(priority))}</li>'
        f'<li><b>Category / دسته‌بندی:</b> {html.escape(str(category))}</li>'
        '</ul>'
    )
    return _container(inner, str(name))


def _next_step_html(req):
    value=str(req.get("next_step") or req.get("owner_action") or "").strip()
    if not value:
        value="No action required"
    inner = f'<h3>🎯 Next Step / قدم بعدی</h3><p>{html.escape(value)}</p>'
    return _container(inner, value)


def _project_progress_html(plan_result):
    pid = _machine_clean(plan_result.get("project_id") or "—", "project_id")
    name = plan_result.get("project_name") or "UNKNOWN"
    category = _machine_clean(plan_result.get("message_category") or "GENERAL_NOTIFICATION", "message_category")
    stage = plan_result.get("project_stage") or "UNKNOWN"
    progress = plan_result.get("project_progress_percent")
    pct = "UNKNOWN" if progress is None else f"{progress}%"
    inner = (
        '<hr><h3>PROJECT PROGRESS / پیشرفت پروژه</h3>'
        '<ul>'
        f'<li><b>Project / پروژه:</b> {html.escape(str(name))} ({html.escape(str(pid))})</li>'
        f'<li><b>Category / دسته‌بندی:</b> {html.escape(str(category))}</li>'
        f'<li><b>Progress / پیشرفت:</b> {html.escape(pct)}</li>'
        f'<li><b>Current Stage / مرحله فعلی:</b> {html.escape(str(stage))}</li>'
        '</ul>'
    )
    return _container(inner, str(name) + str(stage))


def _search_tags_html(plan_result):
    en = " ".join(plan_result.get("search_tags_en") or [])
    fa = " ".join(plan_result.get("search_tags_fa") or [])
    return (
        '<hr><div><h3>Search Tags / هشتگ‌های جستجو</h3>'
        f'<p lang="en" dir="ltr">{html.escape(en)}</p>'
        f'<p lang="fa" dir="rtl">{html.escape(fa)}</p></div>'
    )


def render_message(req, plan_result):
    title = str(req.get("title") or "").strip()
    body_text = str(req.get("body") or "").strip()
    mtype = plan_result.get("message_type") or "MESSAGE"
    icon = "🚨" if mtype == "FAILURE" else "ℹ️"
    priority = _machine_clean(plan_result['priority'], "priority")
    category = _machine_clean(plan_result['message_category'], "message_category")
    subject = f"{icon} [G15][{priority}][{category}] {title}"
    details=""
    supporting=_supporting_details(req)
    if supporting:
        details='<h3>📋 Details / جزئیات</h3><ul>' + ''.join(
            f'<li><b>{html.escape(k)}:</b> {html.escape(v)}</li>' for k,v in supporting
        ) + '</ul>'
    inner = (
        f'<h2>{icon} {html.escape(title)}</h2>'
        f'<p><b>Outcome / نتیجه:</b> {html.escape(body_text)}</p>'
        f'{_project_context_html(plan_result)}{details}'
        f'{_links_html(req.get("source_links"))}{_next_step_html(req)}'
    )
    main = _container(inner, title + " " + body_text)
    return _render_result(subject, main + _project_progress_html(plan_result) + _search_tags_html(plan_result))


def render_decision(req, plan_result):
    q_en = str(req.get("question_en") or req.get("title") or "").strip()
    q_fa = str(req.get("question_fa") or "").strip()
    options = plan_result["decision_options"]
    en_opts = "".join(f"<li><b>[{html.escape(_machine_clean(o['code'], 'option_code'))}]</b> {html.escape(o['label_en'])}</li>" for o in options)
    fa_opts = "".join(f"<li><b>[{html.escape(_machine_clean(o['code'], 'option_code'))}]</b> {html.escape(o['label_fa'])}</li>" for o in options)
    did = html.escape(_machine_clean(plan_result["decision_id"], "decision_id"))
    cat_raw = _machine_clean(plan_result["decision_category"], "decision_category")
    pri_raw = _machine_clean(plan_result["priority"], "priority")
    cat = html.escape(cat_raw)
    pri = html.escape(pri_raw)
    subject = f"{WAITING_ICON} [G15][{pri_raw}][{cat_raw}] {q_en}"
    details = _supporting_details(req)
    links = _safe_links(req.get("source_links"))
    support_parts=[]
    if details:
        support_inner = "<h3>Supporting Information / اطلاعات پشتیبان</h3><ul>" + "".join(
            f"<li><b>{html.escape(k)}:</b> {html.escape(v)}</li>" for k,v in details
        ) + "</ul>"
        support_parts.append(_container(support_inner, " ".join(v for _,v in details)))
    if links:
        support_parts.append("<h3>Source & Evidence Links / لینک‌های منبع و شواهد</h3><ul>" + "".join(
            f'<li><a href="{html.escape(x["url"], quote=True)}">{html.escape(x["label"])}</a></li>' for x in links
        ) + "</ul>")
    support_url = str(req.get("attachment_or_support_file_url") or "").strip()
    if _safe_url(_machine_clean(support_url, "support_url")):
        support_parts.append(f'<p><b>Detailed support file:</b> <a href="{html.escape(support_url, quote=True)}">Open support file</a></p>')
    support_html = "<hr>" + "".join(support_parts) if support_parts else ""
    en_body = (
        f'<h2>{WAITING_ICON} SYSTEM WAITING FOR YOUR DECISION</h2>'
        f'<p><b>Question:</b> {html.escape(q_en)}</p><p><b>Response Priority:</b> {pri}</p>'
        f'<p><b>Category:</b> {cat}</p><h3>Options</h3><ul>{en_opts}</ul>'
        f'<p><b>Controls:</b> [X] Cancel · [D] Defer · [R] Re-ask</p><p><b>Decision ID:</b> {did}</p>'
    )
    fa_body = (
        f'<h2>{WAITING_ICON} سیستم منتظر تصمیم شماست</h2>'
        f'<p><b>سؤال:</b> {html.escape(q_fa)}</p><p><b>اولویت پاسخ:</b> {pri}</p>'
        f'<p><b>دسته‌بندی:</b> {cat}</p><h3>گزینه‌ها</h3><ul>{fa_opts}</ul>'
        f'<p><b>کنترل‌ها:</b> [X] لغو · [D] تعویق · [R] سؤال مجدد</p><p><b>شناسه تصمیم:</b> {did}</p>'
    )
    body = (
        _container(en_body, q_en, "en") + '<hr>' + _container(fa_body, q_fa, "fa")
        + support_html
        + _container('<h3>🎯 Next Step</h3><p>Reply in this same Teams thread with the option/control code and any optional instruction.</p>', '', 'en')
        + _project_progress_html(plan_result)
        + _search_tags_html(plan_result)
    )
    return _render_result(subject, body)


def _localized_report_headers(lang):
    if lang == "fa":
        return {
            "outcome":"نتیجه", "item":"مورد", "summary":"خلاصه", "impact":"تبعات / اثر",
            "next":"قدم بعدی پیشنهادی", "open":"باز کردن", "links":"پیوندهای سریع", "report_id":"شناسه گزارش"
        }
    return {
        "outcome":"Outcome", "item":"Item", "summary":"Summary", "impact":"Impact / Consequence",
        "next":"Recommended Next Step", "open":"Open", "links":"Quick Links", "report_id":"Report ID"
    }


def _report_item_html(row, hdr, lang):
    fields = {k:str(row.get(k) or "").strip() for k in ("item","summary","impact","next_step")}
    if not all(fields.values()):
        return None
    open_url=str(row.get("open") or "").strip()
    open_line=""
    if _safe_url(_machine_clean(open_url, "report_open_url")):
        label="باز کردن" if lang == "fa" else "Open"
        open_line=f'<li><b>{html.escape(hdr["open"])}:</b> <a href="{html.escape(open_url, quote=True)}">{label}</a></li>'
    inner = (
        '<ul>'
        f'<li><b>{html.escape(hdr["item"])}:</b> {html.escape(fields["item"])}</li>'
        f'<li><b>{html.escape(hdr["summary"])}:</b> {html.escape(fields["summary"])}</li>'
        f'<li><b>{html.escape(hdr["impact"])}:</b> {html.escape(fields["impact"])}</li>'
        f'<li><b>{html.escape(hdr["next"])}:</b> {html.escape(fields["next_step"])}</li>'
        f'{open_line}</ul>'
    )
    return _container(inner, " ".join(fields.values()), lang)


def render_report(req, plan_result):
    lang = str(req.get("language") or "en").lower()
    if lang not in {"en", "fa"}:
        lang = "fa" if _contains_persian(req.get("title") or req.get("body") or "") else "en"
    title = str(req.get("title") or "").strip()
    if title.casefold() in GENERIC_REPORT_TITLES:
        return {"status":"REPORT_INCOMPLETE","errors":["MEANINGFUL_REPORT_TITLE_REQUIRED"]}
    outcome = str(req.get("outcome") or req.get("body") or "").strip()
    rows = req.get("report_items") or []
    links = _safe_links(req.get("source_links"))
    if not links:
        return {"status":"REPORT_LINK_REQUIRED","errors":["AT_LEAST_ONE_INSPECTABLE_DEEP_LINK_REQUIRED"]}
    if not rows:
        return {"status":"REPORT_INCOMPLETE","errors":["REPORT_ITEMS_REQUIRED"]}
    hdr = _localized_report_headers(lang)
    item_blocks=[]
    for row in rows:
        if not isinstance(row, dict):
            return {"status":"REPORT_INCOMPLETE","errors":["REPORT_ITEM_OBJECT_REQUIRED"]}
        block=_report_item_html(row,hdr,lang)
        if not block:
            return {"status":"REPORT_INCOMPLETE","errors":["REPORT_ITEM_FIELDS_REQUIRED"]}
        item_blocks.append(block)
    quick = "".join(f'<li><a href="{html.escape(x["url"], quote=True)}">{html.escape(x["label"])}</a></li>' for x in links)
    rid_raw = _machine_clean(plan_result["report_id"], "report_id")
    rid = html.escape(rid_raw)
    priority = _machine_clean(plan_result['priority'], "priority")
    category = _machine_clean(plan_result['message_category'], "message_category")
    inner = (
        f'<h2>📊 {html.escape(title)}</h2>'
        f'<p><b>{hdr["outcome"]}:</b> {html.escape(outcome)}</p>'
        f'{_project_context_html(plan_result)}'
        f'<h3>📋 Summary / خلاصه</h3>{"<hr>".join(item_blocks)}'
        f'<h3>🔗 {hdr["links"]}</h3><ul>{quick}</ul>'
        f'<p><b>{hdr["report_id"]}:</b> {rid}</p>{_next_step_html(req)}'
    )
    main = _container(inner, title + " " + outcome, lang)
    body = main + _project_progress_html(plan_result) + _search_tags_html(plan_result)
    return _render_result(f"📊 [G15][{priority}][{category}] {title}", body)


def telemetry_envelope(plan_result, event_status, **extra):
    allowed = {
        "skill_id":SKILL_ID, "skill_version":VERSION,
        "dispatch_id":plan_result.get("dispatch_id"),
        "decision_id":plan_result.get("decision_id"),
        "report_id":plan_result.get("report_id"),
        "notification_class":plan_result.get("notification_class"),
        "message_type":plan_result.get("message_type"),
        "message_category":plan_result.get("message_category"),
        "project_id":plan_result.get("project_id"),
        "project_name":plan_result.get("project_name"),
        "project_stage":plan_result.get("project_stage"),
        "project_progress_percent":plan_result.get("project_progress_percent"),
        "decision_category":plan_result.get("decision_category"),
        "priority":plan_result.get("priority"), "status":event_status,
        "must_notify":plan_result.get("must_notify"),
        "mandatory_event_class":plan_result.get("mandatory_event_class"),
        "created_at":_now(), "measurement_status":"UNAVAILABLE",
        "encoding": UTF8_ENCODING,
        "renderer_id": RENDERER_ID,
    }
    for key in ("response_code","source_work_ref","teams_thread_ref","source_evidence_ref","responded_at","closed_at","owner_reply_message_id","parent_message_id","acknowledgment_message_id"):
        if key in extra and extra[key] is not None:
            allowed[key] = extra[key]
    for key in ("dispatch_id","decision_id","report_id","message_category","project_id","decision_category","priority","teams_thread_ref","owner_reply_message_id","parent_message_id","acknowledgment_message_id"):
        if key in allowed and allowed[key] is not None:
            _machine_clean(allowed[key], key)
    return {k:v for k,v in allowed.items() if v is not None}
