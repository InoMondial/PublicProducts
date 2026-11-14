"""Bounded material-activity coverage, never inferred from a missing denominator."""
from __future__ import annotations
from typing import Iterable, Mapping, Any

def audit(expected_activity_ids: Iterable[str] | None,
          receipts: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    if expected_activity_ids is None:
        return {'status': 'NOT_MEASURABLE', 'coverage_percent': None}
    expected = list(expected_activity_ids)
    if any(not isinstance(x, str) or not x for x in expected) or len(expected) != len(set(expected)):
        raise ValueError('AUTHORITATIVE_ACTIVITY_SET_INVALID')
    seen: dict[str, Mapping[str, Any]] = {}
    for receipt in receipts:
        key = receipt.get('activity_id')
        if not isinstance(key, str) or not key:
            raise ValueError('RECEIPT_ACTIVITY_REQUIRED')
        if key in seen and seen[key] != receipt:
            raise ValueError('CONFLICTING_RECEIPTS_REQUIRE_RECONCILIATION')
        seen[key] = receipt
    missing, pending, verified = [], [], []
    for key in expected:
        receipt = seen.get(key)
        if not receipt:
            missing.append(key)
        elif receipt.get('status') == 'G11_PERSISTED_VERIFIED' and receipt.get('primary_trace_ref') and receipt.get('observation_ref'):
            verified.append(key)
        else:
            pending.append(key)
    return {'status': 'NO_APPLICABLE_ACTIVITIES' if not expected else 'PASS' if not missing and not pending else 'GAP',
            'expected_count': len(expected), 'verified_count': len(verified),
            'missing_activity_ids': missing, 'pending_activity_ids': pending,
            'coverage_percent': 100 * len(verified) / len(expected) if expected else None,
            'trust_boundary': 'CALLER_SUPPLIES_AUTHENTIC_GATEWAY_RECEIPTS_NOT_A_NEW_PERSISTENCE_CERTIFICATE'}
