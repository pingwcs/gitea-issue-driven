# Triage capability contract

## Required reads

- `issue.get` for the source issue and verification.
- `issue.comments.list-complete`; the bounded comment fallback is permitted.
- `issue.labels.list` for preservation and verification of current labels.
- `repository.labels.list-complete` for exact existing label IDs.
- `repository.issues.list` for follow-up deduplication.

## Authorized writes

- `issue.labels.add` for at most one clearly matching existing repository label.
- `issue.create` only for a missing stable follow-up key.
- `issue.comment.create` when no marked plan exists.
- `issue.comment.update` only for the latest marked plan.

Re-read comments and labels and verify the plan contract, preservation of existing labels, and any selected label. The absence of a clear label match does not block the plan. Every other connector mutation is prohibited, including label creation, replacement or removal, unrelated field/comment edits, closure, and deletion.
