# AI contact safety contract

Status: active concept / review-ready

## 目的

AI同士の contact を、FDE の `entry -> packet -> evidence -> decision -> closure` に戻すための抽象安全契約です。

この file は device app、OS service、Wi-Fi、Bluetooth、avatar、音声UI、download data bundle の製品仕様ではありません。それらは別 product / life-commons-system 側の設計候補として扱い、FDE では contact 前後の判断契約だけを持ちます。

## 基本形

```text
contact entry
-> packet
-> identity / consent check
-> data boundary check
-> evidence
-> decision
-> closure
```

## Contact Identity Contract

自動 contact は、次の項目が未設計なら `blocked` とします。

| field | 見ること |
|---|---|
| `actor` | contact を開始するAI / user / device |
| `peer` | 相手AI / user / device / service |
| `verification_method` | 相手確認の方法。未確認なら trusted 扱いしない |
| `consent_scope` | 何を話してよいか、どの操作まで許可されるか |
| `expiry` | 同意や信頼がいつ失効するか |
| `revocation` | ユーザーが許可を取り消す方法 |
| `blocklist` | 再接触拒否、なりすまし、危険相手の停止線 |
| `replay_protection` | 過去の同意や古い文脈を再利用しないための条件 |

## Data Boundary Contract

contact に渡す data は、便利な文脈束ではなく、最小化された reviewable payload とします。

| field | 見ること |
|---|---|
| `sensitivity` | public / internal / private / secret のどれか |
| `recipient_class` | 相手が本人、信頼相手、未確認相手、外部serviceのどれか |
| `allowed_fields` | 渡してよい項目 |
| `redaction_required` | 伏せるべき個人情報、private handle、source pointer |
| `ttl` | payload の有効期限 |
| `checksum` | 送った内容を後で照合するためのfingerprint |
| `human_approved_at` | 人間確認が必要なpayloadの承認時刻 |
| `no_raw_source_pointer` | private source pointer を丸ごと送らない条件 |

## Contact Packet Schema Candidate

FDE で扱う contact packet は、transport 実装ではなく reviewable な判断入力です。
この schema candidate は、実際に送る payload ではなく、事前レビューで不足を見つけるための最小形です。

```text
contact_packet:
  packet_id:
  actor:
  peer:
  purpose:
  identity:
    verification_method:
    verification_evidence:
  consent:
    consent_scope:
    expiry:
    revocation:
  data_boundary:
    sensitivity:
    recipient_class:
    allowed_fields:
    redaction_required:
    ttl:
    checksum:
    human_approved_at:
    no_raw_source_pointer:
  safety:
    blocklist:
    replay_protection:
    transport_adapter_status: unapproved
  closure:
    decision:
    next_contact_allowed:
    evidence_pointer:
```

`packet_id`、`verification_method`、`consent_scope`、`ttl`、`checksum`、
`human_approved_at`、`replay_protection`、`transport_adapter_status` が未設定なら、
contact は `blocked` とします。

## Transport Boundary

FDE は transport を実装しません。transport adapter は未承認であり、identity / consent / data boundary が通るまで採用しません。

通信方式の候補名はこの contract の採用根拠ではありません。近距離通信、peer通信、cloud relay、音声、avatar のどれであっても、FDE では contact packet と evidence を同じ形で扱います。

## Closure

contact 後は次を残します。

- 誰と contact したか。
- 何を渡したか。
- どの consent / boundary を通したか。
- 何を採用、保留、拒否したか。
- 次の contact を許可するか、止めるか。

## Stop Lines

- この contract は外部送信、相手AIへの自動contact、Wi-Fi / Bluetooth / P2P / cloud relay 実装を承認しません。
- device app、OS service、avatar、音声UI、download data bundle の製品設計は FDE 本体ではなく別 product 設計へ分離します。
- public release、repository visibility 変更、patent filing は別承認です。
