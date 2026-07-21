---
name: gitea-issue-execution
description: Implement and verify the latest marked Gitea plan in Gitea-native mode without branch creation, commits, pushes, PRs, or OpenSpec task handling. Use after gitea-issue-triage and gitea-branch-bootstrap only when OpenSpec is not the implementation owner.
---

# Gitea Issue Execution

Implement the remote contract with traceable tests. This Skill is exclusive to `gitea-native` mode; never combine it with `openspec-apply-change` for the same change.

Before the first remote operation, read the [connector core](../../shared/gitea/connector-core.md) and this phase's read-only [capability contract](references/capability-contract.md).

## Refresh the contract

1. Re-read the issue and every comment. Use the newest `<!-- gitea-issue-driven:plan:v1 -->` comment; stop if it is missing, malformed, or superseded by later maintainer direction.
2. Run `$gitea-issue-evidence` only for new supported attachments.
3. Send newly discovered deferred outcomes to `$gitea-issue-triage` for deduplicated follow-ups.

## Verify the prepared branch

Require the verified output of `$gitea-branch-bootstrap`. Confirm the current branch and base SHA still match it. Do not create, switch, rewrite, or publish branches. Preserve unrelated work and stop if it prevents a scoped implementation.

## Implement verified units

For each numbered module or step:

1. For behavior changes, add the smallest regression test and observe the expected failure. If it already passes, prove coverage or revise it.
2. Implement the unit and required error or compatibility handling.
3. Run focused and affected-subsystem checks.
4. Review diff/status and remove debug output or unrelated files.
5. Review the scoped diff and record changed paths, tests, outcomes, and acceptance mapping.

Do not stage, commit, push, or rewrite history. Scale verification from demonstrated impact, applicable existing labels, and repository policy. Security review requires credible evidence, a changed security boundary, or repository policy.

After all units, run the checks required by repository policy and the caller's verification contract. Verify the full scoped diff, then invoke `$gitea-change-publish` with the issue URL, branch/base, acceptance mapping, changed paths, and compact test ledger.
