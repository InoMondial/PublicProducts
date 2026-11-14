#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, sys
R=Path(__file__).resolve().parents[1]
required=['SKILL.md','GOVERNANCE.yaml','MANIFEST.json','references/sharepoint-destination-policy.yaml','references/sharepoint-backup-registry-contract.yaml','scripts/sharepoint_policy.py','tests/test_g1_v43.py','tests/test_transaction_gate_v43.py','tests/test_binary_fixtures.py','tests/simulate_v43.py']
missing=[x for x in required if not (R/x).exists()]
if missing: raise SystemExit('missing:'+','.join(missing))
m=json.loads((R/'MANIFEST.json').read_text())
assert m['version']=='4.3.0'
allowed_statuses={'STAGE4_CONTRACT_IMPLEMENTATION_VERIFIED','STAGE5_E2E_VERIFIED_RELEASE_PENDING','SUCCESS_VERIFIED'}
assert m['status'] in allowed_statuses, f"unsupported-manifest-status:{m['status']}"
skill=(R/'SKILL.md').read_text()
required_tokens=['v4.3.0','PROJECT_ARTIFACT_EGRESS_COMPLETE','SECURITY_BLOCKED','CAPABILITY_PREFLIGHT_FAILED','SHAREPOINT_CONCURRENCY_CONFLICT','RECOVERY_PROVEN','CONTRACT_COMPATIBILITY_FAILED','EVIDENCE_STALE_OR_WRONG_TRANSACTION','LINEAGE_GRAPH_INVALID','CALLER_SHAREPOINT_DESTINATION_OVERRIDE_FORBIDDEN','NESTED_MANAGED_ARTIFACT_DUPLICATION','CANONICAL_BACKUP_AUTHORITY_CONFLICT','VERSION_AUTHORITY_DRIFT','BRANCH_RESIDUE_NOT_CLOSED','PARTIAL']
missing_tokens=[x for x in required_tokens if x not in skill]
if missing_tokens: raise SystemExit('missing-skill-tokens:'+','.join(missing_tokens))
for script in ['tests/test_g1_v43.py','tests/test_transaction_gate_v43.py','tests/test_binary_fixtures.py','tests/simulate_v43.py']:
    subprocess.run([sys.executable,str(R/script)],cwd=R,check=True)
print('G1_V43_CANDIDATE_VALIDATOR: PASS')
