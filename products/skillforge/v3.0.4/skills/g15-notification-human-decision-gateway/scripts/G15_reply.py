#!/usr/bin/env python3
import re
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from G15_core import CONTROL_CODES, PERSIAN_DIGIT_TRANS, _now

def _normalize_reply_text(text):
    return str(text or "").strip().translate(PERSIAN_DIGIT_TRANS)


def parse_decision_reply(text, options=None, stage="INITIAL"):
    raw = _normalize_reply_text(text)
    if not raw:
        return {"valid":False,"status":"EMPTY_REPLY","code":None,"comment":""}
    match = re.match(r"^\s*(?:\[([A-Za-z0-9]{1,3})\]|([A-Za-z0-9]{1,3}))(?=$|[\s:;,-])\s*(.*)$", raw, re.S)
    if not match:
        return {"valid":False,"status":"INVALID_REPLY_CODE","code":None,"comment":raw}
    code = (match.group(1) or match.group(2)).upper()
    comment = match.group(3).strip(" \t\r\n-:؛،,")
    if code in CONTROL_CODES:
        return {"valid":True,"status":CONTROL_CODES[code],"code":code,"comment":comment}
    valid_codes = {
        str(item.get("code") if isinstance(item, dict) else idx).upper().translate(PERSIAN_DIGIT_TRANS)
        for idx, item in enumerate(options or [], 1)
    }
    if stage == "SECOND_CONFIRMATION":
        if code == "Y":
            return {"valid":True,"status":"FINAL_CONFIRMED","code":"Y","comment":comment}
        if code == "N":
            return {"valid":True,"status":"FINAL_NOT_CONFIRMED","code":"N","comment":comment}
        if code in valid_codes:
            return {"valid":True,"status":"OPTION_SELECTED","code":code,"comment":comment,"reselection":True}
        return {"valid":False,"status":"SECOND_CONFIRMATION_Y_OR_N_OR_NEW_OPTION_REQUIRED","code":code,"comment":comment}
    if code in valid_codes:
        return {"valid":True,"status":"OPTION_SELECTED","code":code,"comment":comment}
    return {"valid":False,"status":"UNKNOWN_OPTION_CODE","code":code,"comment":comment}


def apply_reply(state, text):
    """Apply a reply to a mutable decision-state dict. Deterministic and side-effect free."""
    if state.get("locked") is True:
        parsed = parse_decision_reply(text, state.get("options"), state.get("stage","INITIAL"))
        return {**state, "status":"POST_LOCK_INSTRUCTION", "post_lock_reply":parsed, "updated_at":_now()}
    parsed = parse_decision_reply(text, state.get("options"), state.get("stage","INITIAL"))
    history = list(state.get("history") or [])
    history.append({"at":_now(),"text":str(text),"parsed":parsed})
    new = {**state, "history":history, "updated_at":_now()}
    if not parsed["valid"]:
        new["status"] = parsed["status"]
        return new
    new["operator_comment"] = parsed.get("comment") or ""
    status = parsed["status"]
    if status in CONTROL_CODES.values():
        new["status"] = status
        return new
    if status == "OPTION_SELECTED":
        previous=state.get("selected_code")
        new["selected_code"] = parsed["code"]
        if previous and previous != parsed["code"]:
            new["superseded_code"] = previous
        if state.get("double_confirmation_required"):
            new["stage"] = "SECOND_CONFIRMATION"
            new["status"] = "SECOND_CONFIRMATION_REQUIRED"
        else:
            new["status"] = "FINAL_CONFIRMED"
        return new
    if status in {"FINAL_CONFIRMED","FINAL_NOT_CONFIRMED"}:
        new["status"] = status
        return new
    new["status"] = status
    return new


PRIORITY_PATTERNS = {
    "HIGH": (r"\bhigh(?:er)? priority\b", r"\bpriority\s*[:=]?\s*high\b", r"اولویت\s*(?:بالاتر|بالا|زیاد)"),
    "MED": (r"\bmed(?:ium)? priority\b", r"\bpriority\s*[:=]?\s*med(?:ium)?\b", r"اولویت\s*(?:متوسط)"),
    "LOW": (r"\blow(?:er)? priority\b", r"\bpriority\s*[:=]?\s*low\b", r"اولویت\s*(?:پایین‌تر|پایین|کمتر)"),
}
RELATIVE_PRIORITY = {
    "LOWER": (r"\blower (?:the )?priority\b", r"اولویت.*(?:پایین‌تر|کمتر)"),
    "HIGHER": (r"\bhigher (?:the )?priority\b", r"اولویت.*(?:بالاتر|بیشتر)"),
}
QUESTION_HINTS = ("?", "؟", "why ", "what ", "how ", "when ", "چرا", "چطور", "چگونه", "آیا", "چه ", "کی ", "کدام")
ACTION_HINTS = (
    "rerun", "run again", "execute", "do ", "change ", "update ", "fix ", "send ", "publish ", "delete ", "create ",
    "دوباره اجرا", "اجرا کن", "اصلاح کن", "تغییر بده", "آپدیت کن", "ارسال کن", "منتشر کن", "حذف کن", "بساز",
)


def _priority_intent(raw):
    low=raw.casefold()
    for level, pats in PRIORITY_PATTERNS.items():
        if any(re.search(p, low, re.I) for p in pats):
            return {"kind":"ABSOLUTE","value":level}
    for value,pats in RELATIVE_PRIORITY.items():
        if any(re.search(p, low, re.I) for p in pats):
            return {"kind":"RELATIVE","value":value}
    return None


def parse_owner_reply(text, *, options=None, decision_stage="INITIAL", decision_locked=False):
    """Parse a meaningful owner reply into independent semantic intents."""
    raw=_normalize_reply_text(text)
    if not raw:
        return {"status":"EMPTY_REPLY","meaningful":False,"raw":"","intents":[]}
    intents=[]
    decision=None
    if options:
        decision=parse_decision_reply(raw, options, decision_stage)
        if decision.get("valid"):
            intents.append({"type":"CONTROL" if decision["status"] in CONTROL_CODES.values() else "VOTE", **decision})
            residual=decision.get("comment") or ""
        else:
            residual=raw
    else:
        residual=raw
    pri=_priority_intent(residual)
    if pri:
        intents.append({"type":"PRIORITY_FEEDBACK", **pri})
    low=residual.casefold()
    if any(h in low for h in QUESTION_HINTS):
        intents.append({"type":"QUESTION","text":residual})
    if any(h in low for h in ACTION_HINTS):
        intents.append({"type":"INSTRUCTION","text":residual})
    if residual and not any(x["type"] in {"QUESTION","INSTRUCTION"} for x in intents):
        intents.append({"type":"COMMENT","text":residual})
    if decision_locked and decision and decision.get("valid"):
        intents.append({"type":"POST_LOCK_INSTRUCTION","text":raw})
    return {"status":"PARSED","meaningful":bool(intents),"raw":raw,"intents":intents}


def build_reply_acknowledgment(parsed, *, current_state, next_action, selected_option_label=None, previous_option=None, decision_id=None):
    """Minimum closed-loop reply contract: understood → current state → next action."""
    if not parsed.get("meaningful"):
        return {"status":"NO_ACTION_REQUIRED","text":""}
    understood=[]
    for intent in parsed.get("intents") or []:
        t=intent.get("type")
        if t == "VOTE":
            phrase=f"Option [{intent.get('code')}] selected"
            if selected_option_label: phrase += f" — {selected_option_label}"
            if previous_option and previous_option != intent.get("code"):
                phrase += f"; previous option [{previous_option}] superseded"
            understood.append(phrase)
        elif t == "CONTROL": understood.append(f"Control [{intent.get('code')}] → {intent.get('status')}")
        elif t == "PRIORITY_FEEDBACK": understood.append(f"Priority feedback: {intent.get('kind')} {intent.get('value')}")
        elif t == "QUESTION": understood.append(f"Question: {intent.get('text')}")
        elif t == "INSTRUCTION": understood.append(f"Instruction: {intent.get('text')}")
        elif t == "COMMENT": understood.append(f"Comment: {intent.get('text')}")
    trace=f"\nDecision ID: {decision_id}" if decision_id else ""
    text=(
        "✅ Reply processed\n"
        f"What I understood: {'; '.join(understood)}\n"
        f"Current state: {current_state}\n"
        f"What happens next: {next_action}{trace}"
    )
    return {"status":"ACK_READY","text":text,"understood":understood,"current_state":current_state,"next_action":next_action}
