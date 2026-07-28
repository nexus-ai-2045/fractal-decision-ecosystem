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

## 検証

```powershell
python scripts/fde_feedback_packet.py --input <feedback.json> --json
```

検証はread-onlyです。packetの保存、外部送信、repository変更は行いません。

正本schemaは`schemas/fde_feedback_packet.v1.schema.json`です。consumer側に互換schemaを置く場合も、`schema_version`を変更せず独自fieldを加えてはなりません。契約変更は新しいversionで行います。
