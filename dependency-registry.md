---
title: FDE dependency registry
type: registry
status: active
created: 2026-05-13
updated_at: 2026-07-18
owner: codex
scope: fde-dependencies
tags: [fde, dependency, registry, boundary, public]
---

# FDE 依存レジストリ

FDE 本文は外部の物理 path を直書きしない。必要な依存はこの registry に `dependency-registry:<key>` として集約する。

この repository は public package である。したがって registry も **ローカル環境の絶対 path / 個人 workspace path に依存しない**。key は capability 名として公開し、解決先は下の resolution class で表す。

## ルール

- FDE 内で閉じるものは内部 snapshot として置く。
- 実行時に外部 adapter が必要な時は、この registry に `key / capability / resolution / mode` を置く。
- FDE 本文側に private workspace path、user home 絶対 path、machine-local 絶対 path を直書きしない。
- `mode=snapshot-imported` は FDE 内に取り込み済み。通常は内部 snapshot を読む。
- `mode=external-authority` は概念上の外部正本。公開 package では path を持たず、operator-local adapter がある時だけ任意接続する。
- `mode=planned` は置き場だけ予約済みで、実体作成前。
- `mode=missing-local` は参照候補が未配置。通常実行では読まず、次の registry cleanup 対象にする。
- `mode=withheld` は公開境界外。存在だけ示し、詳細 path は出さない。

## resolution class

| resolution | 意味 | 公開 package での扱い |
|---|---|---|
| `repo-local` | この repository 内の file | そのまま読む |
| `absorbed` | 要点が FDE 内 snapshot / rule に反映済み | 通常は外部を読まない |
| `operator-local-adapter` | 利用者が自分の workspace に持つ任意 adapter | 無いなら skip / hold。path は公開しない |
| `withheld` | private operating material | 公開面では解決しない |
| `planned` | 将来枠 | 実体ができるまで使わない |

## 外部 SSOT closure class

FDE 関連の外部 source / report / inbox / lane rule は、採用前に次の分類へ切る。registry にない外部 source は、FDE の根拠として直接採用しない。

| class | 意味 | FDE 側の扱い |
|---|---|---|
| `absorbed` | 要点が FDE 内 snapshot / rule / pointer に反映済み | 通常は外部を読まない |
| `external-authority` | 概念上の正本は FDE 外。必要時だけ registry 経由で参照する | `key / capability / resolution / mode` を置く |
| `unabsorbed_candidate` | FDE に戻すべき可能性があるが未採否 | audit report / Type1 review に戻す |
| `not_fde` | lane local / report / historical evidence で、FDE 正本ではない | FDE へ入れない |
| `stale` | 古い、矛盾、置き換え済み | FDE 入口から外す |

## 内部 snapshot

| key | internal file | source role |
|---|---|---|
| fde-root | `root-router.md` | 展開版 root router |
| fde-core | `core.md` | 軽量判断 loop |
| external-ai-route | `external-ai-route-registry.md` | browser AI / API route registry snapshot |
| external-ai-file-loop | `external-ai-file-loop.md` | external AI file-backed loop snapshot |
| external-ai-packet | `external-ai-file-review-packet.md` | external AI review packet template snapshot |
| browser-ai-review | `browser-ai-review-synthesis.md` | FDE v1 browser AI review synthesis |
| brain-concept-rollup | `brain-concept-rollup.md` | Brain concept absorb/reference/hold entry |
| ops-best-practice | `ops-best-practice-inventory.md` | Claude ops best-practice FDE filter |
| research-round-trail | `research-lane-round-trail.md` | Research lane FDE trail |
| search-orchestration | `search-orchestration.md` | search delegation / Codex final integrator rule |
| axis-registry | `axis-registry.md` | axis / work mode / closure / storage definitions |
| pattern-vocabulary | `pattern-vocabulary.md` | vocabulary / alias / pattern chain registry |
| dialogue-protocol | `dialogue-protocol.md` | AI-human dialogue protocol |
| source-pointers | `source-pointers.md` | source cluster pointers |
| external-references | `external-references.md` | external AI / raw / report reference entry |
| lifecycle-operating-pattern | `lifecycle-operating-pattern.md` | lifecycle mini for operating cards |
| data-index | `data-index.md` | lightweight data/catalog entry |
| operating-card | `operating-card.md` | 毎 turn の運用入口 |
| public-kernel | `public-kernel/` | sanitized public candidate |
| visual | `visual.html` | FDE visual view |

## 外部 authority（環境非依存）

物理 path 列は持たない。公開読者が追えるのは capability と resolution だけ。

| key | capability | resolution | mode |
|---|---|---|---|
| typology-placement | file type / placement の全体正本 | operator-local-adapter | external-authority |
| typology-lifecycle | lifecycle の全体正本 | operator-local-adapter | external-authority |
| ssot-registry | SSOT topic → owner_file の対応表 | operator-local-adapter | external-authority |
| ssot-loader | registry 経由読み取り強制層 | operator-local-adapter | external-authority |
| ssot-lint | registry 整合性検査 / drift detect | operator-local-adapter | external-authority |
| ssot-git-change-review | SSOT / FDE / registry 変更の commit 前 review protocol | operator-local-adapter | external-authority |
| placement-rules | 責務境界と SSOT 判定基準 | operator-local-adapter | external-authority |
| structural-separation | 抽象レイヤー分離原則 | operator-local-adapter | external-authority |
| ssot-split | global/local SSOT 分離フロー | operator-local-adapter | external-authority |
| ssot-obsidian-alias | note alias による発見性補完（任意） | operator-local-adapter | external-authority |
| fact-gate | fact tag / unknown handling gate | absorbed → `core.md` / `public-kernel/GATES.md` | external-authority |
| scope-gate | scope_route / Type1 / reroute gate | absorbed → `core.md` / `public-kernel/GATES.md` | external-authority |
| security-baseline | security baseline | absorbed → `SECURITY.md` / `ai-contact-safety-contract.md` | external-authority |
| lane-communication | lane 間 packet の正本 | operator-local-adapter | external-authority |
| runtime-boot | runtime 起動入口の正本 | operator-local-adapter | external-authority |
| codex-restart | Codex 起動・復帰 protocol | operator-local-adapter | external-authority |
| official-capability | 新規機構前の公式機能 / 既存例確認 gate | absorbed → `README.md` capability_inventory | external-authority |
| measurement-gate | 測定可能な claim の実測、shadow 観測、昇格判断 | operator-local-adapter | external-authority |
| operational-command-smoke | command の dry-run / smoke / verify / report / regression 接続契約 | operator-local-adapter | external-authority |
| runtime-guarantee-matrix | runtime ごとの hard / warn / fail-closed / fail-open 保証差 | operator-local-adapter | external-authority |
| low-pdca-orchestrator | goal / decomposition / dispatch / check / act を回す shared skill | operator-local-adapter | external-authority |
| cross-runtime-primitives | runtime 横断 primitive / 共通操作語彙 | operator-local-adapter | external-authority |
| fdecc-review-workspace | 外部 review / improvement workspace | withheld | external-authority |
| fde-v1-draft-report | historical draft。通常入口ではない | absorbed → `browser-ai-review-synthesis.md` | external-authority |
| fde-contradiction-audit-report | contradiction audit report | absorbed → `ops-best-practice-inventory.md` | external-authority |
| fde-orchestration-return-stack-report | orchestration return stack report | absorbed → `search-orchestration.md` | external-authority |
| kusanagi-role | TOP lane role の正本 | withheld | external-authority |
| content-decisions | content 原則 / 本人の一言 rule | absorbed → `dialogue-protocol.md` | external-authority |
| lane-status | lane の現在地 cache | operator-local-adapter | external-authority |
| lane-queue | lane queue | operator-local-adapter | external-authority |
| todo | 全体 todo の現在地 | operator-local-adapter | external-authority |
| handoff-index | handoff 索引 | operator-local-adapter | external-authority |
| playbooks | 手順置き場 | operator-local-adapter | external-authority |
| reports | 調査・監査・実測置き場 | operator-local-adapter | external-authority |
| inbox | 通信 packet / 判断待ち置き場 | operator-local-adapter | external-authority |
| tmp-scratch | 一時 result / scratch | operator-local-adapter | external-authority |
| lessons | lesson 置き場 | operator-local-adapter | external-authority |
| ideas | idea / 改善案置き場 | operator-local-adapter | external-authority |
| decisions | project decision log | repo-local → `decisions/` | external-authority |
| brain-general | FDE 外の brain SSOT | withheld | external-authority |
| brain-chains | chain 分離候補 | planned | planned |
| lane-decisions | lane decision log | operator-local-adapter | external-authority |
| lane-operating-card | lane の短い運用入口 | operator-local-adapter | external-authority |
| shared-scripts | 実行 wrapper / resolver | operator-local-adapter | external-authority |
| shared-lib | runtime 共通 library | operator-local-adapter | external-authority |
| grok-tools | Grok browser / http / scraper 実験 | withheld | external-authority |
| cmux-browser-review-send | browser AI surface resolver | operator-local-adapter | external-authority |
| cmux-socket-cli | terminal/browser RPC thin transport | operator-local-adapter | external-authority |
| ai-case-route | external AI route 判定 helper | operator-local-adapter | external-authority |
| inbox-quiet-loop | quiet timer helper | operator-local-adapter | external-authority |
| claude-rules | Cloud Code / Claude Code rule 正本 | operator-local-adapter | external-authority |
| claude-settings | permissions / local settings | operator-local-adapter | external-authority |
| claude-hooks | hook 実体 / control plane | operator-local-adapter | external-authority |
| claude-skills | Cloud Code / Claude Code skills | operator-local-adapter | external-authority |
| project-agents | Project agent entry | repo-local → `AGENTS.md` | external-authority |
| project-claude | Cloud Code project entry | operator-local-adapter | external-authority |
| codex-top-socket-channel | Codex ↔ TOP の socket dogfood 経路 | withheld | external-authority |
| grok-cmux-pane-route | Grok 投入の pane / file-backed 経路 | operator-local-adapter | external-authority |
| project-docs | project docs entry | missing-local | missing-local |
| memory-md | legacy / runtime memory entry | operator-local-adapter | external-authority |
| memory-cache | 起動時 hot cache | operator-local-adapter | external-authority |
| voice-guard | 音声入力 ambiguity guard | operator-local-adapter | external-authority |
| cmux-reference | terminal multiplexer 操作参照 | operator-local-adapter | external-authority |
| cmux-browser-js-error | browser 操作の preflight / fallback | operator-local-adapter | external-authority |
| browser-ai-review-playbook | browser AI review send / collect 手順 | absorbed → `external-ai-file-loop.md` | external-authority |
| multi-ai-design | multi AI orchestration 上位設計 | absorbed → `search-orchestration.md` | external-authority |
| multi-ai-unified-design | multi AI 統合設計候補 | absorbed → `search-orchestration.md` | external-authority |
| multi-ai-review-gate | multi AI review gate 設計 | absorbed → `external-ai-route-registry.md` | external-authority |
| multi-ai-methodology | multi AI review methodology | absorbed → `external-references.md` | external-authority |
| agent-selection | BG agent dispatch / 結果回収の判断候補 | operator-local-adapter | external-authority |
| groq-grok-distinction | Groq / Grok 混同防止 | absorbed → `external-ai-route-registry.md` | external-authority |
| research-multi-ai-prompt | multi AI consultation prompt | operator-local-adapter | external-authority |
| source-routing-budget | source routing / context budget 方針 | absorbed → `search-orchestration.md` | external-authority |
| current-orchestration-premise | 現行 orchestration 前提 | absorbed → `search-orchestration.md` | external-authority |
| visual-status-map-playbook | visual map playbook | absorbed → `visual.html` / `SYSTEM_OVERVIEW.md` | external-authority |
| lane-status-protocol | lane status 形式 | operator-local-adapter | external-authority |
| event-ledger | append-only dispatch / ack / done / blocked / stalled ledger | operator-local-adapter | external-authority |
| ceo-response-gate | CEO-facing 応答 gate | absorbed → `dialogue-protocol.md` | external-authority |
| kusanagi-bato-charter | TOP / 運営 運用 charter | absorbed → `operating-card.md` / `dialogue-protocol.md` | external-authority |
| lane-history-drift-audit | lane history drift audit | withheld | external-authority |
| brain-concept-first-pass | Brain root concept first pass | absorbed → `brain-concept-rollup.md` | external-authority |
| layer-vocabulary-synthesis | layer vocabulary synthesis | absorbed → `pattern-vocabulary.md` | external-authority |
| dev-log | dev log | operator-local-adapter | external-authority |
| entry-guided-fact-label | fact label SSOT round evidence | absorbed → `core.md` | external-authority |
| rice-rescoring | RICE rescoring note | operator-local-adapter | external-authority |
| ideas-ledger | ideas ledger | operator-local-adapter | external-authority |
| ideas-inbox | ideas inbox | operator-local-adapter | external-authority |
| gemini-lightweight-research | Gemini lightweight research test | absorbed → `external-ai-route-registry.md` | external-authority |
| claude-meta-rules | Cloud Code meta rule method | operator-local-adapter | external-authority |
| claude-invariants | Cloud Code invariants | operator-local-adapter | external-authority |
| claude-control-plane | hook control plane | operator-local-adapter | external-authority |
| claude-testing-rule | Cloud Code testing rule | operator-local-adapter | external-authority |
| claude-tdd-skill | TDD skill | operator-local-adapter | external-authority |
| claude-api-key-skill | API key lifecycle skill | operator-local-adapter | external-authority |
| claude-optimization-guide | Claude Code optimization guide | operator-local-adapter | external-authority |
| claude-code-reference | Claude Code official reference digest | operator-local-adapter | external-authority |

## import 済み source label

| label | meaning |
|---|---|
| imported-source | raw / inbox / report から FDE 内へ要点取り込み済み。公開 package では元 path を持たない。吸収先の repo-local file を読む |
| imported-raw-cluster | raw external AI cluster は長文なので FDE 内では要約だけ扱う |
| external-authority | 概念上の外部正本。公開 package では operator-local adapter または absorbed 先を使う |
| planned | 置き場だけ予約済み。実体作成前 |
| missing-local | 参照候補が未配置。通常実行では読まない |
| withheld | 公開境界外。詳細は出さない |

## operator-local adapter の使い方

1. public package だけで閉じる作業は `repo-local` / `absorbed` だけを使う。
2. adapter が無い key は `not_available` として hold / skip し、推測 path を作らない。
3. adapter を接続する時も、その物理 path をこの public registry に書き戻さない。
4. 同じ capability が 2 回必要になったら、要点を FDE 内 snapshot へ absorb する候補にする。

## data / policy / state 分離

| 種別 | 意味 | 置き場 |
|---|---|---|
| core | 判断の動作 | `core.md` |
| data | type / catalog / source pointer | `data-index.md` / `source-pointers.md` |
| policy | してよい/ダメ | `public-kernel/GATES.md` / `SECURITY.md` / `dependency-registry:fact-gate` |
| state | 現在地 / queue / blocker | operator-local adapter (`lane-status` / `lane-queue`) または本 repo の active docs |
| procedure | 手順 | `operating-card.md` / operator-local playbooks |
| knowledge | 知見 | `ops-best-practice-inventory.md` / operator-local reports |

closure_rule: active
