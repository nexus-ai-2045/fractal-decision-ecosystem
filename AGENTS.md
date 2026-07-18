# Repository Safety Rules

## Human Review And Publication

Human review is required before anything in this repository is treated as ready for public release, debut, launch, announcement, submission, posting, or broad sharing.

Do not publish, release, announce, submit, post, share broadly, or otherwise make work public without explicit human review and explicit user approval in the current conversation.

Do not treat broad phrases such as "publish", "share", "post progress", "put it on GitHub", "make it public", or similar wording as permission to skip human review.

Before any public-facing action, clearly state what would become visible, what review has or has not happened, and wait for a clear yes from the user.

## GitHub Repository Visibility

Repository visibility changes are destructive/publication actions.

Never make this GitHub repository public through Codex, CLI, API, GitHub connector, Chrome extension, browser automation, or recurring automation without explicit, repository-specific user confirmation in the current conversation.

Before changing this repository to public, state all of the following and wait for a clear yes:

- Target repository in `owner/name` form.
- Exact operation, such as `gh repo edit owner/name --visibility public`.
- Confirmation that README, license, SECURITY.md, secret scan, personal path scan, and PUBLIC_READY.md have been checked.
- Reminder that commit history and files become visible on the web.

Never create a public GitHub repository by default. New repositories must be private unless the user explicitly says the exact repository should be public.

Never run automation that changes repository visibility. Automations may report visibility and readiness status only.

## 開発環境セットアップと実行

この節は特定の AI ツールに依存しない共通の起動・実行メモです。`AGENTS.md` を参照するすべての AI エージェントおよび人間の開発者を対象とします。

FDE（Fractal Decision Ecosystem）は Python + Markdown による AI ガバナンス「control plane」です。常駐サーバー・DB・Web バックエンドはありません。開発準備 = pytest スイートと集約ガバナンスゲートの実行です。依存は `pytest` + `jsonschema` のみ（`requirements-dev.txt`）で、`pip install -r requirements-dev.txt` で導入します。Python 3.11+ が必要です。

- テスト: `python3 -m pytest -q`（config は `pyproject.toml`、`pythonpath=["."]`）。
- 集約ゲート（コアの end-to-end チェック、クロスプラットフォーム）: `python3 -m scripts.mvp_gate_check`（`--json` で機械可読出力、`--skip-pytest` でテスト省略）。全サブゲート + pytest を実行し、各チェックの OK/FAIL を出力します。
- 正本ラッパー `scripts/run_mvp_gate.ps1` は PowerShell（`pwsh`）を必要とします。`pwsh` が無い環境では不要で、`python3 -m scripts.mvp_gate_check` を代替として使います。
- 専用リンターは未設定です。「verify」層はゲートスクリプトが担い、コードリンターではありません。Python 構文チェックが必要なら `python3 -m compileall scripts tests`。
- 複数のゲートが `git ls-files`/diff を実行するため、実行時は git working tree をクリーンに保ちます（未追跡の必須ファイルは `required_files_tracked` に引っかかります）。
- 視覚エントリポイント: `visual.html` は静的ファイルです。プレビューはリポジトリを配信して（例: `python3 -m http.server 8099`）`http://localhost:8099/visual.html` を開きます。
- 環境によって `pip install` は `--user` install になり、`pytest` の console script が PATH 外（`~/.local/bin`）に入ることがあります。その場合は `pytest` ではなく `python3 -m pytest` で起動します。
