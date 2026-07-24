from __future__ import annotations

import subprocess
from pathlib import Path

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
