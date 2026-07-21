# Triage capability contract

Read [the shared Gitea connector profile](../../gitea-connector-profile.md), then map only the operations below to the live schema.

## Required reads

- `issue.get` for the source issue and write verification.
- `issue.comments.list-complete`, including its bounded Tea read fallback when completeness cannot otherwise be proved.
- `issue.labels.list` for current classifications and verification.
- `repository.labels.list-complete` for exact existing label IDs.
- `repository.issues.list` for follow-up deduplication.

## Authorized writes

- `issue.labels.add` for one resolved existing classification label; never replace or clear labels.
- `issue.create` only for a missing stable follow-up key.
- `issue.comment.create` when no marked plan exists.
- `issue.comment.update` only for the latest marked plan comment.

Re-read comments and labels after writes. Verify the plan marker, acceptance criteria, modules, tests, follow-up links, and actual classification label.

Do not create label taxonomy, mutate unrelated issue fields or comments, close issues, delete remote data, or use any other connector mutation.
