# Repository Guidance

## Git / Worktree execution governance

- main 是唯一长期开发与发布分支。
- 默认使用 canonical checkout；只有真实隔离需求时才创建第二 worktree。
- 同一时间最多保留 1 条活动短期产品分支和 1 个对应隔离 worktree。
- DevSpace / Codex managed worktree 仍然是临时资产；detached HEAD 不得长期承载未提交成果。
- 每个短期 branch/worktree 必须有 owner、创建原因和 exit condition。
- 合并或 supersede 后必须在同一 closeout 回合 Return-to-Trunk：同步 main、删除短期 branch/worktree、git worktree prune、git fetch origin --prune。
- dirty / unmerged worktree 不得强删；Squash merge 必须用 PR/tree/patch equivalence 证明已吸收，不能只看 git branch --merged。
- 详细规则见 docs/engineering/git-worktree-governance.md。

## Public repository boundary

- 不提交私有站点策略、凭据、内部环境路径或未公开商业计划。
- 与私有/运营项目联调时，仅保留公开技术合同、必要兼容性和可公开的验证证据。
