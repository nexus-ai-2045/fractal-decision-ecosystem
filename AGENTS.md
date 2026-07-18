# Repository Safety Rules

## Human Review And Publication

Human review is required before anything in this repository is treated as ready for public release, debut, launch, announcement, submission, posting, or broad sharing.

Do not publish, release, announce, submit, post, share broadly, or otherwise make work public without explicit human review and explicit user approval in the current conversation.

Do not treat broad phrases such as "publish", "share", "post progress", "put it on GitHub", "make it public", or similar wording as permission to skip human review.

Before any public-facing action, clearly state what would become visible, what review has or has not happened, and wait for a clear yes from the user.

## GitHub Repository Visibility

Repository visibility changes are destructive/publication actions.

Never make this GitHub repository public through Codex, CLI, API, GitHub connector, Chrome extension, browser automation, or recurring automation without explicit, repository-specific user confirmation in the current conversation.

Before changing this repository to public, state all of the following and wait for a clear yes:

- Target repository in `owner/name` form.
- Exact operation, such as `gh repo edit owner/name --visibility public`.
- Confirmation that README, license, SECURITY.md, secret scan, personal path scan, and PUBLIC_READY.md have been checked.
- Reminder that commit history and files become visible on the web.

Never create a public GitHub repository by default. New repositories must be private unless the user explicitly says the exact repository should be public.

Never run automation that changes repository visibility. Automations may report visibility and readiness status only.

## Cursor Cloud specific instructions

This is the FDE (Fractal Decision Ecosystem) product: a Python + Markdown AI-governance "control plane". There are no long-running servers, databases, or web backends. Development readiness means running the pytest suite and the aggregate governance gate. Requirements are just `pytest` + `jsonschema` (see `requirements-dev.txt`); the update script installs them.

- Tests: `python3 -m pytest -q` (config in `pyproject.toml`; `pythonpath=["."]`).
- Aggregate gate (core end-to-end check, cross-platform): `python3 -m scripts.mvp_gate_check` (add `--json` for machine output, `--skip-pytest` to skip tests). It runs all sub-gates plus pytest and prints per-check OK/FAIL.
- The canonical wrapper `scripts/run_mvp_gate.ps1` requires PowerShell (`pwsh`), which is NOT installed and is not needed — use the `python3 -m scripts.mvp_gate_check` equivalent instead.
- No dedicated linter is configured. The "verify" layer is the gate scripts, not a code linter. For a Python syntax check: `python3 -m compileall scripts tests`.
- Several gates run `git ls-files`/diff, so keep a clean git working tree when running them (untracked required files can trip `required_files_tracked`).
- Visual entry point: `visual.html` is a static file. To preview it, serve the repo (e.g. `python3 -m http.server 8099`) and open `http://localhost:8099/visual.html`.
- `pip install` here defaults to a `--user` install; the `pytest` console script lands in `~/.local/bin` (not on PATH), so invoke via `python3 -m pytest` rather than bare `pytest`.
