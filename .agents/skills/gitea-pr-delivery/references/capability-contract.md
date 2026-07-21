# Pull-request delivery capability contract

Read [the shared Gitea connector profile](../../gitea-connector-profile.md), then map only the operations below to the live schema.

## Required reads

- `issue.get`, `issue.comments.list-complete`, and `issue.labels.list` for the source issue, latest marked plan, closure decision, and classification labels. The comments read permits the bounded Tea fallback when completeness cannot otherwise be proved.
- `repository.labels.list-complete` for exact existing label IDs.
- `pull-request.get`, `pull-request.files.list-complete`, `pull-request.diff.get`, and `pull-request.status.get` for current-state and write verification.

`pull-request.list` is optional for finding an existing open PR by head branch. If unavailable, require an explicit known PR number or create only when duplicate creation has been ruled out by another advertised read capability.

## Authorized writes

- `pull-request.create` for a pushed issue branch with `base=master` when no matching open PR exists.
- `pull-request.update` for the matching PR's intended title or body fields.
- `issue.labels.add` with `issue_number=<pull_number>` for resolved existing labels; never replace or clear labels.
- `issue.comment.create` for at most one marked source-issue comment containing the verified PR URL.

Re-read the PR and labels after writes. Verify title, body, head, base, evidence, checklist, closure line, head status, and labels. A persistent mismatch may receive one corrective update followed by one final read.

Do not close or merge a PR, update its branch, submit reviews, mutate reviewers, create labels, change unrelated labels or fields, directly close the source issue, delete remote data, or use any other connector mutation.
