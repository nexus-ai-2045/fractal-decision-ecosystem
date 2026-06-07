# Defensive Patent Review

Status: self-filing packet recommended before public release.

This document is not legal advice. It is an internal invention-disclosure
checklist for counsel or a patent professional.

## Recommendation

Do not make the full FDE operating system public before deciding whether to
file a defensive provisional patent application.

If a public release is still desired, publish only a reduced public kernel
after the patent question is handled. Attorney review is preferable, but a
provisional application can be prepared and filed without a patent attorney if
the inventor accepts the quality and enforceability risk.

## Why Patent Review Matters

Copyright can protect the expression of the FDE materials, but it does not
protect the underlying idea, procedure, system, or method of operation.

A patent, if available, can protect a new and useful technical process,
machine, manufacture, composition of matter, or improvement. For FDE, the
candidate patent surface is not "the idea of better decision routing"; it
would need to be a concrete technical implementation.

## Candidate Defensive Claims To Evaluate

These are review candidates, not claims:

1. Recursive skill-routing architecture that maps user intent through core,
   router, and leaf skill layers with machine-checked trigger-gap validation.
2. Source-pointer-based AI operating system that separates SSOT references
   from executable runtime shims across multiple AI runtimes.
3. Publication containment gate integrated with repository visibility,
   credential, external-send, hook, and completion-verification states.
4. Machine-verifiable guarantee scripts that assert trigger coverage,
   runtime coverage, SSOT pointer presence, human approval boundaries, and
   completion evidence before release.
5. Cross-runtime knowledge-operation layer that routes Codex, Claude Code,
   Grok, Mac, and Windows workspaces through one source-of-truth map without
   duplicating private source documents.

## What To Keep Private Until Review

- Full 50-skill generated layer.
- Internal source pointers and local paths.
- `Documents/brain` structure and private operating details.
- External AI route registry and absorbed-dialogue details.
- Guarantee scripts that reveal internal workflow checks.
- Prompt templates and hidden routing heuristics.

## Pre-Filing Evidence Package

Prepare these before counsel review:

- Problem statement: what technical failure FDE solves.
- Prior art notes: known skill systems, prompt routers, agent frameworks,
  workflow engines, and eval/guardrail systems.
- Novelty map: what is different from ordinary prompt libraries or MCP skills.
- Architecture diagram: core/router/leaf recursion and validation loops.
- Implementation examples: generator, index, validation scripts, sample skills.
- Human authorship/provenance log: dates, commits, prompts, edits, and design
  decisions.
- Public/private boundary: what will be disclosed versus withheld.

## Publication Rule

Until patent review is complete:

- Do not publish the full private repo.
- Do not mark anything "Patent Pending" unless an application has actually
  been filed.
- Do not disclose implementation details that may be needed for claims.
- If any disclosure is necessary, use a reduced public kernel with
  `All rights reserved` and no patent license.

## Self-Filing Rule

If filing without a patent professional:

- Include more detail, not less.
- Include diagrams and flow descriptions before filing; do not assume they can
  be added later.
- Name every actual inventor.
- File before public disclosure whenever possible.
- Treat the filing date as a defensive timestamp, not proof that a patent will
  issue.
- Calendar the 12-month deadline for nonprovisional/PCT follow-up.
- Keep the receipt, application number, submitted PDF, and exact file hash.

## Decision

Recommended next step: prepare a provisional patent disclosure packet. If speed
matters more than claim quality, self-file the provisional before public
release, then decide within 12 months whether to pursue nonprovisional/PCT.
