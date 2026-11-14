#!/usr/bin/env python3
from evidence_freshness import validate_object
REQUIRED_PROOFS=['latest_main_reconciled','all_durable_accounted','all_required_committed','all_required_pushed','pr_merged_when_required','main_remote_readback','required_release_gates','registry_reconciled','owned_branch_cleanup','temp_workflow_cleanup','staging_cleanup','security_gate','idempotency_reconciled','capability_preflight','contract_compatibility','lineage_graph_valid','ledger_hash_chain_valid','lineage_lock_released']
REQUIRED_ZERO=['uncommitted_durable_files','unpushed_commits','required_open_prs','owned_temp_branches','owned_temp_workflows','owned_staging_residue']
def valid_proof(p,transaction_id,start,now=None):
    return isinstance(p,dict) and p.get('status')=='PASS' and isinstance(p.get('reference'),str) and bool(p['reference'].strip()) and validate_object(p,transaction_id,start,now).get('ok')
def evaluate(state,transaction_id,transaction_started_at,now=None,require_recovery=False,require_sharepoint_concurrency=False):
    if not isinstance(state,dict):return {'ok':False,'status':'REPOSITORY_HYGIENE_INCOMPLETE','invalid_proofs':['STATE_INVALID'],'nonzero':[]}
    keys=list(REQUIRED_PROOFS)
    if require_recovery: keys.append('recovery_proven')
    if require_sharepoint_concurrency: keys.append('sharepoint_optimistic_concurrency')
    invalid=[k for k in keys if not valid_proof(state.get(k),transaction_id,transaction_started_at,now)]
    nonzero=[k for k in REQUIRED_ZERO if type(state.get(k)) is not int or state[k]!=0]
    ok=not invalid and not nonzero
    if ok: status='SUCCESS_VERIFIED'
    elif 'owned_temp_branches' in nonzero: status='BRANCH_RESIDUE_NOT_CLOSED'
    else: status='REPOSITORY_HYGIENE_INCOMPLETE'
    return {'ok':ok,'invalid_proofs':invalid,'nonzero':nonzero,'status':status}
