# Git / Worktree 治理规范

**状态：** Active
**适用范围：** ShareXtract 的本地开发、公开发布、Marketplace 分发、Codex / DevSpace 执行与维护收口

## 目标

ShareXtract 采用 **trunk-based development + Single Native Checkout First + 显式 WIP 上限**。

Branch 和 worktree 是短期隔离工具，不是长期项目管理层。长期真相必须回到 main、Git commit、release/tag 和可审计文档，不能依赖某个会话或某个 detached worktree。

## 长期分支与稳态预算

- main 是唯一长期开发与发布分支。
- 默认只保留 1 个 canonical checkout。
- 正常稳态：
  - 1 个长期本地分支：main；
  - 1 个 canonical worktree；
  - 实现期间最多额外 1 条活动短期分支 + 1 个对应隔离 worktree。
- codex/*、feature/*、fix/*、research/* 都是短期分支。
- detached HEAD 只允许短时只读验证，不得承载未提交的长期成果。

## 创建分支 / Worktree 的条件

优先直接使用 canonical checkout。只有以下情况才允许创建第二 worktree：

- main 必须保持稳定，而当前任务需要隔离写入；
- 并行验证会真实造成文件冲突或构建/runtime 污染；
- hotfix / recovery 需要独立现场；
- 用户或明确实施计划要求隔离。

不得因为新会话、任务看起来较大、工具默认行为而自动增加 worktree。

每个临时 worktree 必须同时有：

- owner branch；
- 创建原因；
- exit condition。

## WIP 上限

同一时间原则上只允许一条活动产品分支。

支持性 detour 应尽量在当前活动分支完成；不能从临时 branch 再派生第二代 feature branch，也不能把多个 DevSpace managed worktree 当成默认并行方式。

## Return-to-Trunk

每个短期分支完成后、开始下一条分支前必须完成：

1. 运行与改动匹配的测试 / lint / package / release 验证；
2. 确认成果已提交并推送；
3. 将成果整合到 main；
4. canonical main fast-forward 到 origin/main；
5. 对 merged main 做必要 smoke；
6. 删除已 merged / superseded 的本地短期 branch；
7. 删除对应远端短期 branch；
8. 删除临时 worktree；
9. 执行 git worktree prune 与 git fetch origin --prune；
10. 再次确认 branch/worktree budget。

## Squash / Patch 等价审计

不能只依赖 git branch --merged。Squash merge 后应使用 PR 状态、tree hash、git cherry 或 patch equivalence 证明功能已进入 main，再删除 feature branch。

需要保留 exact commit 的历史证据时，使用 archive/<topic>-YYYYMMDD annotated tag，不长期保留 archive branch。

## Dirty / Unmerged 安全规则

任何治理动作前先检查：

- git fetch origin --prune
- git status --short --branch
- git worktree list --porcelain
- git branch -vv
- git branch -r

规则：

- dirty worktree 只审计，不强删；
- detached worktree 先证明其改动已提交、迁移或等价吸收；
- unmerged branch 没有 superseded / patch-equivalent 证据时不能删除；
- 不用 git clean -fdx 做常规治理；
- 不回退其他会话或维护者已有的未提交改动；
- node_modules、build、cache 等可再生产物不是长期保留 worktree 的理由。

## 公开仓库边界

ShareXtract 是公开 Skill 仓库：

- branch、commit、issue、PR、文档中不得写入私有站点策略、凭据、内部路径或未公开商业计划；
- 与 AI智库等私有/运营项目联调时，只记录公开技术合同、commit SHA 和必要兼容性，不反向复制私有实现；
- 发布完成以 main、release/tag 和 Marketplace readback 为准，而不是某个本地 worktree 状态。

## 日常检查

开始和结束一轮开发建议执行：

- git fetch origin --prune
- git status --short --branch
- git worktree list
- git branch --sort=-committerdate
- git worktree prune

目标是：**只有真实活跃工作占用 live branch/worktree，历史只以 commit/tag/doc 形式存在。**
