#!/usr/bin/env python3
"""対象repoの登録済みlocal checksをreview packetまで実行する。"""
from __future__ import annotations
import argparse, ctypes, hashlib, json, os, re, signal, subprocess, sys, tempfile, time, uuid
from pathlib import Path
from typing import Any
from jsonschema import ValidationError, validate

ROOT=Path(__file__).resolve().parents[1]
ID_RE=re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
PYTHON={"python","python.exe","python3","py"}
REGISTRY=ROOT/"trusted-targets.json"

def _digest(value:Any)->str: return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def _safe_argv(argv:list[str],root:Path)->None:
    joined=" ".join(argv).lower()
    if any(x in joined for x in ("gh pr create","git merge","discord send","visibility"," release"," publish"," send")): raise ValueError("forbidden action")
    if Path(argv[0]).name.lower() not in PYTHON or any(x.startswith("@") for x in argv): raise ValueError("command not registered")
    args=argv[1:]
    if not args or args[0].startswith("-"): raise ValueError("command not registered")
    script=(root/args[0]).resolve()
    if not script.is_relative_to(root) or script.parent.name!="scripts" or not script.is_file(): raise ValueError("script not registered")
    if any("=" in x and x.split("=",1)[0].isidentifier() for x in args[1:]): raise ValueError("environment prefix forbidden")

def load_manifest(path:Path, *, target_repo:Path|None=None)->dict[str,Any]:
    data=json.loads(path.read_text(encoding="utf-8")); schema=json.loads((ROOT/"schemas/fde_target_workflow.v1.schema.json").read_text(encoding="utf-8"))
    try: validate(data,schema)
    except ValidationError as exc: raise ValueError("invalid manifest schema") from exc
    if not ID_RE.fullmatch(data["workflow_id"]): raise ValueError("unsafe workflow id")
    raw=data["repo_root"]
    if raw=="${TARGET_REPO}":
        if target_repo is None: raise ValueError("target repo required")
        root=target_repo.resolve()
    else: root=Path(raw).resolve()
    if not root.is_dir(): raise ValueError("repo root invalid")
    names=[x["name"] for x in data["checks"]]
    if len(names)!=len(set(names)): raise ValueError("duplicate check name")
    for check in data["checks"]: _safe_argv(check["argv"],root)
    result=dict(data); result["repo_root_resolved"]=str(root); result["manifest_digest"]=_digest({"manifest":data,"resolved_repo":str(root)}); return result

def _git(root:Path,*args:str)->str:
    result=subprocess.run(["git",*args],cwd=root,encoding="utf-8",errors="replace",stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,check=False,timeout=10)
    return result.stdout.strip() if result.returncode==0 else ""
def _verify_trust(manifest:dict[str,Any])->bool:
    try:
        registry=json.loads(REGISTRY.read_text(encoding="utf-8")); target=registry["targets"][manifest["target_id"]]; root=Path(manifest["repo_root_resolved"])
        head=_git(root,"rev-parse","HEAD"); tree=_git(root,"rev-parse","HEAD^{tree}")
        if _git(root,"remote","get-url","origin")!=target["remote"] or head!=target["head"] or tree!=target["tree"] or _git(root,"status","--porcelain"): return False
        if set(x["name"] for x in manifest["checks"])!=set(target["commands"]): return False
        hashes={}
        for check in manifest["checks"]:
            trusted=target["commands"][check["name"]]
            if check["argv"]!=trusted["argv"]: return False
            script=root/check["argv"][1]
            actual=hashlib.sha256(script.read_bytes()).hexdigest()
            if actual!=trusted["script_sha256"]: return False
            hashes[check["name"]]=actual
        return {"registry_id":target["registry_id"],"base_commit":target["base_commit"],"head":head,"tree":tree,"script_hashes":hashes}
    except Exception: return False

def _atomic(path:Path,payload:dict[str,Any])->None:
    path.parent.mkdir(parents=True,exist_ok=True); fd,name=tempfile.mkstemp(dir=path.parent,prefix=".receipt-",suffix=".tmp")
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as h: json.dump(payload,h,sort_keys=True); h.flush(); os.fsync(h.fileno())
        os.replace(name,path)
    finally: Path(name).unlink(missing_ok=True)
def _alive(pid:int)->bool:
    if os.name == "nt":
        handle=ctypes.windll.kernel32.OpenProcess(0x1000,False,pid)
        if not handle: return False
        try:
            exit_code=ctypes.c_ulong()
            return bool(ctypes.windll.kernel32.GetExitCodeProcess(handle,ctypes.byref(exit_code))) and exit_code.value==259
        finally: ctypes.windll.kernel32.CloseHandle(handle)
    try: os.kill(pid,0); return True
    except OSError: return False
def _terminate(proc:subprocess.Popen[bytes])->bool:
    tree_ok=True
    if os.name=="nt":
        taskkill=Path(os.environ.get("SystemRoot",r"C:\Windows"))/"System32/taskkill.exe"
        try:
            killed=subprocess.run([str(taskkill),"/F","/T","/PID",str(proc.pid)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=False,timeout=5)
            tree_ok=killed.returncode==0
            if not tree_ok: proc.kill()
        except (OSError,subprocess.TimeoutExpired): tree_ok=False; proc.kill()
    else:
        try: os.killpg(proc.pid,signal.SIGKILL)
        except OSError: pass
    try: proc.wait(timeout=5)
    except subprocess.TimeoutExpired: proc.kill(); proc.wait()
    return tree_ok
def _run(argv:list[str],cwd:str,timeout:float)->tuple[int,bytes,str,int]:
    start=time.monotonic(); flags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name=="nt" else 0
    normalized=[sys.executable,*argv[1:]]
    proc=subprocess.Popen(normalized,cwd=cwd,shell=False,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=os.name!="nt",creationflags=flags)
    try: out,_=proc.communicate(timeout=timeout); return proc.returncode,out,"passed" if proc.returncode==0 else "failed",round((time.monotonic()-start)*1000)
    except subprocess.TimeoutExpired as exc:
        terminated=_terminate(proc); return 124,exc.output or b"","timeout" if terminated else "failed",round((time.monotonic()-start)*1000)

def run_workflow(manifest:dict[str,Any],*,state_root:Path,resume:bool=False)->dict[str,Any]:
    trust=_verify_trust(manifest)
    if not trust: return {"schema":"fde.target_workflow_trust_stop.v1","workflow_id":manifest["workflow_id"],"state":"trust_review_required","checks":[],"executed":False}
    if trust is True: trust={"registry_id":"unit-test","base_commit":"0"*40,"head":"0"*40,"tree":"0"*40,"script_hashes":{x["name"]:"0"*64 for x in manifest["checks"]}}
    state_root=state_root.resolve(); state_root.mkdir(parents=True,exist_ok=True); wid=manifest["workflow_id"]; lock=state_root/f"{wid}.lock"; state=state_root/f"{wid}.json"
    if not lock.resolve().is_relative_to(state_root) or not state.resolve().is_relative_to(state_root): raise ValueError("state path escape")
    if lock.exists():
        try: owner=json.loads(lock.read_text()); stale=not _alive(int(owner["pid"]))
        except Exception: stale=time.time()-lock.stat().st_mtime>600
        if stale: lock.unlink()
        else: return {"workflow_id":wid,"state":"locked","external_actions_performed":False,"checks":[]}
    try:
        now=time.time(); fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY); os.write(fd,json.dumps({"pid":os.getpid(),"nonce":uuid.uuid4().hex,"started_at":now,"expires_at":now+900}).encode()); os.fsync(fd); os.close(fd)
    except FileExistsError: return {"workflow_id":wid,"state":"locked","external_actions_performed":False,"checks":[]}
    try:
        prior={}
        if resume and state.exists():
            try:
                old=json.loads(state.read_text());
                if old.get("manifest_digest")==manifest["manifest_digest"]: prior={x["check_digest"]:x for x in old.get("checks",[]) if x.get("status")=="passed"}
            except Exception: pass
        receipts=[]
        for check in manifest["checks"]:
            cd=_digest(check)
            if cd in prior: receipts.append(prior[cd]); continue
            code,out,status,duration=_run(check["argv"],manifest["repo_root_resolved"],check["timeout_seconds"])
            receipts.append({"name":check["name"],"check_digest":cd,"status":status,"exit_code":code,"duration_ms":duration,"output_digest":hashlib.sha256(out).hexdigest()})
            if status!="passed": break
        ok=len(receipts)==len(manifest["checks"]) and all(x["status"]=="passed" for x in receipts)
        payload={"schema":"fde.target_workflow_receipt.v1","workflow_id":wid,"manifest_digest":manifest["manifest_digest"],"trust_attestation":trust,"evidence_integrity":"local_unsealed_consistency","state":"human_review_required" if ok else "blocked","approval_gate":"review_packet","checks":receipts,"expected_check_count":len(manifest["checks"]),"implementation_residue":"none" if ok else "check_failed","operation_residue":"human_review_required" if ok else "retry_required","external_public_residue":"approval_gated","external_actions_performed":False}
        _atomic(state,payload); return payload
    finally: lock.unlink(missing_ok=True)

def main()->int:
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="command",required=True)
    for cmd in ("status","run"):
        x=sub.add_parser(cmd); x.add_argument("manifest",type=Path); x.add_argument("--target-repo",type=Path); x.add_argument("--state-root",type=Path,default=Path(".local/fde-target-workflow")); x.add_argument("--resume",action="store_true"); x.add_argument("--until",choices=["review_packet"],default="review_packet")
    try:
        a=p.parse_args(); m=load_manifest(a.manifest,target_repo=a.target_repo); path=a.state_root/f"{m['workflow_id']}.json"
        if a.command=="status" and path.exists():
            result=json.loads(path.read_text()); schema=json.loads((ROOT/"schemas/fde_target_workflow_receipt.v1.schema.json").read_text()); validate(result,schema)
            if result["workflow_id"]!=m["workflow_id"] or result["manifest_digest"]!=m["manifest_digest"]: raise ValueError("receipt binding failed")
            current=_verify_trust(m)
            if not isinstance(current,dict) or result["trust_attestation"]!=current: raise ValueError("trust consistency failed")
        else: result=({"workflow_id":m["workflow_id"],"state":"not_started","external_actions_performed":False,"checks":[]} if a.command=="status" else run_workflow(m,state_root=a.state_root,resume=a.resume))
    except Exception:
        result={"state":"blocked","failure_stage":"input_validation","recoverable":True,"external_actions_performed":False,"checks":[]}
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if result["state"] in {"not_started","human_review_required"} else 1
if __name__=="__main__": raise SystemExit(main())
