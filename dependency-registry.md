---
title: FDE dependency registry
type: registry
status: active
created: 2026-05-13
owner: codex
scope: fde-dependencies
tags: [fde, dependency, registry, boundary]
---

# FDE 依存レジストリ

FDE folder 内の file は、外部 path を直接ばら撒かない。外部依存はこの registry に集約し、本文側は `dependency-registry:<key>` で参照する。

## ルール

- FDE 内で閉じるものは `` に snapshot / digest / router として置く。
- FDE 外の正本を読む必要がある時は、この registry に `key / path / reason / mode` を置く。
- FDE 本文側に外部 path を直書きしない。
- `mode=snapshot-imported` は FDE 内に取り込み済み。通常は内部 snapshot を読む。
- `mode=external-authority` は FDE の外に正本がある。実行時だけ registry 経由で確認する。
- `mode=planned` は置き場だけ予約済みで、実体作成前。
- `mode=missing-local` は参照候補が未配置。通常実行では読まず、次の registry cleanup 対象にする。

## 外部 SSOT closure class

FDE 関連の外部 source / report / inbox / lane rule は、採用前に次の分類へ切る。registry にない外部 source は、FDE の根拠として直接採用しない。

| class | 意味 | FDE 側の扱い |
|---|---|---|
| `absorbed` | 要点が FDE 内 snapshot / rule / pointer に反映済み | 通常は外部を読まない |
| `external-authority` | 正本は FDE 外にあり、FDE は registry 経由で参照する | `key / path / reason / mode` を置く |
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
| visual | `visual.html` | FDE visual view |

## 外部 authority

| key | external path | reason | mode |
|---|---|---|---|
| typology-placement | `Documents/brain/typology-and-placement.md` | file type / placement の全体正本 | external-authority |
| typology-lifecycle | `Documents/brain/typology-lifecycle-rules.md` | lifecycle の全体正本 | external-authority |
| ssot-registry | `ssot-registry.yaml` | SSOT topic → owner_file の唯一対応表 / ADR-0058 + ssot_lint 根拠 / Layer 2 強制の正本 | external-authority |
| ssot-loader | `shared/lib/ssot_loader.py` | load_ssot(topic_id) による registry 経由読み取り強制層（CLAUDE.md §shared/lib で強制） | external-authority |
| ssot-lint | `shared/scripts/ssot_lint.py` | --staged / --audit / --audit-consumers による registry 整合性検査・drift detect・pre-commit hook（ADR-0058） | external-authority |
| ssot-git-change-review | `Documents/references/ssot-git-change-review.md` | SSOT / FDE / registry / index 変更の commit 前 review protocol。意味単位、scope 純度、companion gate、staged lint、既存 audit failure の切り分けを定義 | external-authority |
| placement-rules | `Documents/brain/placement-rules.md` | ~/.claude/ 責務境界 + 各 dir の責務・SSOT 判定基準の正本（ssot-registry 登録済） | external-authority |
| structural-separation | `Documents/patterns/structural-separation-principle.md` | 抽象レイヤー分離原則（時間軸分離 / schema 分離 / 責務分離 3 パターン + 5 ステップ） / SSOT drift 防止 | external-authority |
| ssot-split | `Documents/patterns/ssot-split-principles.md` | global/local SSOT 分離の 2 軸テスト + 4 質問フローチャート（ADR-0053、2026-05-15 patterns 正規化済） | external-authority |
| ssot-obsidian-alias | `Documents/references/ssot-obsidian-alias.md` | SSOT 管理の Obsidian Wiki link 発見性補完。alias note は `link-aliases/ssot-*.md`（命名規則: ssot-<key>.md） | external-authority |
| fact-gate | `Documents/brain/pre-execution-fact-check-gate.md` | fact tag / unknown handling の全体 gate | external-authority |
| scope-gate | `Documents/brain/scope-routing-gate.md` | scope_route / Type1 / reroute の全体 gate | external-authority |
| security-baseline | `Documents/brain/security-baseline.md` | security baseline | external-authority |
| lane-communication | `Documents/brain/lane-communication-protocol.md` | lane 間 packet の正本 | external-authority |
| runtime-boot | `Documents/brain/runtime-boot-branching.md` | runtime 起動入口の正本 | external-authority |
| codex-restart | `Documents/brain/codex-restart-protocol.md` | Codex 起動・復帰 protocol | external-authority |
| official-capability | `Documents/brain/official-capability-inventory-first.md` | 新規機構前の公式機能 / 既存例確認 gate | external-authority |
| cross-runtime-primitives | `Documents/brain/cross-runtime-operational-primitives.md` | runtime 横断 primitive / 共通操作語彙 | external-authority |
| fdecc-review-workspace | `this repositoryCC/` | 基盤 / Cloud Code による FDE review / improvement workspace | external-authority |
| fde-v1-draft-report | `Documents/reports/fde/2026-05-13-fde-v1-draft.md` | historical draft, not normal entry | external-authority |
| fde-contradiction-audit-report | `Documents/reports/fde/2026-05-13-fde-contradiction-audit.md` | FDE / Cloud Code contradiction audit report | external-authority |
| fde-orchestration-return-stack-report | `Documents/reports/fde/2026-05-13-fde-orchestration-return-stack.md` | 2026-05-13 orchestration return stack report | external-authority |
| kusanagi-role | `Documents/lanes/top/role.md` | TOP lane role の正本 (旧 kusanagi / 2026-05-21 merged into TOP / 旧物理 path は `Documents/lanes/.archive/2026-05-21-kusanagi-merged-into-top/role.md`) | external-authority |
| content-decisions | `Documents/lanes/content/decisions.md` | content 原則 / 本人の一言 rule | external-authority |
| lane-status | `Documents/lanes/<lane>/current-status.md` | lane の現在地 cache | external-authority |
| lane-queue | `Documents/lanes/<lane>/queue.yaml` | lane queue | external-authority |
| todo | `Documents/tasks/todo.md` | 全体 todo の現在地 | external-authority |
| handoff-index | `Documents/handoffs/issue-index.md` | handoff 索引 | external-authority |
| playbooks | `Documents/playbooks/` | 手順置き場 | external-authority |
| reports | `Documents/reports/` | 調査・監査・実測置き場 | external-authority |
| inbox | `Documents/inbox/` | 通信 packet / 判断待ち置き場 | external-authority |
| tmp-scratch | `/tmp` | 一時 result / scratch path | external-authority |
| lessons | `Documents/lessons-learned/` | lesson 置き場 | external-authority |
| ideas | `Documents/ideas/` | idea / 改善案置き場 | external-authority |
| decisions | `Documents/decisions/` | project decision log | external-authority |
| brain-general | `Documents/brain/` | FDE 外の brain SSOT | external-authority |
| brain-chains | `Documents/brain/chains/` | chain 分離候補。実体未作成 | planned |
| lane-decisions | `Documents/lanes/<lane>/decisions.md` | lane decision log | external-authority |
| lane-operating-card | `Documents/lanes/<lane>/operating-card.md` | lane の短い運用入口 | external-authority |
| shared-scripts | `shared/scripts/` | 実行 wrapper / resolver | external-authority |
| shared-lib | `shared/lib/` | runtime 共通 library | external-authority |
| grok-tools | `dev/grok-tools/` | Grok browser / http / scraper / task DB 既存実験 | external-authority |
| cmux-browser-review-send | `shared/scripts/cmux_browser_review_send.py` | browser AI surface resolver | external-authority |
| cmux-socket-cli | `cmux 0.64.5+` (`/Applications/cmux.app/Contents/Resources/bin/cmux`) | Unix socket 経由の lane terminal/browser RPC。`cmux_file_signal.py --transport={file,socket,auto}` の thin transport 層、`--verify-strategy={poll,events}` の push 購読層 (= `cmux events --after`)。lane policy / closed-loop ACK / fact tag は file-backed primary を維持。 | external-authority |
| ai-case-route | `shared/scripts/ai_case_route.py` | external AI route 判定 helper | external-authority |
| inbox-quiet-loop | `shared/scripts/inbox_quiet_tick_loop.py` | quiet timer / Bato tick helper | external-authority |
| claude-rules | `~/.claude/rules/` | Cloud Code / Claude Code rule 正本 | external-authority |
| claude-settings | `~/.claude/settings.local.json` | permissions deny / local settings | external-authority |
| claude-hooks | `~/.claude/hooks/` | hook 実体 / control plane | external-authority |
| claude-skills | `~/.claude/skills/` | Cloud Code / Claude Code skills | external-authority |
| project-agents | `AGENTS.md` | Project agent entry | external-authority |
| project-claude | `CLAUDE.md` | Cloud Code project entry | external-authority |
| codex-top-socket-channel | `external-ai-route-registry.md` | §3者役割分担 + `dependency-registry:cmux-socket-cli` (events 経路)。Codex 5.5 ↔ TOP の socket events dogfood 経路。`cmux identify --id-format uuids` + `feed.item.completed` 監視。Phase 2 DONE / 2026-05-15 初本番運用 (file-backed packet は primary 維持、socket は速度 dogfood) | external-authority |
| grok-cmux-pane-route | `shared/lib/grok_client.py` + `shared/scripts/grok_chat_export.py` | Grok 投入は cmux pane terminal + file-backed packet を canonical。wrapper 経由のみ / secret 直読み禁止 / surface 番号は送信直前に再確認。secondary=Research workspace browser AI / API client は非推奨 (secret・quota 負荷)。2026-05-15 採用 (CEO ACK) | external-authority |
| project-docs | `docs/README.md` | project docs entry。実体未配置 | missing-local |
| memory-md | `MEMORY.md` | legacy / runtime memory entry | external-authority |
| memory-cache | `Documents/memory-cache.md` | 起動時 hot cache | external-authority |
| voice-guard | `Documents/references/voice-input/aqua-voice-ambiguity-guard.md` | 音声入力 ambiguity guard | external-authority |
| cmux-reference | `Documents/references/cmux/` | CMUX操作参照 | external-authority |
| cmux-browser-js-error | `Documents/references/cmux/browser-js-error-playbook.md` | cmux browser 操作の default preflight (`shared/scripts/cmux_ops.py browser-preflight`) / JS-heavy / WKWebView / CSP 時の非 JS fallback 操作 | external-authority |
| browser-ai-review-playbook | `Documents/references/cmux/browser-ai-review-playbook.md` | browser AI review send / collect の標準手順 | external-authority |
| multi-ai-design | `Documents/designs/multi-ai-orchestration-roadmap.md` | multi AI orchestration 上位設計 | external-authority |
| multi-ai-unified-design | `Documents/designs/multi-ai-unified-design.md` | multi AI 統合設計候補 | external-authority |
| multi-ai-review-gate | `Documents/designs/multi-ai-review-gate-spec.md` | multi AI review gate 設計 | external-authority |
| multi-ai-methodology | `Documents/decisions/2026-04-02_multi-ai-review-methodology.md` | multi AI review methodology decision | external-authority |
| agent-selection | `~/.claude/rules/agent-selection.md` | BG agent dispatch / 結果回収の判断候補 | external-authority |
| groq-grok-distinction | `Documents/references/groq-grok-distinction.md` | Groq / Grok 混同防止 | external-authority |
| research-multi-ai-prompt | `Documents/references/prompt-templates/research-multi-ai-consultation.md` | multi AI consultation prompt | external-authority |
| source-routing-budget | `Documents/brain/codex-source-routing-and-context-budget.md` | source routing / context budget 方針 | external-authority |
| current-orchestration-premise | `Documents/brain/current-orchestration-premise.md` | 現行 orchestration 前提 | external-authority |
| visual-status-map-playbook | `Documents/references/visual-status-map-playbook.md` | visual map playbook | external-authority |
| lane-status-protocol | `Documents/brain/lane-status-protocol.md` | lane status 形式 | external-authority |
| event-ledger | `ssot-registry:event-ledger` | append-only dispatch / ack / done / blocked / stalled ledger の正本 pointer | external-authority |
| ceo-response-gate | `Documents/brain/cc-ceo-response-behavior-gate.md` | CEO-facing 応答 gate | external-authority |
| kusanagi-bato-charter | `Documents/brain/operation-charter.md` | TOP / 運営 運用 charter (旧 kusanagi-bato / 2026-05-21 renamed) | external-authority |
| lane-history-drift-audit | `Documents/reports/2026-05-12-lane-history-drift-audit.md` | lane history drift audit | external-authority |
| brain-concept-first-pass | `Documents/reports/2026-05-13-brain-concept-fde-first-pass.md` | Brain root concept absorb/reference/hold first pass | external-authority |
| layer-vocabulary-synthesis | `Documents/research-digest/2026-05-13-layer-vocabulary-review-synthesis.md` | layer vocabulary synthesis | external-authority |
| dev-log | `Documents/dev-log.md` | dev log | external-authority |
| entry-guided-fact-label | `Documents/reports/2026-05-12-entry-guided-fact-label-ssot-v0-8.md` | fact label SSOT round evidence | external-authority |
| rice-rescoring | `Documents/ideas/2026-05-08-rice-rescoring.md` | RICE rescoring note | external-authority |
| ideas-ledger | `Documents/ideas/ideas-ledger.md` | ideas ledger | external-authority |
| ideas-inbox | `Documents/ideas/ideas-inbox.md` | ideas inbox | external-authority |
| gemini-lightweight-research | `Documents/reports/2026-05-08-cloud-code-gemini-lightweight-research-test-result.md` | Gemini lightweight research test | external-authority |
| claude-meta-rules | `~/.claude/docs/meta-rules.md` | Cloud Code meta rule method | external-authority |
| claude-invariants | `~/.claude/docs/invariants.yaml` | Cloud Code invariants | external-authority |
| claude-control-plane | `~/.claude/hooks/CONTROL-PLANE.md` | hook control plane | external-authority |
| claude-testing-rule | `~/.claude/rules/common/testing.md` | Cloud Code testing rule | external-authority |
| claude-tdd-skill | `~/.claude/skills/test-driven-development/SKILL.md` | TDD skill | external-authority |
| claude-api-key-skill | `~/.claude/skills/api-key-inventory/SKILL.md` | API key lifecycle skill | external-authority |
| claude-optimization-guide | `~/.claude/docs/claude-code-optimization-guide.md` | Claude Code optimization guide | external-authority |
| claude-code-reference | `Documents/references/claude-code/index.md` | Claude Code official reference digest | external-authority |

## import 済み source label

| label | meaning |
|---|---|
| imported-source | raw / inbox / report から FDE 内へ要点取り込み済み。元 path は通常読まない |
| imported-raw-cluster | raw external AI cluster は長文なので FDE 内では要約だけ扱う |
| external-authority | FDE外に正本があり、必要時だけ registry 経由で読む |
| planned | 置き場だけ予約済み。実体作成前 |
| missing-local | 参照候補が未配置。通常実行では読まない |

## data / policy / state 分離

| 種別 | 意味 | 置き場 |
|---|---|---|
| core | 判断の動作 | `core.md` |
| data | type / catalog / source pointer | `data-index.md` / `source-pointers.md` |
| policy | してよい/ダメ | `dependency-registry:security-baseline` / `dependency-registry:scope-gate` / `dependency-registry:fact-gate` |
| state | 現在地 / queue / blocker | `dependency-registry:lane-status` / `dependency-registry:lane-queue` |
| procedure | 手順 | `dependency-registry:playbooks` / `dependency-registry:lane-operating-card` |
| knowledge | 知見 | `dependency-registry:lessons` / `dependency-registry:reports` |

closure_rule: active

