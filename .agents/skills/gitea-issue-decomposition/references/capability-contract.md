# Decomposition capability contract

Read [the shared Gitea connector profile](../../gitea-connector-profile.md), then map only the operations below to the live schema.

## Required reads

- `issue.get` for the target, candidate children, and write verification.
- `issue.comments.list-complete`, including its bounded Tea read fallback when completeness cannot otherwise be proved.
- `issue.labels.list` for relevant label reuse.
- `repository.issues.list` for duplicate-child discovery.

## Authorized writes

- `issue.create` only for a missing stable child key.
- `issue.body.update` only for the latest parent body and only to reconcile the managed tracking block.

Re-read every created child and the updated parent. Verify child markers, backlinks, stable keys, and one parent entry per child.

Do not close issues, replace or clear labels, update unrelated parent content, delete remote data, or use any other connector mutation.
