# pingwcs/gitea-mcp decomposition contract

Verify the live schema before use. The current contract requires:

| Task | Tool and method | Fields |
|---|---|---|
| Read target or child | `issue_read`, `get` | `owner`, `repo`, `issue_number` |
| Read comments | `issue_read`, `get_comments` | `owner`, `repo`, `issue_number` |
| Read labels | `issue_read`, `get_labels` | `owner`, `repo`, `issue_number` |
| Find possible duplicates | `list_issues` | `owner`, `repo`, `state=all`, `page`, `per_page` |
| Create child | `issue_write`, `create` | `owner`, `repo`, `title`, `body`; optional numeric `labels`, `milestone`, `assignees` |
| Update parent body | `issue_write`, `update` | `owner`, `repo`, `issue_number`, `body` |

Use `issue_write(create)` only for missing stable keys. Use `issue_write(update)` only after re-reading the latest parent body and reconciling its managed block. Never call close, clear/replace labels, or delete operations in this workflow.

The current comments method has no page arguments. Compare returned comments with the target's comment count when available. If completeness cannot be proven, use Tea's authenticated `api` command as a read-only pagination fallback and merge by comment ID.
