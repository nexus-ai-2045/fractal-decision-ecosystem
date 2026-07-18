from __future__ import annotations

import subprocess
from pathlib import Path

from scripts.post_merge_cleanup import evaluate


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
