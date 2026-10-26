---
name: apple-shortcuts
description: Develop, modify, debug, and version Apple Shortcuts (快捷指令) as editable source code using the shortcuts-src CLI — decompile iCloud links or .shortcut files to JSON/XML, edit actions and AI prompts, compile back to signed .shortcut, inject dev telemetry and read iOS run logs. Use when the user wants to build or change an iOS/macOS shortcut, mentions 快捷指令, .shortcut files, icloud.com/shortcuts links, Shortcuts.app, or WFWorkflowActions.
---

# Apple Shortcuts 开发

用 `shortcuts-src` 把快捷指令当作源码来开发。真源永远是 `*.source.json`（或等价的 `*.source.xml`），`.shortcut` 只是编译产物。

## 第 0 步：自检（每个会话第一次使用时）

```bash
shortcuts-src --version
```

- 命令不存在：定位 kit 仓库根目录（见下），运行 `<kit>/scripts/install.sh`。没有 kit 克隆时，运行 `pip install --user "git+https://github.com/kylwao/shortcuts-kit"`。
- **kit 仓库根目录** = 对本 `SKILL.md` 所在目录取 realpath 后再向上两级（`skills/apple-shortcuts/` → 仓库根目录）。用 `git -C <kit> rev-parse --show-toplevel` 判断它是不是 git 克隆；判断结果决定后面能否直接回流修复（见「踩坑与上游回流」）。

## 第 1 步：确定起点

**有现成的快捷指令**（推荐。用户在 Shortcuts.app 里先搭好骨架，再「分享 → 拷贝 iCloud 链接」）：

```bash
shortcuts-src decompile "<iCloud URL 或 .shortcut 文件>" -o "MyShortcuts/<分类>/V0.1" --name "<名称>"
```

**从零开始**：把 [templates/](templates/) 里的文件复制到 `MyShortcuts/<分类>/V0.1/`，并重命名为 `<名称>.source.json`。复制 `VERSIONS.md` 和 `AI_PROMPTS.md`（如果用到 AI）到 `MyShortcuts/<分类>/`。然后对 `source.json` 运行一次 `decompile`，生成 `flow.md` 和 `meta.json`。

## 第 2 步：开发循环

```
- [ ] 读 <名称>.flow.md 了解结构（不要通读整个 source.json）
- [ ] 用 Grep 定位要改的动作，只读 source.json 的局部片段
- [ ] 编辑 source.json（遵守 references/rules.md 的编辑约束）
- [ ] shortcuts-src decompile <名称>.source.json -o <同目录> --name <名称>   # 刷新 flow.md / meta.json
- [ ] shortcuts-src compile <名称>.source.json --allow-unsigned -o /tmp/<名称>.check.shortcut   # 快速验证
- [ ] shortcuts-src compile <名称>.source.json   # 签名产物，交给用户导入
- [ ] 追加 VERSIONS.md 条目
```

做大改动时，先复制出新版本目录（`V0.1` → `V0.2`），不要覆盖旧版本。

## 第 3 步：真机调试

```bash
shortcuts-src compile <名称>.source.json --profile dev --telemetry branch
# 用户在 iPhone 导入运行若干次，日志经 iCloud Drive 同步回 Mac
shortcuts-src ingest-logs --source <名称>.source.json -o <版本目录>/debuglog/report.md
```

报告里的 `source_line` 指向出错动作在 `source.json` 中的行号，只读那附近即可。没有日志时如实说明「无运行数据」，禁止编造。

## 必须交给人类的步骤

- 导入签名产物：`open -a Shortcuts <名称>.signed.shortcut`。
- 生成 iCloud 分享链接：只能在 Shortcuts.app 里手动「分享 → 拷贝 iCloud 链接」，没有 API。
- 首次运行时的权限授权（健康、照片、备忘录等）。

## 完成标准

1. 改过的 `*.source.json`（和/或 `.source.xml`）；
2. 刷新后的 `*.flow.md` 和 `*.meta.json`；
3. 追加的 `VERSIONS.md` 条目；
4. `compile` 通过的证据（产物路径）；
5. 需要人类完成的操作步骤清单；
6. 如果这次踩了新坑，确认已按下一节完成回流，或者已向用户说明为什么不回流。

## 踩坑与上游回流

遇到以下情况，要把修复送回 kit 仓库，让所有项目受益：

- `shortcuts-src` 本身的缺陷（崩溃、输出错误、往返不等价）；
- 平台行为坑，即 [references/pitfalls.md](references/pitfalls.md) 还没收录的 iOS/macOS 行为，例如某个动作在新版 iOS 上类型推断变了。

只和当前项目业务逻辑有关的问题不回流。

流程：主任务先用临时绕过方案继续推进，同时启动一个子任务修复上游。子任务的完整步骤、提示词模板和隐私红线见 [references/contributing-upstream.md](references/contributing-upstream.md)。

## 参考资料（按需读取）

- [references/rules.md](references/rules.md)：目录规范、编辑硬约束、绝对禁止项。**第一次编辑 source.json 前必读。**
- [references/format.md](references/format.md)：`.shortcut` 结构、控制流、变量引用、常用动作 ID。
- [references/pitfalls.md](references/pitfalls.md)：已知平台坑与解法。**动作行为不符合预期时先查这里。**
- [references/contributing-upstream.md](references/contributing-upstream.md)：子任务修复上游的流程。
- 完整示例：kit 仓库的 `examples/FoodAnalysis/`（462 个动作，含豆包 AI、HealthKit、备忘录持久化）。
- 人类手册：kit 仓库的 `docs/SHORTCUTS_DEVELOPMENT.md`（App Intents、URL Scheme、HealthKit 常量表等）。
