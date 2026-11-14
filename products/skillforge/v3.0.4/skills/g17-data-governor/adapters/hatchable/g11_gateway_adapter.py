"""G17 host-authenticated Hatchable binding for the G11 Adapter protocol.

Transport is a trusted host callable(route, body) -> {status, body}. Configure
its existing administrative identity outside caller requests. This module never
loads keys, changes schema, retries an ambiguous write, or executes caller SQL.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
from typing import Any, Callable, Mapping
from urllib.parse import quote, unquote

ROUTE = 'INC_G11_G17_DB_WRITE_ROUTE_V1'
ENDPOINT = '/api/admin/g11-write'
CAPABILITIES = 'INC_G11_G17_WRITE_CAPABILITIES_V1'
IDS = {'run':'run_id','event':'event_id','action':'action_id','metric':'metric_id',
       'error':'error_id','approval':'approval_id'}
FAMILIES = {'event':'events','action':'actions','metric':'metrics','error':'errors','approval':'approvals'}
TIMES = {'timestamp','started_at','ended_at','requested_at','decided_at','source_observed_at'}


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,
                          separators=(',',':'),allow_nan=False).encode('utf-8')).hexdigest()


def _require(ok: bool, code: str) -> None:
    if not ok:
        raise ValueError(code)


def _identity(value: Any) -> str:
    _require(isinstance(value,str) and 0 < len(value) <= 255 and value.strip()==value
             and all(ord(c)>=33 for c in value),'INVALID_TRACE_IDENTITY')
    return value


def _normalize(actual: Any, expected: Any, field: str) -> Any:
    if field in TIMES and isinstance(expected,str):
        def instant(v):
            _require(isinstance(v,str),'TIMESTAMP_TYPE_MISMATCH')
            d=datetime.fromisoformat(v.replace('Z','+00:00'))
            _require(d.tzinfo is not None,'TIMESTAMP_ZONE_MISSING')
            return d.astimezone(timezone.utc)
        _require(instant(actual)==instant(expected),'TIMESTAMP_CONTENT_MISMATCH')
    elif field=='provider_usage_raw_json' and expected is not None:
        a=json.loads(actual) if isinstance(actual,str) else actual
        e=json.loads(expected) if isinstance(expected,str) else expected
        _require(_digest(a)==_digest(e),'JSON_CONTENT_MISMATCH')
    elif type(expected) in (int,float):
        _require(type(actual) in (int,float,str,Decimal),'NUMERIC_TYPE_MISMATCH')
        a,e=Decimal(str(actual)),Decimal(str(expected))
        _require(a.is_finite() and e.is_finite() and a==e,'NUMERIC_CONTENT_MISMATCH')
    else:
        _require(type(actual) is type(expected) and actual==expected,'SEMANTIC_CONTENT_MISMATCH')
    # Return the canonical semantic representation ONLY after equality is proven
    # against independently retrieved values; never fill a missing field.
    return deepcopy(expected)


def primary_trace_ref(project_ref: str, run_id: str) -> str:
    return 'urn:inc:trace:'+quote(_identity(project_ref),safe='')+':'+quote(_identity(run_id),safe='')


def resolve_trace_ref(reference: str) -> dict[str,str]:
    """Resolve this adapter's stable trace URI into the existing read operation."""
    _require(isinstance(reference,str) and reference.startswith('urn:inc:trace:'),'TRACE_REFERENCE_INVALID')
    parts=reference[len('urn:inc:trace:'):].split(':')
    _require(len(parts) in (2,4),'TRACE_REFERENCE_INVALID')
    if len(parts)==4:
        _require(parts[2]=='observation' and len(parts[3])==64 and
                 all(c in '0123456789abcdef' for c in parts[3]),'TRACE_REFERENCE_INVALID')
    return {'operation':'read','project_ref':_identity(unquote(parts[0])),
            'run_id':_identity(unquote(parts[1]))}


class HatchableG11Adapter:
    def __init__(self, authenticated_transport: Callable, *, project_ref: str):
        _require(callable(authenticated_transport),'AUTHENTICATED_TRANSPORT_REQUIRED')
        self._transport=authenticated_transport
        self.project_ref=_identity(project_ref)
        _require(len(self.project_ref)<=128,'PROJECT_CONTEXT_TOO_LONG')
        self._fields=None

    def _call(self, body: dict[str,Any]) -> Mapping[str,Any]:
        # Exactly one call. Unknown outcomes are returned to the host for
        # reconciliation; this adapter never blindly retries a write.
        raw=self._transport(ENDPOINT,deepcopy(body))
        _require(isinstance(raw,Mapping),'PROVIDER_RESPONSE_INVALID')
        if isinstance(raw.get('text'),str):
            raw=json.loads(raw['text'])
        _require(type(raw.get('status')) is int and raw['status']==200,'PROVIDER_CALL_NOT_ACCEPTED')
        result=raw.get('body')
        _require(isinstance(result,Mapping) and result.get('ok') is True,'PROVIDER_RESULT_NOT_ACCEPTED')
        return result

    def _expected(self,envelope: Mapping[str,Any]) -> list[dict[str,Any]]:
        _require(envelope.get('contract')=='INC_G11_LOG_ENVELOPE_V1' and
                 envelope.get('envelope_version')=='1.1','ENVELOPE_CONTRACT_MISMATCH')
        _require(envelope.get('refs',{}).get('project_ref')==self.project_ref,'PROJECT_SCOPE_MISMATCH')
        _identity(envelope.get('envelope_id'))
        rows=[{'kind':'run',**deepcopy(envelope['run'])},*deepcopy(envelope['semantic_records'])]
        _require(2<=len(rows)<=200 and any(r.get('kind')=='event' for r in rows),'SEMANTIC_SET_INVALID')
        seen=set()
        for row in rows:
            kind=row.get('kind');_require(kind in IDS,'SEMANTIC_KIND_INVALID')
            ident=_identity(row.get(IDS[kind]));key=(kind,ident)
            _require(key not in seen,'DUPLICATE_SEMANTIC_ID');seen.add(key)
            _require(row.get('project_ref',self.project_ref)==self.project_ref,'PROJECT_SCOPE_MISMATCH')
            _require(row.get('run_id')==envelope['run']['run_id'],'RUN_SCOPE_MISMATCH')
            _require(type(row.get('is_test')) is bool and row['is_test'] is envelope['run']['is_test'],'TEST_FLAG_MISMATCH')
            row['project_ref']=self.project_ref
        return rows

    def write(self,envelope: Mapping[str,Any],*,idempotency_key: str) -> Mapping[str,Any]:
        _require(idempotency_key==envelope.get('envelope_id'),'IDEMPOTENCY_KEY_MISMATCH')
        rows=self._expected(envelope)
        if self._fields is None:
            cap=self._call({'operation':'capabilities'})
            _require(cap.get('contract')==CAPABILITIES and cap.get('route')==ROUTE
                     and cap.get('idempotency')=='IMMUTABLE_EXACT_REPLAY','PROVIDER_CAPABILITY_MISMATCH')
            self._fields=cap.get('field_sets')
        _require(isinstance(self._fields,Mapping),'PROVIDER_FIELDS_UNVERIFIED')
        for row in rows:
            fields=self._fields.get(row['kind'])
            _require(isinstance(fields,list) and all(isinstance(k,str) for k in fields),'PROVIDER_FIELDS_UNVERIFIED')
            _require(set(row)<=set(fields)|{'kind','project_ref'},'UNPERSISTABLE_SEMANTIC_FIELD')
        ack=self._call({'envelope':dict(envelope)})
        _require(ack.get('route')==ROUTE and ack.get('run_id')==envelope['run']['run_id']
                 and ack.get('project_ref')==self.project_ref,'WRITE_IDENTITY_MISMATCH')
        # The provider's verified receipt is not our independent readback.
        return {'accepted':True,'envelope_id':envelope['envelope_id'],'durable_readback_verified':False}

    def readback(self,envelope: Mapping[str,Any]) -> Mapping[str,Any]:
        expected=self._expected(envelope)
        body=self._call({'operation':'read','run_id':envelope['run']['run_id'],'project_ref':self.project_ref})
        _require(body.get('route')==ROUTE and body.get('project_ref')==self.project_ref,'READ_SCOPE_MISMATCH')
        data=body.get('data');_require(isinstance(data,Mapping),'EXACT_ROWS_REQUIRED')
        records=[{'kind':'run',**dict(data['run'])}]
        for kind,family in FAMILIES.items():
            rows=data.get(family)
            _require(isinstance(rows,list),'EXACT_FAMILIES_REQUIRED')
            records.extend({'kind':kind,**dict(r)} for r in rows)
        index={}
        for row in records:
            k=(row['kind'],row.get(IDS[row['kind']]))
            _identity(k[1])
            _require(row.get('project_ref')==self.project_ref and row.get('run_id')==envelope['run']['run_id'],'READBACK_SCOPE_MISMATCH')
            _require(k not in index,'DUPLICATE_READBACK_ID');index[k]=row
        # A run may contain earlier envelopes. Verify this envelope's exact
        # subset while still rejecting duplicates or any cross-scope rows.
        _require({(r['kind'],r[IDS[r['kind']]]) for r in expected}<=set(index),'READBACK_RECORD_SET_MISMATCH')
        projected=[]
        for row in expected:
            actual=index[(row['kind'],row[IDS[row['kind']]])]
            _require(set(row)<=set(actual),'READBACK_FIELD_MISSING')
            projected.append({k:_normalize(actual[k],v,k) for k,v in row.items()})
        trace=primary_trace_ref(self.project_ref,envelope['run']['run_id'])
        return {'route':ROUTE,'envelope_id':envelope['envelope_id'],'project_ref':self.project_ref,
                'durable_readback_verified':True,'records':projected,'primary_trace_ref':trace,
                'observation_ref':trace+':observation:'+_digest(projected),
                'reference_resolution':resolve_trace_ref(trace),
                'observation_semantics':'CONTENT_HASH_OF_SEPARATE_PROVIDER_READ_NOT_A_FABRICATED_PROVIDER_RECEIPT'}
