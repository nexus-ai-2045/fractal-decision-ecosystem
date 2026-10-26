import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
EXPECTED_WORKFLOW_SHA256 = {
    "base-guard.yml": "7155de21a9b14a5e5c3753c2c43fbf0babdfd7da84dda956bb962ece218736c4",
    "conventional-pr-title.yml": "a97c336f8df35de4d4b3765280da1392e65047d8debab40075d90d234277efdf",
    "preflight.yml": "55d6a9d1bf542459916d2b319c0e75623d44b467b3f2303499a9075f2fedd90f",
    "pr-hygiene.yml": "7c871a1b7cf1d8acb3ea02cc7de1c927bc68983d2ecf8c1eb0735ecdc76728f1",
    "public-ready.yml": "c996cd84ff38bb1d9b9fe336701b081089bc996e4c950b31fb15f6e22a3d45e0",
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
