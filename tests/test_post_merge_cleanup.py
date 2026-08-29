from __future__ import annotations

import subprocess
from pathlib import Path

from scripts import post_merge_cleanup
from scripts.post_merge_cleanup import evaluate
from scripts.post_merge_cleanup import _sanitize_receipt_detail


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return result.stdout.strip()


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / "README.md").write_text("main\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "init")
    # Ensure branch is named main
    current = _git(repo, "branch", "--show-current")
    if current != "main":
        _git(repo, "branch", "-m", "main")
    return repo


def test_check_reports_merged_local_branch_without_deleting(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _git(repo, "checkout", "-b", "cursor/feature-temp-54bb")
    (repo / "feature.txt").write_text("x\n", encoding="utf-8")
    _git(repo, "add", "feature.txt")
    _git(repo, "commit", "-m", "feature")
    _git(repo, "checkout", "main")
    _git(repo, "merge", "--no-ff", "cursor/feature-temp-54bb", "-m", "merge feature")

    result = evaluate(apply=False, cwd=repo)

    assert "cursor/feature-temp-54bb" in result["residue"]["merged_local_branches"]
    assert result["overall"] == "error"
    assert _git(repo, "branch", "--list", "cursor/feature-temp-54bb")


def test_apply_deletes_merged_local_branch(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _git(repo, "checkout", "-b", "cursor/feature-temp-54bb")
    (repo / "feature.txt").write_text("x\n", encoding="utf-8")
    _git(repo, "add", "feature.txt")
    _git(repo, "commit", "-m", "feature")
    _git(repo, "checkout", "main")
    _git(repo, "merge", "--no-ff", "cursor/feature-temp-54bb", "-m", "merge feature")

    result = evaluate(apply=True, cwd=repo)

    assert result["overall"] == "ok"
    assert result["residue"]["merged_local_branches"] == []
    assert result["external_actions_performed"] is True
    assert _git(repo, "branch", "--list", "cursor/feature-temp-54bb") == ""


def test_ci_checkout_without_local_main_uses_origin_main(tmp_path: Path) -> None:
    """GitHub Actions PR checkouts often lack refs/heads/main."""
    bare = tmp_path / "origin.git"
    bare.mkdir()
    _git(bare, "init", "--bare")

    seed = tmp_path / "seed"
    seed.mkdir()
    _git(seed, "init")
    _git(seed, "config", "user.email", "test@example.com")
    _git(seed, "config", "user.name", "Test")
    (seed / "README.md").write_text("main\n", encoding="utf-8")
    _git(seed, "add", "README.md")
    _git(seed, "commit", "-m", "init")
    if _git(seed, "branch", "--show-current") != "main":
        _git(seed, "branch", "-m", "main")
    _git(seed, "remote", "add", "origin", str(bare))
    _git(seed, "push", "-u", "origin", "main")
    _git(seed, "checkout", "-b", "cursor/ci-feature-54bb")
    (seed / "feature.txt").write_text("x\n", encoding="utf-8")
    _git(seed, "add", "feature.txt")
    _git(seed, "commit", "-m", "feature")
    _git(seed, "push", "-u", "origin", "cursor/ci-feature-54bb")

    # Simulate Actions PR checkout: single-branch feature + fetched origin/main tip.
    pr_checkout = tmp_path / "pr"
    _git(
        tmp_path,
        "clone",
        "--branch",
        "cursor/ci-feature-54bb",
        "--single-branch",
        str(bare),
        str(pr_checkout),
    )
    _git(pr_checkout, "fetch", "origin", "main:refs/remotes/origin/main")
    local_branches = _git(pr_checkout, "branch", "--format=%(refname:short)").splitlines()
    assert "main" not in local_branches
    assert _git(pr_checkout, "show-ref", "--verify", "refs/remotes/origin/main")

    result = evaluate(apply=False, cwd=pr_checkout)

    assert result["overall"] == "ok", result
    assert result["base_ref"] == "refs/remotes/origin/main"
    assert result["residue"]["merged_local_branches"] == []


def test_protected_branches_are_not_deleted(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _git(repo, "branch", "release-please--branches--main--components--demo")
    # Create an empty commit on protected branch then merge so it is "merged"
    _git(repo, "checkout", "release-please--branches--main--components--demo")
    _git(repo, "commit", "--allow-empty", "-m", "release please tip")
    _git(repo, "checkout", "main")
    _git(
        repo,
        "merge",
        "--no-ff",
        "release-please--branches--main--components--demo",
        "-m",
        "merge release please",
    )

    result = evaluate(apply=True, cwd=repo)

    assert (
        "release-please--branches--main--components--demo"
        not in result["residue"]["merged_local_branches"]
    )
    assert _git(
        repo, "branch", "--list", "release-please--branches--main--components--demo"
    )


def test_receipt_detail_sanitizes_tokens_and_user_paths() -> None:
    github_token = "gh" + "p_" + ("a" * 24)
    openai_token = "sk-" + ("b" * 24)
    windows_user_path = "C:" + "\\Users\\" + "example" + "\\Projects\\FDE"
    mac_user_path = "/" + "Users" + "/example/Projects/FDE"
    linux_user_path = "/" + "home" + "/example/Projects/FDE"
    detail = (
        f"remote: {github_token}\n"
        f"Authorization: Bearer {openai_token}\n"
        f"failed at {windows_user_path}\n"
        f"failed at {mac_user_path}\n"
        f"failed at {linux_user_path}"
    )

    sanitized = _sanitize_receipt_detail(detail)

    assert sanitized is not None
    assert github_token not in sanitized
    assert openai_token not in sanitized
    assert windows_user_path not in sanitized
    assert mac_user_path not in sanitized
    assert linux_user_path not in sanitized
    assert "<redacted-token>" in sanitized
    assert ("C:" + "\\Users\\" + "<user>") in sanitized
    assert ("/" + "Users" + "/<user>") in sanitized
    assert ("/" + "home" + "/<user>") in sanitized


def test_failure_receipt_keeps_only_bounded_metadata() -> None:
    secret = "github_pat_" + ("a" * 40)
    result = subprocess.CompletedProcess(
        ["git", "fetch"],
        128,
        stdout=f"internal host output {secret}",
        stderr=f"fatal: https://user:{secret}@internal.example/repo.git",
    )

    detail = post_merge_cleanup._failure_summary("git fetch --prune origin", result)

    assert detail == "git fetch --prune origin failed (exit 128)"
    assert secret not in detail
    assert "internal.example" not in detail


def test_run_is_noninteractive_and_converts_missing_executable(monkeypatch) -> None:
    observed: dict[str, object] = {}
    monkeypatch.setenv("GH_REPO", "attacker/wrong-repo")

    def fake_run(*args, **kwargs):
        observed.update(kwargs)
        raise FileNotFoundError("missing")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = post_merge_cleanup._run(
        ["gh", "api", "repos/{owner}/{repo}"], allow_failure=True
    )

    assert result.returncode == 127
    assert observed["stdin"] is subprocess.DEVNULL
    assert observed["timeout"] == post_merge_cleanup.NETWORK_TIMEOUT_SECONDS
    assert observed["env"]["GIT_TERMINAL_PROMPT"] == "0"
    assert observed["env"]["GH_PROMPT_DISABLED"] == "1"
    assert "GH_REPO" not in observed["env"]


def test_run_converts_timeout_to_bounded_failure(monkeypatch) -> None:
    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = post_merge_cleanup._run(
        ["git", "remote", "prune", "origin"], allow_failure=True
    )

    assert result.returncode == 124
    assert result.stderr == "command timed out"


def test_configured_remote_default_branch_precedes_main_guess(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _git(repo, "branch", "master")
    _git(repo, "update-ref", "refs/remotes/origin/main", "main")
    _git(repo, "update-ref", "refs/remotes/origin/master", "master")
    _git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/master")

    # Default branch name comes from origin/HEAD; local head is preferred when
    # it is not strictly behind the remote-tracking tip.
    assert post_merge_cleanup._resolve_base_ref(repo) == "refs/heads/master"


def test_local_default_branch_preferred_when_ahead_of_origin(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _git(repo, "update-ref", "refs/remotes/origin/main", "main")
    _git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
    _git(repo, "checkout", "-b", "feature/local-ahead")
    (repo / "feature.txt").write_text("x\n", encoding="utf-8")
    _git(repo, "add", "feature.txt")
    _git(repo, "commit", "-m", "feature")
    _git(repo, "checkout", "main")
    _git(repo, "merge", "--no-ff", "feature/local-ahead", "-m", "merge local")

    assert post_merge_cleanup._resolve_base_ref(repo) == "refs/heads/main"

    result = evaluate(apply=False, cwd=repo)

    assert "feature/local-ahead" in result["residue"]["merged_local_branches"]
    assert result["overall"] == "error"


def test_remote_default_branch_used_when_strictly_ahead(tmp_path: Path) -> None:
    bare = tmp_path / "origin.git"
    bare.mkdir()
    _git(bare, "init", "--bare")
    seed_parent = tmp_path / "seed-parent"
    seed_parent.mkdir()
    seed = _init_repo(seed_parent)
    _git(seed, "remote", "add", "origin", str(bare))
    _git(seed, "push", "-u", "origin", "main")

    local = tmp_path / "local"
    _git(tmp_path, "clone", str(bare), str(local))
    _git(local, "config", "user.email", "test@example.com")
    _git(local, "config", "user.name", "Test")

    _git(seed, "commit", "--allow-empty", "-m", "advance main")
    _git(seed, "push", "origin", "main")
    _git(local, "fetch", "origin")

    assert post_merge_cleanup._resolve_base_ref(local) == "refs/remotes/origin/main"


def test_checked_out_integrated_branch_is_reported_as_residue(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _git(repo, "checkout", "-b", "feature/checked-out")
    (repo / "feature.txt").write_text("x\n", encoding="utf-8")
    _git(repo, "add", "feature.txt")
    _git(repo, "commit", "-m", "feature")
    _git(repo, "checkout", "main")
    _git(repo, "merge", "--no-ff", "feature/checked-out", "-m", "merge")
    _git(repo, "checkout", "feature/checked-out")

    result = evaluate(apply=False, cwd=repo)

    assert result["overall"] == "error"
    assert result["residue"]["checked_out_merged_branch"] == "feature/checked-out"
    assert any("switch" in error for error in result["errors"])


def test_apply_fetches_before_recomputing_merged_branches(tmp_path: Path) -> None:
    bare = tmp_path / "origin.git"
    bare.mkdir()
    _git(bare, "init", "--bare")
    seed_parent = tmp_path / "seed-parent"
    seed_parent.mkdir()
    seed = _init_repo(seed_parent)
    _git(seed, "remote", "add", "origin", str(bare))
    _git(seed, "push", "-u", "origin", "main")
    _git(seed, "checkout", "-b", "feature/remote-merged")
    (seed / "feature.txt").write_text("x\n", encoding="utf-8")
    _git(seed, "add", "feature.txt")
    _git(seed, "commit", "-m", "feature")
    _git(seed, "push", "-u", "origin", "feature/remote-merged")

    local = tmp_path / "local"
    _git(tmp_path, "clone", str(bare), str(local))
    _git(local, "config", "user.email", "test@example.com")
    _git(local, "config", "user.name", "Test")
    _git(local, "checkout", "-b", "feature/remote-merged", "origin/feature/remote-merged")
    _git(local, "checkout", "main")

    _git(seed, "checkout", "main")
    _git(seed, "merge", "--no-ff", "feature/remote-merged", "-m", "merge")
    _git(seed, "push", "origin", "main")

    result = evaluate(apply=True, cwd=local)

    assert result["overall"] == "ok", result
    assert _git(local, "branch", "--list", "feature/remote-merged") == ""


def test_apply_deletes_against_fetched_base_when_upstream_gone(tmp_path: Path) -> None:
    """After fetch --prune, local main may lag while origin/<feat> is gone."""
    bare = tmp_path / "origin.git"
    bare.mkdir()
    _git(bare, "init", "--bare")
    seed_parent = tmp_path / "seed-parent"
    seed_parent.mkdir()
    seed = _init_repo(seed_parent)
    _git(seed, "remote", "add", "origin", str(bare))
    _git(seed, "push", "-u", "origin", "main")
    _git(seed, "checkout", "-b", "feature/pruned-upstream")
    (seed / "feature.txt").write_text("x\n", encoding="utf-8")
    _git(seed, "add", "feature.txt")
    _git(seed, "commit", "-m", "feature")
    _git(seed, "push", "-u", "origin", "feature/pruned-upstream")

    local = tmp_path / "local"
    _git(tmp_path, "clone", str(bare), str(local))
    _git(local, "config", "user.email", "test@example.com")
    _git(local, "config", "user.name", "Test")
    _git(
        local,
        "checkout",
        "-b",
        "feature/pruned-upstream",
        "origin/feature/pruned-upstream",
    )
    _git(local, "checkout", "main")

    _git(seed, "checkout", "main")
    _git(seed, "merge", "--no-ff", "feature/pruned-upstream", "-m", "merge")
    _git(seed, "push", "origin", "main")
    _git(seed, "push", "origin", "--delete", "feature/pruned-upstream")

    result = evaluate(apply=True, cwd=local)

    assert result["overall"] == "ok", result
    assert any(
        action.get("action") == "git branch -D feature/pruned-upstream"
        and action.get("ok") is True
        for action in result["actions"]
    )
    assert _git(local, "branch", "--list", "feature/pruned-upstream") == ""


def test_squash_merged_pr_head_is_cleanup_residue(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo(tmp_path)
    _git(repo, "checkout", "-b", "feature/squashed")
    (repo / "feature.txt").write_text("x\n", encoding="utf-8")
    _git(repo, "add", "feature.txt")
    _git(repo, "commit", "-m", "feature")
    head = _git(repo, "rev-parse", "HEAD")
    _git(repo, "checkout", "main")
    _git(repo, "merge", "--squash", "feature/squashed")
    _git(repo, "commit", "-m", "squash feature")

    monkeypatch.setattr(
        post_merge_cleanup,
        "_merged_pr_heads",
        lambda cwd, base_branch, candidates=None: {("feature/squashed", head)},
    )

    result = evaluate(apply=False, cwd=repo)

    assert "feature/squashed" in result["residue"]["merged_local_branches"]
    assert result["residue"]["squash_merged_local_branches"] == [
        "feature/squashed"
    ]

    applied = evaluate(apply=True, cwd=repo)

    assert applied["overall"] == "ok", applied
    assert _git(repo, "branch", "--list", "feature/squashed") == ""


def test_remote_prune_probe_failure_is_fail_closed(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _git(repo, "remote", "add", "origin", str(tmp_path / "missing.git"))

    result = evaluate(apply=False, cwd=repo)

    assert result["overall"] == "error"
    assert any("remote prune" in error for error in result["errors"])


def test_github_setting_query_uses_selected_cwd(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo(tmp_path)
    observed: dict[str, Path] = {}

    def fake_run(args, *, cwd=post_merge_cleanup.ROOT, allow_failure=False):
        observed["cwd"] = cwd
        return subprocess.CompletedProcess(args, 0, stdout="true\n", stderr="")

    monkeypatch.setattr(post_merge_cleanup, "_run", fake_run)

    result = post_merge_cleanup._delete_branch_on_merge_setting(repo)

    assert observed["cwd"] == repo
    assert result["enabled"] is True


def test_squash_probe_accepts_only_resolved_default_base(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _init_repo(tmp_path)
    _git(
        repo,
        "remote",
        "add",
        "origin",
        "https://github.com/nexus-ai-2045/fractal-decision-ecosystem.git",
    )
    oid = "a" * 40
    original_run = post_merge_cleanup._run

    def fake_run(args, **kwargs):
        if args[:3] == ["gh", "pr", "list"]:
            head = args[args.index("--head") + 1]
            return subprocess.CompletedProcess(
                args,
                0,
                stdout=(
                    "["
                    f'{{"headRefName":"{head}","headRefOid":"{oid}",'
                    '"baseRefName":"main"}'
                    "]"
                    if head == "feature/default"
                    else "[]"
                ),
                stderr="",
            )
        return original_run(args, **kwargs)

    monkeypatch.setattr(post_merge_cleanup, "_run", fake_run)

    heads = post_merge_cleanup._merged_pr_heads(
        repo,
        "main",
        [
            ("feature/default", oid),
            ("feature/release", oid),
        ],
    )

    assert heads == {("feature/default", oid)}


def test_squash_probe_binds_query_to_verified_origin_repo(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _init_repo(tmp_path)
    _git(
        repo,
        "remote",
        "add",
        "origin",
        "git@github.com:nexus-ai-2045/fractal-decision-ecosystem.git",
    )
    observed: list[str] = []
    original_run = post_merge_cleanup._run
    oid = "b" * 40

    def fake_run(args, **kwargs):
        if args[:3] == ["gh", "pr", "list"]:
            observed.extend(args)
            return subprocess.CompletedProcess(args, 0, stdout="[]", stderr="")
        return original_run(args, **kwargs)

    monkeypatch.setattr(post_merge_cleanup, "_run", fake_run)

    assert (
        post_merge_cleanup._merged_pr_heads(
            repo, "main", [("feature/candidate", oid)]
        )
        == set()
    )
    assert observed[observed.index("--repo") + 1] == (
        "nexus-ai-2045/fractal-decision-ecosystem"
    )
    assert observed[observed.index("--head") + 1] == "feature/candidate"
    assert "--limit" not in observed


def test_unavailable_squash_probe_is_non_fatal(tmp_path: Path, monkeypatch) -> None:
    repo = _init_repo(tmp_path)
    _git(repo, "checkout", "-b", "feature/unmerged")
    (repo / "feature.txt").write_text("x\n", encoding="utf-8")
    _git(repo, "add", "feature.txt")
    _git(repo, "commit", "-m", "feature")
    _git(repo, "checkout", "main")
    _git(
        repo,
        "remote",
        "add",
        "origin",
        "https://github.com/nexus-ai-2045/fractal-decision-ecosystem.git",
    )
    _git(repo, "update-ref", "refs/remotes/origin/main", "main")

    original_run = post_merge_cleanup._run

    def fake_run(args, **kwargs):
        if args[:3] == ["gh", "pr", "list"]:
            return subprocess.CompletedProcess(
                args, 127, stdout="", stderr="command executable unavailable"
            )
        return original_run(args, **kwargs)

    monkeypatch.setattr(post_merge_cleanup, "_run", fake_run)

    result = evaluate(apply=False, cwd=repo)

    assert result["overall"] == "ok", result
    assert result["residue"]["merged_local_branches"] == []
    assert result["residue"]["squash_merged_local_branches"] == []


def test_squash_probe_queries_each_candidate_without_global_limit(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _init_repo(tmp_path)
    _git(
        repo,
        "remote",
        "add",
        "origin",
        "https://github.com/nexus-ai-2045/fractal-decision-ecosystem.git",
    )
    oid_a = "a" * 40
    oid_b = "b" * 40
    seen_heads: list[str] = []
    original_run = post_merge_cleanup._run

    def fake_run(args, **kwargs):
        if args[:3] == ["gh", "pr", "list"]:
            assert "--limit" not in args
            head = args[args.index("--head") + 1]
            seen_heads.append(head)
            oid = oid_a if head == "feature/a" else oid_b
            return subprocess.CompletedProcess(
                args,
                0,
                stdout=(
                    f'[{{"headRefName":"{head}","headRefOid":"{oid}",'
                    '"baseRefName":"main"}]'
                ),
                stderr="",
            )
        return original_run(args, **kwargs)

    monkeypatch.setattr(post_merge_cleanup, "_run", fake_run)

    heads = post_merge_cleanup._merged_pr_heads(
        repo,
        "main",
        [("feature/a", oid_a), ("feature/b", oid_b)],
    )

    assert seen_heads == ["feature/a", "feature/b"]
    assert heads == {("feature/a", oid_a), ("feature/b", oid_b)}


def test_skipped_actions_do_not_count_as_external_on_error(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _init_repo(tmp_path)

    def boom(*_args, **_kwargs):
        raise RuntimeError("no resolvable base ref")

    monkeypatch.setattr(post_merge_cleanup, "_resolve_base_ref", boom)

    result = evaluate(apply=True, cwd=repo)

    assert result["overall"] == "error"
    assert result["actions"]
    assert all(
        str(action.get("detail") or "").startswith("skipped:")
        for action in result["actions"]
    )
    assert result["external_actions_performed"] is False


def test_github_repo_parse_tolerates_tokenized_https_remote(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _git(
        repo,
        "remote",
        "add",
        "origin",
        "https://x-access-token:ghs_exampletokenvalue1234567890@github.com/"
        "nexus-ai-2045/fractal-decision-ecosystem.git",
    )

    assert (
        post_merge_cleanup._github_repo_from_origin(repo)
        == "nexus-ai-2045/fractal-decision-ecosystem"
    )
