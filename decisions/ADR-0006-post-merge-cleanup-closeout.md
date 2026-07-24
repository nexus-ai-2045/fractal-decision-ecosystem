# ADR-0006: Post-merge cleanup を closeout 実行へ蒸留する

Status: accepted  
Date: 2026-07-18

## Context

マージ後の branch / remote-tracking / worktree 掃除が skill や記憶に依存しており、再発した。検査（`fde_operational_closeout.py` の worktree clean）はあったが、掃除の実行正本がなかった。GitHub の `delete_branch_on_merge` も off のままだった。

## Decision

1. 実行正本は `scripts/post_merge_cleanup.py` とする（check / `--apply`）。
2. skill は手順説明に留め、発火保証に使わない。
3. Claude Code Hook は任意の補助（PostToolUse で同 script を呼ぶ）に留め、正本にはしない。
4. `fde_operational_closeout.py` は cleanup receipt を常に記録し、`--run-post-merge-cleanup` / `--require-post-merge-cleanup` の時だけ fail-closed にする。
5. remote head 自動削除は GitHub 設定 `delete_branch_on_merge=true` を正とする（repo admin 操作）。

## Consequences

- merge 後の標準 closeout:
  - `python3 scripts/post_merge_cleanup.py --apply --json`
  - `python3 scripts/fde_operational_closeout.py --json --require-delivery-ready --require-post-merge-cleanup`
- または closeout 一発: `--run-post-merge-cleanup`
- GitHub 設定変更権限が無い agent は設定を推奨するだけで、local prune は実行できる。
- 手順 skill は `docs/superpowers/skills/post-merge-cleanup.md`。発火保証は script / CI test。

## Incident absorb (2026-07-18)

CI Public Ready が pytest error になった。原因は PR checkout に local `main` が無く、`git branch --merged main` が `malformed object name main` で例外化し、closeout 経由テストが落ちたこと。

再発防止:

1. base ref は resolvable ref（local main → `origin/main`）へ解決する。
2. evaluate は例外を JSON fail-closed で返す。
3. `test_ci_checkout_without_local_main_uses_origin_main` で CI 形を固定する。
4. skill に「bare main 前提禁止」を書く。

## Verification

- `python3 -m pytest -q tests/test_post_merge_cleanup.py`
- `python3 scripts/post_merge_cleanup.py --json`
- CI `Public Ready` green
