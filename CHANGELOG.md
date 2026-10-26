# Changelog

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Added

- `shortcuts-src check`：编译前的结构校验。`UUID` 重复和控制流不配对（未闭合、无开头、块外分支、交错、同组动作 ID 不一致、`GroupingIdentifier` 复用或缺失、非法 `WFControlFlowMode`）报 error，退出码为 1；`ActionOutput` 引用不存在的动作、或引用自身及后面的动作报 warning。`.json` / `.xml` 源码附带行号。Skill 开发循环在 `compile` 前加入这一步。

## [0.1.0] - 2026-10-26

### Added

- `shortcuts-src` 命令行工具：`decompile` / `compile` / `inspect` / `ingest-logs`，支持 iCloud 链接、AEA 自签名、bplist、XML、JSON 互转，dev profile 遥测注入与日志聚合。
- `apple-shortcuts` Agent Skill：标准开发流程、编辑规则、格式速查、平台坑库（P001 到 P008）、上游回流流程、空白模板。
- `examples/FoodAnalysis`：「刚炫了啥」V0.7 完整示例。
- `scripts/install.sh`：安装命令行启动脚本，并把 Skill 软链接到 Cursor、Claude Code、WorkBuddy。
- CI、CODEOWNERS、PR 与 issue 模板。
