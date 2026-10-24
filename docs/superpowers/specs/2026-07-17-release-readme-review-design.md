# リリースPR READMEレビュー設計

## 目的

FDEのリリース時に、READMEが現在の価値、使い方、状態、主要導線を正しく伝えているかを必ず確認する。README変更そのものを目的にせず、改善が必要な時だけ実質的な差分を要求する。

## 対象範囲

- Release Pleaseが作成したFDEのリリースPRだけを対象にする。
- 通常の機能PR、修正PR、文書PRには適用しない。
- GitHub Release作成、tag作成、PR mergeは引き続き人間の明示承認まで停止する。
- 初回適用対象は0.2.0のリリースPRとする。

## 採用方式

判断を支援するREADMEレビュースキルと、確認忘れを防ぐCI gateを組み合わせる。

### READMEレビュースキル

リリースPRの変更内容とREADMEを照合し、次を確認する。

1. 冒頭でFDEが何か分かる。
2. 初めて使う人が開始地点を見つけられる。
3. 現在の機能・状態とREADMEの説明が一致する。
4. `visual.html`、`SYSTEM_OVERVIEW.md`、運用gateへの主要導線が有効である。
5. 公開、外部送信、特許出願などの停止線を過大に保証していない。

スキルはレビュー結果をPR本文へ反映するため、次の契約を返す。

```text
readme_review: complete
readme_change: changed | not-needed
readme_reason: 具体的な確認結果または変更不要の根拠
```

`changed`の場合は、今回のリリース内容に対応する実質的なREADME差分を含める。`not-needed`の場合は、READMEのどの記述が今回の変更を既に正しく表しているかを`readme_reason`へ記録する。

### CI gate

リリースPRだけを識別し、次をfail-closedで検証する。

- `readme_review: complete` がある。
- `readme_change` が `changed` または `not-needed` である。
- `readme_reason` が空でない。
- `changed` の場合、PR差分にルートの `README.md` が含まれる。
- `not-needed` の場合、README差分は要求しない。

リリースPRの識別には、Release Pleaseのbranch命名とPRタイトルの両方を使う。片方だけ一致する不完全な入力はリリース候補として扱い、契約不足なら停止する。

## 処理フロー

```text
Release PleaseがリリースPRを生成
-> READMEレビュースキルで変更内容とREADMEを照合
-> 必要ならREADMEを改善
-> PR本文へレビュー契約を記録
-> CI gateが契約と差分を検証
-> 人間がREADME、CHANGELOG、version、tag導線を目視
-> 明示承認後にmerge
-> Release PleaseがtagとGitHub Releaseを作成
```

## エラーと停止条件

- レビュー記録がない: CI失敗。READMEレビューを実施してPR本文を更新する。
- `changed`なのにREADME差分がない: CI失敗。README変更を追加するか、根拠付きで`not-needed`へ修正する。
- `not-needed`の理由が抽象的: CI失敗。現行READMEの対応箇所を具体化する。
- READMEとリリース内容が矛盾する: merge停止。READMEまたはリリース内容を修正する。
- tag比較リンクが存在しないtagを参照する: merge停止。tag契約を先に整合する。
- CI成功だけで公開承認済みとは扱わない。

## テスト

- リリースPRかつ`changed`、README差分あり: pass
- リリースPRかつ`changed`、README差分なし: fail
- リリースPRかつ`not-needed`、具体的理由あり: pass
- リリースPRかつ`not-needed`、理由なし: fail
- リリースPRでレビュー契約なし: fail
- 通常PRでレビュー契約なし: 対象外としてpass
- branch名だけRelease Please形式、契約なし: fail
- PRタイトルだけrelease形式、契約なし: fail

既存のMVP gate、PR hygiene、Public Readyも併せて通す。

## 0.2.0への適用

0.2.0では`readme_change: changed`を採用する。READMEの初見導線をレビューし、今回追加された閉ループ運用と自動バージョニングを、概念説明を膨らませずに「現在できること」「最初に試す入口」へ反映する。

README改善、tag形式修正、CHANGELOG修正、全gate成功、人間目視レビューが揃うまで、リリースPRはmergeしない。

## 非目標

- 毎回READMEへ意味のない差分を作ること。
- 通常PRすべてにREADMEレビューを強制すること。
- CIまたはスキルがmergeやRelease作成を自動承認すること。
- READMEへ内部設計やprivate情報を大量に複製すること。
