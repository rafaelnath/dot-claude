# Planning

## Triage
A question gets an answer and a stop; an instruction ("fix X") is the go-ahead. For an instruction, decide plan or no plan using the criteria below.

**Execute immediately** only if all of these hold. For bugs, find the root cause first (read-only), then triage; if it can't be found, stop and report instead of guess-fixing.
- 3 files or fewer, and about 100 changed lines or fewer, not counting tests
- one concern, in one repo
- no new dependency, no schema change, no public API change (endpoints, DTOs, message formats, shared signatures)
- no risky area: auth/security, money or ledger logic, data migrations, concurrency/transactions, CI/build/infra
- one reasonable reading of the request and one reasonable approach, each statable in one sentence

Otherwise, plan first.

- **Small:** implement it right away and run its "done when" check without committing. Then ask whether to finish it fully (branch, review loop, commit/push, PR), skip all of that, or pick some steps.
- **Turns out bigger than expected:** stop, report what's done so far and leave it uncommitted, then plan from there. The user decides whether to keep or discard the partial work.

## Plan file
- Produce plans with plan mode (until a substitute skill or plugin is chosen). Plan mode presents the plan and waits for approval before any edit.
- Save the plan to `.claude/plans/YYYY-MM-DD-<topic>.md` in the repo. The folder is gitignored, so the plan belongs to no branch and is never committed.
- Each part has a status line, updated when the part starts and when its PR opens:
  - `pending`
  - `in progress (<branch>)`
  - `PR #<n> open (<branch>)`
  - `dropped (<reason>)`
- Merged state isn't recorded in the file; check it with `gh pr view` when resuming.
- To resume, read the plan file, check PR states, and take the part(s) the user names.

## Plan parts
Each part states its scope boundary (files and modules in and out), its dependencies on other parts (prefer none), and a "done when" check.
- Split a part only where the user could reject one half of the PR and approve the other.
- Fold setup, config and docs work into the part that needs it instead of making it a separate part.
- As a backstop, a part over about 5 files or about 300 changed lines needs a reason not to be split.

## Interfaces between parts
A part that depends on another part names the exact contract it uses from it (e.g. "uses `SkuService.findBySku(String) → Optional<Sku>` from Part 2"), and the part providing it lists the same under "Produces". Independent parts skip this. If review changes a contract, update the dependent part's entry or reject the change.

# Execution

## Branch
Create a branch from the user's current working branch: `<type>/<short-slug>` (e.g. `fix/RBM-17-null-sku`). Never commit to the working branch. When the user approves several parts in one request, put them on one branch with one PR, unless they're unrelated concerns.

## Execution mode
Implement each part yourself in the current session. Use an implementer subagent only when the user asks for it. When the session is already heavy, suggest continuing the next part in a fresh session from the plan file.

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

## Commits
Don't commit while working on a part. Commit only after the pre-review gate, the review loop, and the quality gate (if any) pass.
- **Atomic:** each commit is one logical change (usually one plan item), never mixes parts, and builds with its tests passing on its own.
- **Verify each commit:** stage only that commit's changes, set the rest aside with `git stash push --keep-index`, run the build and relevant tests, commit, then `git stash pop`.
- **If an item can't stand alone** (it doesn't build without another item), combine the two into one commit.
- **After the PR is open:** address feedback with new commits, also atomic. Never amend or force-push.

### Commit messages
Conventional Commits: `<type>(<scope>): <summary>`
- **type:** `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, etc. It usually matches the branch type.
- **scope:** the ticket ID if there is one (`RBM-17`), otherwise the component (`receipt`).
- **summary:** lowercase imperative ("handle", not "handled"). The whole subject line is 72 characters or fewer.
- **body:** why the change was made, plus notable details, wrapped at 72 characters.
- No attribution lines.

## PR
Push the branch and open a PR targeting the branch it was created from. Never merge it; the user reviews and merges. The PR description has these sections, omitting any that are empty:
- **Scope check:** changed files, all inside the boundary, or explained
- **Done when:** the command and its result
- **Decisions made**
- **Minor findings:** for the user to decide on
- **Pre-existing failures**

## Next part
After opening a PR, stop. Start another part only when the user names it. If the named part depends on a part whose PR isn't merged yet, say so and ask whether to wait or branch from that part's branch.

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
