# 運用保証

状態: private repository 運用として保証済み

## 対象範囲

この保証は、Fractal Decision Ecosystem（FDE）の現在の private repository package を対象にします。

- repository content
- local validation script
- local test
- GitHub Actions validation
- repository metadata と operating setting
- private handle と personal path の確認

この保証は repository の public 化を承認しません。

## 残務

実装残務: なし

運用残務: なし

public release 残務: 人間承認が必要

現在の visibility: private

## 必須検証

この package は、以下の check がすべて通った時だけ運用可能とみなします。

- `python scripts/public_ready_check.py`
- `python -m pytest -q`
- `python -m compileall -q scripts tests`
- GitHub Actions workflow `Public Ready`
- Git history の author / committer が `Nexus AI <noreply@nexus-ai.local>` である
- 明示的な publication approval まで repository visibility が private のままである
- 外部 review 失敗には `failure_kind` と `postmortem_action` がある

## 強制チェック

`scripts/public_ready_check.py` は、必須 file、local link、private handle pattern、
personal absolute path、draft status、Git history author metadata、この保証 file、
外部 review 失敗 field、GitHub Actions workflow contract を検証します。

現在の plan では、この private repository に GitHub branch protection と GitHub native secret scanning はありません。
その代わりに、local readiness check と CI workflow で補完します。
