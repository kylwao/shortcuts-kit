# 参与贡献

欢迎修复缺陷、补充平台坑、改进 Skill。所有改动都通过 PR 合入 `main`，由维护者 [@kylwao](https://github.com/kylwao) 审批后合并。

## 能贡献什么

| 类型 | 改哪里 |
| --- | --- |
| 工具缺陷（崩溃、输出错误、往返不等价） | `src/shortcuts_src/` + `tests/` |
| iOS / macOS 平台坑 | `skills/apple-shortcuts/references/pitfalls.md` |
| Skill 流程、规则、模板 | `skills/apple-shortcuts/` |
| 资料补充（动作 ID、URL Scheme 等） | `docs/SHORTCUTS_DEVELOPMENT.md`、`src/shortcuts_src/names.py` |

不确定要不要改时，先开一个 issue 讨论。

## 流程

1. Fork 本仓库（维护者可以直接建分支），从最新的 `main` 拉出 `fix/<主题>` 或 `feat/<主题>` 分支。
2. 修改：
   - 修缺陷时先写能复现问题的失败测试；
   - 平台坑按 `pitfalls.md` 文末的格式追加，编号顺延；
   - 在 `CHANGELOG.md` 的 `## [Unreleased]` 下记一行。
3. 本地验证：

   ```bash
   python3 -m pip install pytest
   python3 -m pytest -q
   ```

4. 隐私自查：提交内容里不能有私人提示词、`/Users/...` 路径、iCloud 分享 ID、邮箱、token。
5. 提交 PR，按模板填写。CI 通过并经维护者批准后合并。

在其他项目里使用 `apple-shortcuts` Skill 的 AI，会按 [contributing-upstream.md](skills/apple-shortcuts/references/contributing-upstream.md) 自动完成上述流程。

## 约束

- 运行时零第三方依赖，兼容 Python 3.7。
- `JSON ↔ bplist ↔ XML` 必须无损往返。
- 更多 AI 协作规则见 [AGENTS.md](AGENTS.md)。

## 发版（维护者）

1. 把 `CHANGELOG.md` 的 `[Unreleased]` 内容移到新版本标题下。
2. 更新 `pyproject.toml` 的 `version`。
3. 合并后打 tag：`git tag v<x.y.z> && git push origin v<x.y.z>`。
