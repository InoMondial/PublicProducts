"""G11 compile/write/readback gateway. Adapter must supply real authenticated I/O.

No SQL/schema/provider credentials are accepted from ordinary callers. A local
fixture can prove consistency, never live persistence or external authenticity.
"""
from __future__ import annotations
from copy import deepcopy
import hashlib
import json
from typing import Any, Mapping, Protocol
from urllib.parse import urlsplit
from compile_caller_request import (compile_request, _check_forbidden, _validate_run,
    _validate_record, _check_duplicate_business_ids)

CONTRACT = 'INC_G11_RUNTIME_GATEWAY_V1'
ROUTE = 'INC_G11_G17_DB_WRITE_ROUTE_V1'
ID_FIELDS = {'run': 'run_id', 'event': 'event_id', 'action': 'action_id',
             'metric': 'metric_id', 'error': 'error_id', 'approval': 'approval_id'}

def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                        separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()

class Adapter(Protocol):
    def write(self, envelope: Mapping[str, Any], *, idempotency_key: str) -> Mapping[str, Any]: ...
    def readback(self, envelope: Mapping[str, Any]) -> Mapping[str, Any]: ...

def _trace_ref(value: Any) -> bool:
    if not isinstance(value, str) or not value or any(ord(c) < 33 for c in value):
        return False
    parts = urlsplit(value)
    if parts.scheme == 'https':
        return bool(parts.hostname) and not (parts.username or parts.password or parts.query or parts.fragment)
    return parts.scheme == 'urn' and value.startswith('urn:inc:trace:') and len(value) > 14

def expected_records(envelope: Mapping[str, Any]) -> list[dict[str, Any]]:
    project = envelope.get('refs', {}).get('project_ref')
    if not isinstance(project, str) or not project.strip():
        raise ValueError('PROJECT_REF_REQUIRED')
    rows = [{'kind': 'run', **deepcopy(envelope['run'])}, *deepcopy(envelope['semantic_records'])]
    if not any(row.get('kind') == 'event' for row in rows):
        raise ValueError('EVENT_REQUIRED')
    for row in rows:
        row['project_ref'] = project
    return rows

def verify_readback(envelope: Mapping[str, Any], observation: Mapping[str, Any]) -> dict[str, Any]:
    receipt = {'contract': CONTRACT, 'route': ROUTE, 'status': 'TRACE_PERSISTENCE_DEGRADED',
               'envelope_id': envelope.get('envelope_id'), 'run_id': envelope.get('run', {}).get('run_id'),
               'project_ref': envelope.get('refs', {}).get('project_ref')}
    try:
        expected = expected_records(envelope)
        if not isinstance(observation, Mapping) or observation.get('route') != ROUTE:
            raise ValueError('CANONICAL_ROUTE_REQUIRED')
        if observation.get('durable_readback_verified') is not True:
            raise ValueError('INDEPENDENT_DURABLE_READBACK_REQUIRED')
        if observation.get('envelope_id') != envelope['envelope_id']:
            raise ValueError('ENVELOPE_MISMATCH')
        if observation.get('project_ref') != receipt['project_ref']:
            raise ValueError('PROJECT_SCOPE_MISMATCH')
        if not _trace_ref(observation.get('primary_trace_ref')) or not _trace_ref(observation.get('observation_ref')):
            raise ValueError('INSPECTABLE_STABLE_TRACE_REQUIRED')
        observed = observation.get('records')
        if not isinstance(observed, list):
            raise ValueError('EXACT_ROWS_REQUIRED_NOT_AGGREGATE_COUNTS')
        index = {}
        for row in observed:
            kind = row.get('kind') if isinstance(row, Mapping) else None
            key_field = ID_FIELDS.get(kind)
            if not key_field or not isinstance(row.get(key_field), str):
                raise ValueError('SEMANTIC_ID_REQUIRED')
            key = (kind, row[key_field])
            if key in index:
                raise ValueError('DUPLICATE_READBACK_ID')
            index[key] = row
        expected_keys = {(r['kind'], r[ID_FIELDS[r['kind']]]) for r in expected}
        if set(index) != expected_keys:
            raise ValueError('EXPECTED_RECORD_SET_MISMATCH')
        for row in expected:
            actual = index[(row['kind'], row[ID_FIELDS[row['kind']]])]
            if digest({k: actual.get(k) for k in row}) != digest(row):
                raise ValueError('SEMANTIC_CONTENT_MISMATCH')
        receipt.update(status='G11_PERSISTED_VERIFIED', primary_trace_ref=observation['primary_trace_ref'],
                       observation_ref=observation['observation_ref'],
                       envelope_digest=digest(envelope), verified_record_count=len(expected),
                       verification_scope='EXACT_SEMANTIC_IDS_PROJECT_AND_REQUIRED_CONTENT')
    except (ValueError, KeyError, TypeError, AttributeError):
        receipt['reason_code'] = 'DURABLE_READBACK_MISMATCH'
    return receipt

def execute(request: Mapping[str, Any], adapter: Adapter | None = None, *, verify: bool = True) -> dict[str, Any]:
    try:
        envelope = compile_request(deepcopy(dict(request)))
        expected_records(envelope)
    except (ValueError, KeyError, TypeError, AttributeError):
        return {'contract': CONTRACT, 'status': 'VALIDATION_FAILED', 'reason_code': 'INVALID_CALLER'}
    return execute_envelope(envelope, adapter, verify=verify, activity_id=request['activity_id'])


def execute_envelope(envelope: Mapping[str, Any], adapter: Adapter | None, *,
                     verify: bool = True, activity_id: str | None = None) -> dict[str, Any]:
    """Retry the SAME persisted compiled envelope; do not re-create its timestamps."""
    try:
        envelope = deepcopy(dict(envelope))
        _check_forbidden(envelope)
        _validate_run(envelope['run'])
        for row in envelope['semantic_records']:
            kind = row.get('kind')
            if kind not in ID_FIELDS or kind == 'run':
                raise ValueError('SEMANTIC_KIND_INVALID')
            _validate_record(kind, row)
            if row['run_id'] != envelope['run']['run_id'] or row['is_test'] is not envelope['run']['is_test']:
                raise ValueError('SEMANTIC_SCOPE_MISMATCH')
        _check_duplicate_business_ids(envelope['semantic_records'])
        expected_records(envelope)
        if envelope.get('contract') != 'INC_G11_LOG_ENVELOPE_V1':
            raise ValueError('ENVELOPE_CONTRACT_REQUIRED')
        if not isinstance(envelope.get('envelope_id'), str):
            raise ValueError('ENVELOPE_ID_REQUIRED')
    except (ValueError, KeyError, TypeError, AttributeError):
        return {'contract': CONTRACT, 'status': 'VALIDATION_FAILED', 'reason_code': 'INVALID_ENVELOPE'}
    receipt = {'contract': CONTRACT, 'route': ROUTE, 'activity_id': activity_id or envelope['envelope_id'],
               'envelope_id': envelope['envelope_id'], 'run_id': envelope['run']['run_id'],
               'status': 'G11_GATEWAY_VALIDATED'}
    if adapter is None:
        return receipt
    try:
        ack = adapter.write(envelope, idempotency_key=envelope['envelope_id'])
        if ack.get('accepted') is not True or ack.get('envelope_id') != envelope['envelope_id']:
            return {**receipt, 'status': 'TRACE_PERSISTENCE_DEGRADED', 'reason_code': 'WRITE_NOT_ACCEPTED'}
        if not verify:
            return {**receipt, 'status': 'G11_ACCEPTED_FOR_PERSISTENCE'}
        return {**receipt, **verify_readback(envelope, adapter.readback(envelope))}
    except Exception:
        return {**receipt, 'status': 'TRACE_PERSISTENCE_PENDING', 'reason_code': 'ADAPTER_OUTCOME_UNKNOWN'}


def execute_hatchable(request: Mapping[str, Any], *, authenticated_transport,
                      project_ref: str, verify: bool = True) -> dict[str, Any]:
    """Bind the actual G17 adapter, supplied only by a trusted authenticated host.

    The host supplies a callable accepting (route, body), returning HTTP status
    and body from its existing admin client/connector. No keys enter caller data.
    """
    from importlib.util import module_from_spec, spec_from_file_location
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    adapter_path = root / 'g17-data-governor/adapters/hatchable/g11_gateway_adapter.py'
    if not adapter_path.is_file():
        return {'contract': CONTRACT, 'status': 'TRACE_PERSISTENCE_DEGRADED',
                'reason_code': 'G17_ADAPTER_NOT_INSTALLED'}
    spec = spec_from_file_location('_g17_hatchable_g11', adapter_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    adapter = module.HatchableG11Adapter(authenticated_transport, project_ref=project_ref)
    return execute(request, adapter=adapter, verify=verify)
