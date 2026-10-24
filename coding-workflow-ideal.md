# Guidelines
## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

# Planning
For any task (feature, bug fix, refactor, post-brainstorm execution),
1. **Triage.** Decide from scale whether to plan or execute immediately.
   - Execute immediately if ALL hold: ≤3 files touched, ≤~100 changed lines, one concern, no new dependency/schema/public-API change, approach obvious.
   - Otherwise plan first.
2. **Plan sizing.** Each plan part must fit one execution pass: ≤~5 files, ≤~300 changed lines, one concern, independently verifiable (has its own "done when" check). If a part exceeds this, split it. `settled` Each part states: scope boundary (files/modules in and out), dependencies on other parts (prefer none) `settled`, verify step.
3. **Present the plan and stop.** Wait for the user to review, or to say execute (whole plan, or specified parts).

# Execution
1. **Execute per part.** Create a new branch from the user's current working branch (`<type>/<short-slug>`, e.g. `fix/RBM-17-null-sku`). Never commit directly to the working branch. When the user asks to execute several parts in one request, put them on one branch (one commit per part) and open a single PR, unless they're unrelated concerns.
2. **Review loop.** `settled` Once the part is implemented:
   1. `settled` Review the changes with the `reviewer-agent`. 
   2. Fix every finding (or note why a finding is acceptable and skip it)
   3. Re-review. 
   4. Repeat until there are no findings or the remaining ones are acceptable.
3. **Quality gate.** (placeholder step, nothing to yet, still a work-in-progress)
4. **Commit and push** freely on the created branch once the part is done, verified, review is clean, and the Quality gate (if applicable) passes.
5. **Open a PR** targeting the user's working branch (the branch the part was created from). The user reviews and merges; never merge it yourself.
6. **Repeat** for the next part. If a later part depends on an unmerged one, say so and ask whether to wait or branch from the unmerged part's branch.
7. `settled` Ask the user when anything is unclear rather than guessing.