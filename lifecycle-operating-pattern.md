---
title: lifecycle operating pattern
type: brain
status: active
created: 2026-05-13
owner: codex
scope: lifecycle-operating-pattern
tags: [lifecycle, operating-card, fde, typology]
related:
  - dependency-registry:typology-lifecycle
  - dependency-registry:typology-placement
  - core.md
---

# lifecycle operating pattern

各 lane の `operating-card.md` が参照する lifecycle mini。具体例を lane ごとに増やさず、共通 slot だけを置く。

## 1. Lifecycle Mini

```text
capture: どこに入るか
clarify: いつ見直すか
promote: 何になったら昇格するか
close: 何をもって閉じるか
archive: どこへ退避するか
reflect: いつ棚卸しするか
```

## 2. Lane Card への書き方

lane 側には詳細を書かない。入口だけ書く。

```text
Lifecycle:
- pattern: lifecycle-operating-pattern.md
- capture:
- close:
- archive:
- reflect:
```

## 3. 昇格の考え方

| 変化 | 扱い |
|---|---|
| 1 回の観測 | report / inbox |
| 2 回以上の再発 | lessons-learned |
| 実行手順になった | playbook |
| 全 lane に効く | brain |
| 自動で回る | pipeline / script config |

## 4. 使い方

- operating-card は 80 行以内を目安にする。
- current-status には「いま / 次 / blocker」だけを置く。
- lifecycle の例や歴史は current-status に積まない。
- 詳細な規約が必要な時だけ `typology-lifecycle-rules.md` を読む。

## 5. Rejected entry persistence

Lane の Final List / 採用候補を rejected / discard にした時は、次 session で再浮上しないように lifecycle を閉じる。

slot:
- decision: `Documents/lanes/<lane>/decisions.md` に Source / Rationale / Impact / reopen condition を記録
- memory: runtime hot-memory / boot pointer がある場合だけ rejected pointer を追加
- propagate: current-status / master-plan / canonical inventory / snapshot など、再浮上源を rejected に同期
- detector: Final List 提案前に canonical inventory の status 列を stable id (LI/decision id) で確認 (= authoritative / 1 行 1 status)。decisions.md / item name grep は人間可読の補助のみで、否定文に誤ヒットするため判定根拠にしない
- repair: 再浮上したら decision / memory / propagate / detector key を同 session で埋め直す

再採用は CEO 明示再開示 + Type1 review packet が必須。pilot は 1 lane で始め、10 Shadow OK 後に全 lane 展開を検討する。例外 1 件で Shadow OK は reset。

> source: lab decisions.md D-11 (antigravity / 2026-05-14) / D-12 (cccost / 2026-05-15) / Codex 5.5 review (`Documents/inbox/.archive/2026-05-15/2026-05-15-codex55-to-lab-fde-final-list-rejection-protocol-review-reply.md`)。pilot owner = lab。rollback = §5 ブロック削除 1 commit。

closure_rule: active

