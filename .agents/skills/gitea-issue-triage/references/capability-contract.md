# Triage capability contract

## Required reads

- `issue.get` for the source issue and verification.
- `issue.comments.list-complete`; the bounded comment fallback is permitted.
- `issue.labels.list` for current classifications and verification.
- `repository.labels.list-complete` for exact existing label IDs.
- `repository.issues.list` for follow-up deduplication.

## Authorized writes

- `issue.labels.add` for one resolved existing classification label.
- `issue.create` only for a missing stable follow-up key.
- `issue.comment.create` when no marked plan exists.
- `issue.comment.update` only for the latest marked plan.

Re-read comments and labels and verify the plan contract and classification. Every other connector mutation is prohibited, including taxonomy creation, unrelated field/comment edits, closure, and deletion.
