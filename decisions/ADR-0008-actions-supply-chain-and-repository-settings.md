# ADR-0008: GitHub Actions の供給網とリポジトリ設定を repo-preflight の推奨に寄せる

Status: accepted
Date: 2026-10-02

## Context

`repo-preflight` の設定確認（`--intent configure_settings --github-settings-profile solo_public`）で、この repository の GitHub 設定を読み取りだけで測った。推奨との差は 6 項目だった。

- 必須: ワークフローの既定の権限が `write`
- 必須: アクションによる PR の作成・承認が許可されている
- 必須: `main` に有効な `ruleset` が無い
- 推奨: アクションの `SHA` 固定が必須になっていない
- 推奨: 使えるアクションの範囲が「すべて」
- 推奨: 非公開の脆弱性報告が無効

推奨の正本（`repo-preflight` の `references/github-settings.md`、最終見直し 2026-08-24）は、GitHub の公式文書と更新履歴で照合した。32 行のうち古くなった行は 0、追記が要る行は 3 だった。そのまま当てると、この repository では次の 2 つの問題が起きる。

- アクションによる PR の作成を禁止すると、リリース自動化（`release-please`）がリリース用の PR を作れなくなる。
- ワークフローがアクションをタグで参照しているため、`SHA` 固定を先に必須にすると、必須チェックとリリースが起動時に失敗する。

## 脅威モデル

| 項目 | 内容 |
|---|---|
| 誰から | 参照先のタグを差し替えられた第三者のアクション。侵害された、または誤って書かれたワークフロー。外部の脆弱性の報告者（善意だが、公開の場に詳細を書いてしまう） |
| 何を | `main` の中身とリリース（タグ）の完全性。ワークフローに渡る `GITHUB_TOKEN` の権限 |
| どうなると困る | 差し替えられたアクションが `GITHUB_TOKEN` 付きで走り、`main` やリリースを書き換える。脆弱性の詳細が公開の課題として晒される |
| 守らないもの | GitHub そのものの侵害。管理者アカウントの乗っ取り。`Dependabot` が出す更新の中身の安全性（人が差分を見て取り込む）。organization や enterprise の方針 |

## Decision

1. アクションの参照は完全なコミット `SHA` で固定する。版はコメントで残し、更新は `Dependabot`（`github-actions`、毎週）で受け取る。公開前チェック（`scripts/public_ready_check.py`）は、全ワークフローの `uses:` が `SHA` で固定されていることを検査する。
2. 固定を済ませた後で、リポジトリ設定の `sha_pinning_required` を有効にする。
3. 使えるアクションを、`GitHub` 製と `googleapis/release-please-action@*` に絞る（`allowed_actions=selected`）。
4. ワークフローの既定の権限は `read` にする。各ワークフローは必要な権限を自分で宣言する。
5. `main` の必須チェックに `CodeQL` を加える（`pr-body-hygiene`、`public-ready`、`CodeQL`）。
6. 非公開の脆弱性報告を有効にし、有効にした後で `SECURITY.md` に報告の経路を書く。

### 変えないもの

| 設定 | 判断 | 理由 | 見直す条件 |
|---|---|---|---|
| `main` の保護 | 旧来の branch protection を維持し、`ruleset` は作らない | 削除禁止・強制 push 禁止・PR 必須（承認 0）・最新化してから取り込み・会話の解決・管理者にも適用、を満たしている。`ruleset` を作っても `repo-preflight` の判定は解消せず、チェック名の管理が 2 か所になる | `repo-preflight` が旧来の保護を評価できるようになったとき、または `ruleset` 固有の規則が必要になったとき |
| アクションによる PR の作成・承認の許可（`can_approve_pull_request_reviews`） | 許可のまま | この設定は PR の作成も止める。リリース自動化は `GITHUB_TOKEN` でリリース用の PR を作っている。必須の承認数が 0 なので、許可を外しても守れるものが無い | 承認数を 1 以上にするとき、またはリリース自動化を `GitHub App` のトークンへ移すとき |
| リリースの改変禁止（immutable releases） | 今回は見送る | 推奨の正本に無い新しい項目で、リリース自動化と併用できるかが未確認 | 次のリリースで併用を確かめたとき |

## Consequences

- 1 はこの ADR と同じ変更で入る。2〜6 はリポジトリ設定の変更で、管理者の権限で行う。自動のエージェントには設定の変更が許されていないので、エージェントは推奨と正確な操作を示すところまでを担う（ADR-0006 と同じ扱い）。
- PR ごとの検査: 必須チェックで確かめる。`SHA` で固定していない `uses:` は公開前チェックで落ち、新しい重大な `CodeQL` の警告がある PR は取り込めない。
- 定期の見直し: `Dependabot` の毎週の更新を取り込む。`repo-preflight` の推奨の鮮度（90 日）が切れたとき、または設定を変えたときに、`configure_settings` で測り直す。残る差分がこの ADR の「変えないもの」だけであることを確かめる。新しい差分が出たら、この ADR を改める。
- `Dependabot` のアクション更新の PR は、そのままでは必須チェックの `public-ready` で落ちる。`tests/test_merge_automation_boundary.py` がワークフローの中身のハッシュを記録していて、「ワークフローの変更は人が見る」ための歯止めになっているため。歯止めは弱めない。取り込むときは、差分が `uses:` 行（`SHA` と版のコメント）だけであることを見てから、同じ PR でハッシュの記録を更新する。更新は 1 週に 1 本へまとめてある（`.github/dependabot.yml` の `groups`）。
- `sha_pinning_required` を有効にした後は、`public-ready` の手動起動、次のリリース自動化、`CodeQL` のチェック、`Dependabot` の更新の実行がそれぞれ成功することを確かめる。`CodeQL` と `Dependabot` は GitHub 側が動かすワークフローで、この設定の影響を受けるかを公式文書で確かめられていない。`CodeQL` は必須チェックなので、失敗すればすべての PR が止まる。その場合はすぐ設定を無効に戻す。
- 戻し方: 1 は変更を取り消すコミットで戻る。2〜6 は同じ設定を元の値に戻す。`sha_pinning_required` を有効にした後に 1 を戻す場合は、先に設定を無効にする。
