#!/usr/bin/env python3
from collections import defaultdict, deque

def validate(graph,transaction_id,require_sharepoint=False,require_teams=False,*,destination_type="github_artifact"):
    if destination_type not in {"github_artifact","sharepoint_artifact"}:
        return {"ok":False,"errors":["destination_type_invalid"],"status":"LINEAGE_GRAPH_INVALID"}
    nodes=graph.get('nodes',[]); edges=graph.get('edges',[]); ids=[n.get('id') for n in nodes]; bad=[]
    if len(ids)!=len(set(ids)) or any(not x for x in ids): bad.append('duplicate_or_missing_node_id')
    by={n.get('id'):n for n in nodes}
    for n in nodes:
        if n.get('transaction_id')!=transaction_id or not n.get('type'): bad.append('node_binding')
    adj=defaultdict(list); indeg={x:0 for x in ids}
    for e in edges:
        if e.get('source') not in by or e.get('target') not in by or not e.get('relation'): bad.append('dangling_edge'); continue
        adj[e['source']].append(e['target']); indeg[e['target']]+=1
    q=deque([x for x,d in indeg.items() if d==0]); seen=0
    while q:
        x=q.popleft(); seen+=1
        for y in adj[x]:
            indeg[y]-=1
            if indeg[y]==0:q.append(y)
    if seen!=len(ids): bad.append('cycle')
    def reachable(src_types,target_type):
        starts=[n['id'] for n in nodes if n.get('type') in src_types]; targets={n['id'] for n in nodes if n.get('type')==target_type}; st=list(starts); vis=set(st)
        while st:
            x=st.pop()
            if x in targets:return True
            for y in adj[x]:
                if y not in vis: vis.add(y); st.append(y)
        return False
    if not reachable({'producer_output'},destination_type): bad.append('producer_to_destination_missing')
    if require_sharepoint and destination_type != 'sharepoint_artifact' and not reachable({destination_type},'sharepoint_backup'): bad.append('github_to_sharepoint_missing')
    if require_teams and not reachable({destination_type},'teams_post'): bad.append('github_to_teams_missing')
    return {'ok':not bad,'errors':sorted(set(bad)),'status':'PASS' if not bad else 'LINEAGE_GRAPH_INVALID'}
