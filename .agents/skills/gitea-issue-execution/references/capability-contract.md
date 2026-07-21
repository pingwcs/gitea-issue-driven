# Execution capability contract

## Required reads

- `issue.get` for the source issue.
- `issue.comments.list-complete` for the latest plan and later direction; the bounded comment fallback is permitted.
- `issue.labels.list` for applicable repository context used to scale verification.

This phase authorizes no connector writes. Git fetch, branch creation, commits, and a non-force issue-branch push are governed by the Skill; PR and optional source-comment writes belong to `$gitea-pr-delivery`.

Every Gitea mutation is prohibited during execution.
