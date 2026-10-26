# 规则：目录、编辑约束、禁止项

优先级（高到低）：本文件的 MUST / MUST NOT 条款 > Apple 官方文档 > [format.md](format.md) 与 [pitfalls.md](pitfalls.md) > 社区资料。同级冲突时以更严格的一方为准。

## 1. 工具链（MUST）

- 反编译、解析：用 `shortcuts-src decompile`，不要手写 `curl` + `plutil` + `aea`。
- 编译、签名：用 `shortcuts-src compile`，不要直接调 `shortcuts sign`。
- 读结构：先读 `flow.md`，再用 Grep 定位 `source.json` 的局部片段。`source.json` 动辄几百 KB，禁止整份读取。
- 读 iOS 运行日志：用 `shortcuts-src ingest-logs`，不要手工 grep 原始 `.jsonl`。
- 真机调试：用 `compile --profile dev`，不要手工往 `source.json` 插 `savefile` / `appendfile`。

## 2. 目录与命名（MUST）

在使用本 Skill 的项目里：

```
MyShortcuts/
└── <分类>/                        例如 FoodAnalysis
    ├── VERSIONS.md                必备：版本日志
    ├── AI_PROMPTS.md              用到 AI Intent 时必备：提示词唯一真源
    └── V<major>.<minor>/          例如 V0.1
        ├── <名称>.source.json     真源，可编辑
        ├── <名称>.source.xml      真源，可编辑（与 json 等价，二选一维护即可）
        ├── <名称>.flow.md         只读，由 decompile 生成
        └── <名称>.meta.json       只读，由 decompile 生成
```

- 四件套前缀相同，后缀固定，不要自造后缀。
- `--profile dev` 会从路径里的 `MyShortcuts/<分类>/` 推断日志分类。目录不符合这个布局时，要显式传 `--category`。
- 项目 `.gitignore` 必须包含：

  ```gitignore
  *.signed.shortcut
  *.unsigned.shortcut
  *.bplist
  **/debuglog/
  *.jsonl
  *.log
  ```

## 3. 编辑 source.json（MUST）

- 只编辑 `*.source.json` / `*.source.xml`。`flow.md`、`meta.json`、二进制产物都不是真源。
- 保持字段顺序原样，不做排序或格式化重排。
- 保留既有动作的 `UUID`。新增动作用 `str(uuid.uuid4()).upper()` 生成新 UUID。
- 控制流（`conditional` / `choosefrommenu` / `repeat.*`）的开始（mode 0）、分支（mode 1）、结束（mode 2）必须配对，并共享同一个 `GroupingIdentifier`。
- 引用前序动作的输出时，优先用 `ActionOutput`（`OutputUUID` + `OutputName`），而不是 `Variable`（`VariableName`）。原因见 [pitfalls.md](pitfalls.md)。
- 修改 AI 提示词时，先改 `AI_PROMPTS.md`，再同步到 `source.json`。
- 每次修改后，用 `decompile` 刷新 `flow.md` / `meta.json`，再用 `compile --allow-unsigned` 验证能编译。

## 4. 绝对禁止（MUST NOT）

- 尝试自动生成 `https://www.icloud.com/shortcuts/...` 分享链接（没有公开的上传接口）。
- 尝试解密 Apple Gallery 官方签名的 `.shortcut`（密钥不在用户侧）。
- 写入 `~/Library/Shortcuts/Shortcuts.sqlite`；只允许 `sqlite3 -readonly` 查询。
- 在快捷指令或任何提交的文件里硬编码 token、密钥、Apple ID、手机号；改用 `ask` 输入或运行时读取。
- 提交 `*.jsonl` / `*.log` 调试日志。
- 伪造 dev 日志或 `ingest-logs` 报告。没有日志就如实报告「无运行数据」。
- 手工编辑带 `_ShortcutsSrcTelemetry` 字段的动作（它们是遥测注入物，由工具自动注入和剥离）。

## 5. 不确定时

- 动作 ID 含义：查 [format.md](format.md)，再查 kit 仓库的 `src/shortcuts_src/names.py` 和 `docs/SHORTCUTS_DEVELOPMENT.md`，最后查官方文档。
- 不确定某个字段或行为时，说明「需要查证」，再用 `decompile` 一个在 Shortcuts.app 里手工搭出的最小样例做对照，不要凭印象编。
