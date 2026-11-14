#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Mapping
DOCUMENT_EXTENSIONS={'.doc','.docx','.xls','.xlsx','.xlsm','.pdf','.ppt','.pptx'}
DOCUMENT_CLASSES={'DOCUMENT_CLASS','HUMAN_BUSINESS_REPORT_BINARY'}
FORBIDDEN_POINTER_FIELDS={'embedded_bytes','base64_payload','document_bytes','binary_payload','inline_file_content'}
@dataclass(frozen=True)
class PolicyFailure(Exception):
    code: str
    detail: str=''
    def __str__(self): return self.code + (f': {self.detail}' if self.detail else '')
def _fail(code,detail=''): raise PolicyFailure(code,detail)
def is_document_class(path: str|None=None, semantic_class: str|None=None) -> bool:
    ext=PurePosixPath(str(path or '')).suffix.lower(); sem=str(semantic_class or '').upper()
    return ext in DOCUMENT_EXTENSIONS or sem in DOCUMENT_CLASSES
def route_artifact(*, path: str, semantic_class: str|None, durability: str, artifact_role: str='DELIVERABLE') -> dict[str,Any]:
    durable=str(durability or '').upper() in {'DURABLE','FINAL','CANONICAL','REUSABLE','EVIDENCE'}
    doc=is_document_class(path,semantic_class); role=str(artifact_role or '').upper()
    if durable and doc and role not in {'SOURCE_CODE','GENERATOR_CODE','POINTER_METADATA'}:
        return {'canonical_storage':'SHAREPOINT','github_binary_allowed':False,'verified_sharepoint_link_required':True,'contract':'INC_G1_DOCUMENT_CLASS_STORAGE_V1'}
    return {'canonical_storage':'GOVERNED_ROUTE','github_binary_allowed':True,'verified_sharepoint_link_required':False,'contract':'INC_G1_DOCUMENT_CLASS_STORAGE_V1'}
def validate_publish_target(*, path: str, semantic_class: str|None, durability: str, destination: str, artifact_role: str='DELIVERABLE') -> dict[str,Any]:
    route=route_artifact(path=path,semantic_class=semantic_class,durability=durability,artifact_role=artifact_role); dest=str(destination or '').upper()
    if route['canonical_storage']=='SHAREPOINT' and dest=='GITHUB': _fail('G1_DOCUMENT_CLASS_GITHUB_STORAGE_FORBIDDEN',path)
    if route['canonical_storage']=='SHAREPOINT' and dest in {'LOCAL','SANDBOX','WINDOWS'}: _fail('LOCAL_ONLY_DELIVERY_FORBIDDEN',path)
    return {'ok':True,'destination':dest,**route}
def validate_github_pointer(pointer: Mapping[str,Any]) -> dict[str,Any]:
    bad=sorted(k for k in FORBIDDEN_POINTER_FIELDS if pointer.get(k) not in (None,'',[],{}))
    if bad: _fail('G1_DOCUMENT_POINTER_EMBEDDED_BYTES_FORBIDDEN',','.join(bad))
    if not (pointer.get('sharepoint_ref') or pointer.get('sharepoint_stable_id') or pointer.get('sharepoint_url')): _fail('G1_DOCUMENT_POINTER_SHAREPOINT_REF_REQUIRED')
    if not (pointer.get('provenance_ref') or pointer.get('source_commit') or pointer.get('generator_ref')): _fail('G1_DOCUMENT_POINTER_PROVENANCE_REQUIRED')
    return {'ok':True,'status':'GITHUB_POINTER_ALLOWED','document_bytes_embedded':False}
def verify_sharepoint_closure(evidence: Mapping[str,Any]) -> dict[str,Any]:
    required=('write','readback','identity_verified','verified_link'); missing=[k for k in required if evidence.get(k)!='PASS']
    if missing: _fail('REMOTE_ARTIFACT_DELIVERY_BLOCKED',','.join(missing))
    return {'ok':True,'status':'SHAREPOINT_DOCUMENT_DELIVERY_VERIFIED'}
