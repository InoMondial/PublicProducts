#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import tomllib

try:
    import yaml
except Exception as exc:
    raise SystemExit("PyYAML is required for SkillForge structural validation") from exc

class DuplicateKeyError(ValueError):
    pass

class UniqueKeyLoader(yaml.SafeLoader):
    pass

def _construct_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise DuplicateKeyError(f"duplicate key: {key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping

UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)

REQUIRED_PARAM_FIELDS = {
    "setup_parameter_id","value_type","scope","owner_skill","consumers","requirement_state",
    "required_when","validation","sensitivity","auth_mode","capability","recommended_provider",
    "recommended_default","alternatives","documentation_refs","migration_behavior","compatibility",
}
PHYSICAL_PATTERNS = [
    re.compile(r"https?://", re.I),
    re.compile(r"^[A-Za-z]:[\\/]"),
    re.compile(r"^/Users/|^/home/|^/mnt/|^/var/", re.I),
    re.compile(r"(tenant|account|subscription|resource)[_-]?id", re.I),
]
STRUCTURED_EXTENSIONS={".yaml",".yml",".json",".toml"}

def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()

def strict_utf8(path):
    data=Path(path).read_bytes()
    try:
        text=data.decode("utf-8","strict")
    except UnicodeDecodeError as exc:
        raise ValueError(f"STRUCTURAL_ENCODING_INVALID:{path}:{exc}")
    return data,text

def json_unique(text):
    def hook(pairs):
        out={}
        for k,v in pairs:
            if k in out:
                raise DuplicateKeyError(f"duplicate key: {k}")
            out[k]=v
        return out
    return json.loads(text, object_pairs_hook=hook)

def parse_path(path):
    path=Path(path)
    raw,text=strict_utf8(path)
    suffix=path.suffix.lower()
    if suffix in (".yaml",".yml"):
        if "\\n" in text:
            raise ValueError(f"STRUCTURAL_LITERAL_ESCAPE_ARTIFACT:{path}")
        parser="yaml"; value=yaml.load(text, Loader=UniqueKeyLoader)
    elif suffix==".json":
        parser="json"; value=json_unique(text)
    elif suffix==".toml":
        parser="toml"; value=tomllib.loads(text)
    elif suffix==".md" and text.startswith("---\n"):
        end=text.find("\n---\n",4)
        if end<0:
            raise ValueError(f"STRUCTURAL_FRONTMATTER_TRUNCATED:{path}")
        front=text[4:end]
        if "\\n" in front:
            raise ValueError(f"STRUCTURAL_LITERAL_ESCAPE_ARTIFACT:{path}")
        parser="frontmatter-yaml"; value=yaml.load(front, Loader=UniqueKeyLoader)
    else:
        return None
    return {"parser":parser,"semantic":value,"sha256":sha256_bytes(raw)}

def validate_setup_contract(path):
    parsed=parse_path(path)
    if not parsed or not isinstance(parsed["semantic"],dict):
        raise ValueError("SETUP_CONTRACT_INVALID")
    doc=parsed["semantic"]
    if doc.get("contract_id")!="INC_SKILL_SETUP_CONTRACT_V1":
        raise ValueError("SETUP_CONTRACT_ID_INVALID")
    params=doc.get("parameters",[])
    seen={}
    for p in params:
        missing=REQUIRED_PARAM_FIELDS-set(p)
        if missing:
            raise ValueError("SETUP_PARAMETER_FIELDS_MISSING:"+",".join(sorted(missing)))
        sid=p["setup_parameter_id"]
        if not isinstance(sid,str) or not sid.strip() or sid=="NUM#":
            raise ValueError("SETUP_PARAMETER_ID_INVALID")
        normalized={k:p.get(k) for k in sorted(REQUIRED_PARAM_FIELDS)}
        if sid in seen and seen[sid]!=normalized:
            raise ValueError("SETUP_PARAMETER_CONFLICT:"+sid)
        seen[sid]=normalized
        value=p.get("recommended_default")
        if isinstance(value,str) and any(rx.search(value) for rx in PHYSICAL_PATTERNS):
            raise ValueError("CUSTOMER_PHYSICAL_VALUE_IN_PUBLIC_CORE:"+sid)
    return {"status":"PASS","parameter_count":len(seen),"sha256":parsed["sha256"]}

def structured_files(root):
    root=Path(root); out=[]
    for p in root.rglob("*"):
        if not p.is_file(): continue
        if p.suffix.lower() in STRUCTURED_EXTENSIONS:
            out.append(p)
        elif p.suffix.lower()==".md":
            try:
                if p.read_bytes().startswith(b"---\n"): out.append(p)
            except OSError:
                pass
    return sorted(out)

def validate_tree(root):
    root=Path(root); report={}
    for p in structured_files(root):
        parsed=parse_path(p)
        if parsed: report[str(p.relative_to(root))]=parsed
    return report

def compare_trees(source,package):
    s=validate_tree(source); p=validate_tree(package)
    if set(s)!=set(p):
        raise ValueError("STRUCTURAL_SEMANTIC_PARITY_FAILED:PATH_SET")
    for rel in s:
        if s[rel]["semantic"]!=p[rel]["semantic"]:
            raise ValueError("STRUCTURAL_SEMANTIC_PARITY_FAILED:"+rel)
    return {
        "status":"PASS","file_count":len(s),
        "source_tree_sha256":hashlib.sha256(json.dumps({k:v["sha256"] for k,v in s.items()},sort_keys=True).encode()).hexdigest(),
        "package_tree_sha256":hashlib.sha256(json.dumps({k:v["sha256"] for k,v in p.items()},sort_keys=True).encode()).hexdigest()
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--setup-contract")
    ap.add_argument("--source")
    ap.add_argument("--package")
    args=ap.parse_args()
    result={}
    try:
        if args.setup_contract: result["setup_contract"]=validate_setup_contract(args.setup_contract)
        if bool(args.source)!=bool(args.package): raise ValueError("--source and --package must be provided together")
        if args.source: result["source_package"]=compare_trees(args.source,args.package)
        if not result: raise ValueError("no validation target provided")
        result["status"]="PASS"; print(json.dumps(result,sort_keys=True)); return 0
    except Exception as exc:
        print(json.dumps({"status":"FAIL","error":str(exc)},sort_keys=True)); return 2

if __name__=="__main__":
    sys.exit(main())
