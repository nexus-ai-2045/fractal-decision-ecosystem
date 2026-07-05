# FDE Publication Review Packet

Status: review packet only / no public action approved
Date: 2026-07-05

この packet は、将来 public release、repository visibility 変更、external send、
patent filing を検討する時の人間レビュー用 checklist です。
この file 自体は、それらの action を承認しません。

## Target

- Repository: `nexus-ai-2045/fractal-decision-ecosystem`
- Current visibility: private
- Approved operation now: none
- External actions performed by this packet: false

## If Repository Visibility Changes

GitHub repository を public に変更すると、少なくとも次が web 上で visible になります。

- commit history
- tracked files
- pull request metadata
- issue / discussion / release surfaces if enabled later
- license and rights posture
- public-kernel candidate

Visibility change は、次の exact operation が現在の会話で明示承認されるまで実行しません。

```text
gh repo edit nexus-ai-2045/fractal-decision-ecosystem --visibility public
```

## Required Human Review Before Any Public Action

- target repository in `owner/name` form
- exact operation / command
- visible content summary
- README review
- LICENSE review
- SECURITY.md review
- PUBLIC_READY.md review
- personal path scan
- secret scan
- public-kernel diff manifest
- patent / rights wording review
- confirmation that `Patent Pending` is not used before actual filing
- confirmation that private source pointers and machine-local procedures are not included in public candidate

## Local Evidence Bundle

- `PUBLIC_READY.md`
- `SECURITY.md`
- `LICENSE`
- `RIGHTS_NOTICE.md`
- `PUBLIC_KERNEL_PLAN.md`
- `TODO_FDE_PUBLIC_KERNEL_RIGHTS.md`
- `public-kernel/`
- `scripts/public_ready_check.py`
- `scripts/pre_publication_gate_check.py`
- `scripts/public_kernel_diff_manifest.py`
- `scripts/human_review_packet_check.py`

## Stop Lines

- Do not make the repository public from this packet.
- Do not submit a patent filing from this packet.
- Do not send external messages from this packet.
- Do not treat local gate success as publication approval.
- Do not treat public-kernel candidate as the full private operating package.
