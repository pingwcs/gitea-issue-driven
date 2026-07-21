---
name: gitea-issue-decomposition
description: Decompose a Gitea issue into independently deliverable child issues through a compatible live Gitea connector and reconcile its parent tracking block. Use for 拆分 Issue, sub-issues, epic/tracker conversion, or mixed responsibilities.
---

# Gitea Issue Decomposition

Create or reuse focused child issues, then update only the parent's managed tracking block.

Before the first remote operation, read the [connector core](../../shared/gitea/connector-core.md) and this phase's [capability contract](references/capability-contract.md).

## Workflow

1. Read the target, all comments, labels, latest marked plan, existing tracking block, and linked issues. Prove comment completeness; stop if the target is closed or not writable.
2. Split only outcomes that can each be implemented, tested, reviewed, and accepted. Give each child one cohesive outcome, explicit boundaries and criteria, an independent test/PR path, and acyclic dependencies. Keep coupled criteria together; never split by file, layer, or implementation step.
3. Assign each responsibility a stable lowercase hyphenated key and search for its marker:

   `<!-- gitea-issue-driven:child parent=<parent-number> key=<stable-key> -->`

4. Classify each proposal as `existing`, `create`, or `merge-with-existing`; preserve issue numbers and order by dependency. Redraw cyclic boundaries.
5. Render [assets/child-issue-template.md](assets/child-issue-template.md). Give each child its own stable source-order `AC-*` IDs and retain parent acceptance references where applicable. Include only child-specific constraints and relevant existing labels. Create and read back each missing child before continuing; stop on failure without deleting completed writes.
6. Re-read the parent. Build `children.json` from verified child numbers, titles, URLs, responsibilities, dependencies, and states, then run:

   `python scripts/reconcile_parent.py --parent-body <latest-body-file> --children-json <children-json> --output <updated-body-file>`

7. Update only the parent body. Read it back and verify one entry per child plus each child's backlink and stable key.

Report created/reused children, dependency order, boundaries, and verification. Deferred future work belongs to `$gitea-issue-triage`.
