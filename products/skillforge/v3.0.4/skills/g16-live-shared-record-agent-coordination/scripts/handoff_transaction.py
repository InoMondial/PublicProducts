#!/usr/bin/env python3
"""Deterministic G16 dual-sequence transactional writer core.

This module does not call SharePoint/GitHub. A real adapter MUST perform the remote
read, conditional write (CAS/If-Match when available), and post-write readback.
The core computes S/M internally and emits receipts that the adapter persists.
"""
from __future__ import annotations
import copy
import hashlib
import json

CONTRACT = "INC_G16_HANDOFF_TRANSACTIONAL_WRITER_V1"
SCHEMA = "G16_HANDOFF_DUAL_SEQUENCE_V1"
EVENT_STATES = {"OPEN", "INTERRUPTED", "COMPLETED", "BLOCKED", "TRANSFERRED"}

class Invalid(ValueError): pass

def require(ok, code):
    if not ok: raise Invalid(code)

def is_int(v): return type(v) is int and v >= 0
def nonempty(v): return isinstance(v, str) and bool(v.strip())

def digest(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()

def _maps(state):
    return state.get("interaction_idempotency", {}), state.get("checkpoint_idempotency", {})

def validate_state(state):
    require(isinstance(state, dict), "G16_TX_STATE_REQUIRED")
    require(state.get("schema_version") == SCHEMA, "G16_TX_SCHEMA_MISMATCH")
    require(nonempty(state.get("handoff_id")), "G16_TX_HANDOFF_ID_REQUIRED")
    require(is_int(state.get("interaction_seq")), "G16_TX_S_INVALID")
    require(is_int(state.get("material_seq")), "G16_TX_M_INVALID")
    expected = f"{state['handoff_id']} | S:{state['interaction_seq']} | M:{state['material_seq']}"
    require(state.get("visible_ref") == expected, "G16_TX_VISIBLE_REF_MISMATCH")
    ev = state.get("current_interaction")
    require(ev is None or isinstance(ev, dict), "G16_TX_CURRENT_INTERACTION_INVALID")
    if ev is not None:
        require(isinstance(ev.get("status"),str) and ev.get("status") in EVENT_STATES, "G16_TX_INTERACTION_STATUS_INVALID")
        require(type(ev.get("S")) is int and ev.get("S") == state["interaction_seq"], "G16_TX_INTERACTION_S_MISMATCH")
        require(nonempty(ev.get("turn_id")), "G16_TX_TURN_ID_REQUIRED")
        require(isinstance(ev.get("causal_M"),list) and all(type(m) is int and 0<m<=state["material_seq"] for m in ev["causal_M"]), "G16_TX_CAUSAL_M_INVALID")
    for field in ("interaction_idempotency", "checkpoint_idempotency"):
        require(field not in state or isinstance(state[field], dict), "G16_TX_IDEMPOTENCY_MAP_INVALID")

def validate_remote_observation(obs, state):
    require(isinstance(obs, dict), "G16_TX_REMOTE_OBSERVATION_REQUIRED")
    require(obs.get("readback_verified") is True, "G16_TX_PREWRITE_READBACK_REQUIRED")
    require(nonempty(obs.get("remote_revision")), "G16_TX_REMOTE_REVISION_REQUIRED")
    require(obs.get("observed_state_sha256") == digest(state), "G16_TX_REMOTE_STATE_STALE")
    require(obs.get("single_writer_or_cas_verified") is True, "G16_TX_SINGLE_WRITER_OR_CAS_REQUIRED")

def visible_ref(state): return f"{state['handoff_id']} | S:{state['interaction_seq']} | M:{state['material_seq']}"

def _interaction_fingerprint(event):
    return digest({"type": event.get("type"), "turn_id": event.get("turn_id"), "surface": event.get("surface")})

def _checkpoint_fingerprint(event, ledger):
    return digest({"S": event.get("S"), "checkpoint_id": event.get("checkpoint_id"), "ledger_digest": ledger.get("ledger_digest")})

def _resume(state,obs,event):
    out=copy.deepcopy(state)
    cur=out['current_interaction'];cur['status']='OPEN';cur['resumed_at']=event.get('at')
    cur.pop('closed_at',None);cur.pop('response_digest',None)
    out.setdefault('interaction_idempotency',{})[event['turn_id']]={'S':cur['S'],'event_fingerprint':_interaction_fingerprint(event)}
    return {'state':out,'receipt':{'contract':CONTRACT,'operation':'RESUME_INTERACTION','S':cur['S'],'M':out['material_seq'],
        'turn_id':event['turn_id'],'remote_revision_before':obs['remote_revision'],
        'state_sha256_before':digest(state),'state_sha256_after':digest(out),'increment_S':0,'increment_M':0}}

def allocate_interaction(state, obs, event):
    validate_state(state); validate_remote_observation(obs, state)
    require(isinstance(event,dict), "G16_TX_EVENT_REQUIRED")
    require(event.get("type") == "EXTERNAL_USER_TURN", "G16_TX_EVENT_TYPE_INVALID")
    require(nonempty(event.get("turn_id")), "G16_TX_TURN_ID_REQUIRED")
    fp = _interaction_fingerprint(event)
    imap, _ = _maps(state)
    prior = imap.get(event["turn_id"])
    if prior is not None:
        require(isinstance(prior,dict), "G16_TX_IDEMPOTENCY_MAP_INVALID")
        require(prior.get("event_fingerprint") == fp, "G16_TX_INTERACTION_IDEMPOTENCY_CONFLICT")
        existing=state.get("current_interaction")
        if existing and existing.get("turn_id")==event["turn_id"] and existing.get("status") in {"INTERRUPTED","TRANSFERRED"}:
            return _resume(state,obs,event)
        return {"state": copy.deepcopy(state), "receipt": {
            "contract": CONTRACT, "operation": "REPLAY_INTERACTION", "S": prior["S"], "M": state["material_seq"],
            "turn_id": event["turn_id"], "remote_revision_before": obs["remote_revision"],
            "state_sha256_before": digest(state), "state_sha256_after": digest(state), "increment_S": 0, "increment_M": 0,
            "idempotent_replay": True,
        }}
    existing = state.get("current_interaction")
    if existing and existing.get("turn_id") == event["turn_id"]:
        require(existing.get("surface")==event.get("surface"), "G16_TX_SURFACE_TRANSFER_AUTHORITY_REQUIRED")
        if existing.get("status") in {"INTERRUPTED","TRANSFERRED"}:
            return _resume(state,obs,event)
        # Legacy state may predate persisted idempotency maps. Same interaction identity never allocates another S.
        return {"state": copy.deepcopy(state), "receipt": {
            "contract": CONTRACT,
            "operation": "RESUME_INTERACTION" if existing.get("status") in {"OPEN", "INTERRUPTED", "TRANSFERRED"} else "REPLAY_INTERACTION",
            "S": existing["S"], "M": state["material_seq"], "turn_id": event["turn_id"],
            "remote_revision_before": obs["remote_revision"], "state_sha256_before": digest(state), "state_sha256_after": digest(state),
            "increment_S": 0, "increment_M": 0, "idempotent_replay": True,
        }}
    if existing and existing.get("status") in {"OPEN", "INTERRUPTED", "TRANSFERRED"}:
        raise Invalid("G16_TX_OPEN_TURN_ALREADY_EXISTS")
    out = copy.deepcopy(state)
    out.setdefault("interaction_idempotency", {})
    out.setdefault("checkpoint_idempotency", {})
    out["interaction_seq"] += 1
    out["current_interaction"] = {"S": out["interaction_seq"], "turn_id": event["turn_id"], "status": "OPEN", "surface": event.get("surface"), "opened_at": event.get("at"), "causal_M": []}
    out["interaction_idempotency"][event["turn_id"]] = {"S": out["interaction_seq"], "event_fingerprint": fp}
    out["visible_ref"] = visible_ref(out)
    return {"state": out, "receipt": {
        "contract": CONTRACT, "operation": "ALLOCATE_INTERACTION", "S": out["interaction_seq"], "M": out["material_seq"],
        "turn_id": event["turn_id"], "remote_revision_before": obs["remote_revision"], "state_sha256_before": digest(state),
        "state_sha256_after": digest(out), "increment_S": 1, "increment_M": 0,
    }}

def commit_material(state, obs, ledger, event):
    validate_state(state); validate_remote_observation(obs, state)
    require(isinstance(ledger, dict), "G16_TX_TOOL_LEDGER_REQUIRED")
    require(ledger.get("immutable") is True, "G16_TX_TOOL_LEDGER_IMMUTABLE_REQUIRED")
    require(nonempty(ledger.get("ledger_digest")), "G16_TX_TOOL_LEDGER_DIGEST_REQUIRED")
    require(ledger.get("material_change_detected") is True, "G16_TX_MATERIAL_EVIDENCE_REQUIRED")
    require(isinstance(event,dict), "G16_TX_EVENT_REQUIRED")
    require(nonempty(event.get("checkpoint_id")), "G16_TX_CHECKPOINT_ID_REQUIRED")
    fp = _checkpoint_fingerprint(event, ledger)
    _, cmap = _maps(state)
    prior = cmap.get(event["checkpoint_id"])
    if prior is not None:
        require(prior.get("event_fingerprint") == fp, "G16_TX_CHECKPOINT_IDEMPOTENCY_CONFLICT")
        return {"state": copy.deepcopy(state), "receipt": {
            "contract": CONTRACT, "operation": "REPLAY_MATERIAL", "S": prior["S"], "M": prior["M"],
            "checkpoint_id": event["checkpoint_id"], "ledger_digest": ledger["ledger_digest"],
            "remote_revision_before": obs["remote_revision"], "state_sha256_before": digest(state), "state_sha256_after": digest(state),
            "increment_S": 0, "increment_M": 0, "idempotent_replay": True,
        }}
    cur = state.get("current_interaction")
    require(isinstance(cur, dict) and cur.get("status") == "OPEN", "G16_TX_OPEN_INTERACTION_REQUIRED")
    require(event.get("S") == state["interaction_seq"] == cur.get("S"), "G16_TX_CAUSAL_S_MISMATCH")
    out = copy.deepcopy(state)
    out.setdefault("interaction_idempotency", {})
    out.setdefault("checkpoint_idempotency", {})
    out["material_seq"] += 1
    m = out["material_seq"]
    out["current_interaction"]["causal_M"].append(m)
    out["last_material_checkpoint"] = {"M": m, "causal_S": out["interaction_seq"], "checkpoint_id": event["checkpoint_id"], "ledger_digest": ledger["ledger_digest"], "committed_at": event.get("at")}
    out["checkpoint_idempotency"][event["checkpoint_id"]] = {"S": out["interaction_seq"], "M": m, "event_fingerprint": fp, "ledger_digest": ledger["ledger_digest"]}
    out["visible_ref"] = visible_ref(out)
    return {"state": out, "receipt": {
        "contract": CONTRACT, "operation": "COMMIT_MATERIAL", "S": out["interaction_seq"], "M": m,
        "checkpoint_id": event["checkpoint_id"], "ledger_digest": ledger["ledger_digest"], "remote_revision_before": obs["remote_revision"],
        "state_sha256_before": digest(state), "state_sha256_after": digest(out), "increment_S": 0, "increment_M": 1,
    }}

def close_interaction(state, obs, event):
    validate_state(state); validate_remote_observation(obs, state)
    require(isinstance(event,dict), "G16_TX_EVENT_REQUIRED")
    cur = state.get("current_interaction")
    require(isinstance(cur, dict), "G16_TX_INTERACTION_REQUIRED")
    require(event.get("S") == state["interaction_seq"] == cur.get("S"), "G16_TX_CLOSE_S_MISMATCH")
    require(event.get("status") in {"COMPLETED", "BLOCKED", "INTERRUPTED", "TRANSFERRED"}, "G16_TX_CLOSE_STATUS_INVALID")
    if cur.get("status") == event["status"] and cur.get("status") != "OPEN":
        return {"state": copy.deepcopy(state), "receipt": {
            "contract": CONTRACT, "operation": "REPLAY_CLOSE", "S": state["interaction_seq"], "M": state["material_seq"],
            "status": event["status"], "remote_revision_before": obs["remote_revision"], "state_sha256_before": digest(state),
            "state_sha256_after": digest(state), "increment_S": 0, "increment_M": 0, "idempotent_replay": True,
        }}
    require(cur.get("status") not in {"COMPLETED", "BLOCKED"}, "G16_TX_TERMINAL_INTERACTION_CONFLICT")
    out = copy.deepcopy(state)
    out["current_interaction"]["status"] = event["status"]
    out["current_interaction"]["closed_at"] = event.get("at")
    out["current_interaction"]["response_digest"] = event.get("response_digest")
    out["visible_ref"] = visible_ref(out)
    return {"state": out, "receipt": {
        "contract": CONTRACT, "operation": "CLOSE_INTERACTION", "S": out["interaction_seq"], "M": out["material_seq"],
        "status": event["status"], "remote_revision_before": obs["remote_revision"], "state_sha256_before": digest(state),
        "state_sha256_after": digest(out), "increment_S": 0, "increment_M": 0,
    }}

def validate_postwrite(before, proposed, observed_after, receipt):
    validate_state(before); validate_state(proposed); validate_state(observed_after)
    require(observed_after == proposed, "G16_TX_POSTWRITE_STATE_MISMATCH")
    require(nonempty(receipt.get("remote_revision_after")), "G16_TX_REMOTE_REVISION_AFTER_REQUIRED")
    unchanged=before==proposed and receipt.get('idempotent_replay') is True and receipt.get('increment_S')==0 and receipt.get('increment_M')==0
    require(unchanged or receipt.get("remote_revision_after") != receipt.get("remote_revision_before"), "G16_TX_REMOTE_REVISION_NOT_ADVANCED")
    require(receipt.get('state_sha256_before')==digest(before), 'G16_TX_RECEIPT_BEFORE_DIGEST_MISMATCH')
    require(receipt.get("postwrite_readback_verified") is True, "G16_TX_POSTWRITE_READBACK_REQUIRED")
    require(receipt.get("state_sha256_after") == digest(observed_after), "G16_TX_RECEIPT_DIGEST_MISMATCH")
