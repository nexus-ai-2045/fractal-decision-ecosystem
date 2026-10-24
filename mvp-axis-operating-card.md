---
title: FDE MVP axis operating card
type: brain
status: active
created: 2026-06-22
owner: codex
scope: fde-mvp-axis-operating-card
tags: [fde, mvp, operating-card, axis]
related:
  - ai-development-living-harness.md
  - ROADMAP.md
  - axis-registry.md
---

# FDE MVP軸別13運用カード

FDE で MVP を作る時に、機能単位だけでなく「どの軸の MVP か」を先に切るためのカード。新しい MVP 候補は、まずこの 13 項目で 1 枚に圧縮してから実装、検証、ADR、PR へ進める。

## 13項目

| # | 項目 | 書くこと |
|---:|---|---|
| 1 | MVP軸 | product / security / ops / creative / AI dev / search / publication / rights など、どの軸の MVP か |
| 2 | ユーザー行動 | その MVP で人間が実際にできるようになる 1 行動 |
| 3 | 最小価値 | その行動が通ると何が楽になるか、何を防げるか |
| 4 | 対象境界 | private repo / public-kernel / local automation / external connector など、対象 surface |
| 5 | 保存単位 | どの file、ADR、script、test、PR に残すか |
| 6 | 最小E2E | 最初に通す 1 本の smoke / verifier / manual path |
| 7 | 失敗検知 | 何が起きたら route drift、境界漏れ、過剰実装とみなすか |
| 8 | public/private境界 | 公開、外部送信、個人情報、secret、visibility の停止線 |
| 9 | 権利/特許境界 | rights / patent / license / Patent Pending に触れるか、触れないか |
| 10 | 完了条件 | local complete、operation guaranteed、public releasable を分けて書く |
| 11 | 検証証跡 | pytest、mvp gate、public-ready、screenshot、manual review など |
| 12 | ADR/採番 | durable decision なら `decisions/` に ADR 化し、`python scripts\adr_next.py` で採番する |
| 13 | 次の一手 | この turn で実行する 1 件。大きければ分割する |

## 使い方

```text
mvp_axis:
user_action:
minimum_value:
surface:
storage_unit:
minimum_e2e:
drift_detection:
public_private_boundary:
rights_boundary:
done_when:
evidence:
adr_numbering:
next_action:
```

## 軸の例

| 軸 | MVP例 | 先に通す gate |
|---|---|---|
| product | README から入口と価値が分かる | `python scripts\roadmap_gate_check.py` |
| security | 公開・visibility・secret の停止線が落ちない | `python scripts\public_ready_check.py` |
| ops | 残務ゼロ回答が git / test / external boundary を分ける | `python scripts\mvp_gate_check.py` |
| AI dev | 開発カード、ADR、採番、test がつながる | `python scripts\adr_next.py` + pytest |
| publication | public release が人間承認なしに進まない | `python scripts\pre_publication_gate_check.py --json` |
| rights | patent / filing / ownership が broad gate に残る | `PUBLIC_READY.md` / `INVENTION_RECORD.md` |

## Stop Lines

- MVP は public release approval ではない。
- MVP は Patent Pending approval ではない。
- MVP は repository visibility 変更 approval ではない。
- MVP は外部 connector write approval ではない。
- MVP が緑でも、人間 review が必要なものは human gate に残す。

