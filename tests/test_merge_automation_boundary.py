import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
EXPECTED_WORKFLOW_SHA256 = {
    "conventional-pr-title.yml": "a97c336f8df35de4d4b3765280da1392e65047d8debab40075d90d234277efdf",
    "pr-hygiene.yml": "ae42313567dc97e2fc83c6daee0ea968ff13de5e18b096959ac184d674350361",
    "public-ready.yml": "5750182687457fdf79fbf22ab3f95a314d946355b067b919bfca388b8ec3c05d",
    "release-please.yml": "45c54c009508d8d295cf070cce051da3768dbdd16b2657eb6a8b6e899fcb3b77",
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
