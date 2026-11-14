#!/usr/bin/env python3
import re
from datetime import datetime, timezone

ORDER = ["LOW","MED","HIGH"]

def normalize_priority(value):
    if value is None:
        return None
    v = str(value).strip().upper()
    return {
        "CRITICAL":"HIGH","URGENT":"HIGH","P0":"HIGH","P1":"HIGH","HIGH":"HIGH",
        "MEDIUM":"MED","MED":"MED","NORMAL":"MED","P2":"MED",
        "LOW":"LOW","INFO":"LOW","INFORMATIONAL":"LOW","P3":"LOW",
    }.get(v)

def learning_key(req):
    cls = str(req.get("notification_class") or "").strip()
    if cls:
        return "class:" + cls.casefold()
    source = str(req.get("source_skill") or "").strip()
    event = str(req.get("event_type") or "").strip()
    return "source_event:" + source.casefold() + "::" + event.casefold() if source and event else None

def shift_priority(current, direction):
    cur = normalize_priority(current) or "MED"
    i = ORDER.index(cur)
    if direction == "HIGHER":
        return ORDER[min(i+1, 2)]
    if direction == "LOWER":
        return ORDER[max(i-1, 0)]
    raise ValueError("INVALID_DIRECTION")

def parse_feedback(text, current_priority="MED"):
    raw = str(text or "").strip()
    low = raw.casefold()
    if not raw:
        return {"valid":False,"reason":"EMPTY"}
    patterns = [
        ("HIGH",[r"\bhigh\b",r"\bcritical\b",r"اولویت\s*(بالا|زیاد|بیشتر)",r"پریوریتی\s*(بالا|high)"]),
        ("MED",[r"\bmed(?:ium)?\b",r"اولویت\s*(متوسط|میانی)",r"پریوریتی\s*(متوسط|med|medium)"]),
        ("LOW",[r"\blow\b",r"اولویت\s*(پایین|کم|کمتر)",r"پریوریتی\s*(پایین|low)"]),
    ]
    for priority, pats in patterns:
        if any(re.search(p, low, re.I) for p in pats):
            return {"valid":True,"direction":"ABSOLUTE","target_priority":priority,"raw":raw}
    if any(t in low for t in ["higher priority","more important","بالاتر","مهم‌تر","مهمتر","اولویت بیشتری","اولویت بیشتر"]):
        return {"valid":True,"direction":"HIGHER","target_priority":shift_priority(current_priority,"HIGHER"),"raw":raw}
    if any(t in low for t in ["lower priority","less important","پایین‌تر","پایینتر","کم‌اهمیت‌تر","کم اهمیت تر","اولویت کمتری","اولویت کمتر"]):
        return {"valid":True,"direction":"LOWER","target_priority":shift_priority(current_priority,"LOWER"),"raw":raw}
    return {"valid":False,"reason":"NO_PRIORITY_INTENT","raw":raw}

def clamp_to_floor(target_priority, mandatory_floor=None):
    target = normalize_priority(target_priority)
    floor = normalize_priority(mandatory_floor)
    if floor == "HIGH":
        return "HIGH"
    return target

def make_rule_record(req, parsed_feedback, updated_by=None, source_message_ref=None, mandatory_floor=None):
    key = learning_key(req)
    if not key:
        return {"status":"DURABLE_KEY_REQUIRED","record":None}
    if not parsed_feedback or parsed_feedback.get("valid") is not True:
        return {"status":"INVALID_PRIORITY_FEEDBACK","record":None}
    target = clamp_to_floor(parsed_feedback["target_priority"], mandatory_floor)
    record = {
        "RuleKey":key,
        "NotificationClass":req.get("notification_class"),
        "TargetPriority":target,
        "Direction":parsed_feedback["direction"],
        "SourceSkill":req.get("source_skill"),
        "EventType":req.get("event_type"),
        "UpdatedBy":updated_by,
        "UpdatedAt":datetime.now(timezone.utc).isoformat(),
        "SourceMessageRef":source_message_ref,
        "Comment":parsed_feedback.get("raw"),
        "Active":True,
    }
    return {"status":"PRIORITY_RULE_UPDATED","record":record}
