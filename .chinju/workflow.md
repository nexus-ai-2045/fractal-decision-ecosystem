# chinju Workflow

## Default Change Loop

1. Run `/spec` before implementation.
2. Implement the smallest safe change.
3. Run `/regression` against the current diff, PR, or branch.
4. Use `/fix` for repair planning when findings appear.
5. Run `/regression` again after fixes.
6. Run the project quality gates.
7. Commit, PR, merge, or release only when permissions and repo capabilities allow it.

If a step cannot run, write a handoff with the reason and the next manual action.
