import { persistG11Envelope, readG11Run, deleteTestRun, persistG11ResourceObservation, readG11ResourceObservations, persistG11BillingLedger, readG11BillingLedger, deleteG11ResourceFinopsTestRows } from 'lib/g11-db-writer.js';

export const access='admin';
export const methods=['POST'];

export default async function(req,res){
  const body=req.body||{};
  try{
    if(body.operation==='read'){
      const project_ref=String(body.project_ref||'').trim();
      if(!project_ref) return res.status(400).json({ok:false,error:'PROJECT_CONTEXT_REQUIRED'});
      const data=await readG11Run(String(body.run_id||''),project_ref);
      return data ? res.json({ok:true,route:'INC_G11_G17_DB_WRITE_ROUTE_V1',project_ref,data}) : res.status(404).json({ok:false,error:'RUN_NOT_FOUND'});
    }
    if(body.operation==='delete_test'){
      const project_ref=String(body.project_ref||'').trim();
      if(!project_ref) return res.status(400).json({ok:false,error:'PROJECT_CONTEXT_REQUIRED'});
      return res.json(await deleteTestRun(String(body.run_id||''),project_ref));
    }
    if(body.operation==='persist_resource') return res.json(await persistG11ResourceObservation(body.observation||{}));
    if(body.operation==='read_resource') return res.json({ok:true,route:'INC_G11_G17_RESOURCE_FINOPS_WRITE_ROUTE_V1',data:await readG11ResourceObservations(body.filter||{})});
    if(body.operation==='persist_billing') return res.json(await persistG11BillingLedger(body.entry||{}));
    if(body.operation==='read_billing') return res.json({ok:true,route:'INC_G11_G17_RESOURCE_FINOPS_WRITE_ROUTE_V1',data:await readG11BillingLedger(body.filter||{})});
    if(body.operation==='delete_resource_finops_test') return res.json(await deleteG11ResourceFinopsTestRows(body.test_ref,body.project_ref));
    const envelope=body.envelope||body;
    return res.json(await persistG11Envelope(envelope));
  }catch(error){
    if(error?.code==='PROJECT_SCOPE_DENIED') return res.status(403).json({ok:false,error:'PROJECT_SCOPE_DENIED'});
    if(error?.code==='PROJECT_CONTEXT_REQUIRED') return res.status(400).json({ok:false,error:'PROJECT_CONTEXT_REQUIRED'});
    return res.status(400).json({ok:false,error:error?.code||'G11_DB_WRITE_FAILED',detail:error?.detail||null,message:String(error?.message||'').slice(0,500)});
  }
}