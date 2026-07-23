---
name: gitea-issue-decomposition
description: Turn one Gitea issue into confirmed local feature-branch scopes through a mandatory grill-me interview, then create all branch refs and record each branch boundary on the source issue. Use when an issue contains multiple features or its implementation boundaries need interactive clarification.
---

# Gitea Issue Decomposition

Create feature branches, never child issues.

1. Invoke `$gitea-issue-scope` to read the source issue, complete comments, labels, and attachment evidence.
2. Invoke `$grill-me`. Do not copy or replace its interview rules. If it is unavailable, stop.
3. Resolve every decision that changes feature boundaries. Define independently deliverable features rather than files, layers, or implementation steps.
4. Give each feature a stable lowercase kebab-case key. Name its branch:

   `feature/issue<issue-number>-<stable-feature-key>`

5. Invoke `$gitea-branch-scope` to resolve and fetch the remote default branch. Plan every new local branch ref from the same verified base. Do not switch branches, create worktrees, edit files, commit, or push.
6. Present the final feature list and ask:

   `是否确认按以上边界创建全部本地 feature branches，并在原 issue 发布对应的 branch 名与 feature 边界 comments？`

7. Proceed only after explicit confirmation. A dirty worktree is allowed because ref creation must not touch files or the index; report it.
8. Create every confirmed branch ref. For an existing name, verify its base and semantic boundary without overwriting or renaming it.
9. For each branch, invoke `$gitea-issue-scope` to create or update one source-issue comment containing only:

   `Branch: <full-branch-name>`

   `Feature boundary: <confirmed boundary>`

Use the full normalized branch name as the comment identity. Update the existing matching comment on reruns instead of adding a duplicate.

On any failure, stop and report completed, failed, and pending branches/comments. Preserve successful results; never roll them back or delete them. A rerun must continue idempotently.
