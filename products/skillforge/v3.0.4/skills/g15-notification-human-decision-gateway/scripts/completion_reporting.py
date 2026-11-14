"""G15 authorized long-report completion. Composes with G15_router, not a sender.

An alternate target is usable only through separately resolved authorization.
Planning does not send or certify delivery. The host owns real transport/readback.
"""
from __future__ import annotations
import hashlib
from typing import Any, Mapping
from urllib.parse import urlsplit
from G15_router import plan as teams_plan
from G15_delivery_policy import is_explicit_transport_test

CONTRACT = 'INC_G15_MULTICHANNEL_COMPLETION_V1'

def payload_digest(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def plan_completion(request: Mapping[str, Any], *, run_id: str, full_report: str,
                    teams_capacity_bytes: int, authorized_alternate: Mapping[str, Any] | None = None,
                    **router_capabilities: Any) -> dict[str, Any]:
    if not isinstance(run_id, str) or not run_id or not isinstance(full_report, str) or not full_report.strip():
        return {'status': 'INVALID_REQUEST'}
    if type(teams_capacity_bytes) is not int or teams_capacity_bytes <= 0:
        return {'status': 'CAPACITY_UNVERIFIED'}
    base = teams_plan(dict(request), **router_capabilities)
    if base.get('status') != 'READY':
        return base
    size = len(full_report.encode('utf-8'))
    result = {'contract': CONTRACT, 'status': 'PLANNED_NOT_SENT', 'run_id': run_id,
              'priority': base['priority'], 'dispatch_id': base['dispatch_id'],
              'payload_sha256': payload_digest(full_report), 'payload_bytes': size,
              'teams_plan': base, 'transport_owner': 'G15_SINGLE_WRITER',
              'is_test': is_explicit_transport_test(request)}
    complete_request = dict(request)
    complete_request['body'] = full_report
    complete_plan = teams_plan(complete_request, **router_capabilities)
    rendered = complete_plan.get('rendered', {}).get('html', '')
    rendered_size = len(rendered.encode('utf-8'))
    if complete_plan.get('status') == 'READY' and rendered and rendered_size <= teams_capacity_bytes:
        result.update(primary_channel='TEAMS', target_ref=complete_plan['destination_ref'],
                      teams_plan=complete_plan, payload_sha256=payload_digest(rendered),
                      payload_bytes=rendered_size, payload_representation='CANONICAL_TEAMS_HTML')
        return result
    if len(base.get('rendered', {}).get('html', '').encode('utf-8')) > teams_capacity_bytes:
        return {**result, 'status': 'TEAMS_SUMMARY_TOO_LARGE'}
    alt = authorized_alternate or {}
    required = ('decision_ref', 'target_ref', 'channel', 'run_id')
    if (any(not isinstance(alt.get(k), str) or not alt[k] for k in required)
            or alt.get('verified') is not True or alt['run_id'] != run_id
            or alt.get('classification_allowed') is not True or alt.get('recipient_scope_verified') is not True
            or alt['channel'] not in ('SHAREPOINT', 'OUTLOOK', 'GMAIL', 'TEAMS')):
        return {**result, 'status': 'AUTHORIZED_ALTERNATE_REQUIRED'}
    if not result['is_test'] and alt.get('purpose') in ('TEST', 'ECHO'):
        return {**result, 'status': 'TEST_ROUTE_NOT_AUTHORIZED_FOR_PRODUCTION_EVENT'}
    result.update(primary_channel=alt['channel'], target_ref=alt['target_ref'],
                  authorization_ref=alt['decision_ref'], teams_summary_required=True)
    return result

def verify_completion(plan: Mapping[str, Any], observation: Mapping[str, Any]) -> dict[str, Any]:
    result = {'contract': CONTRACT, 'run_id': plan.get('run_id'), 'status': 'DELIVERY_UNVERIFIED'}
    ref = observation.get('primary_ref', '')
    url = urlsplit(ref) if isinstance(ref, str) else None
    checks = [plan.get('status') == 'PLANNED_NOT_SENT', observation.get('readback_verified') is True,
              observation.get('run_id') == plan.get('run_id'),
              observation.get('target_ref') == plan.get('target_ref'),
              observation.get('channel') == plan.get('primary_channel'),
              observation.get('payload_sha256') == plan.get('payload_sha256'),
              observation.get('payload_bytes') == plan.get('payload_bytes'),
              observation.get('complete') is True, bool(observation.get('observation_ref')),
              bool(url and url.scheme == 'https' and url.hostname and not url.username and not url.password and not url.query)]
    if not plan.get('is_test') and observation.get('purpose') in ('TEST', 'ECHO'):
        checks.append(False)
    if plan.get('teams_summary_required'):
        checks.append(observation.get('teams_summary_readback_verified') is True)
        checks.append(observation.get('teams_summary_primary_ref') == ref)
    if all(checks):
        result.update(status='SENT_COMPLETE', primary_ref=ref, observation_ref=observation['observation_ref'],
                      priority=plan.get('priority'), transport_owner='G15_SINGLE_WRITER')
    return result
