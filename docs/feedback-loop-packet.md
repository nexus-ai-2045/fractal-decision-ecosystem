# FDE feedback packet

`fde.feedback.v1`は、FDEと実装保証runtimeの間で学びを受け渡す最小契約です。

## 責務

- FDEは、問い、scope、owner、risk、human gate、学習の戻り先を決めます。
- 実装保証runtimeは、Plan / Do / Check / Actの実行証拠を作ります。
- FDEは受領した`act.next_plan_input`を次のroute判断へ戻します。
- packetは会話全文やraw tool outputを運びません。`check.evidence`は`kind + ref`の型付きpointerとし、次Planには必要最小限の判断だけを運びます。

## 流れ

```text
FDE route
  -> implementation runtime Plan / Do / Check / Act
  -> fde.feedback.v1
  -> FDE validate
  -> system updateまたはhuman gate
  -> next Plan
```

## Autonomy bridge

Autonomous Execution の target workflow は、`intake.return_path` で戻り先を固定します。

- `kind` は `feedback_packet` のみ
- `schema` は `fde.feedback.v1` のみ
- workflow 側の `autonomy_contract.return_packet=fde.feedback.v1` と同じ値に揃える

これは schema 上の接続契約です。実行停止線は従来どおり `review_packet` です。

- **許可:** target workflow の metadata-only receipt から `fde.feedback.v1` の **draft** を生成し、validate すること。draft の `act.decision` は `hold` / `revise` のみで、`check.human_review` は `pending`、`boundaries.external_actions_performed` は false 固定です。
- **禁止:** runtime が `act.decision=adopt` を出すこと、学習を自動適用すること、push / PR / merge / 外部送信へ進むこと。

closeout の薄い `feedback` field（failure_kind 等）は **execution receipt 用の別契約**であり、`fde.feedback.v1` 本体ではありません。

local chat / session からの呼び出し順は `docs/local-chat-integration-map.md` を正本とします。raw chat や raw tool output は packet に入れません。

## 検証

```powershell
python scripts/fde_feedback_packet.py --input <feedback.json> --json
python scripts/fde_feedback_packet.py --from-receipt <receipt.json> --manifest <manifest.json> --write <draft.json> --json
```

`--input` 検証はread-onlyです。`--from-receipt` は metadata-only draft を組み立てて validate し、`--write` 指定時だけ local JSON を書きます。外部送信、repository visibility 変更、adopt は行いません。

`act.decision=adopt`はpacket内の自己申告だけでは許可されません。公開CLIは承認contextを受け取らず、常にfail-closedです。FDE内部で採用判断する場合だけ、FDEが所有する承認状態と照合した承認済みpacketのcanonical SHA-256集合をprogrammatic validatorへ渡します。IDだけの承認は、review後の内容差し替えを防げないため使いません。

`act.failure_kind`、`act.regression_test`、`act.update_targets`は`fde_workflow.yaml`のfeedback / system-update契約に揃えます。新しいtargetを増やす場合はpacketだけでなくworkflow contractもversion更新します。

成功してシステム更新が不要な場合だけ、`act.failure_kind`は`none`、`act.update_targets`は`["none"]`にします。失敗または改善がある場合は`none`を混ぜず、`route / skill / gate / test / ssot / roadmap`から選びます。

検証CLIは入力を読み込む前にサイズ上限（128 KiB）を検査し、whitespace-onlyの必須文字列とsecret/personal-path混入をfail-closedで拒否します。aggregate gateでは`docs/feedback-loop-packet.md`、`schemas/fde_feedback_packet.v1.schema.json`、`scripts/fde_feedback_packet.py`、`tests/test_feedback_packet.py`を必須tracked fileとして扱います。

正本schemaは`schemas/fde_feedback_packet.v1.schema.json`です。consumer側に互換schemaを置く場合も、`schema_version`を変更せず独自fieldを加えてはなりません。契約変更は新しいversionで行います。
