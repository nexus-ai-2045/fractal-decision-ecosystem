# FDE ロードマップ

状態: first iteration ready / local implementation residue zero

外部 action: none

このロードマップは、Fractal Decision Ecosystem（FDE）の private repository 内で最初の実装サイクルを始めるための作業正本です。public release、repository visibility 変更、外部投稿、告知、送信は承認しません。

## 方針

- roadmap は機能一覧ではなく、`goal / evidence / gate / owner / done_when` を持つ運用 contract として扱う。
- Now / Next / Future は release plan ではなく、現在の優先度、次の検証、将来候補を分けるために使う。
- merge は人間目視レビュー後にだけ行う。
- human review 前のPRは draft または review待ちとして扱い、公開・visibility 変更へ進めない。

## Now

| lane | goal | evidence | gate | owner | done_when |
|---|---|---|---|---|---|
| Core/Product | FDE の価値仮説と使い方を1つの入口へ束ねる | `README.md` / `operating-card.md` / `ROADMAP.md` | roadmap gate | Codex + human | 最初のPRで roadmap gate が通る |
| UX/Product Design | 読む人が迷わず入口、境界、次アクションを見つけられるようにする | `README.md` / `visual.html` | human review | human | 目視で入口と境界が確認される |
| Security | 公開・secret・visibility・LLM security の停止線を維持する | `PUBLIC_READY.md` / `SECURITY.md` / scripts | pre-publication gate | Codex | local gate が external action false で通る |
| AI/OpenAI Dev | AI実装を eval / smoke / preflight で閉じる | `tests/` / `scripts/` | pytest + mvp gate | Codex | pytest と MVP gate が通る |
| Creative/Comms | 公開候補素材と説明素材を human review 前提に分ける | `assets/` / `PUBLIC_KERNEL_PLAN.md` | publication containment gate | human | 公開前の未承認境界が明記される |
| Operations | PR、review、merge の手順を外部影響ゲートつきで運用する | Git branch / PR / checks | human review before merge | Codex + human | PR作成後、merge前に人間確認が残る |

## Next

- Local implementation residue: none.
- Roadmap gate is already connected to `scripts/mvp_gate_check.py`.
- Product Design / Security / Creative / OpenAI Dev の追加TDDサイクルは、次に明示された実装要求が出た場合だけ切る。
- PR / merge / public release は、このロードマップでは承認しない。必要な場合は `smoke -> preflight -> diff review -> PR -> human review -> merge` の順序を別承認で記録する。

## Future

- design system maturity、SAMM/SSDF maturity、eval-driven AI development、creative operations governance を lane 別の成熟度表へ落とす。
- public kernel と private operating package の差分を、公開前チェックで機械確認できるようにする。
- human review 後の merge receipt と post-merge verification を `OPERATIONAL_GUARANTEE.md` に反映する。

## Stop Lines

- repository public 化はこのロードマップでは承認しない。
- external posting、announcement、submission、public release はこのロードマップでは承認しない。
- merge は人間目視レビュー後の明示GOまで実行しない。
