# Gitea connector profile

Use this profile only to map semantic Gitea operations to the live connector. It does not authorize an operation; the active Skill's capability contract defines allowed reads, writes, fallbacks, and read-back checks.

## Discover and map the connector

1. Inspect the tools exposed in the current session before the first remote operation.
2. Select an enabled connector by its advertised Gitea capabilities and input schema, not by server name, package, or the baseline names below.
3. Map every required semantic operation from the active capability contract to one advertised tool and method. Optional operations may be omitted when unsupported.
4. Stop and report the missing semantic capability when a required operation cannot be mapped. Do not invent REST calls, install or reconfigure a connector, or source alternate credentials.

The following table is a compatibility baseline for the current connector. The live schema is authoritative.

| Semantic operation | Current baseline | Required fields |
|---|---|---|
| `issue.get` | `issue_read`, `get` | `owner`, `repo`, `issue_number` |
| `issue.comments.list-complete` | `issue_read`, `get_comments` | `owner`, `repo`, `issue_number` |
| `issue.labels.list` | `issue_read`, `get_labels` | `owner`, `repo`, `issue_number` |
| `repository.labels.list-complete` | `label_read`, `list_repo_labels` | `owner`, `repo`, plus pagination when advertised |
| `repository.issues.list` | `list_issues` | `owner`, `repo`, `state`, `page`, `per_page` |
| `issue.create` | `issue_write`, `create` | `owner`, `repo`, `title`, `body`; optional numeric `labels`, `milestone`, `assignees` |
| `issue.body.update` | `issue_write`, `update` | `owner`, `repo`, `issue_number`, `body` |
| `issue.labels.add` | `issue_write`, `add_labels` | `owner`, `repo`, `issue_number`, numeric `labels` |
| `issue.comment.create` | `issue_write`, `add_comment` | `owner`, `repo`, `issue_number`, `body` |
| `issue.comment.update` | `issue_write`, `edit_comment` | `owner`, `repo`, `commentID`, `body` |
| `pull-request.list` | `list_pull_requests` | `owner`, `repo`, filters and pagination when advertised |
| `pull-request.get` | `pull_request_read`, `get` | `owner`, `repo`, `pull_number` |
| `pull-request.files.list-complete` | `pull_request_read`, `get_files` | `owner`, `repo`, `pull_number`, plus pagination when advertised |
| `pull-request.diff.get` | `pull_request_read`, `get_diff` | `owner`, `repo`, `pull_number` |
| `pull-request.status.get` | `pull_request_read`, `get_status` | `owner`, `repo`, `pull_number` |
| `pull-request.create` | `pull_request_write`, `create` | `owner`, `repo`, `title`, `body`, `head`, `base` |
| `pull-request.update` | `pull_request_write`, `update` | `owner`, `repo`, `pull_number`, changed fields |

Gitea exposes pull-request labels through the shared issue index. Map `issue.labels.list` and `issue.labels.add` with `issue_number=<pull_number>` after resolving exact label IDs through `repository.labels.list-complete`.

## Complete reads

Paginate list operations until complete when the live schema exposes pagination. The current baseline for `issue_read(get_comments)` has no page arguments. For a stage that permits the comments fallback, compare returned comments with the issue's comment count when available. If completeness cannot be proved, use the selected local Tea login's authenticated `api` command as a read-only pagination fallback and merge comments by ID.

MCP remains primary for supported reads and writes. Tea is not a general REST fallback and must not perform writes.

## Credentials and verification

Connector credentials such as `GITEA_HOST` and `GITEA_ACCESS_TOKEN` are server configuration, never generated command arguments. Do not echo, copy, or expose them. Attachment downloads use the separate `$gitea-issue-evidence` credential flow.

Use additive label operations, preserve unrelated labels, and read remote state back after every write as required by the active capability contract. Never infer success from a tool call alone.
