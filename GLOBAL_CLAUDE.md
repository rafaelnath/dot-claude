# Working Rules

## Questions are not a go-ahead

- Questions ("how can we…", "why is X…", "isn't X the same as Y?"), pushback, and agreeing to a design are discussion, not permission to edit files or write code.
- Answer, propose the change, then stop and ask whether to start.
- Only implement on an explicit instruction: "go ahead", "do it", "implement it", "add it".
- Small edits the user directly asks for can be done right away; keep them to exactly what was asked.
- This overrides any skill or plugin that says to ship first and ask later.

## Coding workflow

- Before any code change, even a one-line fix, load the `coding-workflow` skill and follow it. It also covers planning, executing plan parts, committing, pushing, and opening PRs.
- Triage every instruction first: small, low-risk changes are done right away; anything bigger is planned first. The skill has the criteria.
- Never merge a PR, force-push, amend a commit, or commit outside a `<type>/<slug>` branch.
- Stop and ask before anything destructive or irreversible, security-sensitive outside the approved scope, or with side effects beyond the working branch.

## Graphify

- Use the graphify skill only when the user types `/graphify`, or when `graphify-out/graph.json` already exists in the working directory (then query the existing graph).
- Never build a new graph unless explicitly asked, even if the skill's description suggests it.
