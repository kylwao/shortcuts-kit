# AGENTS.md：在 shortcuts-kit 仓库内工作的 AI 规则

本文件约束「修改 shortcuts-kit 本身」的 AI。用 Skill 开发快捷指令的规则在 [skills/apple-shortcuts/references/rules.md](skills/apple-shortcuts/references/rules.md)。

## 1. 工作方式（MUST）

- 所有改动都在 `fix/*`、`feat/*`、`docs/*` 分支上进行，通过 PR 合入 `main`，不要直接提交到 `main`。
- 从其他项目回流时，按 [contributing-upstream.md](skills/apple-shortcuts/references/contributing-upstream.md) 使用 `.worktrees/` 下的独立 worktree。
- 提交前运行 `python3 -m pytest -q`，必须全部通过。
- 提交信息前缀：`fix:` / `feat:` / `docs(pitfalls):` / `docs(skill):` / `docs:` / `test:` / `chore:`。
- 在 `CHANGELOG.md` 的 `## [Unreleased]` 下记一行。

## 2. 代码约束（MUST）

- `src/shortcuts_src/` 保持零第三方运行时依赖，兼容 Python 3.7。`pytest` 只用于 `tests/`。
- 保证无损往返：`JSON ↔ bplist ↔ XML` 在 dict 层面完全相等，字段顺序和 `UUID` 不变。
- 修复缺陷时，先写能复现问题的失败测试，再改代码。
- 新增动作 ID 的中文名映射写在 `src/shortcuts_src/names.py`。

## 3. Skill 约束（MUST）

- `skills/apple-shortcuts/SKILL.md` 控制在 500 行以内；细节放在 `references/`，只从 `SKILL.md` 链接一层深。
- `pitfalls.md` 条目编号只增不改，按文末格式书写；没有实证的内容要标「推测」。
- 修改 `templates/blank.source.json` 后，`tests/test_skill_templates.py` 必须通过。

## 4. 隐私红线（MUST NOT）

- 不提交任何私人项目的提示词、绝对路径（`/Users/...`）、iCloud 分享 ID、Apple ID、邮箱、手机号、token。
- 不提交 `*.signed.shortcut` / `*.unsigned.shortcut` / `*.bplist` / `*.jsonl` / `*.log`。
- fixture 和示例必须是脱敏后的最小片段。

## 5. 需要维护者同意的改动

下列改动必须在 PR 描述里单独说明理由，由 @kylwao 明确批准：

- 本文件、`skills/apple-shortcuts/references/rules.md` 第 3、4 节；
- README 的「能力一览」「运行环境」「已知限制」；
- `scripts/install.sh` 的安装位置和行为；
- 引入任何运行时依赖，或提高 Python 最低版本。
