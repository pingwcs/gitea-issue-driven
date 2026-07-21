---
name: gitea-issue-execution
description: Implement the latest marked Gitea design from fetched origin/master with regression-first tests, scoped commits, and a non-force push. Use after gitea-issue-triage publishes a plan.
---

# Gitea Issue Execution

Implement the remote contract with traceable tests and commits.

Before the first remote operation, read the [connector core](../../shared/gitea/connector-core.md) and this phase's read-only [capability contract](references/capability-contract.md).

## Refresh the contract

1. Re-read the issue and every comment. Use the newest `<!-- gitea-issue-driven:plan:v1 -->` comment; stop if it is missing, malformed, or superseded by later maintainer direction.
2. Run `$gitea-issue-evidence` only for new supported attachments.
3. Send newly discovered deferred outcomes to `$gitea-issue-triage` for deduplicated follow-ups.

## Start from current remote master

Read repository guidance; inspect status, branch, remotes, and worktrees. Do not stash, reset, discard, or mix unrelated work.

1. Run `git fetch origin master --prune`.
2. Verify `origin/master` and record its commit.
3. Create `issue/<number>-<short-slug>` from `origin/master`; inspect an existing branch instead of overwriting it.
4. Verify the branch point equals the fetched commit.

## Implement verified units

For each numbered module or step:

1. For behavior changes, add the smallest regression test and observe the expected failure. If it already passes, prove coverage or revise it.
2. Implement the unit and required error or compatibility handling.
3. Run focused and affected-subsystem checks.
4. Review diff/status and remove debug output or unrelated files.
5. Stage explicit paths, commit the complete unit, and record SHA, tests, outcomes, and acceptance mapping.

Do not commit failing checkpoints, automatically amend published commits, or rewrite history. Scale verification from demonstrated impact, applicable existing labels, and repository policy. Security review requires credible evidence, a changed security boundary, or repository policy.

After all units, run repository-required format, lint, typecheck, unit, and integration checks. Verify the full diff and commit order, push with `git push -u origin <branch>`, and confirm the remote head SHA. Invoke `$gitea-pr-delivery` with only the issue URL, branch, acceptance mapping, and compact commit/test ledger.
