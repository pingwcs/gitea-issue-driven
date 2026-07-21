# Decomposition capability contract

## Required reads

- `issue.get` for the target, candidate children, and verification.
- `issue.comments.list-complete`; the bounded comment fallback is permitted.
- `issue.labels.list` for relevant label reuse.
- `repository.issues.list` for duplicate-child discovery.

## Authorized writes

- `issue.create` only for a missing stable child key.
- `issue.body.update` only to reconcile the latest parent's managed tracking block.

Re-read every created child and the updated parent. Verify markers, backlinks, stable keys, and one parent entry per child. Every other connector mutation is prohibited, including closure, label replacement, unrelated parent edits, and deletion.
