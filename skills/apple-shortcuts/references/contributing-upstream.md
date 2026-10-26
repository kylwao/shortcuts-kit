# 上游回流：在其他项目里修复 shortcuts-kit

目标：在任何项目里踩到工具缺陷或平台坑时，不中断当前工作，同时把修复以 PR 的形式送回 [kylwao/shortcuts-kit](https://github.com/kylwao/shortcuts-kit)，由维护者审批合并。

## 1. 要不要回流

| 情况 | 处理 |
| --- | --- |
| `shortcuts-src` 崩溃、输出错误、往返不等价 | 回流：修代码 + 补测试 |
| 新的平台行为坑（[pitfalls.md](pitfalls.md) 未收录） | 回流：追加 pitfalls 条目 |
| Skill 文档有错、缺失或误导 | 回流：改 `skills/apple-shortcuts/` |
| 只和当前项目业务逻辑有关 | 不回流 |

## 2. 主任务怎么做

1. 先用临时绕过方案让当前项目继续推进，不要等上游合并。
2. 准备好脱敏后的回流材料：
   - 现象：错误信息或异常输出；
   - 最小复现：只保留相关的几个动作，去掉私人提示词、名字、路径、iCloud ID；
   - 环境：iOS/macOS 版本、`shortcuts-src --version`；
   - 已知的绕过方案。
3. 确定 kit 仓库根目录 `KIT`（见 SKILL.md 第 0 步），然后按平台分派子任务：
   - **Cursor**：用 Task 工具启动子代理（`generalPurpose` 类型），提示词见第 4 节。
   - **Claude Code**：用 Task / subagent，提示词相同。
   - **不支持子代理的工具（例如 WorkBuddy）**：在当前会话里执行第 3 节，完成后切回原任务。
4. 子任务返回后，把 PR 链接告诉用户，并提醒用户：合并后需要在 kit 克隆里执行 `git pull` 才会生效。

如果 `KIT` 不是 git 克隆（例如只用 `pip install git+...` 安装），就改为提 issue：把第 2 步的材料填进 `https://github.com/kylwao/shortcuts-kit/issues/new/choose`。

## 3. 子任务步骤

```bash
# 3.1 独立 worktree，绝不在 main 上直接改
cd "$KIT"
git fetch origin
git worktree add ".worktrees/fix-<topic>" -b "fix/<topic>" origin/main
cd ".worktrees/fix-<topic>"
```

3.2 修改：

- 工具缺陷：在 `tests/` 里先写一个能复现的失败测试（fixture 放 `tests/fixtures/`，必须脱敏），再修 `src/shortcuts_src/`，保持零第三方运行时依赖。
- 平台坑：按 [pitfalls.md](pitfalls.md) 文末格式追加条目，编号顺延。
- 在 `CHANGELOG.md` 的 `## [Unreleased]` 下追加一行。

```bash
# 3.3 验证
python3 -m pytest -q
```

3.4 隐私自查。下面的命令应当没有输出；有输出就先清理：

```bash
git diff origin/main --unified=0 | grep -nE '/Users/|/home/|icloud\.com/shortcuts/[0-9a-fA-F]{32}|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}|sk-[A-Za-z0-9]{16,}'
```

3.5 提交并推送。先判断有没有写权限：

```bash
gh repo view kylwao/shortcuts-kit --json viewerPermission -q .viewerPermission
```

- 结果是 `ADMIN` / `MAINTAIN` / `WRITE`：`git push -u origin "fix/<topic>"`。
- 其他结果：`gh repo fork --remote --remote-name fork`，然后 `git push -u fork "fix/<topic>"`。

提交信息格式：`fix: ...`（工具缺陷）、`docs(pitfalls): ...`（平台坑）、`docs(skill): ...`（Skill 文档）、`feat: ...`（新能力）。

3.6 创建 PR，正文按 `.github/pull_request_template.md` 填写：

```bash
gh pr create --repo kylwao/shortcuts-kit --base main --title "<提交信息>" --body-file <填好的模板>
```

3.7 清理 worktree（分支已在远端）：

```bash
cd "$KIT" && git worktree remove ".worktrees/fix-<topic>"
```

**没有 `gh` 时**：有写权限就直接 `git push`，再把 `https://github.com/kylwao/shortcuts-kit/compare/main...fix/<topic>` 交给用户手动开 PR。没有写权限就用 `git format-patch origin/main` 生成补丁，交给用户。

## 4. 子任务提示词模板

```text
你是 shortcuts-kit 的贡献者。请按 <KIT>/skills/apple-shortcuts/references/contributing-upstream.md 第 3 节，修复下面的问题并提交 PR。

KIT 仓库根目录：<KIT>
类型：工具缺陷 | 平台坑 | Skill 文档
现象：<错误信息或异常输出>
环境：<iOS/macOS 版本>，shortcuts-src <版本>
最小复现（已脱敏）：
<几个动作的 JSON 片段，或复现命令>
已知绕过方案：<主任务正在使用的做法>

要求：
- 在独立 worktree 的 fix/<topic> 分支上工作，不要改 main。
- 工具缺陷必须先写失败测试再修复；pytest 必须全部通过。
- 提交前执行隐私自查，提交内容不得包含私人项目的提示词、路径、iCloud ID、token、邮箱。
- 完成后返回：PR 链接（或补丁路径）、改动摘要、测试结果。
```

## 5. 合并之后

- 维护者合并 PR 后，各使用者在 kit 克隆里执行 `git pull`。`shortcuts-src` 启动脚本直接运行克隆里的 `src/`，Skill 是软链接，所以无需重新安装就立即生效。
- 使用者想固定版本时，在 kit 克隆里 `git checkout v<x.y.z>`。
