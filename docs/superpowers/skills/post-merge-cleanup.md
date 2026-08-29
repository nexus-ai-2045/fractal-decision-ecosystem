# Skill: Post-merge cleanup

## When

PR を merge した直後、または CI / closeout が `post_merge_cleanup` residue / crash を返した時。

## Do not

- 「branch 消しておいて」を記憶や skill 文だけで閉じない。
- bare `main` が local にある前提で `git branch --merged main` を直書きしない。
- Hook だけで保証した気にならない（Claude 経由 merge 以外では発火しない）。

## Authority

実行正本: `scripts/post_merge_cleanup.py`

```bash
python3 scripts/post_merge_cleanup.py --apply --json
python3 scripts/fde_operational_closeout.py --json --require-delivery-ready --require-post-merge-cleanup
```

または:

```bash
python3 scripts/fde_operational_closeout.py --json --run-post-merge-cleanup
```

## Hard rules absorbed from incident 2026-07-18

1. base ref は **resolvable ref** を使う。default branch 名は `origin/HEAD` から取り、次を選ぶ:
   - local head（`refs/heads/<name>`）が存在し、remote tip より遅れてもいないとき → local
   - remote tip（`refs/remotes/origin/<name>`）が local より厳密に先行しているとき → remote
   - local が無い CI PR checkout → `origin/main` 等へ fallback
2. GitHub Actions の PR checkout は local `main` が無いことが多い。`origin/main` へ fallback 必須。
3. cleanup は JSON fail-closed。例外で pytest / MVP gate を落とさない。
4. squash 検出の `gh` probe は補助。欠落 / 未認証でも ancestry merge 検出を落とさない。
5. remote head 自動削除は GitHub `delete_branch_on_merge`（admin 設定）。script は local / tracking 掃除担当。

## Done when

- `post_merge_cleanup.py --json` が `overall: ok`
- closeout に `checks.post_merge_cleanup` があり、require 時も ok
- CI Public Ready が green
- GitHub `delete_branch_on_merge` が on（人間設定。off なら receipt に recommended_human_action）

## Regression gate

- `tests/test_post_merge_cleanup.py::test_ci_checkout_without_local_main_uses_origin_main`
