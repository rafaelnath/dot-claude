---
name: coding-workflow
description: The user's required workflow for any code change in a repo — fixing bugs, adding features, refactoring, or otherwise editing code — and for planning work, executing plan parts, committing, pushing, and opening PRs. Use it before making any code change, even a one-line fix. Not needed for questions about code that don't ask for a change.
---

# Coding workflow

A question gets an answer and a stop; an instruction ("fix X") is the go-ahead. For an instruction, triage first.

## Triage

Decide plan or no plan. For bugs, find the root cause first (read-only), then triage; if it can't be found, stop and report instead of guess-fixing.

**Execute immediately** only if all of these hold:
- 3 files or fewer, and about 100 changed lines or fewer. Exclude test files from both counts.
- one concern, in one repo
- no new dependency, no schema change, no public API change (endpoints, DTOs, message formats, shared signatures)
- no risky area: auth/security, money or ledger logic, data migrations, concurrency/transactions, CI/build/infra
- one reasonable reading of the request and one reasonable approach, each statable in one sentence

If it qualifies:
1. State a one-line scope and a "done when" check.
2. Implement it and run the check, without committing.
3. Ask whether to finish it fully (branch, review loop, commit/push, PR), skip all of that, or pick some steps. For the steps chosen, follow [execution.md](execution.md).

If, during the work, any criterion turns out to be broken, stop, report what's done so far and leave it uncommitted, then plan from there. The user decides whether to keep or discard the partial work.

Otherwise, plan first: read [planning.md](planning.md).

## Executing a plan part

Before starting any plan part, read [execution.md](execution.md). Start a part only when the user names it.

## Ask vs decide

- During planning, always ask.
- During execution of an approved part, decide small ambiguities yourself and record them under "Decisions made" in the PR description.
- Stop and ask only if the answer would change the part's scope, approach, or interfaces.
- If a check fails in a test or code the part didn't touch, run that test on the base branch in a temporary worktree (`git worktree add <temp-dir> <base-branch>`, removed afterwards with `git worktree remove`) before fixing it. If it fails there too, it's a pre-existing failure: don't fix it, don't let it block the gate or commits, and record it under "Pre-existing failures" in the PR.

## Hard stops

Even mid-part, stop and ask before anything:
- destructive or irreversible, like deleting data, force-pushing, or rewriting history
- security-sensitive (credentials, auth, permissions) outside the approved part's scope
- with side effects beyond the part's branch, like shared branches, deploys, or external services. Pushing the part's branch and opening its PR are exempt.

Some git rules are also enforced by a hook. If a command is blocked, follow the message; never work around it.
