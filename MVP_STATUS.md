# FDE MVP状態

MVP状態: private local gate として完了

## 現在の判断

- リポジトリ可視性: private
- 外部公開 action: 未実行
- 特許出願 action: 未実行。出願は optional で、別途承認が必要
- connector write action: 未実行
- 発明者判断: ユーザー単独発明者として確認済み
- 所有者判断: ユーザーが保持
- 譲受人判断: なし / 未割当
- 権利方針: 出願または公開の別判断があるまで、特許・出願詳細は意図的に広めに保つ
- 表記方針: `Patent Pending` / `特許出願中` は、実際に出願した後だけ使う
- local MVP gate command: `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mvp_gate.ps1`

## 完了済みのローカルゲート

- public readiness check は MVP gate に含まれる
- pre-publication gate check は MVP gate に含まれる
- pytest は MVP gate に含まれる
- public kernel は sanitized candidate であり、release action ではない

## 残っている人間 / 外部承認ブロッカー

- 特許出願は optional external work として扱い、local implementation residue には含めない
- 後で出願する場合は、現在の会話で明示承認を得てから実行する
- 出願した場合は、filing receipt / application number / submitted PDF / file hash を保存する
- `Patent Pending` / `特許出願中` は、application が実際に filed されるまで使わない
- GitHub repository visibility は、対象repoを明示した承認が出るまで private のまま維持する

## 次の節目

次の節目: public release が要求された場合だけ、publication approval に進む
