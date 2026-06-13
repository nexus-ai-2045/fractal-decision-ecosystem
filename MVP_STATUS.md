# FDE MVP Status

MVP status: complete for private local gate

## Current Decision

- Repository visibility: private
- No external publication action performed
- No patent filing action performed
- No connector write action performed
- Inventor decision: user-confirmed sole inventor
- Owner decision: user retains ownership
- Assignee decision: none / unassigned
- Filing strategy: self-file defensive provisional patent application before any public disclosure
- Guard wording strategy: use `Patent Pending` / `特許出願中` only after an application is actually filed
- Local MVP gate command: `python scripts\mvp_gate_check.py`

## Completed Local Gate

- Public readiness check is part of the MVP gate.
- Pre-publication gate check is part of the MVP gate.
- Pytest is part of the MVP gate.
- The public kernel remains a sanitized candidate, not a release action.

## Remaining Human / External Blockers

- Perform patent filing only with explicit current-conversation approval.
- Save filing receipt / application number / submitted PDF / file hash after filing.
- Calendar 12-month nonprovisional / PCT follow-up deadline after filing.
- Keep `Patent Pending` wording unused until an application is actually filed.
- Keep GitHub repository visibility private unless exact repo-specific approval is given.

## Next

Next milestone: provisional filing execution
