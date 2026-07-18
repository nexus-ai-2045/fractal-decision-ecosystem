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

## Verification

- `python3 -m pytest -q tests/test_post_merge_cleanup.py`
- `python3 scripts/post_merge_cleanup.py --json`
