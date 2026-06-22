# セキュリティポリシー

## 報告

セキュリティ上の懸念は、公開前に非公開の経路で報告してください。secret、
credential、account access、機微な運用詳細について、public issue を作らないでください。

## 対象範囲

この repository は Fractal Decision Ecosystem（FDE）の文書と軽量な検証 script を含みます。
production credential、private key、personal access token、machine-local secret file を含めてはいけません。

## private MVP gate

private repository の主検証は `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mvp_gate.ps1` です。
この gate は public readiness check、pre-publication gate、pytest を集約します。

public release の前に private MVP gate と人間 review を完了してください。
reviewer が対象 repository を明示承認するまで、GitHub repository visibility を public に変更してはいけません。
