#!/usr/bin/env python3
"""Report configuration validity. A profile is not authenticated authorization.

No network, mutations, secrets, auto-install or native enforcement claim. The
host/G8 must authorize each real action separately using current observations.
"""
import hashlib
import json
import os
import re
from pathlib import Path

CONTRACT_REF='INC_SKILLFORGE_SESSION_START_ENVIRONMENT_GATE_V1'
FORBIDDEN_KEYS={'password','token','access_token','refresh_token','client_secret','api_key','cookie','otp','mfa','private_key'}

def normalize(key):return re.sub(r'([a-z0-9])([A-Z])',r'\1_\2',re.sub(r'([A-Z]+)([A-Z][a-z])',r'\1_\2',str(key))).lower().replace('-','_')
def contains_forbidden(value):
    if isinstance(value,dict):return any(normalize(k) in FORBIDDEN_KEYS or contains_forbidden(v) for k,v in value.items())
    if isinstance(value,list):return any(contains_forbidden(v) for v in value)
    return False

def no_duplicates(pairs):
    out={}
    for k,v in pairs:
        if k in out:raise ValueError('DUPLICATE_JSON_KEY')
        out[k]=v
    return out

def valid_text(v):return isinstance(v,str) and bool(v.strip()) and not any(ord(c)<32 for c in v)

def assess(profile):
    state={'contract_ref':CONTRACT_REF,'status':'PROFILE_SCHEMA_INVALID','runtime_state':'CONFIGURATION_UNVERIFIED',
           'mutation_allowed':False,'cross_surface_dispatch_allowed':False,'publication_allowed':False,
           'release_allowed':False,'terminal_success_allowed':False,'host_abort_supported':False,
           'authorization_basis':'HOST_OPERATION_SCOPED_EVIDENCE_REQUIRED'}
    if isinstance(profile,dict) and profile.get('state')=='UNBOUND':
        state['status']='SETUP_REQUIRED_PROFILE_UNBOUND';return state
    if (not isinstance(profile,dict) or profile.get('schema_version')!='1.0'
        or not all(valid_text(profile.get(k)) for k in ('profile_id','profile_version','environment_id'))
        or not isinstance(profile.get('references'),dict) or not isinstance(profile.get('required_aliases'),list)
        or not all(valid_text(a) for a in profile['required_aliases'])
        or len(set(profile['required_aliases']))!=len(profile['required_aliases']) or contains_forbidden(profile)):
        return state
    if not profile['required_aliases'] and profile.get('selected_services')!=['LOCAL_ONLY']:
        state['status']='PROFILE_SCHEMA_INVALID';return state
    for alias in profile['required_aliases']:
        item=profile['references'].get(alias)
        if not isinstance(item,dict) or not all(valid_text(item.get(k)) for k in ('kind','target')):
            return state
        if item.get('state')!='BOUND':
            state['status']='REQUIRED_ALIAS_UNRESOLVED';return state
    mode=profile.get('acceptance_mode')
    if mode not in ('SIMULATION_ONLY','HOST_VERIFIED'):
        state['status']='ACCEPTANCE_MODE_UNVERIFIED';return state
    raw=json.dumps(profile,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
    state.update(status='SIMULATION_PROFILE_VALID_NO_NATIVE_AUTHORIZATION' if mode=='SIMULATION_ONLY' else 'PROFILE_VALID_HOST_AUTHORIZATION_REQUIRED',
                 runtime_state='CONFIGURATION_VALID_ONLY',profile_digest=hashlib.sha256(raw).hexdigest(),
                 profile_id=profile['profile_id'],profile_version=profile['profile_version'])
    return state

def main():
    root=Path(os.environ.get('PLUGIN_ROOT',Path(__file__).resolve().parents[1]))
    try:
        external=os.environ.get('SKILLFORGE_EXTERNAL_PROFILE')
        if external:
            import importlib.util
            engine=next((root/'skills').glob('g8-*/scripts/public_boundary.py'))
            spec=importlib.util.spec_from_file_location('sf_privacy',engine);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
            bound=mod.load_external_profile(external,os.environ.get('SKILLFORGE_EXTERNAL_PROFILE_SHA256',''),str(root))
            text=json.dumps(bound.get('environment_profile',{}))
        else:
            text=(root/'config/environment-profile.json').read_text(encoding='utf-8')
        profile=json.loads(text,object_pairs_hook=no_duplicates,parse_constant=lambda value:(_ for _ in ()).throw(ValueError('NONFINITE_JSON')))
        result=assess(profile)
    except (OSError,ValueError,TypeError,RecursionError):
        result=assess(None);result['status']='PROFILE_LOAD_FAILED'
    # Only documented SessionStart fields. Machine details live inside the
    # supported additionalContext string, not a fictitious host gate field.
    context='SkillForge configuration check: '+result['status']+'. If setup is required, follow setup/CHATGPT_FIRST_RUN.md (for a connected conversational host) or setup/README.md (shell host). Configuration is not permission. Require current host/G8 authorization for real mutations.\nSKILLFORGE_GATE_JSON='+json.dumps(result,sort_keys=True,separators=(',',':'))
    print(json.dumps({'hookSpecificOutput':{'hookEventName':'SessionStart','additionalContext':context}}))
    return 0

if __name__=='__main__':raise SystemExit(main())
