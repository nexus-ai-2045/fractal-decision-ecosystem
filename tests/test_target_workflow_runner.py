import json
import sys
import os
from pathlib import Path

import pytest
import scripts.fde_target_workflow as runner
import subprocess
from scripts.fde_operational_closeout import evaluate as closeout_evaluate

from scripts.fde_target_workflow import load_manifest, run_workflow


def test_dcb_post_merge_manifest_matches_trust_registry() -> None:
    root = Path(__file__).parents[1]
    manifest_data = json.loads((root / "examples/dcb_target_workflow.json").read_text(encoding="utf-8"))
    target = json.loads((root / "trusted-targets.json").read_text(encoding="utf-8"))["targets"]["discord-context-bridge"]

    assert target["head"] == "fa19ac27d5f00e7ab1cbe5d77b3aee428c56fd12"
    assert target["tree"] == "4f78d3c5eb8ce8802a456eb3ce1f17b3b17f6b04"
    assert {check["name"] for check in manifest_data["checks"]} == set(target["commands"])
    assert "pr_readiness" not in target["commands"]

@pytest.fixture(autouse=True)
def trusted_unit_target(monkeypatch, request):
    if not request.node.name.startswith("test_real_"):
        monkeypatch.setattr(runner, "_verify_trust", lambda manifest: True)


def manifest(tmp_path, checks=None):
    root=Path(__file__).parents[1]
    return {"schema":"fde.target_workflow.v1","workflow_id":"test","target_id":"unit","repo_root":str(root),"approval_gate":"review_packet","checks":checks or [{"name":"ok","argv":[sys.executable,"scripts/public_ready_check.py"],"timeout_seconds":30}]}


def test_manifest_requires_argv_timeout_and_review_gate(tmp_path):
    path=tmp_path/"m.json"; data=manifest(tmp_path); data["approval_gate"]="merge"; path.write_text(json.dumps(data))
    with pytest.raises(ValueError): load_manifest(path)


@pytest.mark.parametrize("argv", [["gh","pr","create"],["git","merge","main"],["discord","send"],["gh","repo","edit","--visibility","public"]])
def test_forbidden_actions_rejected(tmp_path, argv):
    path=tmp_path/"m.json"; path.write_text(json.dumps(manifest(tmp_path,[{"name":"bad","argv":argv,"timeout_seconds":5}])))
    with pytest.raises(ValueError, match="forbidden"):
        load_manifest(path)


def test_run_stops_at_review_packet_and_receipt_is_metadata_only(tmp_path):
    path=tmp_path/"m.json"; path.write_text(json.dumps(manifest(tmp_path)))
    result=run_workflow(load_manifest(path), state_root=tmp_path/".local")
    rendered=json.dumps(result)
    assert result["state"]=="human_review_required"
    assert "PRIVATE" not in rendered and str(tmp_path) not in rendered
    assert result["checks"][0].keys() >= {"name","exit_code","duration_ms","output_digest"}


def test_failure_stops_and_resume_skips_success(tmp_path):
    checks=[{"name":"ok","argv":[sys.executable,"scripts/public_ready_check.py"],"timeout_seconds":30},{"name":"bad","argv":[sys.executable,"scripts/fde_target_workflow.py","--bad-option"],"timeout_seconds":5}]
    path=tmp_path/"m.json"; path.write_text(json.dumps(manifest(tmp_path,checks)))
    first=run_workflow(load_manifest(path),state_root=tmp_path/".local")
    second=run_workflow(load_manifest(path),state_root=tmp_path/".local",resume=True)
    assert first["state"]==second["state"]=="blocked"
    assert len(second["checks"])==2


def test_timeout_and_lock_are_bounded(tmp_path, monkeypatch):
    checks=[{"name":"slow","argv":[sys.executable,"scripts/public_ready_check.py"],"timeout_seconds":0.01}]
    path=tmp_path/"m.json"; path.write_text(json.dumps(manifest(tmp_path,checks)))
    monkeypatch.setattr(runner,"_run",lambda *args:(124,b"","timeout",10))
    result=run_workflow(load_manifest(path),state_root=tmp_path/".local")
    assert result["checks"][0]["status"]=="timeout"
    lock=tmp_path/".local/test.lock"; lock.write_text("locked")
    assert run_workflow(load_manifest(path),state_root=tmp_path/".local")["state"]=="locked"


@pytest.mark.parametrize("argv", [[sys.executable,"-c","pass"],[sys.executable,"-m","http.server"],[sys.executable,"@args"],["pwsh","-Command","echo x"]])
def test_command_bypasses_are_rejected(tmp_path, argv):
    path=tmp_path/"m.json"; path.write_text(json.dumps(manifest(tmp_path,[{"name":"x","argv":argv,"timeout_seconds":5}])))
    with pytest.raises(ValueError): load_manifest(path)


def test_safe_workflow_id_and_unique_names(tmp_path):
    data=manifest(tmp_path); data["workflow_id"]="../escape"
    path=tmp_path/"m.json"; path.write_text(json.dumps(data))
    with pytest.raises(ValueError): load_manifest(path)
    data=manifest(tmp_path); data["checks"]=[data["checks"][0],data["checks"][0]]; path.write_text(json.dumps(data))
    with pytest.raises(ValueError): load_manifest(path)


def test_manifest_change_invalidates_resume(tmp_path):
    path=tmp_path/"m.json"; data=manifest(tmp_path); path.write_text(json.dumps(data)); loaded=load_manifest(path)
    first=run_workflow(loaded,state_root=tmp_path/".local")
    data["checks"][0]["timeout_seconds"]=31; path.write_text(json.dumps(data))
    second=run_workflow(load_manifest(path),state_root=tmp_path/".local",resume=True)
    assert first["manifest_digest"] != second["manifest_digest"]


def _git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, encoding="utf-8", stdout=subprocess.PIPE).stdout.strip()


@pytest.fixture
def real_target(tmp_path, monkeypatch):
    repo=tmp_path/"repo"; repo.mkdir(); (repo/"scripts").mkdir()
    gate=repo/"scripts/gate.py"; gate.write_text("print('ok')\n",encoding="utf-8")
    _git(repo,"init"); _git(repo,"config","user.email","test@example.invalid"); _git(repo,"config","user.name","Test")
    _git(repo,"add","."); _git(repo,"commit","-m","base"); base=_git(repo,"rev-parse","HEAD")
    _git(repo,"remote","add","origin","https://example.invalid/trusted.git")
    digest=__import__("hashlib").sha256(gate.read_bytes()).hexdigest()
    tree=_git(repo,"rev-parse","HEAD^{tree}")
    registry=tmp_path/"registry.json"; registry.write_text(json.dumps({"schema":"fde.trusted_targets.v1","targets":{"target":{"registry_id":"test-registry","base_commit":base,"head":base,"tree":tree,"remote":"https://example.invalid/trusted.git","commands":{"gate":{"argv":["python","scripts/gate.py"],"script_sha256":digest}}}}}),encoding="utf-8")
    monkeypatch.setattr(runner,"REGISTRY",registry)
    data={"schema":"fde.target_workflow.v1","workflow_id":"real","target_id":"target","repo_root":str(repo),"approval_gate":"review_packet","checks":[{"name":"gate","argv":["python","scripts/gate.py"],"timeout_seconds":10}]}
    manifest_path=tmp_path/"manifest.json"; manifest_path.write_text(json.dumps(data),encoding="utf-8")
    return repo,gate,registry,manifest_path


def test_real_positive_clean_pinned_tree_allowed(real_target):
    repo,gate,registry,path=real_target
    trust=runner._verify_trust(load_manifest(path))
    assert isinstance(trust,dict) and trust["head"]==_git(repo,"rev-parse","HEAD")


def test_real_dirty_or_unpinned_tree_stops(real_target):
    repo,gate,registry,path=real_target; (repo/"dirty.txt").write_text("dirty",encoding="utf-8")
    assert runner._verify_trust(load_manifest(path)) is False


def test_real_remote_mismatch_rejected(real_target):
    repo,gate,registry,path=real_target; _git(repo,"remote","set-url","origin","https://example.invalid/wrong.git")
    assert runner._verify_trust(load_manifest(path)) is False


def test_real_unpinned_head_rejected(real_target):
    repo,gate,registry,path=real_target; (repo/"feature.txt").write_text("feature",encoding="utf-8"); _git(repo,"add","feature.txt"); _git(repo,"commit","-m","feature")
    assert runner._verify_trust(load_manifest(path)) is False


def test_real_gate_modified_hash_mismatch_and_no_execution(real_target, tmp_path):
    repo,gate,registry,path=real_target; gate.write_text("raise SystemExit('MUST NOT RUN')",encoding="utf-8")
    result=run_workflow(load_manifest(path),state_root=tmp_path/"state")
    assert result["state"]=="trust_review_required" and result["executed"] is False and result["checks"]==[]


def test_real_generated_receipt_schema_and_closeout_roundtrip(real_target, tmp_path):
    repo,gate,registry,path=real_target; state=tmp_path/"state"; result=run_workflow(load_manifest(path),state_root=state)
    assert result["state"]=="human_review_required"
    receipt=state/"real.json"
    closed=closeout_evaluate(run_pytest=False,target_receipt=receipt,target_manifest=path)
    assert closed["checks"]["target_workflow"]["ok"] is True
    assert closed["operation_residue"] == "human_review_required"
    assert closed["next_required_human_decision"] == "target PR human review"
    assert closed["external_public_residue"] == "approval_gated"


def test_real_forged_untrusted_closeout_fails(real_target, tmp_path):
    repo,gate,registry,path=real_target; state=tmp_path/"state"; run_workflow(load_manifest(path),state_root=state); receipt=state/"real.json"
    payload=json.loads(receipt.read_text()); payload["trust_attestation"]["head"]="0"*40; receipt.write_text(json.dumps(payload))
    assert closeout_evaluate(run_pytest=False,target_receipt=receipt,target_manifest=path)["checks"]["target_workflow"]["ok"] is False


def test_real_live_but_expired_lock_remains_blocked(real_target, tmp_path):
    repo,gate,registry,path=real_target; state=tmp_path/"state"; state.mkdir(); (state/"real.lock").write_text(json.dumps({"pid":os.getpid(),"nonce":"x","started_at":0,"expires_at":0}))
    assert run_workflow(load_manifest(path),state_root=state)["state"]=="locked"


def test_real_taskkill_nonzero_reports_tree_termination_failure(monkeypatch):
    if os.name!="nt": pytest.skip("Windows taskkill contract")
    class Proc:
        pid=12345
        killed=False
        def kill(self): self.killed=True
        def wait(self,timeout=None): return 1
    proc=Proc()
    monkeypatch.setattr(runner.subprocess,"run",lambda *a,**k:type("R",(),{"returncode":1})())
    assert runner._terminate(proc) is False and proc.killed is True


def test_real_windows_alive_detects_current_and_missing_pid():
    if os.name!="nt": pytest.skip("Windows PID contract")
    assert runner._alive(os.getpid()) is True
    assert runner._alive(0x7FFFFFFF) is False


def test_real_status_rejects_forged_trust_attestation(real_target, tmp_path, monkeypatch, capsys):
    repo,gate,registry,path=real_target; state=tmp_path/"state"; run_workflow(load_manifest(path),state_root=state)
    receipt=state/"real.json"; payload=json.loads(receipt.read_text()); payload["trust_attestation"]["head"]="0"*40; receipt.write_text(json.dumps(payload))
    monkeypatch.setattr(sys,"argv",["fde_target_workflow.py","status",str(path),"--state-root",str(state)])
    assert runner.main()==1
    output=json.loads(capsys.readouterr().out)
    assert output["state"]=="blocked" and output["failure_stage"]=="input_validation"
