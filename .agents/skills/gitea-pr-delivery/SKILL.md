---
name: gitea-pr-delivery
description: Create or update a verified Gitea PR from a pushed issue branch with concise evidence, repository labels, a focused checklist, and conditional close-on-merge.
---

# Gitea PR Delivery

Build the PR from current issue, diff, commits, and test evidence.

## Prepare the body

Before the first remote operation, read the [shared connector profile](../gitea-connector-profile.md) and this Skill's [capability contract](references/capability-contract.md). The profile maps live tools; the contract limits this phase's authority. Re-read the source issue and labels, latest marked plan, `origin/master...HEAD` diff, commits, acceptance mapping, and exact test outcomes. Derive code claims from the diff and behavior claims from the plan/tests; state unrun checks.

Render [assets/pr-body-template.md](assets/pr-body-template.md). State behavior and implementation once; include only material constraints, risks, and follow-ups. Add security content only for credible evidence or security-boundary changes. Exclude credentials, private logs, personal data, signed URLs, and exploit detail.

Keep classification in actual PR labels, never the body. Copy applicable existing source-issue classification labels by exact ID. Do not create or approximate missing labels; report skipped labels outside the PR body.

Generate 2-4 checklist items from actual acceptance behavior, changed boundaries, risks, and tests. No generic security item.

## Link the source issue for close-on-merge

Add `Closes #<source-issue-number>` only when:

1. the source issue is in the same Gitea repository, is open, and this PR satisfies all of its current acceptance criteria;
2. it is not a decomposition parent/tracker, a follow-up issue, or an issue with remaining independently actionable work;
3. the repository has not documented a different administrator-configured close keyword.

Keep exactly one standalone close reference; otherwise write `Issue closure: not requested — <reason>`. Do not call `issue_write(method=update, state=closed)`, do not merge the PR, or claim the issue is closed before merge.

## Create or update the PR

1. Confirm remote head SHA equals local `HEAD`; find an open PR for the same branch when supported.
2. Create or update the PR with `head=<issue branch>` and `base=master`, then add resolved labels through its issue index. Preserve unrelated labels.
3. Read back the PR and labels; verify title, body, branches, evidence sections, checklist, closure line, and actual PR labels.
4. On mismatch, update once and read back again; report a persistent mismatch.

Do not merge, close, mutate unrelated reviewers, or change unrelated labels.

For normal delivery, optionally add one marked source-issue comment with the verified PR URL. Never claim success before read-back.
