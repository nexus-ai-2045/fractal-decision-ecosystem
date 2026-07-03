# FDE Public Gates

## Pre-Execution Fact Check

実行前に、known facts、inferences、unknowns を分けます。memory や assumption
より source evidence を優先します。

## Scope Routing

変更前に、正しい work surface、source boundary、public/private classification
を決めます。

### Orchestration Probe

Scope routing では、作業を main runtime だけで閉じるか、bounded delegate
へ分けるかも最初に判定します。これは追加の gate ではなく、scope routing
を迷子にしないための薄い probe です。

最小 probe は次を分けます。

- `initial_size_probe`: 対象 file 数、論点数、必要 tool 数、実装と検証の有無、
  長い diff / log、publication boundary の有無を短く見積もる。
- `orchestration_required`: tiny なら main runtime、non-trivial なら bounded
  delegate、publication / secret / auth / settings / destructive operation は
  main runtime が停止線を保持する。
- `delegate_plan`: 委任する場合は、要約、候補抽出、log 圧縮、second-pass
  risk check など、採否判断を奪わない薄い task に限定する。
- `no_delegate_reason`: 委任しない場合は、小さすぎる、tool 不在、停止線あり、
  overhead が価値を上回る、のように理由を残す。

delegate は evidence を返す補助であり、public/private classification、
publication approval、credential / auth / settings / destructive operation、
final decision は main runtime が保持します。

## Publication Containment

public release、external send、repository visibility change、credential change、
hook enablement、settings change、auth change、connector write の前には、
現在の会話で explicit human approval を必須にします。

## Done Verification Closeout

done と言う前に、何を変更したか、どの evidence を確認したか、何が未検証か、
どの risk が残るかを報告します。
