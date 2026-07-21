---
name: gitea-issue-execution
description: Implement the latest marked Gitea design from fetched origin/master with regression-first tests, scoped commits, and a non-force push. Use after gitea-issue-triage publishes a plan.
---

# Gitea Issue Execution

Implement the remote contract with traceable tests and commits.

## Refresh the contract

1. Re-read the issue and every comment. Use the newest `<!-- gitea-issue-driven:plan:v1 -->` comment; stop if missing, malformed, or superseded by later maintainer direction.
2. Run `$gitea-issue-evidence` only for new supported attachments.
3. Send newly discovered deferred outcomes to `$gitea-issue-triage` for deduplicated follow-ups.

## Start from current remote master

Read repository guidance; inspect status, branch, remotes, and worktrees. Do not stash, reset, discard, or mix unrelated work.

1. run `git fetch origin master --prune`;
2. verify `origin/master` exists and record its commit;
3. create `issue/<number>-<short-slug>` with `git switch -c <branch> origin/master`;
4. if the branch exists, inspect it instead of overwriting it.

Verify the branch point equals fetched `origin/master`.

## Implement module by module

For each numbered module/step:

1. For behavior changes, add the smallest regression test and observe the expected failure. If it already passes, prove coverage or revise it.
2. Implement that unit and its required error/compatibility handling.
3. Run the focused test and affected subsystem checks.
4. Review diff/status; remove debug output and unrelated files.
5. Stage explicit paths, commit the complete unit, and record SHA, tests, outcomes, and acceptance mapping.

Do not commit incomplete or failing checkpoints, amend published commits automatically, or rewrite history. P0/P1 work requires broader regression verification before push.

Run security-specific review or checks only when the issue has credible security evidence or the diff touches authentication, authorization, secrets, cryptography, untrusted-input parsing, or a network trust boundary. Priority alone is not a security trigger.

## Push and hand off

After all modules, run repository-required format, lint, typecheck, unit, and integration checks. Add security checks only under the trigger above or when repository policy requires them. Record exact outcomes and verify the full diff and commit order.

Push with `git push -u origin <branch>`; never force-push. Confirm remote head SHA. Invoke `$gitea-pr-delivery` with the issue URL, branch, acceptance mapping, and compact commit/test ledger; it must read the current plan and diff directly.
