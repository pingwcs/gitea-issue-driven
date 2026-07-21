# pingwcs/gitea-mcp pull request contract

Check the live tool schema first. The current `main` contract exposes:

| Task | Tool and method | Required fields |
|---|---|---|
| Read PR | `pull_request_read`, `get` | `owner`, `repo`, `pull_number` |
| Read changed files | `pull_request_read`, `get_files` | `owner`, `repo`, `pull_number`; paginate |
| Read diff | `pull_request_read`, `get_diff` | `owner`, `repo`, `pull_number` |
| Read head status | `pull_request_read`, `get_status` | `owner`, `repo`, `pull_number` |
| Create PR | `pull_request_write`, `create` | `owner`, `repo`, `title`, `body`, `head`, `base` |
| Update PR | `pull_request_write`, `update` | `owner`, `repo`, `pull_number`, changed fields |

Do not use `close`, `merge`, `update_branch`, reviewer mutation, or review-submission methods as part of automatic delivery. If an installed older MCP exposes separate create/get tools, map these semantic operations to its advertised schema and retain the same read-back verification.
