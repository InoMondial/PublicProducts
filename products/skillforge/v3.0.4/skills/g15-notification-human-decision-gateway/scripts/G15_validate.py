#!/usr/bin/env python3
import hashlib, json, pathlib, re, sys, zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
TECH_NAME = "g15-notification-human-decision-gateway"
REQUIRED = [
    "SKILL.md","G15-NOTICE.md","G15-GOVERNANCE.yaml","G15-artifact.yaml","G15-INSTALL.md","G15-VALIDATION.md","G15-CHANGELOG.md","G15-MANIFEST.sha256",
    "scripts/G15_core.py","scripts/G15_router.py","scripts/G15_render.py","scripts/G15_reply.py","scripts/G15_priority_feedback.py",
    "scripts/G15_contract.py","scripts/G15_reply_monitor.py","scripts/G15_single_writer_guard.py","scripts/G15_delivery_policy.py",
    "schemas/G15-notification-request.schema.json","schemas/G15-priority-feedback-record.schema.json","schemas/G15-decision-record.schema.json",
    "references/G15-decision-reply-standard.md","references/G15-report-visual-standard.md","references/G15-teams-reporting-standard.md",
    "references/G15-reply-monitoring-runtime-architecture-decision.md","references/G15-governance-compliance.md",
    "references/G15-mandatory-notification-catalog-v3.md","references/G15-stable-references.yaml","references/G15-capability-boundaries.md","references/G15-logging-contract.md",
    "references/G15-priority-feedback-contract.md","references/G15-routing-policy.json","references/G15-sqs-precheck.md","references/G15-examples.json",
    "references/G15-native-approval-bridge.md","references/G15-adaptive-card-bridge.md",
    "assets/G15-teams-report-template.html","assets/G15-teams-decision-template.html",
    "scripts/G15_validate.py","tests/G15_test_v3.py","tests/G15_test_v43_stage3.py","tests/G15_test_v431_route_style.py","G15-TEST-MATRIX.csv",
]
PACKAGE_EXCLUDED_DIRS = {"deploy", "dist", "evidence", "__pycache__"}
PLACEHOLDER_SECRET_VALUES = {"abc","test","example","dummy","placeholder","redacted","xxx","xxxx","none","null"}


def parse_frontmatter(text):
    if not text.startswith("---\n"):
        raise ValueError("FRONTMATTER_START")
    end=text.find("\n---\n",4)
    if end<0: raise ValueError("FRONTMATTER_END")
    block=text[4:end]
    data={}
    current=None
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"): continue
        if line.startswith("  ") and current:
            k,v=line.strip().split(":",1); data.setdefault(current,{})[k.strip()]=v.strip().strip('"')
        elif ":" in line:
            k,v=line.split(":",1); k=k.strip(); v=v.strip()
            if v:
                data[k]=v.strip('"'); current=None
            else:
                data[k]={}; current=k
    return data, text[end+5:]


def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(65536),b""): h.update(b)
    return h.hexdigest()


def _package_candidate_files(root):
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix in {".pyc", ".zip"}:
            continue
        rel=p.relative_to(root)
        if any(part in PACKAGE_EXCLUDED_DIRS for part in rel.parts):
            continue
        yield p


def _secret_scan_errors(root):
    errors=[]
    tenant_pattern=re.compile(r"(?i)tenantId\s*[:=]\s*([0-9a-f-]{20,})")
    env_uuid_pattern=re.compile(r"(?i)\b([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\b.*\b(tenant|channel|team|site)\b")
    secret_kv_pattern=re.compile(r"(?i)\b(password|passwd|cvv|private[_ -]?key|access[_ -]?token|refresh[_ -]?token)\b\s*[:=]\s*[\"']?([^\s\"',}\]]+)")
    for p in _package_candidate_files(root):
        text=p.read_text(encoding="utf-8",errors="ignore")
        rel=str(p.relative_to(root))
        if tenant_pattern.search(text): errors.append("FORBIDDEN_TENANT_ID:"+rel)
        if env_uuid_pattern.search(text): errors.append("FORBIDDEN_ENVIRONMENT_UUID:"+rel)
        for m in secret_kv_pattern.finditer(text):
            value=m.group(2).strip().casefold()
            if value in PLACEHOLDER_SECRET_VALUES or len(value) < 8: continue
            errors.append("POTENTIAL_SECRET_VALUE:"+rel+":"+m.group(1)); break
    return errors


def validate_root(root=ROOT, check_manifest=True):
    errors=[]
    for rel in REQUIRED:
        if not (root/rel).is_file(): errors.append("MISSING:"+rel)
    skill=(root/"SKILL.md").read_text(encoding="utf-8")
    fm,body=parse_frontmatter(skill)
    name=fm.get("name")
    if name != TECH_NAME: errors.append("BAD_NAME")
    if root.name != TECH_NAME: errors.append("DIR_NAME_MISMATCH")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",name or "") or len(name or "")>64: errors.append("AGENT_SKILLS_NAME")
    desc=fm.get("description","")
    if not (1<=len(desc)<=1024): errors.append("DESCRIPTION_LENGTH")
    if len(skill.splitlines())>=500: errors.append("SKILL_MD_TOO_LONG")
    if len(body.encode("utf-8"))>30000: errors.append("SKILL_MD_BODY_EXCESSIVE")
    if "version: 4.3.1" not in skill or "v4.3.1" not in skill: errors.append("G15_VERSION_431_REQUIRED")

    governance=(root/"G15-GOVERNANCE.yaml").read_text(encoding="utf-8")
    for token in (
        "canonical_reporting_standard_ref", "reply_runtime_architecture_ref", "outbound_message_ledger_required",
        "same_thread_acknowledgment_required", "CENTRAL_SCHEDULER_DISPATCHER_TIMER",
        "default_priority_destination_mandatory", "producer_destination_discretion: prohibited",
        "user_explicit_destination_override_only", "test_channel_for_actual_transport_tests_only",
        "canonical_renderer_mandatory", "canonical_renderer_id: G15_TEAMS_NATIVE_V1",
        "transport_content_field_required: html_content", "flat_plain_text_fallback_prohibited",
        "actual_route_readback_required",
    ):
        if token not in governance: errors.append("GOVERNANCE_CONTRACT_MISSING:"+token)

    core=(root/"scripts"/"G15_core.py").read_text(encoding="utf-8")
    if 'VERSION = "4.3.1"' not in core: errors.append("CORE_VERSION_DRIFT")
    router=(root/"scripts"/"G15_router.py").read_text(encoding="utf-8")
    for token in ("resolve_destination", "explicit_destination_authorized", "canonical_render_metadata"):
        if token not in router: errors.append("ROUTER_HARD_GATE_MISSING:"+token)
    render=(root/"scripts"/"G15_render.py").read_text(encoding="utf-8")
    if re.search(r"<table\b",render,re.I): errors.append("RENDERER_HTML_TABLE_PROHIBITED")
    contract=(root/"scripts"/"G15_contract.py").read_text(encoding="utf-8")
    for token in ("validate_destination_plan", "CANONICAL_G15_RENDERER_REQUIRED", "HTML_CONTENT_FIELD_REQUIRED", "READBACK_CHANNEL_MISMATCH"):
        if token not in contract: errors.append("CONTRACT_HARD_GATE_MISSING:"+token)
    delivery=(root/"scripts"/"G15_delivery_policy.py").read_text(encoding="utf-8")
    for token in ("DEFAULT_PRIORITY_ROUTE","USER_EXPLICIT_OVERRIDE","DESTINATION_OVERRIDE_NOT_AUTHORIZED","TEST_ROUTE_NOT_AUTHORIZED_FOR_PRODUCTION_EVENT","G15_TEAMS_NATIVE_V1","html_content"):
        if token not in delivery: errors.append("DELIVERY_POLICY_CONTRACT_MISSING:"+token)
    guard=(root/"scripts"/"G15_single_writer_guard.py").read_text(encoding="utf-8")
    if "has_write and (has_prod or has_event)" not in guard: errors.append("SINGLE_WRITER_EVENT_BYPASS_GAP")

    errors.extend(_secret_scan_errors(root))
    refs=re.findall(r'`((?:references|scripts|assets|tests|schemas)/[^`]+)`',skill)
    for rel in refs:
        if not (root/rel).exists(): errors.append("DANGLING_REF:"+rel)
    for p in list((root/"schemas").glob("*.json"))+[(root/"references"/"G15-routing-policy.json")]:
        try: json.loads(p.read_text(encoding="utf-8"))
        except Exception as e: errors.append("INVALID_JSON:"+p.name+":"+str(e))
    manifest=(root/"G15-MANIFEST.sha256")
    if check_manifest and manifest.exists():
        for line in manifest.read_text(encoding="utf-8").splitlines():
            if not line.strip(): continue
            digest,rel=line.split("  ",1)
            path=root/rel
            if not path.exists() or sha256(path)!=digest: errors.append("MANIFEST_MISMATCH:"+rel)
    return errors


def validate_zip(zip_path):
    errors=[]
    with zipfile.ZipFile(zip_path) as z:
        bad=z.testzip()
        if bad: errors.append("ZIP_CRC:"+bad)
        names=z.namelist(); prefix=TECH_NAME+"/"
        if any(not n.startswith(prefix) for n in names): errors.append("ZIP_ROOT")
        if prefix+"SKILL.md" not in names: errors.append("ZIP_SKILL_MISSING")
        if any("/deploy/" in n or "/dist/" in n or "/evidence/" in n or "__pycache__" in n or n.endswith(".pyc") for n in names): errors.append("ZIP_BUILD_ARTIFACT")
    return errors


if __name__=="__main__":
    source_only = "--source-only" in sys.argv
    errs=validate_root(check_manifest=not source_only)
    if errs:
        print(json.dumps({"status":"FAIL","mode":"SOURCE_ONLY" if source_only else "FULL","errors":errs},indent=2)); sys.exit(1)
    print(json.dumps({"status":"PASS","mode":"SOURCE_ONLY" if source_only else "FULL","root":str(ROOT)},indent=2))
