# Gitea Issue Driven Skills

Three Codex Skills provide a deliberately small Gitea workflow. There is no packaged agent, phase orchestration, OpenSpec mode, or Gitea-native execution mode.

## Skills

| Skill | Responsibility |
|---|---|
| `gitea-issue-scope` | Read and explicitly mutate issues, comments, existing labels, and bounded attachment evidence |
| `gitea-branch-scope` | Create or inspect branches, commit an existing change, push with authorization, and create or update a PR |
| `gitea-issue-decomposition` | Use `$grill-me` to confirm feature boundaries, create all local feature branch refs, and comment those boundaries on the source issue |

The Skills use only capabilities exposed by the initialized Gitea MCP tools. They do not define MCP initialization, tool discovery, or a fixed tool-name map.

## Gitea MCP and attachment token

Configure a Gitea MCP connector with the issue, comment, label, repository, and pull-request capabilities required by the selected Skill.

Expose the same access token to the host Codex process:

```text
GITEA_ACCESS_TOKEN=<token>
```

`gitea-issue-scope` reads this host environment variable only when an issue contains attachment candidates. It never accepts the token as a command argument or writes or prints it. Attachment downloads are HTTPS and same-origin only, with hard limits of 20 candidates, 25 MiB per file, and 100 MiB per issue. Downloads live in a random system temporary directory and are removed when the task ends.

## Branch and PR behavior

Feature branches created by decomposition use:

```text
feature/issue<issue-number>-<stable-feature-key>
```

Every branch is based on the dynamically resolved remote default branch. Decomposition creates refs without switching or modifying a dirty worktree.

Before push or PR creation/update, `gitea-branch-scope` asks whether automatic push and PR operation is allowed. An explicit instruction to “自动操作PR” authorizes the already scoped branches only for the current task. It never authorizes merge, force-push, branch deletion, history rewriting, credential changes, or direct issue closure.

PR bodies use exactly Purpose, Reason, What changed, and Impact. PR labels are selected independently from existing repository labels; no repository label is created.

## Install

Python 3.10 or newer installs every direct child directory containing `SKILL.md` from a specified source:

```shell
python scripts/install_agent.py .agents/skills --dry-run
python scripts/install_agent.py .agents/skills
```

Use `--codex-home <path>` to target a different Codex home. A same-name Skill is transactionally overwritten. Other installed Skills are untouched.
