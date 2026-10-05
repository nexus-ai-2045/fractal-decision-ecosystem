import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
EXPECTED_WORKFLOW_SHA256 = {
    "conventional-pr-title.yml": "a97c336f8df35de4d4b3765280da1392e65047d8debab40075d90d234277efdf",
    "pr-hygiene.yml": "7c871a1b7cf1d8acb3ea02cc7de1c927bc68983d2ecf8c1eb0735ecdc76728f1",
    "public-ready.yml": "c80e1745070cac06ae17a60175637559d0df1d3c8c2136f37a2182caa5dc0380",
    "release-please.yml": "dc0451a6353283a7fb1a0b8d3a43ccd667d2a7693b168863e68bef281370f5c7",
}


def test_repository_has_no_privileged_pr_merge_workflow() -> None:
    """許可済みworkflow集合と内容を固定し、別表現のmerge再導入も止める。"""

    paths = {path.name: path for path in WORKFLOWS.glob("*.y*ml")}
    assert set(paths) == set(EXPECTED_WORKFLOW_SHA256), (
        "workflow allowlist changed; review permissions, triggers, and merge capability before "
        "updating this ratchet"
    )

    actual = {
        name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in paths.items()
    }
    assert actual == EXPECTED_WORKFLOW_SHA256, (
        "workflow content changed; review the complete trusted workflow diff before updating hashes"
    )


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
