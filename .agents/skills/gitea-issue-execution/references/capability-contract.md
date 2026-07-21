# Execution capability contract

Read [the shared Gitea connector profile](../../gitea-connector-profile.md), then map only the operations below to the live schema.

## Required reads

- `issue.get` for the current source issue.
- `issue.comments.list-complete` for the latest marked plan and later maintainer direction, including its bounded Tea read fallback when completeness cannot otherwise be proved.
- `issue.labels.list` for the actual classification used to scale verification.

This phase authorizes no Gitea MCP writes. Git fetch, branch creation, commits, and the non-force issue-branch push are governed by the Skill workflow rather than this connector contract. PR and optional source-comment writes belong to `$gitea-pr-delivery`.

Do not mutate issues, comments, labels, pull requests, repository settings, or any other Gitea resource during execution.
