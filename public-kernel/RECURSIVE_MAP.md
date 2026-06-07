# Recursive Map

The public FDE kernel uses a three-layer routing map.

```text
User request
  -> Core gate
  -> Router choice
  -> Leaf source pointer
  -> Evidence-backed action or hold
  -> Done verification
```

## Core

Core gates protect truth, scope, rights, safety, and completion claims.

## Router

Router logic chooses the correct lane, runtime, or public/private path.

## Leaf

Leaf modules point to the minimum source needed for the task. The private
implementation uses richer source pointers that are intentionally not disclosed
in this public kernel.
