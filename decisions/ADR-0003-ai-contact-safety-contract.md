# ADR-0003: AI contact safety contract

Status: accepted
Date: 2026-07-02

## Context

ユーザーから、隣接 product / life-commons-system 側では、掲示板のような情報面だけでなく、device app、OS service、AI同士の通信、音声、avatar、初期設定、download data まで含む体験として考えたい、という方向性が示されました。

批判レビューでは、この構想をそのまま FDE の required MVP surface に入れると、FDE の責務が「判断OS」から product / app spec へ広がりすぎると判断しました。FDE は product 体験を保持せず、隣接 product から来る contact 構想を判断契約へ抽象化します。

## Decision

FDE には device app / OS service / avatar / transport の製品仕様を入れません。

FDE に残すのは、AI同士の contact を安全に扱うための抽象契約です。具体的には、contact を次の形へ戻します。

```text
contact entry -> packet -> identity / consent check -> data boundary check -> evidence -> decision -> closure
```

詳細は `ai-contact-safety-contract.md` に置きます。

## Consequences

- FDE は AI contact の実装構想ではなく、contact 前後の判断契約を持ちます。
- device app、OS service、avatar、音声UI、download data bundle は FDE 本体から分離し、別 product / life-commons-system 側の候補として扱います。
- transport 名は採用根拠にしません。identity、consent、data boundary、evidence、closure が先です。
- 自動 contact は、identity / consent / data boundary が未設計なら `blocked` とします。

## Alternatives Considered

| alternative | 判断 |
|---|---|
| device app / OS service 構想をFDEのMVP gate必須にする | scope が広すぎるため不採用 |
| FDEから完全に削除する | AI同士の contact をFDE packetへ戻す抽象価値があるため不採用 |
| FDEには抽象安全契約だけ残す | 採用 |

## Non-Goals

- この ADR は Wi-Fi、Bluetooth、P2P、PCP、cloud relay の実装を承認しません。
- この ADR は外部AI送信、相手AIへの自動contact、public release、repository visibility 変更を承認しません。
- この ADR は avatar asset、音声UI、OS integration、download data bundle UX を今すぐ作る決定ではありません。

## Verification

- `ai-contact-safety-contract.md` が抽象安全契約として存在する。
- `python scripts\public_ready_check.py` と MVP gate が、この ADR と安全契約を required documentation として確認する。
- テストは単語存在だけでなく、`blocked`、`identity / consent / data boundary`、外部送信非承認を確認する。
