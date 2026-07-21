---
name: gitea-pr-delivery
description: Create or update a verified Gitea PR from a pushed issue branch with concise evidence, repository labels, a focused checklist, and conditional close-on-merge.
---

# Gitea PR Delivery

Build the PR from current issue, diff, commits, and test evidence.

Require the workflow mode. Reject mixed OpenSpec and Gitea-native planning inputs.

Before the first remote operation, read the [connector core](../../shared/gitea/connector-core.md) and this phase's [capability contract](references/capability-contract.md).

## Prepare the body

Re-read the source issue and labels, `origin/master...HEAD` diff, commits, acceptance mapping, and exact test outcomes. In `gitea-native` mode also read the latest marked plan. In `openspec` mode require the change name and artifact fingerprint from the caller; do not require or publish a duplicate Gitea plan. Derive code claims from the diff and behavior claims from the acceptance mapping and tests; state unrun checks.

Render [assets/pr-body-template.md](assets/pr-body-template.md). State behavior and implementation once; include only material constraints, risks, and follow-ups. Exclude credentials, private logs, personal data, signed URLs, and exploit detail. Add security content only for credible evidence or a changed security boundary.

Copy applicable existing source labels to the PR by exact ID while preserving unrelated PR labels. Do not create or approximate missing labels. Generate 2-4 checklist items from acceptance behavior, changed boundaries, risks, and tests. Include the stable acceptance IDs.

## Link close-on-merge

Add `Closes #<source-issue-number>` only when the source issue is open in the same repository, this PR satisfies all current acceptance criteria, it is not a tracker/follow-up/partial delivery, and the repository has no different close keyword. Keep exactly one standalone close reference; otherwise render `Issue closure: not requested — <reason>`.

## Create or update the PR

1. Confirm remote head SHA equals local `HEAD`; find an open PR for the branch when supported.
2. Create or update it with the issue branch and `base=master`, then add resolved labels through its issue index while preserving unrelated labels.
3. Read back the PR and labels; verify title, body, branches, evidence, checklist, closure line, and labels.
4. On mismatch, update once and read back again; report a persistent mismatch.

Optionally add one marked source-issue comment containing the verified PR URL. Never claim success before read-back.
