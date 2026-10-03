import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
EXPECTED_WORKFLOW_SHA256 = {
    "conventional-pr-title.yml": "a97c336f8df35de4d4b3765280da1392e65047d8debab40075d90d234277efdf",
    "pr-hygiene.yml": "fc114ad2fdf7845343c1a821f03730e11138a873474fa46ea9cefc88179d54e7",
    "public-ready.yml": "e72e48a0c894db97ca64ec68b0a7f3bc7551188581c67064f35bf519512262e6",
    "release-please.yml": "1ef6fbd55c93aeddf72eecb7d6c57837f3886f85652c2c00663fec530b510cde",
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
