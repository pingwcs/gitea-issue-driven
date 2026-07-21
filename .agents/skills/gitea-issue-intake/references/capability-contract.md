# Intake capability contract

## Required reads

- `issue.get` for the source issue.
- `issue.comments.list-complete`; the bounded comment fallback is permitted.
- `issue.labels.list` for current issue context.

This phase authorizes no connector writes. Attachment downloads belong only to `$gitea-issue-evidence`. Every Gitea mutation is prohibited.
