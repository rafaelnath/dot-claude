---
name: coding-workflow
description: The user's required workflow for any code change in a repo — fixing bugs, adding features, refactoring, or otherwise editing code — and for planning code work in a repo, executing plan parts, committing, pushing, and opening PRs. Use it before making any code change, even a one-line fix. Not needed for questions about code that don't ask for a change.
---

# Coding workflow

A question gets an answer and a stop; an instruction ("fix X") is the go-ahead. For an instruction, triage first.

## Triage

Decide plan or no plan. For bugs, find the root cause first (read-only), then triage; if it can't be found, stop and report instead of guess-fixing. If a simpler approach exists, say so; push back when warranted.

**Execute immediately** only if all of these hold:
- 3 files or fewer, and about 100 changed lines or fewer. Exclude test files from both counts.
- one concern, in one repo
- no new dependency, no schema change, no public API change (endpoints, DTOs, message formats, shared signatures)
- no risky area: auth/security, money or ledger logic, data migrations, concurrency/transactions, CI/build/infra
- one reasonable reading of the request and one reasonable approach, each statable in one sentence

If it qualifies:
1. State a scope boundary (the files you expect to change) and a "done when" check, like a one-part plan entry.
2. Read [execution.md](execution.md) and follow it from Branch to PR.

A good "done when" fails before the change and passes after it: for a bug, a test that reproduces it; for a feature, tests for its behavior, including invalid inputs; for a refactor, the existing tests passing before and after. "It compiles" isn't one.

If, during the work, any criterion turns out to be broken, stop, report what's done so far and leave it uncommitted, then plan from there. The user decides whether to keep or discard the partial work.

Otherwise, plan first: read [planning.md](planning.md).

## Executing a plan part

Before starting any plan part, read [execution.md](execution.md). Start a part only when the user names it.

## Committing the user's own changes

When the user asks to commit, push, or open a PR for changes they made themselves, skip triage. Their changed files are the scope boundary, and "done when" is the build and relevant tests passing. Read [execution.md](execution.md) and follow it from Branch, skipping implement. The uncommitted-changes check before branching doesn't apply to these changes.

## Feedback on an open PR

When the user asks to address feedback on an open PR, check out its branch, read [execution.md](execution.md) and follow "After the PR is open" under Commits, then push. Don't create a new branch or PR.

## Ask vs decide

- During planning, always ask.
- During execution, if the request or plan can be read more than one way (different behavior), stop, present the readings, and ask. Don't pick silently. If several come up at once, ask them together.
- Implementation details that don't change behavior (naming, internal structure, following existing patterns) aren't interpretations: decide them, matching the existing code.
- If a check fails in a test or code the part didn't touch, run that test on the base branch (the branch the part was created from) in a temporary worktree (`git worktree add --detach <temp-dir> <base-branch>`, removed afterwards with `git worktree remove`) before fixing it. If it fails there too, it's a pre-existing failure: don't fix it, don't let it block the gate or commits, and record it under "Pre-existing failures" in the PR.

## Hard stops

Even mid-part, stop and ask before anything:
- destructive or irreversible, like deleting data, force-pushing, or rewriting history
- security-sensitive (credentials, auth, permissions) outside the approved part's scope
- with side effects beyond the part's branch, like shared branches, deploys, or external services. Pushing the part's branch and opening its PR are exempt.

Some git rules are also enforced by a hook. If a command is blocked, follow the message; never work around it.
