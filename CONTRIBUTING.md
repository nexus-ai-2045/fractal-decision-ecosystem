# コントリビューション

## セットアップ

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Windows では MVP gate も使えます。

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mvp_gate.ps1 --json
```

## 開発ルール

- 既定は read-only。公開・push・merge・visibility 変更・外部送信は実装しない。
- `unknown` や tool failure を pass へ丸めない。
- secret 本文を test output や report へ残さない。
- Windows / macOS / Linux の path 表現を考慮する。
- 挙動変更は失敗する test を先に追加する（TDD）。
- 人間が読む本文は日本語、identifier / schema field / file name は英語を維持する。
- commit 名義は公開 package では `nexus_ai <273569186+nexus-ai-2045@users.noreply.github.com>` を使う。

## 変更の切り方

| 種類 | 置き場 |
|---|---|
| workflow 契約 | `fde_workflow.yaml` + `scripts/fde_workflow_check.py` |
| feedback 契約 | `schemas/fde_feedback_packet.v1.schema.json` + `scripts/fde_feedback_packet.py` |
| 概念の詳細 | `docs/fde-concept-guide.md`（README は入口のみ） |
| 運用保証 | `OPERATIONAL_GUARANTEE.md` / closeout scripts |

PR は小さく保ち、検証コマンドと結果を本文に書いてください。
