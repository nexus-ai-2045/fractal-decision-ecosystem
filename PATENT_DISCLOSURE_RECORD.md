# Patent Disclosure Record

Status: 事実記録のみ。法的助言ではない。

## 経緯 (事実)

- 本 repository (`nexus-ai-2045/fractal-decision-ecosystem`) は 2026-07 に public 化された。
- その public 化に伴い、`PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md` (仮出願検討用の技術開示ドラフト) と
  `patent-packet/` (PDF + `MANIFEST.sha256` + README で構成される packet) が世界に公開された。
- 当該ドラフトは冒頭で "Do not publish this draft" と明記していたが、public 化の際にこの境界は
  実際には守られていなかった。
- 個人情報 (発明者の実名等) は当該ファイル群に含まれていないことを確認済み。発明者欄は
  「出願時に記入」のままだった。

## 本 PR での対応

- `PROVISIONAL_PATENT_DISCLOSURE_DRAFT.md` と `patent-packet/` を git の tracked file から除去し、
  `.gitignore` に追加した。以後、これらを誤って再度 commit することを防ぐ。
- `scripts/build_patent_packet.py` (生成 script) は削除せず残す。出力先の `patent-packet/` が
  gitignore 済みになったため、生成はローカルでのみ行われ、公開 repo には含まれない。
- 特許の技術内容そのものは本記録に再掲しない。

## 除去してもできないこと (事実)

- 公開されたという事実自体を取り消すことはできない。本 repository の過去コミット履歴、および
  GitHub 側や外部の cache / mirror / crawler に保存された分には、当該内容が残っている可能性がある。
- 本 PR では git 履歴の書き換え (force push によるコミット改変・削除等) は行っていない。
  既に public 化されており novelty の回復にはつながらないこと、force push はリスクを増やすだけで
  あることから、履歴の書き換えは実施しない方針とした。

## 出願検討時の一般的事実 (法的助言ではない)

- 自己の公開行為を起点とした grace period (猶予期間) の扱いは国・地域によって異なるとされる。
  一般に、米国・日本には自己開示から 12 か月の猶予制度があるとされる一方、欧州・中国には
  原則としてこの種の猶予制度がないとされる。
- 上記は一般的に言われている制度の要約に過ぎない。本件への適用可否・期限の起算日・
  実際に出願できるかどうかについては、必ず専門家 (弁理士・特許 attorney 等) に確認すること。
  本記録はその代わりにはならない。

## 次の判断

- 出願する / しない、および timing の判断は人間が行う。本記録はその判断を代行せず、
  事実の記録と証跡の保存のみを目的とする。
