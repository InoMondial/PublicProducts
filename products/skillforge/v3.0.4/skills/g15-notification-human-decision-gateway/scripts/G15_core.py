#!/usr/bin/env python3
import hashlib, re, uuid
from datetime import datetime, timezone

VERSION = "4.4.0"
SKILL_ID = "G15-SKL-001"
WAITING_ICON = "⏳"

PRIORITIES = ("LOW", "MED", "HIGH")
ALIASES = {
    "CRITICAL":"HIGH","URGENT":"HIGH","P0":"HIGH","P1":"HIGH","HIGH":"HIGH",
    "MEDIUM":"MED","MED":"MED","NORMAL":"MED","P2":"MED",
    "LOW":"LOW","INFO":"LOW","INFORMATIONAL":"LOW","P3":"LOW",
}
DESTINATION_REFS = {
    "HIGH":"INC_G15_PRIORITY_HIGH_CHANNEL",
    "MED":"INC_G15_PRIORITY_MED_CHANNEL",
    "LOW":"INC_G15_PRIORITY_LOW_CHANNEL",
    "TEST":"INC_G15_TEST_CHANNEL",
}
DECISION_CATEGORIES = {
    "PURCHASE","SALE","TRADE_ORDER","FINANCIAL_TRANSACTION","PAYMENT","TRANSFER","REFUND",
    "LEGAL_APPROVAL","CONTRACT_COMMITMENT","LOGIN_AUTHORIZATION","SECURITY_AUTHORIZATION",
    "DATA_DELETION","DEPLOYMENT_CHANGE","EXTERNAL_COMMUNICATION","SYSTEM_RECOVERY",
    "WORKFLOW_DECISION","GENERAL_INSTRUCTION",
}
FINANCIAL_CATEGORIES = {
    "PURCHASE","SALE","TRADE_ORDER","FINANCIAL_TRANSACTION","PAYMENT","TRANSFER","REFUND"
}
NOTIFICATION_CATEGORIES = {
    "GENERAL_NOTIFICATION","GITHUB_PUBLISH","DOCUMENT_PUBLISH","ARTIFACT_RELEASE","BACKUP",
    "TEST_VALIDATION","PROJECT_MILESTONE","SYSTEM_INCIDENT","WORKFLOW_STATUS","TASK_COMPLETION",
    "AUDIT","SYNC","REGISTRY_UPDATE","PRIORITY_UPDATE",
} | DECISION_CATEGORIES
MESSAGE_TYPES = {
    "MESSAGE","REPORT","FAILURE","DECISION_REQUEST","APPROVAL",
    "ACKNOWLEDGMENT","CHOICE","QUICK_CONFIRM","FORM",
}
ADAPTIVE_CARD_TYPES = {"ACKNOWLEDGMENT","CHOICE","QUICK_CONFIRM","FORM"}
CONTROL_CODES = {"X":"CANCELLED","D":"DEFERRED","R":"REASK_REQUESTED"}
MANDATORY_HIGH_FLAGS = {
    "financial_transaction","purchase_or_sale","system_waiting_for_user","blocking",
    "critical_issue","serious_legal_impact","high_consequence","system_crash","workflow_blocked",
    "process_stopped","serious_error","service_outage","data_integrity_risk",
}
EMERGENCY_FLAGS = {
    "system_crash","workflow_blocked","process_stopped","serious_error","service_outage","data_integrity_risk"
}
MED_FLAGS = {"degraded_service","recoverable_error","action_required","must_read"}
GENERIC_REPORT_TITLES = {
    "report","status","update","test report","summary",
    "گزارش","وضعیت","بروزرسانی","به روز رسانی","خلاصه",
}
PERSIAN_DIGIT_TRANS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

MESSAGE_TYPE_FA = {
    "MESSAGE":"پیام","REPORT":"گزارش","FAILURE":"خطا","DECISION_REQUEST":"تصمیم",
    "APPROVAL":"تأیید","ACKNOWLEDGMENT":"تأیید_دریافت","CHOICE":"انتخاب",
    "QUICK_CONFIRM":"تأیید_سریع","FORM":"فرم",
}
PRIORITY_FA = {"HIGH":"اولویت_بالا","MED":"اولویت_متوسط","LOW":"اولویت_پایین"}
CATEGORY_FA = {
    "GENERAL_NOTIFICATION":"اطلاع_رسانی","GITHUB_PUBLISH":"انتشار_گیتهاب","DOCUMENT_PUBLISH":"انتشار_مستند",
    "ARTIFACT_RELEASE":"انتشار_آرتیفکت","BACKUP":"پشتیبان","TEST_VALIDATION":"تست_اعتبارسنجی",
    "PROJECT_MILESTONE":"نقطه_عطف_پروژه","SYSTEM_INCIDENT":"رخداد_سیستم","WORKFLOW_STATUS":"وضعیت_گردش_کار",
    "TASK_COMPLETION":"تکمیل_تسک","AUDIT":"ممیزی","SYNC":"همگام_سازی","REGISTRY_UPDATE":"بروزرسانی_رجیستری",
    "PRIORITY_UPDATE":"تغییر_اولویت","PURCHASE":"خرید","SALE":"فروش","TRADE_ORDER":"سفارش_معامله",
    "FINANCIAL_TRANSACTION":"تراکنش_مالی","PAYMENT":"پرداخت","TRANSFER":"انتقال","REFUND":"بازپرداخت",
    "LEGAL_APPROVAL":"تأیید_حقوقی","CONTRACT_COMMITMENT":"تعهد_قراردادی","LOGIN_AUTHORIZATION":"مجوز_ورود",
    "SECURITY_AUTHORIZATION":"مجوز_امنیتی","DATA_DELETION":"حذف_داده","DEPLOYMENT_CHANGE":"تغییر_استقرار",
    "EXTERNAL_COMMUNICATION":"ارتباط_خارجی","SYSTEM_RECOVERY":"بازیابی_سیستم","WORKFLOW_DECISION":"تصمیم_گردش_کار",
    "GENERAL_INSTRUCTION":"دستور_عمومی",
}

EVENT_POLICIES = {
    "human_decision_requested": {"event_class":"DECISION_AUTHORIZATION","priority":"HIGH","category":"WORKFLOW_DECISION"},
    "purchase": {"event_class":"FINANCIAL_TRANSACTION","priority":"HIGH","category":"PURCHASE"},
    "sale": {"event_class":"FINANCIAL_TRANSACTION","priority":"HIGH","category":"SALE"},
    "trade_order": {"event_class":"FINANCIAL_TRANSACTION","priority":"HIGH","category":"TRADE_ORDER"},
    "payment": {"event_class":"FINANCIAL_TRANSACTION","priority":"HIGH","category":"PAYMENT"},
    "transfer": {"event_class":"FINANCIAL_TRANSACTION","priority":"HIGH","category":"TRANSFER"},
    "refund": {"event_class":"FINANCIAL_TRANSACTION","priority":"HIGH","category":"REFUND"},
    "legal_approval": {"event_class":"DECISION_AUTHORIZATION","priority":"HIGH","category":"LEGAL_APPROVAL"},
    "contract_commitment": {"event_class":"DECISION_AUTHORIZATION","priority":"HIGH","category":"CONTRACT_COMMITMENT"},
    "login_authorization": {"event_class":"DECISION_AUTHORIZATION","priority":"HIGH","category":"LOGIN_AUTHORIZATION"},
    "security_authorization": {"event_class":"DECISION_AUTHORIZATION","priority":"HIGH","category":"SECURITY_AUTHORIZATION"},
    "data_deletion": {"event_class":"DECISION_AUTHORIZATION","priority":"HIGH","category":"DATA_DELETION"},
    "system_crash": {"event_class":"CRITICAL_FAILURE_RISK","priority":"HIGH","category":"SYSTEM_INCIDENT"},
    "workflow_blocked": {"event_class":"CRITICAL_FAILURE_RISK","priority":"HIGH","category":"SYSTEM_INCIDENT"},
    "process_stopped": {"event_class":"CRITICAL_FAILURE_RISK","priority":"HIGH","category":"SYSTEM_INCIDENT"},
    "serious_error": {"event_class":"CRITICAL_FAILURE_RISK","priority":"HIGH","category":"SYSTEM_INCIDENT"},
    "service_outage": {"event_class":"CRITICAL_FAILURE_RISK","priority":"HIGH","category":"SYSTEM_INCIDENT"},
    "data_integrity_risk": {"event_class":"CRITICAL_FAILURE_RISK","priority":"HIGH","category":"SYSTEM_INCIDENT"},
    "required_release_failed": {"event_class":"CRITICAL_FAILURE_RISK","priority":"HIGH","category":"SYSTEM_INCIDENT"},
    "required_backup_failed": {"event_class":"CRITICAL_FAILURE_RISK","priority":"HIGH","category":"SYSTEM_INCIDENT"},
    "degraded_service": {"event_class":"RECOVERABLE_FAILURE","priority":"MED","category":"SYSTEM_INCIDENT"},
    "recoverable_error": {"event_class":"RECOVERABLE_FAILURE","priority":"MED","category":"SYSTEM_INCIDENT"},
    "contained_partial_failure": {"event_class":"RECOVERABLE_FAILURE","priority":"MED","category":"SYSTEM_INCIDENT"},
    "github_document_published": {"event_class":"PUBLICATION_SUCCESS","priority":"LOW","category":"GITHUB_PUBLISH"},
    "github_source_merged": {"event_class":"PUBLICATION_SUCCESS","priority":"LOW","category":"GITHUB_PUBLISH"},
    "artifact_published": {"event_class":"PUBLICATION_SUCCESS","priority":"LOW","category":"ARTIFACT_RELEASE"},
    "install_package_verified": {"event_class":"PUBLICATION_SUCCESS","priority":"LOW","category":"ARTIFACT_RELEASE"},
    "tag_release_asset_verified": {"event_class":"PUBLICATION_SUCCESS","priority":"LOW","category":"ARTIFACT_RELEASE"},
    "production_release_completed": {"event_class":"PUBLICATION_SUCCESS","priority":"LOW","category":"ARTIFACT_RELEASE"},
    "sharepoint_recovery_copy_verified": {"event_class":"BACKUP_SUCCESS","priority":"LOW","category":"BACKUP"},
    "canonical_archive_verified": {"event_class":"BACKUP_SUCCESS","priority":"LOW","category":"BACKUP"},
    "registry_reconciled": {"event_class":"PUBLICATION_SUCCESS","priority":"LOW","category":"REGISTRY_UPDATE"},
    "project_stage_changed": {"event_class":"PROJECT_LIFECYCLE","priority":"MED","category":"PROJECT_MILESTONE"},
    "milestone_achieved": {"event_class":"PROJECT_LIFECYCLE","priority":"MED","category":"PROJECT_MILESTONE"},
    "production_ready": {"event_class":"PROJECT_LIFECYCLE","priority":"MED","category":"PROJECT_MILESTONE"},
    "major_test_gate_passed": {"event_class":"PROJECT_LIFECYCLE","priority":"MED","category":"TEST_VALIDATION"},
    "major_test_gate_failed": {"event_class":"PROJECT_LIFECYCLE","priority":"MED","category":"TEST_VALIDATION"},
    "task_completed": {"event_class":"OPERATIONAL_COMPLETION","priority":"LOW","category":"TASK_COMPLETION"},
    "workflow_completed": {"event_class":"OPERATIONAL_COMPLETION","priority":"LOW","category":"WORKFLOW_STATUS"},
    "phase_completed": {"event_class":"OPERATIONAL_COMPLETION","priority":"LOW","category":"PROJECT_MILESTONE"},
    "scheduled_report_ready": {"event_class":"OPERATIONAL_COMPLETION","priority":"LOW","category":"WORKFLOW_STATUS"},
    "audit_completed": {"event_class":"OPERATIONAL_COMPLETION","priority":"LOW","category":"AUDIT"},
    "validation_completed": {"event_class":"OPERATIONAL_COMPLETION","priority":"LOW","category":"TEST_VALIDATION"},
    "sync_completed": {"event_class":"OPERATIONAL_COMPLETION","priority":"LOW","category":"SYNC"},
    "evidence_bundle_ready": {"event_class":"OPERATIONAL_COMPLETION","priority":"LOW","category":"AUDIT"},
    "priority_rule_updated": {"event_class":"PRIORITY_FEEDBACK","priority":"MED","category":"PRIORITY_UPDATE"},
}
MANDATORY_HIGH_EVENT_TYPES = {k for k,v in EVENT_POLICIES.items() if v["priority"] == "HIGH" and v["event_class"] in {"CRITICAL_FAILURE_RISK","FINANCIAL_TRANSACTION","DECISION_AUTHORIZATION"}}


def _now(): return datetime.now(timezone.utc).isoformat()


def normalize_priority(value):
    if value is None: return None
    key = str(value).strip().upper()
    if key not in ALIASES: raise ValueError("INVALID_PRIORITY")
    return ALIASES[key]


def _decision_category(req): return str(req.get("decision_category") or "").upper().strip()
def _event_type(req): return str(req.get("event_type") or "").strip().casefold()


def mandatory_event_policy(req):
    event = _event_type(req); policy = EVENT_POLICIES.get(event)
    if policy: return {"must_notify": True, "event_type": event, **policy}
    if req.get("must_notify") is True:
        return {"must_notify": True, "event_type": event or None, "event_class": "EXPLICIT_MANDATORY", "priority": None, "category": None}
    if any(req.get(flag) is True for flag in MANDATORY_HIGH_FLAGS):
        return {"must_notify": True, "event_type": event or None, "event_class": "SAFETY_MANDATORY", "priority": "HIGH", "category": "SYSTEM_INCIDENT"}
    if _decision_category(req) in FINANCIAL_CATEGORIES:
        return {"must_notify": True, "event_type": event or None, "event_class": "FINANCIAL_TRANSACTION", "priority": "HIGH", "category": _decision_category(req)}
    return {"must_notify": False, "event_type": event or None, "event_class": None, "priority": None, "category": None}


def mandatory_floor(req):
    if _decision_category(req) in FINANCIAL_CATEGORIES: return "HIGH"
    if _event_type(req) in MANDATORY_HIGH_EVENT_TYPES: return "HIGH"
    return "HIGH" if any(req.get(flag) is True for flag in MANDATORY_HIGH_FLAGS) else None


def classify_priority(req, learned_priority=None):
    floor = mandatory_floor(req)
    if floor: return floor, "MANDATORY_HIGH_FLOOR"
    if learned_priority: return normalize_priority(learned_priority), "LEARNED_PRIORITY_RULE"
    if req.get("priority") is not None: return normalize_priority(req.get("priority")), "EXPLICIT_PRIORITY"
    policy = mandatory_event_policy(req)
    if policy.get("priority"): return policy["priority"], "MANDATORY_EVENT_DEFAULT"
    if any(req.get(flag) is True for flag in MED_FLAGS): return "MED", "IMPORTANT_NONBLOCKING"
    if (req.get("routine_report") is True or req.get("activity_confirmation") is True) and not (req.get("action_required") is True or req.get("must_read") is True):
        return "LOW", "ROUTINE_INFORMATIONAL"
    return "MED", "UNKNOWN_DEFAULT_MED"


def normalize_message_category(req, message_type=None):
    mtype = str(message_type or req.get("message_type") or "MESSAGE").upper()
    if mtype == "DECISION_REQUEST":
        cat = _decision_category(req); return cat if cat else "WORKFLOW_DECISION"
    raw = str(req.get("message_category") or "").upper().strip()
    if raw:
        if raw not in NOTIFICATION_CATEGORIES: raise ValueError("INVALID_MESSAGE_CATEGORY")
        return raw
    policy = mandatory_event_policy(req)
    if policy.get("category"): return policy["category"]
    return "GENERAL_NOTIFICATION"


def is_emergency_event(req):
    if any(req.get(flag) is True for flag in EMERGENCY_FLAGS): return True
    return _event_type(req) in {"system_crash","workflow_blocked","process_stopped","serious_error","service_outage","data_integrity_risk"}


def _normalize_progress(value):
    if isinstance(value, bool): raise ValueError("PROJECT_PROGRESS_REQUIRED")
    try: number = int(value)
    except (TypeError, ValueError): raise ValueError("PROJECT_PROGRESS_REQUIRED")
    if not 0 <= number <= 100: raise ValueError("PROJECT_PROGRESS_RANGE")
    return number


def resolve_project_context(req, priority, message_type=None):
    emergency = priority == "HIGH" and is_emergency_event(req)
    name = str(req.get("project_name") or "").strip(); project_id = str(req.get("project_id") or "").strip() or None
    if not name and req.get("ecosystem_level") is True:
        name = "ECOSYSTEM"; project_id = project_id or "ECOSYSTEM"
    warnings=[]
    if not name:
        if emergency: name="UNKNOWN"; warnings.append("PROJECT_CONTEXT_DEGRADED")
        else: raise ValueError("PROJECT_CONTEXT_REQUIRED")
    stage = str(req.get("project_stage") or "").strip()
    if not stage:
        if emergency: stage="UNKNOWN"; warnings.append("PROJECT_PROGRESS_DEGRADED")
        else: raise ValueError("PROJECT_PROGRESS_REQUIRED")
    try: progress=_normalize_progress(req.get("project_progress_percent"))
    except ValueError as exc:
        if emergency:
            progress=None
            if "PROJECT_PROGRESS_DEGRADED" not in warnings: warnings.append("PROJECT_PROGRESS_DEGRADED")
        else: raise exc
    category=normalize_message_category(req,message_type)
    return {"project_id":project_id,"project_name":name,"project_name_fa":str(req.get("project_name_fa") or "").strip() or None,
            "project_stage":stage,"project_progress_percent":progress,"message_category":category,"metadata_warnings":warnings}


def _keyword_list(value):
    if value is None: return []
    if isinstance(value,str): return [x.strip() for x in re.split(r"[,;،]",value) if x.strip()]
    if isinstance(value,list): return [str(x).strip() for x in value if str(x).strip()]
    raise ValueError("SEARCH_KEYWORDS_REQUIRED")


def _unsafe_keyword(value):
    low=str(value).casefold()
    return any(token in low for token in ("password","passwd","cvv","otp","access_token","refresh_token","private_key","secret","رمز","گذرواژه","توکن"))


def normalize_search_keywords(req,priority):
    en=_keyword_list(req.get("keywords_en")); fa=_keyword_list(req.get("keywords_fa")); warnings=[]
    emergency=priority=="HIGH" and is_emergency_event(req)
    if any(_unsafe_keyword(x) for x in en+fa): raise ValueError("UNSAFE_SEARCH_KEYWORD")
    if not en or not fa:
        if not emergency: raise ValueError("SEARCH_KEYWORDS_REQUIRED")
        warnings.append("SEARCH_TAGS_DEGRADED")
    return en[:5],fa[:5],warnings


def _slug_en(value):
    text=re.sub(r"[^A-Za-z0-9]+","_",str(value or "").strip()).strip("_"); return text or "Unknown"
def _slug_fa(value):
    text=re.sub(r"[^\w\u0600-\u06FF]+","_",str(value or "").strip(),flags=re.UNICODE).strip("_"); return text or "نامشخص"


def build_search_tags(req,plan_result):
    priority=plan_result["priority"]; en_keywords,fa_keywords,warnings=normalize_search_keywords(req,priority)
    mtype=plan_result["message_type"]; category=plan_result["message_category"]
    project_en=_slug_en(plan_result["project_name"]); project_fa=_slug_fa(plan_result.get("project_name_fa") or plan_result["project_name"])
    en_tags=["#G15",f"#{_slug_en(mtype)}",f"#Project_{project_en}",f"#Category_{_slug_en(category)}",f"#Priority_{priority}"]+[f"#{_slug_en(x)}" for x in en_keywords]
    fa_type=MESSAGE_TYPE_FA.get(mtype,"پیام"); fa_cat=CATEGORY_FA.get(category,_slug_fa(category))
    fa_tags=["#جی15",f"#{_slug_fa(fa_type)}",f"#پروژه_{project_fa}",f"#دسته_{_slug_fa(fa_cat)}",f"#{PRIORITY_FA.get(priority,'اولویت_متوسط')}"]+[f"#{_slug_fa(x)}" for x in fa_keywords]
    return list(dict.fromkeys(en_tags))[:10],list(dict.fromkeys(fa_tags))[:10],warnings


def stable_dispatch_id(req):
    if req.get("dispatch_id"): return str(req["dispatch_id"])
    basis="|".join(str(req.get(k) or "") for k in ("source_work_id","dedupe_key","notification_class","title"))
    return "G15-N-"+hashlib.sha256(basis.encode("utf-8")).hexdigest()[:20].upper()


def _valid_uuid4_prefixed(value,prefix):
    if not isinstance(value,str) or not value.startswith(prefix): return False
    try:
        parsed=uuid.UUID(value[len(prefix):]); return parsed.version==4 and str(parsed)==value[len(prefix):].lower()
    except Exception: return False


def make_decision_id(value=None):
    if value:
        if not _valid_uuid4_prefixed(str(value),"G15-DQ-"): raise ValueError("INVALID_DECISION_ID")
        return str(value)
    return "G15-DQ-"+str(uuid.uuid4())


def make_report_id(value=None):
    if value:
        if not _valid_uuid4_prefixed(str(value),"G15-RPT-"): raise ValueError("INVALID_REPORT_ID")
        return str(value)
    return "G15-RPT-"+str(uuid.uuid4())


def interaction_surface(message_type):
    t=str(message_type or "MESSAGE").upper()
    if t=="DECISION_REQUEST": return "TEAMS_THREAD_REPLY"
    if t=="APPROVAL": return "MICROSOFT_TEAMS_APPROVALS"
    if t in ADAPTIVE_CARD_TYPES: return "TEAMS_ADAPTIVE_CARD"
    return "NONE"


def normalize_options(req):
    raw=req.get("decision_options",req.get("options"))
    if not isinstance(raw,list) or not (2<=len(raw)<=9): raise ValueError("DECISION_OPTIONS_2_TO_9_REQUIRED")
    out=[]; seen=set()
    for idx,item in enumerate(raw,1):
        if isinstance(item,dict):
            code=str(item.get("code") or idx).strip().upper().translate(PERSIAN_DIGIT_TRANS); en=str(item.get("label_en") or item.get("en") or "").strip(); fa=str(item.get("label_fa") or item.get("fa") or "").strip()
        else: code,en,fa=str(idx),str(item).strip(),""
        if not re.fullmatch(r"[A-Z0-9]{1,3}",code) or not en: raise ValueError("INVALID_DECISION_OPTION")
        if not fa: raise ValueError("PERSIAN_OPTION_LABEL_REQUIRED")
        if code in seen or code in CONTROL_CODES or code in {"Y","N"}: raise ValueError("RESERVED_OR_DUPLICATE_DECISION_CODE")
        seen.add(code); out.append({"code":code,"label_en":en,"label_fa":fa})
    return out


def requires_double_confirmation(req):
    if req.get("serious_legal_impact") is True or req.get("high_consequence") is True: return True
    category=_decision_category(req); amount=req.get("amount")
    if amount is None: return category in FINANCIAL_CATEGORIES
    try: numeric=float(amount)
    except (ValueError,TypeError): return category in FINANCIAL_CATEGORIES or req.get("financial_transaction") is True
    if numeric>50: return True
    if category in FINANCIAL_CATEGORIES and not str(req.get("currency") or "").strip(): return True
    return False
