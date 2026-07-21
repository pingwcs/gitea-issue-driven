# pingwcs/gitea-mcp contract

Check the live tool schema first; use these names for the current `main` contract:

| Task | Tool and method | Required fields |
|---|---|---|
| Read issue | `issue_read`, `get` | `owner`, `repo`, `issue_number` |
| Read comments | `issue_read`, `get_comments` | `owner`, `repo`, `issue_number`; prove completeness against comment count |
| Read issue labels | `issue_read`, `get_labels` | `owner`, `repo`, `issue_number` |
| List repository labels | `label_read`, `list_repo_labels` | `owner`, `repo`; paginate until complete |
| Add priority label | `issue_write`, `add_labels` | `owner`, `repo`, `issue_number`, numeric `labels` |
| Create follow-up | `issue_write`, `create` | `owner`, `repo`, `title`, `body` |
| Add design comment | `issue_write`, `add_comment` | `owner`, `repo`, `issue_number`, `body` |
| Update design comment | `issue_write`, `edit_comment` | `owner`, `repo`, `commentID`, `body` |

Use `add_labels`, never `replace_labels` or `clear_labels`. Read comments again after any comment write. Read labels again after adding a priority label. If the installed MCP exposes an older tool schema, map the same semantic operations to its advertised tools rather than calling REST directly.

The current `issue_read(get_comments)` schema has no page parameters. When the issue reports more comments than returned, or completeness cannot otherwise be proven, use the local Tea `api` command as a read-only pagination fallback and merge pages by comment ID. MCP remains the primary path for all supported reads and writes.

The MCP connection normally uses `GITEA_HOST` and `GITEA_ACCESS_TOKEN`. These are server configuration, not arguments to generated shell commands. Do not echo or copy the token. Attachment downloads have a separate rule: they must use the selected local Tea login through `$gitea-issue-evidence`.
