"""G9 deterministic reserve planner; no charge or actual-cost claim.

Documented owner-delegated PRIOR_RELEASE substitute, not recovered historical source.
One provider/account/currency/horizon; exact arithmetic within explicit bounds.
"""
from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, Context, Inexact, Rounded, localcontext
import re
from typing import Any, Mapping

CONTRACT = 'INC_G9_USEFUL_SURPLUS_RESERVE_V1'
MAX_COEFFICIENT_DIGITS = 128
MAX_EXPONENT_MAGNITUDE = 128
MAX_INPUT_CHARACTERS = 256
ARITHMETIC_PRECISION = MAX_COEFFICIENT_DIGITS + 2 * MAX_EXPONENT_MAGNITUDE + 4


def _instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('TIMEZONE_REQUIRED')
    return parsed.astimezone(timezone.utc)


def _money(value: Any) -> Decimal:
    if not isinstance(value, (str, int, Decimal)) or isinstance(value, bool):
        raise ValueError('EXACT_DECIMAL_REQUIRED')
    if isinstance(value, (str, int)) and len(str(value)) > MAX_INPUT_CHARACTERS:
        raise ValueError('DECIMAL_PRECISION_LIMIT')
    try:
        result = Decimal(value)
    except (InvalidOperation, ValueError):
        raise ValueError('INVALID_DECIMAL') from None
    if not result.is_finite() or result <= 0:
        raise ValueError('POSITIVE_FINITE_SOURCE_REQUIRED')
    parts = result.as_tuple()
    if (len(parts.digits) > MAX_COEFFICIENT_DIGITS
            or abs(parts.exponent) > MAX_EXPONENT_MAGNITUDE
            or abs(result.adjusted()) > MAX_EXPONENT_MAGNITUDE):
        raise ValueError('DECIMAL_PRECISION_LIMIT')
    return result


def plan_reserve(available: Mapping[str, Any], bill: Mapping[str, Any], *,
                 observed_at: str, max_age_seconds: int = 604800) -> dict[str, Any]:
    result: dict[str, Any] = {'contract': CONTRACT, 'status': 'SKIPPED',
                             'telemetry_status': 'UNAVAILABLE', 'provider_write': False}
    try:
        if type(max_age_seconds) is not int or max_age_seconds <= 0:
            raise ValueError('INVALID_FRESHNESS_POLICY')
        now = _instant(observed_at)
        for source in (available, bill):
            if not isinstance(source, Mapping):
                raise ValueError('SOURCE_REQUIRED')
            for key in ('provider_ref', 'account_ref', 'currency', 'source_ref',
                        'horizon_start', 'horizon_end', 'captured_at', 'value_kind'):
                if not isinstance(source.get(key), str) or not source[key].strip():
                    raise ValueError('SOURCE_METADATA_REQUIRED:' + key)
            if not re.fullmatch('[A-Z]{3}', source['currency']):
                raise ValueError('CURRENCY_INVALID')
            if source['value_kind'] not in ('MEASURED', 'VALIDATED_ESTIMATE'):
                raise ValueError('SOURCE_PROVENANCE_UNVERIFIED')
            age = (now - _instant(source['captured_at'])).total_seconds()
            if not 0 <= age <= max_age_seconds:
                raise ValueError('SOURCE_STALE_OR_FUTURE')
            start, end = _instant(source['horizon_start']), _instant(source['horizon_end'])
            if not start <= now < end:
                raise ValueError('HORIZON_INVALID_OR_EXPIRED')
        for key in ('provider_ref', 'account_ref', 'currency'):
            if available[key] != bill[key]:
                raise ValueError('SOURCE_SCOPE_MISMATCH:' + key)
        for key in ('horizon_start', 'horizon_end'):
            if _instant(available[key]) != _instant(bill[key]):
                raise ValueError('HORIZON_MISMATCH')
        funds, expected = _money(available.get('amount')), _money(bill.get('amount'))
        context = Context(prec=ARITHMETIC_PRECISION)
        context.traps[Inexact] = True
        context.traps[Rounded] = True
        # Never inherit a caller's low-precision Decimal context.
        with localcontext(context):
            reserve = min(funds, expected)
            surplus = max(Decimal(0), funds - expected)
            shortfall = max(Decimal(0), expected - funds)
        result.update(status='PLANNED', telemetry_status='DERIVED_PLAN_NOT_ACTUAL_COST',
                      provider_ref=available['provider_ref'], account_ref=available['account_ref'],
                      currency=available['currency'], reserve_amount=str(reserve),
                      useful_surplus=str(surplus), shortfall=str(shortfall),
                      horizon_start=available['horizon_start'], horizon_end=available['horizon_end'],
                      source_refs=[available['source_ref'], bill['source_ref']],
                      input_value_kinds=[available['value_kind'], bill['value_kind']])
    except (ValueError, TypeError, AttributeError, InvalidOperation, Inexact, Rounded) as error:
        code = str(error)
        result['reason_code'] = code if re.fullmatch('[A-Z0-9_:a-z]+', code) else 'INVALID_INPUT'
    return result
