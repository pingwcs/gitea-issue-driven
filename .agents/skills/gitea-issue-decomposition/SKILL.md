---
name: gitea-issue-decomposition
description: Decompose a Gitea issue into independently deliverable child issues through a compatible live Gitea connector and reconcile its parent tracking block. Use for 拆分 Issue, sub-issues, epic/tracker conversion, or mixed responsibilities.
---

# Gitea Issue Decomposition

Create or reuse focused child issues, then update only the parent's managed tracking block. A concrete decomposition request authorizes those writes.

## Workflow

Before the first remote operation, read the [shared connector profile](../gitea-connector-profile.md) and this Skill's [capability contract](references/capability-contract.md). The profile maps live tools; the contract limits this phase's authority.

1. Read the target, all comments, labels, latest marked plan, existing tracking block, and linked issues. Prove comment completeness; stop if the target is closed or not writable.
2. Split only outcomes that can each be implemented, tested, reviewed, and accepted. Each child owns one cohesive outcome, boundaries, criteria, an independent test/PR path, and acyclic dependencies. Keep coupled criteria together; never split by file, layer, or implementation step.
3. Assign each responsibility a stable lowercase hyphenated key and search for its marker:

`<!-- gitea-issue-driven:child parent=<parent-number> key=<stable-key> -->`

4. Classify each proposal as `existing`, `create`, or `merge-with-existing`; preserve existing issue numbers and order by dependency. Redraw any cyclic boundary.
5. Render [assets/child-issue-template.md](assets/child-issue-template.md). Include only constraints required by that child's acceptance; do not add generic security review. Reuse relevant labels only. Create and read back each missing child before continuing. On failure, stop without deleting completed writes.
6. Re-read the parent. Build `children.json` from verified child numbers, titles, URLs, responsibilities, dependencies, and states, then run:

```text
python scripts/reconcile_parent.py --parent-body <latest-body-file> --children-json <children-json> --output <updated-body-file>
```

7. Update only the parent `body`. Read it back and verify each child appears once; verify each child links back with the expected key.

## Completion

Report created/reused children, dependency order, boundaries, and verification. Do not close issues. Deferred future work remains with `$gitea-issue-triage`.
