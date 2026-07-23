# Gitea Issue Driven Skills

Use only these workflow Skills:

- `$gitea-issue-scope` for Gitea issue reads, explicit issue/comment/label mutations, closure, and attachments.
- `$gitea-branch-scope` for local branches, commits, authorized non-force push, and pull requests.
- `$gitea-issue-decomposition` to run `$grill-me`, confirm feature boundaries, create local feature branch refs, and comment the branch boundaries on the source issue.

Do not recreate phase orchestration, OpenSpec/Gitea-native modes, an agent wrapper, or separate connector contracts. The initialized Gitea MCP tool scope is authoritative; each Skill only states which provided capabilities it uses.

Never merge, force-push, delete branches or remote content, rewrite history, or modify credentials. Close an issue only after explicit closure authorization.
