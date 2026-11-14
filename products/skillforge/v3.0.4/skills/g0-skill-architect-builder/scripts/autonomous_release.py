#!/usr/bin/env python3
"""Owner-authorized release acceptance; no external-executor waiting.

The host authenticates owner instructions and collects real observations. This
module checks consistency; it is not an authenticator, publisher, or installer.
Release acceptance does not grant production mutation rights or an independent
certificate. Historical strict release profiles remain available separately.
"""
from __future__ import annotations
import hashlib
import json
import re
from collections.abc import Mapping
from datetime import date, datetime
from typing import Any
from urllib.parse import urlsplit

CONTRACT = 'INC_AUTONOMOUS_RELEASE_ACCEPTANCE_V1'
PROFILE = 'AUTONOMOUS_EVIDENCE_BASED'
STAGES = {'prepare_g12', 'prepare_g13', 'publish', 'deploy', 'close'}
CONTROLS = frozenset({'authorization', 'security', 'integrity', 'dependencies',
                      'rollback', 'quality_review', 'scope_coverage'})
EVIDENCE_KINDS = {'EXECUTED_LOCAL', 'EXECUTED_API', 'EXECUTED_PLUGIN', 'EXECUTED_SIMULATION'}
OPTIONAL_KINDS = {'THIRD_PARTY_REVIEW', 'EXTERNAL_RUNNER', 'NATIVE_INSTALL',
                  'LIVE_PROVIDER_END_TO_END', 'USER_ASSISTED_TEST', 'GITHUB_MAIN_MERGE',
                  'GITHUB_RELEASE_OBJECT', 'VISUAL_HOST_CHECK'}
PROTECTED_IDS = frozenset('SF-G8-001 SF-G8-002 SF-G8-003 SF-G17-005 SF-G17-008 SF-G17-010 SF-G17-013 SF-G17-015 SF-G17-019 SF-G17-022 SF-G17-023 SF-G17-024 SF-G17-025 SF-G11-002 SF-G11-003 SF-XCUT-032 SF-G12-001 SF-G13-001 SF-G14-001 SF-G7-003 SF-G1-004 SF-G16-006 SF-G16-008'.split())
HEX64 = re.compile(r'[0-9a-f]{64}')


def canonical_digest(value: Any) -> str:
    def default(v: Any) -> str:
        if isinstance(v, (datetime, date)):
            return v.isoformat()
        raise TypeError('UNSUPPORTED_DIGEST_VALUE')
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
        separators=(',', ':'), allow_nan=False, default=default).encode()).hexdigest()


def _map(value: Any) -> Mapping:
    return value if isinstance(value, Mapping) else {}


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _hash(value: Any) -> bool:
    return isinstance(value, str) and HEX64.fullmatch(value) is not None


def _zero(value: Any) -> bool:
    return type(value) is int and value == 0


def _https(value: Any) -> bool:
    if not isinstance(value, str) or any(ord(c) < 33 for c in value):
        return False
    try:
        p = urlsplit(value)
        return p.scheme == 'https' and bool(p.hostname) and not (
            p.username or p.password or p.query or p.fragment)
    except ValueError:
        return False


def _evaluate(stage: str, backlog: Mapping[str, Any], backlog_bytes: bytes,
              manifest: Mapping[str, Any], trusted: Mapping[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    def need(ok: bool, code: str) -> None:
        if not ok:
            errors.append(code)
    manifest, trusted, backlog = _map(manifest), _map(trusted), _map(backlog)
    need(stage in STAGES, 'UNKNOWN_STAGE')
    need(manifest.get('release_policy') == PROFILE, 'RELEASE_PROFILE_REQUIRED')
    owner = _map(trusted.get('owner_release_authorization'))
    mission = manifest.get('mission_id')
    need(_text(mission) and mission == trusted.get('mission_id'), 'MISSION_MISMATCH')
    need(owner.get('verified') is True and owner.get('decision') == 'APPROVE'
         and owner.get('profile') == PROFILE and owner.get('mission_id') == mission
         and owner.get('source_kind') in {'OWNER_MESSAGE', 'OWNER_SIGNED_APPROVAL'}
         and _text(owner.get('source_ref')), 'OWNER_RELEASE_AUTHORIZATION_REQUIRED')
    candidate = _map(manifest.get('candidate'))
    observed = _map(trusted.get('observed_candidate'))
    fields = ('package_sha256', 'source_tree_sha256', 'bom_sha256')
    for key in fields:
        need(_hash(candidate.get(key)) and candidate.get(key) == observed.get(key),
             'EXACT_ARTIFACT_IDENTITY_REQUIRED:' + key)
    version = candidate.get('version')
    need(isinstance(version, str) and re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', version) is not None,
         'FINAL_SEMVER_REQUIRED')
    need(owner.get('release_version') == version, 'OWNER_VERSION_SCOPE_MISMATCH')
    need(candidate.get('visibility') in {'PRIVATE', 'INTERNAL'}, 'PRIVATE_RELEASE_SCOPE_REQUIRED')
    dest = _map(trusted.get('destination_observation'))
    need(dest.get('verified') is True and dest.get('visibility') == 'PRIVATE' and
         _text(dest.get('repository_id')) and _text(dest.get('observed_at')),
         'ACTUAL_PRIVATE_DESTINATION_REQUIRED')
    need(candidate.get('lifecycle') == 'RELEASE', 'RELEASE_LIFECYCLE_REQUIRED')
    need(trusted.get('freeze_verified') is True, 'FROZEN_ARTIFACT_REQUIRED')
    need(_text(trusted.get('observation_ref')), 'OBSERVATION_REFERENCE_REQUIRED')
    identity = {key: candidate.get(key) for key in fields}
    identity.update(version=version, visibility=candidate.get('visibility'), release_policy=PROFILE)
    decision_digest = canonical_digest(identity)
    need(backlog.get('canonical') is True and backlog.get('backlog_id') == 'INC_SKILLFORGE_UNIFIED_BACKLOG',
         'CANONICAL_BACKLOG_REQUIRED')
    need(isinstance(backlog_bytes, bytes), 'BACKLOG_BYTES_REQUIRED')
    actual_backlog_hash = hashlib.sha256(backlog_bytes).hexdigest() if isinstance(backlog_bytes, bytes) else None
    need(_hash(candidate.get('backlog_sha256')) and candidate.get('backlog_sha256') == actual_backlog_hash and
         candidate.get('backlog_sha256') == observed.get('backlog_sha256'), 'BACKLOG_IDENTITY_MISMATCH')
    items = backlog.get('items')
    need(isinstance(items, list) and bool(items), 'BACKLOG_RECORDS_REQUIRED')
    records = {}
    if isinstance(items, list):
        for item in items:
            item = _map(item); key = item.get('change_id')
            need(_text(key) and key not in records, 'BACKLOG_ID_INVALID_OR_DUPLICATE')
            if _text(key):
                records[key] = item
    scope = _map(backlog.get('operational_release_scope_v3'))
    decisions = _map(scope.get('item_dispositions'))
    need(scope.get('authority') == 'OWNER_MANDATE' and scope.get('status') == 'OWNER_DISPOSITIONS_FINALIZED'
         and set(decisions) == set(records), 'OWNER_SCOPE_COVERAGE_REQUIRED')
    counts = {k: 0 for k in ('RETAIN_REQUIRED', 'RELAX_CONDITIONAL', 'CANCEL_RELEASE_OBLIGATION')}
    required = set()
    for cid, d in decisions.items():
        d = _map(d); action = d.get('disposition')
        need(action in counts and _text(d.get('rationale')), 'SCOPE_DISPOSITION_INVALID:' + cid)
        if action in counts:
            counts[action] += 1
        need(not (action == 'CANCEL_RELEASE_OBLIGATION' and cid in PROTECTED_IDS),
             'PROTECTED_REQUIREMENT_CANCELLATION:' + cid)
        if action == 'RETAIN_REQUIRED':
            required.add(cid)
    need(counts == scope.get('decision_counts'), 'SCOPE_COUNT_MISMATCH')
    ledger = manifest.get('requirement_assessments'); assessed = set()
    need(isinstance(ledger, list), 'REQUIREMENT_ASSESSMENTS_REQUIRED')
    if isinstance(ledger, list):
        for row in ledger:
            row = _map(row); cid = row.get('change_id')
            need(_text(cid) and cid not in assessed, 'REQUIREMENT_ASSESSMENT_ID_INVALID')
            if _text(cid):
                assessed.add(cid)
            need(cid in records and row.get('record_sha256') == canonical_digest(records.get(cid)),
                 'STALE_REQUIREMENT_ASSESSMENT:' + str(cid))
            need(row.get('status') in {'PASS_EXECUTED', 'PASS_SIMULATED', 'PASS_CONTRACT_REVIEW'}
                 and _text(row.get('evidence_ref')) and row.get('package_sha256') == candidate.get('package_sha256'),
                 'REQUIREMENT_ASSESSMENT_NOT_PASS:' + str(cid))
    need(assessed == required, 'RETAINED_REQUIREMENT_COVERAGE_MISMATCH')
    controls = _map(trusted.get('controls'))
    need(CONTROLS <= set(controls), 'MANDATORY_CONTROLS_MISSING')
    for name in sorted(CONTROLS):
        r = _map(controls.get(name))
        need(r.get('verified') is True and r.get('result') == 'PASS' and _text(r.get('evidence_ref'))
             and r.get('package_sha256') == candidate.get('package_sha256'), 'CONTROL_NOT_PASS:' + name)
    need(_zero(trusted.get('unresolved_critical_findings')), 'UNRESOLVED_CRITICAL_FINDINGS')
    need(_hash(trusted.get('rollback_package_sha256')) and _text(trusted.get('rollback_ref')),
         'ROLLBACK_SOURCE_REQUIRED')
    required_tests = manifest.get('required_test_ids')
    need(isinstance(required_tests, list) and bool(required_tests) and all(_text(x) for x in required_tests)
         and len(required_tests) == len(set(required_tests)), 'REQUIRED_TEST_PLAN_INVALID')
    runs = trusted.get('test_runs'); seen = set(); count = 0
    need(isinstance(runs, list) and bool(runs), 'EXECUTED_TEST_EVIDENCE_REQUIRED')
    if isinstance(runs, list):
        for r in runs:
            r = _map(r); rid = r.get('id')
            need(_text(rid) and rid not in seen, 'DUPLICATE_OR_INVALID_TEST_RUN')
            if _text(rid):
                seen.add(rid)
            n = r.get('tests_executed')
            need(r.get('kind') in EVIDENCE_KINDS and r.get('executed') is True and
                 r.get('result') == 'PASS' and type(n) is int and n > 0 and
                 _zero(r.get('failures')) and _zero(r.get('errors')) and
                 _hash(r.get('log_sha256')) and _text(r.get('evidence_ref')) and
                 r.get('package_sha256') == candidate.get('package_sha256') and
                 r.get('source_tree_sha256') == candidate.get('source_tree_sha256'),
                 'TEST_EVIDENCE_NOT_PASS:' + str(rid))
            if type(n) is int and n > 0:
                count += n
    if isinstance(required_tests, list) and all(_text(x) for x in required_tests):
        need(seen == set(required_tests), 'TEST_PLAN_COVERAGE_MISMATCH')
    optional = manifest.get('optional_assurance', [])
    need(isinstance(optional, list), 'OPTIONAL_ASSURANCE_INVALID')
    if isinstance(optional, list):
        for r in optional:
            r = _map(r)
            need(r.get('kind') in OPTIONAL_KINDS and r.get('status') in {'NOT_RUN_OPTIONAL', 'SIMULATED_NOT_LIVE', 'VERIFIED'}
                 and r.get('blocking') is False and _text(r.get('reason')), 'OPTIONAL_ASSURANCE_ROW_INVALID')
            if r.get('status') == 'VERIFIED':
                receipt = _map(_map(trusted.get('optional_assurance_observations')).get(r.get('kind')))
                need(receipt.get('verified') is True and receipt.get('result') == 'PASS'
                     and receipt.get('package_sha256') == candidate.get('package_sha256')
                     and _text(receipt.get('evidence_ref')), 'OPTIONAL_VERIFIED_CLAIM_UNSUPPORTED')
    need(manifest.get('independent_certification_claimed') is False, 'FALSE_INDEPENDENCE_CLAIM')
    need(manifest.get('zero_bug_guarantee') is False, 'ZERO_BUG_GUARANTEE_UNSUPPORTED')
    if stage in {'deploy', 'close'}:
        pub = _map(trusted.get('publication'))
        need(pub.get('verified') is True and pub.get('readback_verified') is True and
             pub.get('result') == 'PASS' and pub.get('kind') == 'ACTUAL_REMOTE_READBACK' and
             pub.get('package_sha256') == candidate.get('package_sha256') and
             type(pub.get('size_bytes')) is int and pub.get('size_bytes') > 0 and
             pub.get('size_bytes') == observed.get('size_bytes') and
             _https(pub.get('url')) and _text(pub.get('observation_ref')), 'ACTUAL_PUBLICATION_READBACK_REQUIRED')
    if stage == 'close':
        need(trusted.get('handoff_readback_verified') is True and _text(trusted.get('handoff_ref')),
             'HANDOFF_READBACK_REQUIRED')
    return {'contract': CONTRACT, 'release_policy': PROFILE, 'stage': stage, 'allowed': not errors,
            'result': ('RELEASED' if stage == 'close' else 'RELEASE_APPROVED') if not errors else 'BLOCKED',
            'release_version': version, 'candidate_digest': decision_digest, 'errors': sorted(set(errors)),
            'tests_executed': count, 'retained_requirements_assessed': len(assessed),
            'independent_certification': False, 'native_installation_claimed': False,
            'optional_assurance_count': len(optional) if isinstance(optional, list) else 0,
            'authorizes_production_mutation': False,
            'trust_boundary': 'HOST_VERIFIES_INPUT_AUTHENTICITY; gate checks evidence consistency'}


def evaluate(stage: str, backlog: Mapping[str, Any], backlog_bytes: bytes,
             manifest: Mapping[str, Any], trusted: Mapping[str, Any]) -> dict[str, Any]:
    """Malformed caller input is a denial, never an optimistic PASS."""
    try:
        return _evaluate(stage, backlog, backlog_bytes, manifest, trusted)
    except (TypeError, ValueError, KeyError, AttributeError, OverflowError):
        return {'contract': CONTRACT, 'release_policy': PROFILE,
                'stage': stage if isinstance(stage, str) else None,
                'allowed': False, 'result': 'BLOCKED', 'errors': ['INVALID_INPUT_SHAPE'],
                'independent_certification': False, 'native_installation_claimed': False,
                'authorizes_production_mutation': False}
