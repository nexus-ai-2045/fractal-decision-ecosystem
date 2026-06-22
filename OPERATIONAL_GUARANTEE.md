# 運用保証

状態: private repository 運用として保証済み

## 対象範囲

この保証は、Fractal Decision Ecosystem（FDE）の現在の private repository package を対象にします。

- repository content
- local MVP gate script
- local test
- GitHub Actions validation
- repository metadata と operating setting
- private handle と personal path の確認
- optional Linear handoff packet の local readiness
- roadmap first iteration gate の local readiness
- project-local Chinju guidance の local readiness

この保証は repository の public 化を承認しません。

## 残務

実装残務: なし

運用残務: なし

public release 残務: 人間承認が必要

patent decision 残務: なし

patent filing 実行残務: なし（optional / approval-gated）

Linear handoff 実装残務: なし

Linear issue 作成残務: なし（optional）

現在の visibility: private

## 必須検証

この package は、以下の check がすべて通った時だけ運用可能とみなします。

- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mvp_gate.ps1`
- `python scripts/linear_handoff_check.py`
- `python scripts/roadmap_gate_check.py`
- `python scripts/chinju_guidance_check.py`
- `python -m compileall -q scripts tests`
- GitHub Actions workflow `Public Ready`
- Git history の author / committer が `Nexus AI <noreply@nexus-ai.local>` である
- 明示的な publication approval まで repository visibility が private のままである
- `Patent Pending` / `特許出願中` は application filed 後だけ使う
- 外部 review 失敗には `failure_kind` と `postmortem_action` がある

## 強制チェック

`scripts/run_mvp_gate.ps1` は、Windows local の supported entrypoint として Python launcher の差を吸収します。
`scripts/mvp_gate_check.py` は、public readiness check、pre-publication gate、
`MVP_STATUS.md`、pytest を集約する private MVP gate です。
`scripts/linear_handoff_check.py` は、Linear を使う場合の optional packet、manual fallback、
post-creation evidence placeholder、TODO の境界文言を検証します。
`scripts/roadmap_gate_check.py` は、`ROADMAP.md` の Now / Next / Future、
lane、goal、evidence、gate、owner、done_when、人間目視レビュー後 merge 境界を検証します。
`scripts/chinju_guidance_check.py` は、`.chinju/` の local-first guidance、
quality gates、invariants、incidents、edge cases、外部 provider approval 境界を検証します。
内側の `scripts/public_ready_check.py` は、必須 file、local link、private handle pattern、
personal absolute path、draft status、Git history author metadata、この保証 file、
外部 review 失敗 field、GitHub Actions workflow contract を検証します。

現在の plan では、この private repository に GitHub branch protection と GitHub native secret scanning はありません。
その代わりに、local readiness check と CI workflow で補完します。
