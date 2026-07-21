# Pull-request delivery capability contract

## Required reads

- `issue.get`, `issue.comments.list-complete`, and `issue.labels.list` for source state, plan, closure decision, and classification; the bounded comment fallback is permitted.
- `repository.labels.list-complete` for exact existing label IDs.
- `pull-request.get`, `pull-request.files.list-complete`, `pull-request.diff.get`, and `pull-request.status.get` for current state and verification.
- Optional `pull-request.list` to find an open PR by head branch. Without it, require a known PR number or another advertised read that rules out duplication.

## Authorized writes

- `pull-request.create` for a pushed issue branch with `base=master` when no matching PR exists.
- `pull-request.update` for the matching PR's intended title or body.
- `issue.labels.add` with `issue_number=<pull-number>` for resolved existing labels.
- `issue.comment.create` for at most one marked source comment containing the verified PR URL.

Re-read the PR and labels and verify title, body, head/base, evidence, checklist, closure line, status, and labels. One corrective update and final read are allowed. Every other mutation is prohibited, including merge, closure, branch updates, reviews/reviewers, label creation, unrelated edits, source closure, and deletion.
