from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def test_repository_has_no_privileged_pr_merge_workflow() -> None:
    """PR headから変更可能なcheckを根拠にGITHUB_TOKENでmergeさせない。"""

    offenders: list[str] = []
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        text = path.read_text(encoding="utf-8")
        if "gh pr merge" in text or "/merge" in text or "--match-head-commit" in text:
            offenders.append(path.name)

    assert offenders == [], f"privileged PR merge automation is forbidden: {offenders}"


def test_operational_guarantee_keeps_exact_head_manual_merge_boundary() -> None:
    text = (ROOT / "OPERATIONAL_GUARANTEE.md").read_text(encoding="utf-8")
    required = (
        "gh pr merge --match-head-commit",
        "GitHub Actions の `GITHUB_TOKEN` で merge しない",
        "head SHA",
        "人間",
    )
    missing = [term for term in required if term not in text]
    assert missing == [], f"manual merge boundary is incomplete: {missing}"
