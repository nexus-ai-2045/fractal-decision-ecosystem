# FDE MVP Status

MVP status: complete for private local gate

## Current Decision

- Repository visibility: private
- No external publication action performed
- No patent filing action performed; filing is optional and approval-gated
- No connector write action performed
- Inventor decision: user-confirmed sole inventor
- Owner decision: user retains ownership
- Assignee decision: none / unassigned
- Rights strategy: keep patent / filing details intentionally broad until a separate filing decision or action is approved
- Guard wording strategy: use `Patent Pending` / `特許出願中` only after an application is actually filed
- Local MVP gate command: `python scripts\mvp_gate_check.py`

## Completed Local Gate

- Public readiness check is part of the MVP gate.
- Pre-publication gate check is part of the MVP gate.
- Pytest is part of the MVP gate.
- The public kernel remains a sanitized candidate, not a release action.

## Remaining Human / External Blockers

- Treat patent filing as optional external work, not local implementation residue.
- If filing is later chosen, perform it only with explicit current-conversation approval.
- If filing happens later, save filing receipt / application number / submitted PDF / file hash after filing.
- Keep `Patent Pending` wording unused until an application is actually filed.
- Keep GitHub repository visibility private unless exact repo-specific approval is given.

## Next

Next milestone: publication approval only if public release is requested
