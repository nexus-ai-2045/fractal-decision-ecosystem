#!/usr/bin/env python3
"""Post-merge cleanup: prune stale refs, delete merged local branches, prune worktrees.

This is the executable closeout step for merge residue. Skill/docs explain the
procedure; this script is the authority that can actually clean.

Default mode is check-only (no mutation). Pass --apply to perform cleanup.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTECTED_BRANCH_PATTERNS = (
    re.compile(r"^main$"),
    re.compile(r"^master$"),
    re.compile(r"^release-please"),
    re.compile(r"^cursor/setup-dev-environment"),
)
SECRET_PATTERNS = (
    re.compile(r"\b(?:ghp|gho|github_pat)_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"(?i)\b(Authorization:\s*(?:Bearer|token)\s+)[^\s]+"),
)
USER_PATH_PATTERNS = (
    re.compile(r"([A-Za-z]:[\\/]+Users[\\/]+)[^\\/\s]+"),
    re.compile(r"(/Users/)[^/\s]+"),
    re.compile(r"(/home/)[^/\s]+"),
)


def _sanitize_receipt_detail(value: object) -> str | None:
    if value is None:
        return None

    text = str(value)
    if not text:
        return None

    for pattern in SECRET_PATTERNS:
        text = pattern.sub(
            lambda match: (
                f"{match.group(1)}<redacted-token>"
                if match.lastindex
                else "<redacted-token>"
            ),
            text,
        )
    for pattern in USER_PATH_PATTERNS:
        text = pattern.sub(r"\1<user>", text)
    return text


def _run(
    args: list[str],
    *,
    cwd: Path = ROOT,
    allow_failure: bool = False,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=cwd,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0 and not allow_failure:
        detail = result.stderr.strip() or result.stdout.strip() or "no error output"
        raise RuntimeError(f"{' '.join(args)} failed: {detail}")
    return result


def _git(args: list[str], *, cwd: Path = ROOT, allow_failure: bool = False) -> str:
    return _run(["git", *args], cwd=cwd, allow_failure=allow_failure).stdout.strip()


def _is_protected(branch: str) -> bool:
    return any(pattern.search(branch) for pattern in PROTECTED_BRANCH_PATTERNS)


def _ref_exists(cwd: Path, ref: str) -> bool:
    result = _run(
        ["git", "show-ref", "--verify", "--quiet", ref],
        cwd=cwd,
        allow_failure=True,
    )
    return result.returncode == 0


def _resolve_base_ref(cwd: Path) -> str:
    """Return a resolvable merge-base ref for CI and local checkouts.

    GitHub Actions PR checkouts often have only the feature branch locally and
    `origin/main` as a remote-tracking ref. Using bare `main` then makes
    `git branch --merged main` fail with `malformed object name main`.
    """
    for candidate in (
        "refs/heads/main",
        "refs/heads/master",
        "refs/remotes/origin/main",
        "refs/remotes/origin/master",
    ):
        if _ref_exists(cwd, candidate):
            return candidate

    symbolic = _git(
        ["symbolic-ref", "refs/remotes/origin/HEAD"],
        cwd=cwd,
        allow_failure=True,
    )
    if symbolic and _ref_exists(cwd, symbolic):
        return symbolic

    raise RuntimeError(
        "no resolvable base ref "
        "(tried local main/master and origin/main|master); "
        "CI must checkout with fetch-depth that includes the base branch tip"
    )


def _short_ref_name(ref: str) -> str:
    for prefix in (
        "refs/heads/",
        "refs/remotes/origin/",
        "refs/remotes/",
    ):
        if ref.startswith(prefix):
            return ref[len(prefix) :]
    return ref


def _merged_local_branches(cwd: Path, base_ref: str, current: str) -> list[str]:
    result = _run(
        ["git", "branch", "--format=%(refname:short)", "--merged", base_ref],
        cwd=cwd,
        allow_failure=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown git error"
        raise RuntimeError(
            f"git branch --merged {base_ref} failed: {detail}"
        )
    base_short = _short_ref_name(base_ref)
    branches: list[str] = []
    for line in result.stdout.splitlines():
        name = line.strip()
        if (
            not name
            or name == current
            or name == base_short
            or name == base_ref
            or _is_protected(name)
        ):
            continue
        branches.append(name)
    return branches


def _stale_remote_refs(cwd: Path) -> list[str]:
    result = _run(
        ["git", "remote", "prune", "origin", "--dry-run"],
        cwd=cwd,
        allow_failure=True,
    )
    if result.returncode != 0:
        return []
    stale: list[str] = []
    for line in result.stdout.splitlines():
        # e.g. * [would prune] origin/cursor/foo
        if "prune" in line.lower() and "origin/" in line:
            ref = line.rsplit("origin/", 1)[-1].strip()
            if ref:
                stale.append(f"origin/{ref}")
    return stale


def _pruneable_worktrees(cwd: Path) -> list[str]:
    result = _run(["git", "worktree", "list", "--porcelain"], cwd=cwd, allow_failure=True)
    if result.returncode != 0:
        return []
    pruneable: list[str] = []
    current_path: str | None = None
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            current_path = line[len("worktree ") :].strip()
        elif line.startswith("prunable") and current_path:
            pruneable.append(current_path)
            current_path = None
        elif line == "":
            current_path = None
    return pruneable


def _delete_branch_on_merge_setting() -> dict[str, object]:
    result = _run(
        [
            "gh",
            "api",
            "repos/{owner}/{repo}",
            "--jq",
            ".delete_branch_on_merge",
        ],
        allow_failure=True,
    )
    if result.returncode != 0:
        return {
            "checked": False,
            "enabled": None,
            "status": "unavailable",
            "detail": _sanitize_receipt_detail(
                (result.stderr or result.stdout).strip() or "gh api unavailable"
            ),
        }
    value = result.stdout.strip().lower()
    enabled = value == "true"
    return {
        "checked": True,
        "enabled": enabled,
        "status": "ok" if enabled else "disabled",
        "detail": None if enabled else "GitHub Automatically delete head branches is off",
    }


def evaluate(*, apply: bool = False, cwd: Path | None = None) -> dict[str, object]:
    root = cwd or ROOT
    errors: list[str] = []
    actions: list[dict[str, object]] = []

    try:
        return _evaluate_body(apply=apply, root=root, errors=errors, actions=actions)
    except Exception as exc:  # fail-closed JSON, never crash closeout/CI
        return {
            "overall": "error",
            "external_actions_performed": False,
            "apply": apply,
            "errors": [f"{type(exc).__name__}: {exc}"],
            "residue": {
                "merged_local_branches": [],
                "stale_remote_refs": [],
                "pruneable_worktrees": [],
            },
            "actions": actions,
            "github_delete_branch_on_merge": {
                "checked": False,
                "enabled": None,
                "status": "unavailable",
            },
            "base_branch": None,
            "current_branch": None,
            "recommended_human_action": None,
        }


def _evaluate_body(
    *,
    apply: bool,
    root: Path,
    errors: list[str],
    actions: list[dict[str, object]],
) -> dict[str, object]:
    current = _git(["branch", "--show-current"], cwd=root) or "HEAD"
    base_ref = _resolve_base_ref(root)
    base = _short_ref_name(base_ref)

    merged = _merged_local_branches(root, base_ref, current)
    stale = _stale_remote_refs(root)
    pruneable = _pruneable_worktrees(root)
    github_setting = _delete_branch_on_merge_setting()

    if apply:
        remotes = {
            line.strip()
            for line in _git(["remote"], cwd=root, allow_failure=True).splitlines()
            if line.strip()
        }
        if "origin" in remotes:
            fetch = _run(
                ["git", "fetch", "--prune", "origin"],
                cwd=root,
                allow_failure=True,
            )
            actions.append(
                {
                    "action": "git fetch --prune origin",
                    "ok": fetch.returncode == 0,
                    "detail": _sanitize_receipt_detail(
                        (fetch.stderr or fetch.stdout).strip() or None
                    ),
                }
            )
            if fetch.returncode != 0:
                errors.append("git fetch --prune origin failed")
            else:
                stale_after_fetch = _stale_remote_refs(root)
                if stale and not stale_after_fetch:
                    actions.append(
                        {
                            "action": "prune stale remote-tracking refs",
                            "ok": True,
                            "removed": stale,
                        }
                    )
                stale = stale_after_fetch
        else:
            actions.append(
                {
                    "action": "git fetch --prune origin",
                    "ok": True,
                    "detail": "skipped: origin remote not configured",
                }
            )

        for branch in list(merged):
            delete = _run(
                ["git", "branch", "-d", branch],
                cwd=root,
                allow_failure=True,
            )
            ok = delete.returncode == 0
            actions.append(
                {
                    "action": f"git branch -d {branch}",
                    "ok": ok,
                    "detail": _sanitize_receipt_detail(
                        (delete.stderr or delete.stdout).strip() or None
                    ),
                }
            )
            if ok:
                merged.remove(branch)
            else:
                errors.append(f"failed to delete merged local branch: {branch}")

        wt = _run(["git", "worktree", "prune", "-v"], cwd=root, allow_failure=True)
        actions.append(
            {
                "action": "git worktree prune",
                "ok": wt.returncode == 0,
                "detail": _sanitize_receipt_detail(
                    (wt.stderr or wt.stdout).strip() or None
                ),
            }
        )
        if wt.returncode != 0:
            errors.append("git worktree prune failed")
        else:
            pruneable = _pruneable_worktrees(root)

    residue = {
        "merged_local_branches": merged,
        "stale_remote_refs": stale,
        "pruneable_worktrees": pruneable,
    }
    has_local_residue = bool(merged or stale or pruneable)
    if has_local_residue:
        errors.append("post-merge cleanup residue remains")
    if github_setting.get("checked") and github_setting.get("enabled") is False:
        # Platform gap: warn in receipt, do not fail local cleanup overall by itself
        # when only the GitHub setting is off. Callers can treat status separately.
        pass

    overall = "ok" if not errors else "error"
    return {
        "overall": overall,
        "external_actions_performed": bool(apply),
        "apply": apply,
        "base_branch": base,
        "base_ref": base_ref,
        "current_branch": current,
        "errors": errors,
        "residue": residue,
        "actions": actions,
        "github_delete_branch_on_merge": github_setting,
        "recommended_human_action": (
            None
            if github_setting.get("enabled")
            else "Enable GitHub Automatically delete head branches "
            "(Settings → General → Pull Requests), or: "
            "gh api -X PATCH repos/{owner}/{repo} -f delete_branch_on_merge=true"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Perform fetch --prune, delete merged local branches, and worktree prune.",
    )
    parser.add_argument(
        "--cwd",
        type=Path,
        help="Repository root to clean (default: this package root).",
    )
    args = parser.parse_args()
    result = evaluate(apply=args.apply, cwd=args.cwd)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        mode = "APPLY" if args.apply else "CHECK"
        print(f"POST-MERGE CLEANUP {mode} {result['overall'].upper()}")
        residue = result["residue"]
        print(f"merged_local_branches: {residue['merged_local_branches']}")
        print(f"stale_remote_refs: {residue['stale_remote_refs']}")
        print(f"pruneable_worktrees: {residue['pruneable_worktrees']}")
        setting = result["github_delete_branch_on_merge"]
        print(f"github_delete_branch_on_merge: {setting.get('status')}")
        for error in result["errors"]:
            print(f"- {error}")
        if result.get("recommended_human_action"):
            print(f"human_action: {result['recommended_human_action']}")
    return 0 if result["overall"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
