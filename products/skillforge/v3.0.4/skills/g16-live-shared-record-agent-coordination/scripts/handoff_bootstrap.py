#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, secrets
import handoff_transaction as tx

CONTRACT=tx.CONTRACT
PROFILE='FIRST_HANDOFF_BOOTSTRAP_V1'
HOF_RE=re.compile(r'^HOF-[0-9A-F]{16}$')

class Invalid(ValueError): pass

def require(ok, code):
    if not ok: raise Invalid(code)

def nonempty(v): return isinstance(v,str) and bool(v.strip())
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()

def resolve_start_mode(*, explicit_handoff_url=None, explicit_url_found=None, bound_handoff_refs=None, handoff_ids_in_context=None):
    # Existing project bindings, memory, registry hits, IDs, titles or inferred continuity
    # NEVER authorize reuse. Only an explicit Handoff URL present in the current
    # Chat/Work/Codex conversation or instruction payload can continue an existing Handoff.
    if explicit_handoff_url:
        require(
            isinstance(explicit_handoff_url,str) and explicit_handoff_url.startswith('https://'),
            'G16_BOOTSTRAP_EXPLICIT_HANDOFF_URL_INVALID'
        )
        require(type(explicit_url_found) is bool,'G16_BOOTSTRAP_EXPLICIT_URL_RESOLUTION_REQUIRED')
        if explicit_url_found:
            return {'mode':'USE_EXISTING_EXPLICIT_URL','handoff_url':explicit_handoff_url}
        raise Invalid('G16_BOOTSTRAP_EXPLICIT_HANDOFF_URL_NOT_FOUND')
    return {
        'mode':'BOOTSTRAP_REQUIRED',
        'handoff_url':None,
        'ignored_existing_bindings':len(list(bound_handoff_refs or [])),
        'ignored_bare_handoff_ids':len(list(handoff_ids_in_context or [])),
    }

def generate_handoff_id(existing_ids=(), token_factory=None, max_attempts=8):
    existing=set(existing_ids or [])
    factory=token_factory or (lambda: secrets.token_hex(8))
    require(type(max_attempts) is int and 1 <= max_attempts <= 64,'G16_BOOTSTRAP_ATTEMPT_LIMIT_INVALID')
    for _ in range(max_attempts):
        raw=str(factory()).replace('-','').upper()
        require(bool(re.fullmatch(r'[0-9A-F]{16}',raw)),'G16_BOOTSTRAP_ID_FACTORY_INVALID')
        hid='HOF-'+raw
        if hid not in existing:
            return hid
    raise Invalid('G16_BOOTSTRAP_ID_COLLISION_EXHAUSTED')

def seed_state(handoff_id):
    require(bool(HOF_RE.fullmatch(str(handoff_id))),'G16_BOOTSTRAP_HANDOFF_ID_INVALID')
    return {
        'schema_version': tx.SCHEMA,
        'handoff_id': handoff_id,
        'interaction_seq': 0,
        'material_seq': 0,
        'visible_ref': f'{handoff_id} | S:0 | M:0',
        'current_interaction': None,
        'interaction_idempotency': {},
        'checkpoint_idempotency': {},
        'bootstrap': {
            'contract': CONTRACT,
            'profile': PROFILE,
            'state': 'SEED_CREATED_PENDING_FIRST_INTERACTION',
            'seed_is_internal_not_terminal_visible_ref': True,
        },
    }

def prepare_bootstrap(*, existing_ids=(), token_factory=None, provider=None):
    p=provider or {}
    require(p.get('provider_resolved') is True,'G16_HANDOFF_BOOTSTRAP_PROVIDER_UNRESOLVED')
    require(p.get('write_capability_verified') is True,'G16_HANDOFF_BOOTSTRAP_PROVIDER_WRITE_UNAVAILABLE')
    require(p.get('create_only_or_single_writer_verified') is True,'G16_HANDOFF_BOOTSTRAP_CREATE_EXCLUSION_REQUIRED')
    hid=generate_handoff_id(existing_ids,token_factory)
    state=seed_state(hid)
    return {
      'contract':CONTRACT,
      'operation':'PREPARE_FIRST_HANDOFF',
      'profile':PROFILE,
      'handoff_id':hid,
      'canonical_filename':hid+'.txt',
      'seed_state':state,
      'seed_sha256':digest(state),
      'counter_increment_S':0,
      'counter_increment_M':0,
      'next_operation':'PROVIDER_CREATE_ONLY_THEN_READBACK_THEN_ALLOCATE_FIRST_INTERACTION',
    }

def validate_created_handoff(prepared, observation):
    require(isinstance(prepared,dict) and prepared.get('contract')==CONTRACT,'G16_BOOTSTRAP_PREPARED_REQUIRED')
    require(isinstance(observation,dict),'G16_BOOTSTRAP_CREATE_OBSERVATION_REQUIRED')
    require(observation.get('create_only_verified') is True,'G16_BOOTSTRAP_CREATE_ONLY_NOT_VERIFIED')
    require(observation.get('post_create_readback_verified') is True,'G16_BOOTSTRAP_POSTCREATE_READBACK_REQUIRED')
    require(nonempty(observation.get('remote_revision')),'G16_BOOTSTRAP_REMOTE_REVISION_REQUIRED')
    require(type(observation.get('canonical_handoff_count_for_project')) is int and observation.get('canonical_handoff_count_for_project')==1,'G16_BOOTSTRAP_CANONICAL_COUNT_INVALID')
    state=prepared['seed_state']
    require(observation.get('observed_state_sha256')==digest(state),'G16_BOOTSTRAP_POSTCREATE_STATE_MISMATCH')
    require(observation.get('observed_handoff_id')==prepared['handoff_id'],'G16_BOOTSTRAP_HANDOFF_ID_MISMATCH')
    return {
      'contract':CONTRACT,
      'operation':'BOOTSTRAP_HANDOFF_CREATED',
      'profile':PROFILE,
      'handoff_id':prepared['handoff_id'],
      'S':0,'M':0,
      'remote_revision_after_create':observation['remote_revision'],
      'post_create_readback_verified':True,
      'next_operation':'ALLOCATE_FIRST_INTERACTION',
    }

def first_interaction(created_state, remote_revision, event, *, observation=None):
    """Consume a real host observation; never synthesize permission or readback."""
    require(isinstance(observation, dict), 'G16_BOOTSTRAP_PROVIDER_OBSERVATION_REQUIRED')
    require(observation.get('remote_revision') == remote_revision, 'G16_BOOTSTRAP_REMOTE_REVISION_MISMATCH')
    return tx.allocate_interaction(created_state, observation, event)


def reconcile_ambiguous_create(*, exact_id_match_count, same_state_digest_match=False):
    require(type(exact_id_match_count) is int and exact_id_match_count >= 0,'G16_BOOTSTRAP_RECONCILE_COUNT_INVALID')
    if exact_id_match_count>1:
        raise Invalid('G16_BOOTSTRAP_DUPLICATE_CANONICAL_HANDOFF_CONFLICT')
    if exact_id_match_count==1 and same_state_digest_match:
        return 'USE_EXISTING_CREATED_OBJECT'
    if exact_id_match_count==1:
        raise Invalid('G16_BOOTSTRAP_AMBIGUOUS_CREATE_STATE_MISMATCH')
    return 'RETRY_SAME_ID_CREATE_ONLY_AFTER_RECONCILIATION'
