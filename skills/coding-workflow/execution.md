# Execution

Follow these in order: branch, implement, pre-review gate, review loop, commits, PR, then stop.

## Branch
- Before branching, run `git status --porcelain`. If anything is uncommitted, stop and ask the user how to handle it.
- Branch from the plan's base branch (for a small task or the user's own changes: the branch the user is on), unless the user chose to branch from a dependency's branch: `<type>/<short-slug>` (e.g. `fix/RBM-17-null-sku`), where `<type>` is one of the commit types below.
- The branch a part was created from is its base branch: diff and test against it, and target its PR at it.
- Never commit to the base branch.
- One PR per part by default. When the user approves several parts in one request, put them on one branch with one PR. If they're unrelated concerns, give each its own branch and PR instead, done one after another without stopping in between. Each part's commits stay separate, so one part can still be reverted. Run the pre-review gate and review loop for each part separately.

## Execution mode
Implement each part yourself in the current session. Use an implementer subagent only when the user asks for it. When the session is already heavy, suggest continuing the next part in a fresh session from the plan file.

## Plan status
For a plan part (small tasks have no plan file):
- The plan lives at `.claude/plans/YYYY-MM-DD-<topic>.md` in the repo.
- To resume, read the plan file, check each open PR's state with `gh pr view` (merged state isn't recorded in the file), and take the part(s) the user names.
- Update the part's status line as it moves:
  - `pending`
  - `in progress (<branch>)`: when the part starts
  - `PR #<n> open (<branch>)`: when its PR opens
  - `dropped (<reason>)`: only when the user says so

## Pre-review gate
Before review, check the part against its plan entry (for a small task: the scope boundary and "done when" stated at triage; for the user's own changes: their changed files, and the build plus relevant tests). Both results go in the PR description:
- Every changed file must be inside its scope boundary. Explain or revert any that aren't.
- Every changed line must trace to the request. Don't improve adjacent code, comments or formatting, or refactor what isn't broken. Remove imports, variables and functions your change made unused; mention unrelated dead code instead of deleting it.
- Its "done when" check must pass. Pre-existing failures (see Ask vs decide in SKILL.md) don't block it.

## Review loop
Once the part passes the pre-review gate:
1. Review the part with the reviewer agent for each language in its diff (e.g. `java-reviewer`, `vue-reviewer`), each on its own files. Files with no matching reviewer, or every file if no reviewer agents are installed, go to `/code-review`.
2. Sort findings by severity.
3. Fix critical and important findings, or explain why a finding isn't valid. If a fix would change a contract the part lists under "Produces" or uses from another part, stop and ask.
4. Re-review, up to 3 rounds in total.
5. If critical or important findings remain after round 3, stop and ask the user: fix further, accept them (listed under "Open findings" in the PR), or drop the part. If they drop it, ask whether to discard or keep the uncommitted work, and set its plan status to `dropped (<reason>)`.
6. Re-run the pre-review gate after the last round.
7. Remaining minor findings go in the PR description for the user to decide on.

### Reviewer agents
- Live in `~/.claude/agents/`, shared across projects.
- Report every finding as critical, important or minor.
- Apply the project's CLAUDE.md rules on top of their language checks; don't duplicate them.

## Commits
Don't commit while working on a part. Commit only after the pre-review gate and the review loop pass.
- **Atomic:** each commit is one logical change, never mixes parts, and builds with its tests passing on its own.
- **Verify each commit:** stage only that commit's changes, set the rest aside with `git stash push --keep-index -u`, run the build and relevant tests, commit, then `git stash pop`. To stage part of a file, apply a patch to the index with `git apply --cached` (interactive `git add -p` isn't available).
- **If a change can't stand alone** (it doesn't build without another change in the same part), combine the two into one commit.
- **After the PR is open:** address feedback with new atomic commits, run through the review loop scoped to those commits. Never amend.

### Commit messages
Conventional Commits: `<type>(<scope>): <summary>`
- **type:** `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `build`, `ci`, `style`, `revert`. It usually matches the branch type.
- **scope:** the ticket ID if there is one (`RBM-17`), otherwise the component (`receipt`).
- **summary:** lowercase imperative ("handle", not "handled"). The whole subject line is 72 characters or fewer.
- **body:** why the change was made, plus notable details, wrapped at 72 characters.
- Pass the message inline with `-m`.
- No attribution lines.

## PR
Push the branch and open a PR targeting the branch it was created from. Never merge it; the user reviews and merges. The PR description has these sections, omitting any that are empty (for a bundled PR, give the scope check and done-when result per part):
- **Scope check:** changed files, all inside the boundary, or explained
- **Done when:** the command and its result
- **Decisions made:** notable implementation choices (e.g. reused `SkuValidator` instead of adding a new check)
- **Open findings:** critical or important findings the user accepted
- **Minor findings:** for the user to decide on
- **Pre-existing failures**

## Next part
After opening a PR, stop. Start another part only when the user names it. If the named part depends on a part that is neither merged nor on the current branch, say so and ask whether to wait or branch from that part's branch.
