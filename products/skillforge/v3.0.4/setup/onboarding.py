#!/usr/bin/env python3
"""Offline, no-secret SkillForge onboarding planner and schema checker.

This CLI DOES NOT contact a provider, authenticate an account, grant access,
create ChatGPT apps, or post public feedback. Host-bound authorization requires
current trusted connector readback at the moment of a material operation.
"""
from __future__ import annotations
import argparse
import hashlib
import base64
import json
import os
import re
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'config' / 'setup-service-catalog.json'
FORBIDDEN_KEYS = {'password','passwd','token','access_token','refresh_token','client_secret','api_key','private_key','cookie','authorization','otp','mfa','pin'}
SECRET_PATTERNS = [
    re.compile(p, re.I) for p in [
        r'-----BEGIN\s+(?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
        r'\bgh[pousr]_[A-Za-z0-9]{20,}\b',
        r'\bgithub_pat_[A-Za-z0-9_]{25,}\b',
        r'\bsk-[A-Za-z0-9_-]{25,}\b',
        r'\bBearer\s+[A-Za-z0-9_./+-]{15,}\b',
    ]
]
PERSONAL = [
    re.compile(p,re.I) for p in [r'\b[0-9]+\+[\w.-]+@users\.noreply\.github\.com\b',
                                   r'\b[\w.+-]+@(?!inomondial\.com\b|example\.(?:com|org|invalid)\b)[\w.-]+\.[A-Za-z]{2,}\b',
                                   r'\b(?:[a-z0-9-]+\.)?sharepoint\.com\b',
                                   r'\b(?:[a-z0-9-]+\.)?onmicrosoft\.com\b',
                                   r'\b[A-Za-z]:\\Users\\[^\\\s]+',
                                   r'\b/Users/[^/\s]+']
]

def load_json(path:Path)->dict:
    def unique(pairs):
        d={}
        for k,v in pairs:
            if k in d:raise ValueError('DUPLICATE_JSON_KEY')
            d[k]=v
        return d
    data=json.loads(path.read_text(encoding='utf-8'),object_pairs_hook=unique,
                    parse_constant=lambda x:(_ for _ in ()).throw(ValueError('NONFINITE_JSON')))
    if not isinstance(data,dict):raise ValueError('OBJECT_REQUIRED')
    return data

def catalog()->dict:
    c=load_json(CATALOG)
    if c.get('schema_version')!='1.0' or not isinstance(c.get('services'),dict):
        raise ValueError('CATALOG_INVALID')
    return c

def validate_choices(host:str,services:list[str])->list[str]:
    c=catalog()
    if host not in c['allowed_hosts']:raise ValueError('UNSUPPORTED_HOST')
    if not services:services=['LOCAL_ONLY']
    if len(services)!=len(set(services)):raise ValueError('DUPLICATE_SERVICE')
    for s in services:
        if s not in c['services']:raise ValueError('UNKNOWN_SERVICE')
    if 'LOCAL_ONLY' in services and len(services)>1:
        raise ValueError('LOCAL_ONLY_MUST_STAND_ALONE')
    return services

def plan(host:str,services:list[str],language:str='en')->dict:
    services=validate_choices(host,services)
    if language not in {'en','fr','fa'}:raise ValueError('UNSUPPORTED_LANGUAGE')
    c=catalog()
    steps=[{'id':'SETUP-LANGUAGE','status':'QUESTION','answer_required':'language'},
           {'id':'SETUP-HOST','status':'HOST_CAPABILITIES_UNVERIFIED','host':host}]
    for s in services:
        x=c['services'][s]
        steps.append({'id':'SERVICE-'+s,'status':'AWAITING_SELECTION_OR_AUTHORIZATION',
                      'kind':x['kind'],'description':x['description'],
                      'parameter_names':x['parameters'],
                      'required_aliases':x['required_aliases'],
                      'no_secrets_in_chat':True,'permission_default':'READ_ONLY',
                      'connector_readback_required':s!='LOCAL_ONLY'})
    steps.append({'id':'PRIVATE-PERSISTENCE','status':'HOST_STORAGE_UNVERIFIED',
                  'rule':'PRIVATE_OUTSIDE_PACKAGE; NEVER PUBLIC GITHUB'})
    if 'PUBLIC_FEEDBACK' in services:
        steps.append({'id':'PUBLIC-FEEDBACK','status':'OFF_UNTIL_EXACT_PAYLOAD_CONSENT',
                      'target':'InoMondial/INOMondial-Public-Products',
                      'public_repo_current_state':'WITHDRAWN_NO_NEW_SUBMISSION_AUTHORIZED'})
    return {'contract':'INC_G20_SETUP_RUNTIME_V1','catalog_version':c['version'],
            'host':host,'language':language,'services':services,'steps':steps,
            'status':'PLAN_ONLY_NO_PROVIDER_AUTHORIZATION','external_profile_required':True}

def encoded_private_content(value:str)->bool:
    # Do not treat ordinary SHA-256 hex digests as secrets. Inspect actual
    # decodable UTF-8 payload; never echo the decoded value in errors.
    for item in re.findall(r'(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{24,2048}={0,2}(?![A-Za-z0-9+/])',value):
        if re.fullmatch(r'[0-9a-fA-F]{32,128}',item):continue
        try:
            decoded=base64.b64decode(item,validate=True).decode('utf-8')
        except (ValueError,UnicodeError):continue
        if any(p.search(decoded) for p in PERSONAL+SECRET_PATTERNS):return True
    return False

def no_raw_secrets(o):
    def visit(val):
        if isinstance(val,dict):
            for k,v in val.items():
                key=re.sub(r'[^a-z0-9]','',str(k).lower())
                if any(key.endswith(re.sub(r'[^a-z0-9]','',w)) for w in FORBIDDEN_KEYS):
                    if v not in (None,'','UNBOUND'):return False
                if not visit(v):return False
        elif isinstance(val,list):
            if any(not visit(x) for x in val):return False
        elif isinstance(val,str):
            if any(p.search(val) for p in SECRET_PATTERNS) or encoded_private_content(val):return False
        return True
    return visit(o)

def private_draft(host:str,services:list[str],language:str)->dict:
    p=plan(host,services,language);allkeys=set()
    c=catalog()
    for s in p['services']:allkeys.update(c['services'][s]['parameters'])
    aliases=sorted(set(a for s in p['services'] for a in c['services'][s]['required_aliases']))
    env={'schema_version':'1.0','profile_id':'SKILLFORGE_OWNER_DRAFT',
         'profile_version':'3.0.4','environment_id':'UNBOUND',
         'acceptance_mode':'SIMULATION_ONLY','state':'DRAFT',
         'selected_services':p['services'],'references':{},'required_aliases':aliases}
    return {'schema_version':'1.0','version':'3.0.4','state':'DRAFT_NOT_AUTHORIZED',
            'environment_profile':env,'parameters':{k:None for k in sorted(allkeys)},
            'raw_secrets_embedded':False,'public_export_allowed':False,
            'permissions_granted':False,'setup_plan':p}

def write_draft(path:Path,obj:dict)->str:
    if not no_raw_secrets(obj):raise ValueError('RAW_SECRET_IN_DRAFT')
    target=path.expanduser().absolute()
    if target.is_symlink() or target.exists():raise ValueError('DRAFT_TARGET_EXISTS_OR_SYMLINK')
    try:target.relative_to(ROOT)
    except ValueError:pass
    else:raise ValueError('DRAFT_MUST_BE_OUTSIDE_PACKAGE')
    if not target.parent.is_dir():raise ValueError('PARENT_PRIVATE_STORE_MISSING')
    if os.name!='nt':
        mode=stat.S_IMODE(target.parent.stat().st_mode)
        if mode & 0o002:raise ValueError('WORLD_WRITABLE_PARENT')
    raw=(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')
    fd=os.open(str(target),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    except BaseException:
        target.unlink(missing_ok=True);raise
    return hashlib.sha256(raw).hexdigest()

def checked_profile(path:Path,sha256:str)->dict:
    if not re.fullmatch(r'[0-9a-f]{64}',sha256):raise ValueError('EXPECTED_SHA256_REQUIRED')
    import importlib.util
    module=next((ROOT/'skills').glob('g8-*/scripts/public_boundary.py'))
    spec=importlib.util.spec_from_file_location('sfg8_public_boundary_v304',module)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    profile=m.load_external_profile(str(path),sha256,str(ROOT))
    env=profile.get('environment_profile')
    if not isinstance(env,dict):raise ValueError('ENVIRONMENT_PROFILE_REQUIRED')
    if not no_raw_secrets(profile):raise ValueError('RAW_SECRET_IN_PROFILE')
    if env.get('profile_version')!='3.0.4':raise ValueError('PROFILE_VERSION_MISMATCH')
    if env.get('profile_id') in (None,'','SKILLFORGE_OWNER_DRAFT'):
        raise ValueError('REAL_PROFILE_ID_REQUIRED')
    if not isinstance(env.get('required_aliases'),list):raise ValueError('REQUIRED_ALIASES_INVALID')
    for alias in env['required_aliases']:
        ref=env.get('references',{}).get(alias)
        if not isinstance(ref,dict) or ref.get('state')!='BOUND' or not ref.get('target') or not ref.get('kind'):
            raise ValueError('REQUIRED_ALIAS_UNBOUND')
    return {'status':'PROFILE_SCHEMA_AND_DIGEST_VALID_HOST_AUTHORIZATION_NOT_PROVEN',
            'sha256':sha256,'required_alias_count':len(env['required_aliases']),
            'real_connector_permission':'NOT_VERIFIED_BY_OFFLINE_TOOL',
            'public_release_authorized':False}

def feedback_check(proposal:dict)->dict:
    if not isinstance(proposal,dict):raise ValueError('PROPOSAL_OBJECT_REQUIRED')
    if proposal.get('mode','OFF')!='ON':
        return {'status':'OFF_NO_PUBLIC_WRITE','public_post_allowed':False}
    if proposal.get('destination')!='InoMondial/INOMondial-Public-Products':
        raise ValueError('UNKNOWN_PUBLIC_DESTINATION')
    title=proposal.get('title');body=proposal.get('body')
    if not isinstance(title,str) or not 8<=len(title)<=120 or not isinstance(body,str) or not 10<=len(body)<=3000:
        raise ValueError('CONTENT_OUT_OF_BOUNDS')
    if not no_raw_secrets(proposal):raise ValueError('SECRET_IN_PROPOSAL')
    if any(p.search(title+'\n'+body) for p in PERSONAL):
        raise ValueError('SENSITIVE_PRIVATE_IDENTIFIER_IN_PROPOSAL')
    expected=hashlib.sha256(json.dumps({'title':title,'body':body,'destination':proposal['destination']},
          ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()
    if proposal.get('owner_consent_digest')!=expected or proposal.get('owner_consent') is not True:
        return {'status':'EXACT_PAYLOAD_OWNER_CONSENT_MISSING','digest':expected,'public_post_allowed':False}
    # Explicit approval does not override destination withdrawal or platform permissions.
    return {'status':'BLOCKED_PUBLIC_REPOSITORY_WITHDRAWN','digest':expected,
            'public_post_allowed':False,'note':'No public Issue API call performed'}

def cli(argv=None)->int:
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='action',required=True)
    sub.add_parser('catalog')
    for action in ('plan','draft'):
        p=sub.add_parser(action);p.add_argument('--host',required=True)
        p.add_argument('--services',default='LOCAL_ONLY');p.add_argument('--language',default='en')
        if action=='draft':p.add_argument('--output',required=True)
    p=sub.add_parser('check');p.add_argument('--file',required=True);p.add_argument('--sha256',required=True)
    p=sub.add_parser('feedback-check');p.add_argument('--file',required=True)
    args=parser.parse_args(argv)
    try:
        if args.action=='catalog':out=catalog()
        elif args.action=='plan':out=plan(args.host,args.services.split(','),args.language)
        elif args.action=='draft':
            obj=private_draft(args.host,args.services.split(','),args.language)
            digest=write_draft(Path(args.output),obj)
            out={'status':'DRAFT_NOT_AUTHORIZED','sha256':digest,'provider_mutations':False}
        elif args.action=='check':out=checked_profile(Path(args.file),args.sha256)
        else:out=feedback_check(load_json(Path(args.file)))
        print(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2))
        return 0
    except (OSError,ValueError,TypeError,KeyError,StopIteration) as error:
        print(json.dumps({'status':'FAIL_CLOSED','error':str(error)[:100]},sort_keys=True))
        return 2

if __name__=='__main__':raise SystemExit(cli())
