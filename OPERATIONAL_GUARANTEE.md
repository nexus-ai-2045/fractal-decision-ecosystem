# Operational Guarantee

Status: guaranteed for private-repository operation

## Scope

This guarantee covers the current private repository package for Fractal
Decision Ecosystem（FDE）:

- repository content
- local validation scripts
- local tests
- GitHub Actions validation
- repository metadata and operating settings
- private-handle and personal-path checks

It does not authorize making the repository public.

## Residuals

Implementation residual: none

Operational residual: none

Public-release residual: human approval required

Current visibility: private

## Required Verification

The package is considered operational only when all checks below pass:

- `python scripts/public_ready_check.py`
- `python -m pytest -q`
- `python -m compileall -q scripts tests`
- GitHub Actions workflow `Public Ready`
- Git history author and committer use `Nexus AI <noreply@nexus-ai.local>`
- repository visibility remains private until explicit publication approval

## Enforcement

`scripts/public_ready_check.py` enforces required files, local links, private
handle patterns, personal absolute paths, draft status, Git history author
metadata, this guarantee file, and the GitHub Actions workflow contract.

GitHub branch protection and GitHub native secret scanning are not available for
this private repository on the current plan. The repository compensates with the
local readiness check and CI workflow.
