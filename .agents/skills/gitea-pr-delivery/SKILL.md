---
name: gitea-pr-delivery
description: Create or update a verified Gitea pull request from a pushed issue branch, with a concise evidence-based body, change-specific checklist, and conditional close-on-merge reference.
---

# Gitea PR Delivery

Build the PR from current issue, diff, commits, and test evidence.

## Prepare the body

Read [references/mcp-contract.md](references/mcp-contract.md) before the first MCP call. Read the source issue, latest marked plan, `origin/master...HEAD` diff, ordered commits, acceptance mapping, and exact test outcomes. Derive code claims from the diff and behavior claims from the contract/tests; state unrun checks.

Render [assets/pr-body-template.md](assets/pr-body-template.md). Summarize behavior and implementation once; do not repeat the issue or plan. Include only material constraints, risks, and follow-ups. Add security notes/checklist items only for credible security evidence or changes to authentication, authorization, secrets, cryptography, untrusted-input parsing, or network trust boundaries. Never include credentials, private logs, personal data, signed URLs, or actionable exploit detail.

Generate 2-4 checklist items from actual acceptance behavior, changed boundaries, risks, and tests. No generic security item.

## Link the source issue for close-on-merge

Add `Closes #<source-issue-number>` only when:

1. the source issue is in the same Gitea repository, is open, and this PR satisfies all of its current acceptance criteria;
2. it is not a decomposition parent/tracker, a follow-up issue, or an issue with remaining independently actionable work;
3. the repository has not documented a different administrator-configured close keyword.

Keep exactly one standalone close reference; otherwise write `Issue closure: not requested — <reason>`. Do not call `issue_write(method=update, state=closed)`, do not merge the PR, or claim the issue is closed before merge.

## Create or update the PR

1. Confirm remote head SHA equals local `HEAD`; find an open PR for the same branch when supported.
2. Create or update the PR with `head=<issue branch>` and `base=master`. Do not merge, close, mutate unrelated reviewers, or change unrelated labels.
3. Read it back; verify title/body/head/base, source, summary, tests, notes, checklist markers, and closure line.
4. On mismatch, update once and read back again; report a persistent mismatch.

For normal delivery, optionally add one marked source-issue comment with the verified PR URL. Never claim success before read-back.
