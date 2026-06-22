# Quality Gates

Project-specific commands for local FDE operation.

```powershell
python scripts\mvp_gate_check.py
python scripts\linear_handoff_check.py
python scripts\chinju_guidance_check.py
python scripts\adr_next.py
python scripts\public_ready_check.py
python scripts\pre_publication_gate_check.py --json
python -m compileall -q scripts tests
python -m pytest -q
```

Before commit, merge, release, publication discussion, or handoff, confirm the relevant gates for the touched area.

For private local MVP completion, `python scripts\mvp_gate_check.py` is the top-level gate.

For optional Linear handoff, `python scripts\linear_handoff_check.py` must pass and `LINEAR_ISSUE_RECORD.md` remains optional unless Linear is actually used.

For public release, these local gates are necessary but not sufficient. Exact repository approval and human review are still required.
