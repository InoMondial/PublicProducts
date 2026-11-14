from pathlib import Path
import hashlib, json, re, yaml, zipfile

r=Path(__file__).resolve().parents[1]
required=[
    'SKILL.md','GOVERNANCE.yaml','MANIFEST.json','NOTICE.md','CHANGELOG.md',
    'references/vnext-contract.yaml','references/c7-live-writer-route.yaml',
    'references/caller-interface.yaml','references/caller-quickstart.md',
    'references/writer-envelope-v1.schema.json','scripts/compile_caller_request.py',
    'scripts/build_candidate.py','tests/test-cases.yaml','deploy/PACKAGE.yaml'
]
missing=[x for x in required if not (r/x).exists()]
if missing:
    raise SystemExit('missing:'+','.join(missing))

s=(r/'SKILL.md').read_text(encoding='utf-8')
q=(r/'references/caller-quickstart.md').read_text(encoding='utf-8')
ch=(r/'CHANGELOG.md').read_text(encoding='utf-8')
g=yaml.safe_load((r/'GOVERNANCE.yaml').read_text(encoding='utf-8'))
m=json.loads((r/'MANIFEST.json').read_text(encoding='utf-8'))
w=yaml.safe_load((r/'references/c7-live-writer-route.yaml').read_text(encoding='utf-8'))
c=yaml.safe_load((r/'references/caller-interface.yaml').read_text(encoding='utf-8'))
v=yaml.safe_load((r/'references/vnext-contract.yaml').read_text(encoding='utf-8'))
t=yaml.safe_load((r/'tests/test-cases.yaml').read_text(encoding='utf-8'))
p=yaml.safe_load((r/'deploy/PACKAGE.yaml').read_text(encoding='utf-8'))

version='4.4.2'
assert g['stable_id']=='O6-SKL-011' and g['stable_id'] in s
assert g['visible_id']=='G11'
assert g['version']==m['version']==v['version']==p['version']==version
assert f'Standardizer {version} — Candidate' in s
assert f'# G11-Logging & Traceability Standardizer v{version} — Candidate' in s
assert f'# G11 Caller Quick Start — v{version}' in q
assert f'## {version} — 2026-08-16' in ch
assert g['logging']['target_ref']=='INC_LOG_STORE'
assert g['logging']['caller_interface_ref']=='INC_G11_CALLER_INTERFACE_V1'
assert g['logging']['writer_route_ref']=='INC_G11_C7_WRITE_ROUTE_V1'
assert g['logging']['writer_envelope_ref']=='INC_G11_LOG_ENVELOPE_V1'
assert g['logging']['writer_envelope_schema_ref']=='INC_G11_LOG_ENVELOPE_V1_SCHEMA'
assert g['logging']['internal_compiler_ref']=='G11_CALLER_TO_WRITER_COMPILER_V1'
assert g['logging']['connector_queue_parent_path']=='Example Governance Records/c7-g11/write-queue'
assert g['logging']['physical_schema_loading_by_callers']=='PROHIBITED'
assert g['logging']['hourly_wait_or_queue_poll_by_callers']=='PROHIBITED'
assert g['logging']['fake_semantic_record_generation']=='PROHIBITED'
assert g['critical_control_assurance']['contract_ref']=='INC_CRITICAL_CONTROL_ASSURANCE_V2'
assert len(g['critical_control_assurance']['controls'])==6
assert any(x['capability']=='G3' and x['applicability']=='REQUIRED' for x in g['cross_cutting'])
assert w['canonical_store']['logical_ref']=='INC_LOG_STORE'
assert w['producer_contract']['caller_interface_ref']=='INC_G11_CALLER_INTERFACE_V1'
assert w['producer_contract']['compiled_writer_envelope_ref']=='INC_G11_LOG_ENVELOPE_V1'
assert w['ingress']['folder_path']=='Example Governance Records/c7-g11/write-queue'
assert w['ingress']['forbidden_connector_prefix']=='Shared Documents/Shared Documents/'
assert w['writer']['flow_name']=='C7-G11-Write-Hourly'
assert set(w['writer']['approved_operations'])=={'CREATE','READ','UPDATE'}
assert w['producer_contract']['direct_list_mutation']=='PROHIBITED'
assert w['producer_contract']['physical_schema_loading']=='PROHIBITED'
assert w['producer_contract']['queue_polling_or_hourly_wait']=='PROHIBITED'
assert w['verification']['caller_does_not_poll'] is True
assert w['verification']['queue_acceptance_alone_is_pass'] is False
assert w['schema_change']['explicit_owner_approval']=='REQUIRED'
assert c['contract_id']=='INC_G11_CALLER_INTERFACE_V1'
assert c['writer_contract']['transport_envelope_ref']=='INC_G11_LOG_ENVELOPE_V1'
assert c['writer_contract']['caller_must_not_construct_directly'] is True
assert c['anti_duplication']['one_handoff_per_governed_activity'] is True
assert c['verification']['ASYNC']['caller_behavior']=='DO_NOT_POLL_OR_WAIT'
assert c['verification']['REQUIRED']['caller_behavior']=='DELEGATE_VERIFICATION_TO_G11'
assert all(x.get('result')=='PASS' for x in t['tests'])
assert len(t['tests'])==32 and m['tests']==32
assert f'Ver{version}_' in p['filename']
zips=list((r/'deploy').glob('*.zip'))
assert len(zips)==1 and zips[0].name==p['filename']
data=zips[0].read_bytes()
assert hashlib.sha256(data).hexdigest()==p['sha256']
with zipfile.ZipFile(zips[0]) as z:
    assert z.testzip() is None
print('PASS',len(t['tests']),f'G11 v{version} consistency + operational compiler + live-writer route validated')
