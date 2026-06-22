# Invariants

- FDE remains private unless exact repo-specific public visibility approval is given in the current conversation.
- Public release is never implied by local MVP completion.
- Patent filing is optional external work and is never implied by local MVP completion.
- `Patent Pending` / `特許出願中` is not used until an application is actually filed.
- Linear handoff is optional and must not become a local operation blocker.
- The public kernel stays sanitized and separate from the private FDE operating system.
- Local gates must preserve `external_actions_performed: false`.
- Completion claims must separate implementation complete, operationally guaranteed, and publicly releasable.
- Durable repo behavior decisions use repo-local ADRs under `decisions/` and `python scripts\adr_next.py` for auto-numbering.
