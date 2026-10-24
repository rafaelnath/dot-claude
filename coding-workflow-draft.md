# Planning

## Sizing test
Alongside the numeric caps:
- Split a part only where the user could reject one half of the PR and approve the other.
- Fold setup, config and docs work into the part that needs it instead of making it a separate part.

## Interfaces between parts
A part that depends on another part names the exact contract it uses from it (e.g. "uses `SkuService.findBySku(String) → Optional<Sku>` from Part 2"), and the part providing it lists the same under "Produces". Independent parts skip this. If review changes a contract, update the dependent part's entry or reject the change.

# Execution

## Pre-review gate
Before review, check the part against its plan entry:
- Every changed file must be inside its scope boundary. Explain or revert any that aren't.
- Its "done when" check must pass.

Put both results in the PR description.

## Review loop
Once the part passes the pre-review gate:
1. Review the part with the reviewer agent for each language in its diff (e.g. `java-reviewer`, `vue-reviewer`), each on its own files. Files with no matching reviewer go to `/code-review`.
2. Sort findings by severity.
3. Fix critical and important findings.
4. Re-review, capped at 2–3 rounds.
5. List the remaining minor findings in the PR description for the user to decide on.

### Reviewer agents
- Live in `~/.claude/agents/`, shared across projects.
- Report every finding as critical, important or minor.
- Apply the project's CLAUDE.md rules on top of their language checks; don't duplicate them.

## Ask vs decide
- During planning, always ask.
- During execution of an approved part, decide small ambiguities yourself and record them under "Decisions made" in the PR description.
- Stop and ask only if the answer would change the part's scope, approach, or interfaces.
- If a check fails in a test or code the part didn't touch, run that test on the base branch before fixing it. If it fails there too, don't fix it; record it in the PR under "Pre-existing failures".

### Hard stops
Even mid-part, stop and ask before anything:
- destructive or irreversible, like deleting data, force-pushing, or rewriting history
- security-sensitive, like credentials, auth, or permissions
- with side effects beyond the part's branch, like shared branches, deploys, or external services
