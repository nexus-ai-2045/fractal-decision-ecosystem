#!/usr/bin/env python3
"""Post-merge cleanup: prune stale refs, delete merged local branches, prune worktrees.

This is the executable closeout step for merge residue. Skill/docs explain the
procedure; this script is the authority that can actually clean.

Default mode is check-only (no mutation). Pass --apply to perform cleanup.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NETWORK_TIMEOUT_SECONDS = 15
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
    re.compile(r"(/" + r"Users/)[^/\s]+"),
    re.compile(r"(/" + r"home/)[^/\s]+"),
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
    environment = os.environ.copy()
    environment.pop("GH_REPO", None)
    environment["GIT_TERMINAL_PROMPT"] = "0"
    environment["GH_PROMPT_DISABLED"] = "1"
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            timeout=NETWORK_TIMEOUT_SECONDS,
            env=environment,
            check=False,
        )
    except FileNotFoundError:
        result = subprocess.CompletedProcess(
            args, 127, stdout="", stderr="command executable unavailable"
        )
    except subprocess.TimeoutExpired:
        result = subprocess.CompletedProcess(
            args, 124, stdout="", stderr="command timed out"
        )
    if result.returncode != 0 and not allow_failure:
        raise RuntimeError(_failure_summary(" ".join(args), result))
    return result


def _failure_summary(
    operation: str, result: subprocess.CompletedProcess[str]
) -> str:
    """Return bounded metadata without persisting child stdout or stderr."""
    return f"{operation} failed (exit {result.returncode})"


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


def _is_ancestor(cwd: Path, maybe_ancestor: str, maybe_descendant: str) -> bool:
    result = _run(
        ["git", "merge-base", "--is-ancestor", maybe_ancestor, maybe_descendant],
        cwd=cwd,
        allow_failure=True,
    )
    return result.returncode == 0


def _default_branch_name(cwd: Path) -> str | None:
    symbolic = _git(
        ["symbolic-ref", "refs/remotes/origin/HEAD"],
        cwd=cwd,
        allow_failure=True,
    )
    if symbolic and _ref_exists(cwd, symbolic):
        return _short_ref_name(symbolic)
    for name in ("main", "master"):
        if _ref_exists(cwd, f"refs/heads/{name}") or _ref_exists(
            cwd, f"refs/remotes/origin/{name}"
        ):
            return name
    return None


def _resolve_base_ref(cwd: Path) -> str:
    """Return a resolvable merge-base ref for CI and local checkouts.

    Prefer the local default-branch head when it exists and is not behind its
    remote-tracking tip. When the remote tip is strictly ahead (common after
    `fetch --prune` while local main lags), use the remote tip so merge proof
    matches the fetched base. GitHub Actions PR checkouts often lack local
    main and must fall back to `refs/remotes/origin/main`.
    """
    name = _default_branch_name(cwd)
    if name is None:
        raise RuntimeError(
            "no resolvable base ref "
            "(tried local main/master and origin/main|master); "
            "CI must checkout with fetch-depth that includes the base branch tip"
        )

    local_ref = f"refs/heads/{name}"
    remote_ref = f"refs/remotes/origin/{name}"
    local_ok = _ref_exists(cwd, local_ref)
    remote_ok = _ref_exists(cwd, remote_ref)

    if local_ok and remote_ok:
        remote_ahead = _is_ancestor(cwd, local_ref, remote_ref) and not _is_ancestor(
            cwd, remote_ref, local_ref
        )
        return remote_ref if remote_ahead else local_ref
    if local_ok:
        return local_ref
    if remote_ok:
        return remote_ref

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


def _remote_names(cwd: Path) -> set[str]:
    result = _run(["git", "remote"], cwd=cwd, allow_failure=True)
    if result.returncode != 0:
        raise RuntimeError(_failure_summary("git remote", result))
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _local_branches(cwd: Path) -> list[tuple[str, str]]:
    result = _run(
        ["git", "for-each-ref", "--format=%(refname:short) %(objectname)", "refs/heads"],
        cwd=cwd,
        allow_failure=True,
    )
    if result.returncode != 0:
        raise RuntimeError(_failure_summary("git for-each-ref refs/heads", result))
    branches: list[tuple[str, str]] = []
    for line in result.stdout.splitlines():
        name, separator, oid = line.strip().partition(" ")
        if separator and re.fullmatch(r"[0-9a-f]{40}", oid):
            branches.append((name, oid))
    return branches


def _github_repo_from_origin(cwd: Path) -> str | None:
    # Prefer the stored remote URL so url.*.insteadOf rewrites (tokenized
    # https remotes in managed agent environments) do not break owner/repo parse.
    remote_url = _git(
        ["config", "--local", "--get", "remote.origin.url"],
        cwd=cwd,
        allow_failure=True,
    )
    if not remote_url:
        remote_url = _git(["remote", "get-url", "origin"], cwd=cwd, allow_failure=True)
    match = re.fullmatch(
        r"(?:https://(?:[^/\s]+@)?github\.com/|git@github\.com:|ssh://git@github\.com/)"
        r"([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?",
        remote_url,
    )
    if not match:
        return None
    return f"{match.group(1)}/{match.group(2)}"


def _merged_pr_heads(
    cwd: Path,
    base_branch: str,
    candidates: list[tuple[str, str]] | None = None,
) -> set[tuple[str, str]]:
    """Return squash-merge evidence for local branch tips.

    Queries each candidate head directly so evidence is not capped by a global
    `--limit`. Missing `gh`, missing credentials, or probe errors are treated as
    "no squash evidence" (empty set) so unauthenticated local/CI checks stay
    usable; ancestry-merge detection remains authoritative without GitHub auth.
    """
    if not candidates:
        return set()
    if "origin" not in _remote_names(cwd):
        return set()
    repo = _github_repo_from_origin(cwd)
    if repo is None:
        return set()

    heads: set[tuple[str, str]] = set()
    for name, oid in candidates:
        result = _run(
            [
                "gh",
                "pr",
                "list",
                "--repo",
                repo,
                "--state",
                "merged",
                "--head",
                name,
                "--base",
                base_branch,
                "--json",
                "headRefName,headRefOid,baseRefName",
            ],
            cwd=cwd,
            allow_failure=True,
        )
        if result.returncode != 0:
            # Unavailable probe must not fail an otherwise clean check.
            continue
        try:
            records = json.loads(result.stdout)
        except json.JSONDecodeError:
            continue
        for record in records if isinstance(records, list) else []:
            if not isinstance(record, dict):
                continue
            record_name = record.get("headRefName")
            record_oid = record.get("headRefOid")
            if (
                record.get("baseRefName") == base_branch
                and record_name == name
                and str(record_oid) == oid
                and re.fullmatch(r"[0-9a-f]{40}", str(record_oid))
            ):
                heads.add((name, oid))
                break
    return heads


def _actions_were_performed(actions: list[dict[str, object]]) -> bool:
    """True when a non-skipped mutating/probe action was recorded."""
    for action in actions:
        detail = action.get("detail")
        if isinstance(detail, str) and detail.startswith("skipped:"):
            continue
        return True
    return False


def _merged_local_branches(cwd: Path, base_ref: str) -> tuple[list[str], set[str]]:
    result = _run(
        ["git", "branch", "--format=%(refname:short)", "--merged", base_ref],
        cwd=cwd,
        allow_failure=True,
    )
    if result.returncode != 0:
        raise RuntimeError(_failure_summary(f"git branch --merged {base_ref}", result))
    base_short = _short_ref_name(base_ref)
    ancestry_merged: set[str] = set()
    for line in result.stdout.splitlines():
        name = line.strip()
        if (
            not name
            or name == base_short
            or name == base_ref
            or _is_protected(name)
        ):
            continue
        ancestry_merged.add(name)

    candidates = [
        (name, oid)
        for name, oid in _local_branches(cwd)
        if name not in ancestry_merged
        and name != base_short
        and name != base_ref
        and not _is_protected(name)
    ]
    merged_pr_heads = (
        _merged_pr_heads(cwd, base_short, candidates) if candidates else set()
    )
    squash_merged = {name for name, oid in candidates if (name, oid) in merged_pr_heads}
    return sorted(ancestry_merged | squash_merged), squash_merged


def _stale_remote_refs(cwd: Path) -> list[str]:
    if "origin" not in _remote_names(cwd):
        return []
    result = _run(
        ["git", "remote", "prune", "origin", "--dry-run"],
        cwd=cwd,
        allow_failure=True,
    )
    if result.returncode != 0:
        raise RuntimeError(_failure_summary("git remote prune origin --dry-run", result))
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
        raise RuntimeError(_failure_summary("git worktree list --porcelain", result))
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


def _delete_branch_on_merge_setting(cwd: Path) -> dict[str, object]:
    result = _run(
        [
            "gh",
            "api",
            "repos/{owner}/{repo}",
            "--jq",
            ".delete_branch_on_merge",
        ],
        cwd=cwd,
        allow_failure=True,
    )
    if result.returncode != 0:
        return {
            "checked": False,
            "enabled": None,
            "status": "unavailable",
            "detail": _failure_summary("gh api delete_branch_on_merge", result),
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
            "external_actions_performed": _actions_were_performed(actions),
            "apply": apply,
            "errors": [f"{type(exc).__name__}: {exc}"],
            "residue": {
                "merged_local_branches": [],
                "squash_merged_local_branches": [],
                "stale_remote_refs": [],
                "pruneable_worktrees": [],
                "checked_out_merged_branch": None,
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
    if apply:
        remotes = _remote_names(root)
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
                    "detail": (
                        None
                        if fetch.returncode == 0
                        else _failure_summary("git fetch --prune origin", fetch)
                    ),
                }
            )
            if fetch.returncode != 0:
                raise RuntimeError("git fetch --prune origin failed")
        else:
            actions.append(
                {
                    "action": "git fetch --prune origin",
                    "ok": True,
                    "detail": "skipped: origin remote not configured",
                }
            )

    current = _git(["branch", "--show-current"], cwd=root) or "HEAD"
    base_ref = _resolve_base_ref(root)
    base = _short_ref_name(base_ref)
    merged, squash_merged = _merged_local_branches(root, base_ref)
    stale = _stale_remote_refs(root)
    pruneable = _pruneable_worktrees(root)
    github_setting = _delete_branch_on_merge_setting(root)
    checked_out_merged_branch = current if current in merged else None

    if apply:
        for branch in list(merged):
            if branch == current:
                errors.append(
                    f"switch to {base} before deleting checked-out merged branch: {branch}"
                )
                continue
            # Merge was already proven against base_ref (ancestry or exact squash
            # head). `git branch -d` only checks HEAD/upstream, so after
            # fetch --prune with a lagging local base and a gone upstream it
            # refuses even when origin/<base> proof succeeded. Use -D with the
            # established proof for both squash and ancestry-merged branches.
            delete = _run(
                ["git", "branch", "-D", branch],
                cwd=root,
                allow_failure=True,
            )
            ok = delete.returncode == 0
            actions.append(
                {
                    "action": f"git branch -D {branch}",
                    "ok": ok,
                    "detail": (
                        None
                        if ok
                        else _failure_summary(f"git branch -D {branch}", delete)
                    ),
                }
            )
            if ok:
                merged.remove(branch)
                squash_merged.discard(branch)
            else:
                errors.append(f"failed to delete merged local branch: {branch}")

        wt = _run(["git", "worktree", "prune", "-v"], cwd=root, allow_failure=True)
        actions.append(
            {
                "action": "git worktree prune",
                "ok": wt.returncode == 0,
                "detail": (
                    None
                    if wt.returncode == 0
                    else _failure_summary("git worktree prune", wt)
                ),
            }
        )
        if wt.returncode != 0:
            errors.append("git worktree prune failed")
        else:
            pruneable = _pruneable_worktrees(root)

    if checked_out_merged_branch and not apply:
        errors.append(
            f"switch to {base} before deleting checked-out merged branch: "
            f"{checked_out_merged_branch}"
        )

    residue = {
        "merged_local_branches": merged,
        "squash_merged_local_branches": sorted(squash_merged),
        "stale_remote_refs": stale,
        "pruneable_worktrees": pruneable,
        "checked_out_merged_branch": checked_out_merged_branch,
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
        "external_actions_performed": _actions_were_performed(actions),
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
