#!/usr/bin/env python3
"""Cooperatively locked local journal; authenticated provider evidence is external."""
import hashlib, json, os, tempfile
from pathlib import Path
from contextlib import contextmanager
from concurrency_lock import acquire, release

def compute_key(project_id,operation,canonical_route,artifacts):
    payload={'project_id':project_id,'operation':operation,'canonical_route':canonical_route,'artifacts':sorted([{'path':a['path'],'sha256':a['sha256']} for a in artifacts],key=lambda x:(x['path'],x['sha256']))}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

class Store:
    def __init__(self,path):
        self.path=Path(path);self.data={}
        if self.path.exists():self._reload()
    def _reload(self):
        if self.path.is_symlink():raise ValueError('IDEMPOTENCY_SYMLINK_PROHIBITED')
        self.data=json.loads(self.path.read_text(encoding='utf-8')) if self.path.exists() else {}
        if not isinstance(self.data,dict):raise ValueError('IDEMPOTENCY_STORE_INVALID')
    @contextmanager
    def _locked(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        lock=self.path.with_name(self.path.name+'.lock')
        receipt=acquire(lock,'G1_IDEMPOTENCY',str(os.getpid()))
        try:self._reload();yield
        finally:release(lock,receipt['token'])
    def _save(self):
        fd,tmp=tempfile.mkstemp(prefix='.g1-idempotency-',dir=self.path.parent)
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as stream:
                json.dump(self.data,stream,sort_keys=True,indent=2,allow_nan=False);stream.flush();os.fsync(stream.fileno())
            os.replace(tmp,self.path)
        finally:
            if os.path.exists(tmp):os.unlink(tmp)
    def begin(self,key,transaction_id):
        if not all(isinstance(v,str) and v.strip() for v in (key,transaction_id)):raise ValueError('IDEMPOTENCY_IDENTITY_INVALID')
        with self._locked():
            cur=self.data.get(key)
            if cur and cur.get('status')=='SUCCESS_VERIFIED':return {'status':'REPLAY_SUCCESS','record':cur}
            if cur and cur.get('status')=='IN_PROGRESS' and cur.get('transaction_id')!=transaction_id:return {'status':'IDEMPOTENCY_IN_PROGRESS_CONFLICT'}
            self.data[key]={'status':'IN_PROGRESS','transaction_id':transaction_id};self._save();return {'status':'STARTED'}
    def finish(self,key,transaction_id,result):
        if not isinstance(result,dict) or result.get('status')!='SUCCESS_VERIFIED':raise ValueError('IDEMPOTENCY_VERIFIED_RESULT_REQUIRED')
        with self._locked():
            cur=self.data.get(key)
            if not cur or cur.get('transaction_id')!=transaction_id:raise RuntimeError('IDEMPOTENCY_OWNER_MISMATCH')
            if cur.get('status')=='SUCCESS_VERIFIED':
                if cur.get('result')!=result:raise RuntimeError('IDEMPOTENCY_RESULT_CONFLICT')
                return cur
            self.data[key]={'status':'SUCCESS_VERIFIED','transaction_id':transaction_id,'result':result};self._save();return self.data[key]
