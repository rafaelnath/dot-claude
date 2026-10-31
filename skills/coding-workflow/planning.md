# Planning

## Plan file
- Produce plans with plan mode (until a substitute skill or plugin is chosen). Plan mode presents the plan and waits for approval before any edit.
- Approving the plan only saves it. Execute only the parts the user names afterwards.
- Save the plan to `.claude/plans/YYYY-MM-DD-<topic>.md` in the repo. The folder is gitignored, so the plan belongs to no branch and is never committed.
- The plan's header records the base branch: the branch the user was on when the plan was made.
- Each part has a status line, starting as `pending`. Status updates and resuming are in [execution.md](execution.md) (Plan status).

## Plan parts
Each part states its scope boundary (files and modules in and out), its dependencies on other parts (prefer none), and a "done when" check.
- Split a part only where the user could reject one half of the PR and approve the other.
- Fold setup, config and docs work into the part that needs it instead of making it a separate part.
- As a backstop, a part over about 5 files or about 300 changed lines needs a reason not to be split. Exclude test files from both counts.

## Interfaces between parts
A part that depends on another part names the exact contract it uses from it (e.g. "uses `SkuService.findBySku(String) → Optional<Sku>` from Part 2"), and the part providing it lists the same under "Produces". Independent parts skip this. If review would change a contract, stop and ask.
