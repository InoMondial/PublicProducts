#!/usr/bin/env python3
import argparse,hashlib,json,re
from pathlib import Path
try: import yaml
except Exception: yaml=None
from skillforge_pairwise_gate import validate_matrix
from carry_forward_gate import validate_manifest as validate_carry_forward_manifest

def tree_hash(root):
 h=hashlib.sha256()
 for p in sorted(x for x in root.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  rel=p.relative_to(root).as_posix(); h.update(rel.encode()); h.update(b'\0'); h.update(hashlib.sha256(p.read_bytes()).digest())
 return h.hexdigest()

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('skills_root'); ap.add_argument('--executor-surface',default='LOCAL_CODEX'); ap.add_argument('--artifact-digest',default='UNBUILT'); ap.add_argument('--regression-evidence-json'); ap.add_argument('--pairwise-members'); ap.add_argument('--pairwise-matrix'); ap.add_argument('--carry-forward-previous'); ap.add_argument('--carry-forward-current'); ap.add_argument('--carry-forward-manifest'); ap.add_argument('--out'); ap.add_argument('--scope-profile',choices=['FULL','PRIVATE_V3_RISK_PROPORTIONAL'],default='FULL'); ap.add_argument('--impact-evidence-json'); a=ap.parse_args()
 root=Path(a.skills_root); steps=[]; fails=[]
 if not root.is_dir():raise SystemExit('SKILLS_ROOT_MISSING')
 source_digest=tree_hash(root)
 if not re.fullmatch('[0-9a-f]{64}',a.artifact_digest):fails.append('ARTIFACT_DIGEST_INVALID')
 skills=[p for p in root.iterdir() if p.is_dir() and (p/'SKILL.md').exists()]
 steps.append({'id':'SKILL_ENTRYPOINT_CHECK','status':'PASS' if len(skills)==19 else 'FAIL','count':len(skills),'runtime_scope':'G0-G18 with one canonical G17 Data Governor'})
 if len(skills)!=19:fails.append('SKILL_COUNT_NOT_19')
 parse_fail=[]
 for p in root.rglob('*.json'):
  try: json.loads(p.read_text(encoding='utf-8'))
  except Exception as e: parse_fail.append(f'JSON:{p}:{e}')
 if yaml is None: parse_fail.append('YAML_PARSER_UNAVAILABLE')
 if yaml:
  for p in root.rglob('*.yaml'):
   try: yaml.safe_load(p.read_text(encoding='utf-8'))
   except Exception as e: parse_fail.append(f'YAML:{p}:{e}')
 steps.append({'id':'PARSE_JSON_YAML','status':'PASS' if not parse_fail else 'FAIL','failures':parse_fail[:20]})
 fails.extend(parse_fail)
 if a.regression_evidence_json:
  ev=json.loads(Path(a.regression_evidence_json).read_text(encoding='utf-8'))
  valid=(isinstance(ev,dict) and ev.get('source_tree_sha256')==source_digest and ev.get('output_artifact_digest')==a.artifact_digest and all(isinstance(ev.get(k),dict) and ev[k].get('status')=='PASS' and type(ev[k].get('tests_executed')) is int and ev[k]['tests_executed']>0 and type(ev[k].get('failures')) is int and ev[k]['failures']==0 for k in ('g16','g18','release_simulation')))
  steps.append({'id':'TARGETED_REGRESSION_EVIDENCE','status':'PASS' if valid else 'FAIL','evidence':ev})
  if not valid:fails.append('REGRESSION_EVIDENCE_FAIL')
 else:
  steps.append({'id':'TARGETED_REGRESSION_EVIDENCE','status':'FAIL','detail':'missing --regression-evidence-json'}); fails.append('REGRESSION_EVIDENCE_MISSING')
 if a.scope_profile=='PRIVATE_V3_RISK_PROPORTIONAL':
  try: impact=json.loads(Path(a.impact_evidence_json).read_text(encoding='utf-8')) if a.impact_evidence_json else {}
  except (OSError,ValueError,TypeError):impact={}
  valid=(isinstance(impact,dict) and impact.get('source_tree_sha256')==source_digest and impact.get('output_artifact_digest')==a.artifact_digest and impact.get('status')=='PASS' and all(impact.get(k) is True for k in ('changed_critical_paths_covered','security_negative_tests_pass','prior_active_contracts_reconciled')) and type(impact.get('unresolved_release_critical_count')) is int and impact['unresolved_release_critical_count']==0)
  steps.append({'id':'PRIVATE_V3_IMPACT_SCOPE','status':'PASS' if valid else 'FAIL'})
  if not valid:fails.append('IMPACT_SCOPE_EVIDENCE_INVALID')
 else:
  if a.pairwise_members and a.pairwise_matrix:
   members=json.loads(Path(a.pairwise_members).read_text(encoding='utf-8')); matrix=json.loads(Path(a.pairwise_matrix).read_text(encoding='utf-8'))
   pair_errors=validate_matrix(matrix,members,True)
   steps.append({'id':'EXHAUSTIVE_PAIRWISE_GATE','status':'PASS' if not pair_errors else 'FAIL','member_count':matrix.get('member_count'),'directed_relationship_count':matrix.get('directed_relationship_count'),'unique_unordered_pair_count':matrix.get('unique_unordered_pair_count'),'matrix_sha256':matrix.get('matrix_sha256'),'errors':pair_errors[:20]})
   fails.extend('PAIRWISE:'+x for x in pair_errors)
  else:
   steps.append({'id':'EXHAUSTIVE_PAIRWISE_GATE','status':'FAIL','detail':'missing --pairwise-members/--pairwise-matrix'}); fails.append('PAIRWISE_MATRIX_MISSING')
  if a.carry_forward_previous and a.carry_forward_current and a.carry_forward_manifest:
   prev=json.loads(Path(a.carry_forward_previous).read_text(encoding='utf-8')); cur=json.loads(Path(a.carry_forward_current).read_text(encoding='utf-8')); cf=json.loads(Path(a.carry_forward_manifest).read_text(encoding='utf-8'))
   cf_errors=validate_carry_forward_manifest(cf,prev,cur,True)
   steps.append({'id':'PREVIOUS_VERSION_CARRY_FORWARD_GATE','status':'PASS' if not cf_errors else 'FAIL','manifest_sha256':cf.get('manifest_sha256'),'previous_snapshot_sha256':cf.get('previous_snapshot_sha256'),'current_snapshot_sha256':cf.get('current_snapshot_sha256'),'unresolved_count':(cf.get('summary') or {}).get('unresolved_count'),'errors':cf_errors[:20]})
   fails.extend('CARRY_FORWARD:'+x for x in cf_errors)
  else:
   steps.append({'id':'PREVIOUS_VERSION_CARRY_FORWARD_GATE','status':'FAIL','detail':'missing carry-forward previous/current/manifest inputs'}); fails.append('CARRY_FORWARD_INPUT_MISSING')
 att={'schema_version':'1.2','public_release_authorized':False,'publicization_gate':'INC_PUBLICIZATION_PRIVACY_GATE_V2_REQUIRED','independent_certification':False,'scope_profile':a.scope_profile,'trust_boundary':'Caller evidence must be authenticated by host; aggregator checks consistency only','pipeline_version':'INC_RUNNER_INDEPENDENT_CI_V1','executor_surface':a.executor_surface,'source_tree_sha256':tree_hash(root),'steps':steps,'result':'PASS' if not fails else 'FAIL','output_artifact_digest':a.artifact_digest,'failures':fails}
 out=json.dumps(att,ensure_ascii=False,indent=2)+'\n'
 if a.out:Path(a.out).write_text(out,encoding='utf-8')
 print(out,end=''); return 0 if not fails else 1
if __name__=='__main__': raise SystemExit(main())
