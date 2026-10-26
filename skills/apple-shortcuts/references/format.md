# `.shortcut` 源码格式速查

更完整的资料（版本对照、URL Scheme、HealthKit 常量、App Intents）见 kit 仓库的 `docs/SHORTCUTS_DEVELOPMENT.md`。

## 顶层键

| 键 | 说明 |
| --- | --- |
| `WFWorkflowActions` | 动作数组，主体 |
| `WFWorkflowIcon` | `{WFWorkflowIconStartColor: int, WFWorkflowIconGlyphNumber: int}` |
| `WFWorkflowClientVersion` | 编写时的客户端版本 |
| `WFWorkflowMinimumClientVersion` / `...String` | 最低客户端版本（iOS 17 约 2400–3500，iOS 18 约 4000+） |
| `WFWorkflowTypes` | 入口：`WFWorkflowTypeShowInSearch`、`WFWorkflowTypeShareExtension`、`WFWorkflowTypeWatch`、`WFWorkflowTypeNCWidget` 等 |
| `WFWorkflowInputContentItemClasses` | 分享表单接受的输入类型 |
| `WFWorkflowImportQuestions` | 导入时向用户提问 |

## 单个动作

```json
{
  "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
  "WFWorkflowActionParameters": {
    "UUID": "8B4E1234-AAAA-4444-8888-0123456789AB",
    "WFVariableName": "TodayCalories",
    "WFInput": { "...": "..." }
  }
}
```

`UUID` 全局唯一，后续动作通过它引用本动作的输出。

## 控制流

`conditional` / `choosefrommenu` / `repeat.count` / `repeat.each` 都由多条动作组成，靠 `GroupingIdentifier` 配对（不是靠顺序）：

| `WFControlFlowMode` | 含义 |
| --- | --- |
| `0` | 开始（if / 菜单 / repeat） |
| `1` | 中间分支（否则 / 菜单项） |
| `2` | 结束 |

`choosefrommenu` 的 mode 0 动作带 `WFMenuItems` 列表，每个 mode 1 动作带 `WFMenuItemTitle`，两边要一一对应。

## 变量引用

| `WFSerializationType` | 用途 |
| --- | --- |
| `WFTextTokenAttachment` | 整个参数就是一个变量 |
| `WFTextTokenString` | 字符串里嵌变量：文本中用 `\uFFFC` 占位，`attachmentsByRange` 的 `"{位置, 1}"` 映射到变量 |
| `WFNumberSubstitutableState` | 数字参数用变量替换 |
| `WFDictionaryFieldValue` | 字典字段 |

引用前序动作输出（推荐）：

```json
{
  "Value": { "Type": "ActionOutput", "OutputUUID": "<动作 UUID>", "OutputName": "<输出名>" },
  "WFSerializationType": "WFTextTokenAttachment"
}
```

引用命名变量：`{"Type": "Variable", "VariableName": "<名>"}`。其他内置来源：`"Type": "ExtensionInput"`（快捷指令输入）、`"CurrentDate"`、`"Clipboard"`、`"Ask"`。

## 常用动作 ID

| 类别 | ID（省略前缀 `is.workflow.actions.`） |
| --- | --- |
| 变量与控制 | `setvariable` `getvariable` `appendvariable` `conditional` `choosefrommenu` `repeat.count` `repeat.each` `exit` `nothing` `delay` `runworkflow` `comment` |
| 文本与数字 | `gettext` `number` `math` `calculateexpression` `round` `statistics` `format.number` `text.combine` `text.split` `text.replace` `text.match` `count` `detect.text` |
| 列表与字典 | `list` `getitemfromlist` `dictionary` `getvalueforkey` `setvalueforkey` `detect.dictionary` |
| 日期 | `date` `adjustdate` `gettimebetweendates` `format.date` `addnewevent` `addnewreminder` |
| 文件与网络 | `url` `downloadurl` `openurl` `openx-callback` `getfile` `savefile` `appendfile` |
| 媒体 | `takephoto` `selectphoto` `recordaudio` `properties.images` `savetophotoalbum` `detect.qrcode` |
| 健康 | `filter.health.quantity` `health.quantity.log` |
| 交互 | `ask` `alert` `showresult` `choosefromlist` `notification` `speak` `dictate` `share` `copytoclipboard` `getclipboard` |
| 备忘录 | `filter.notes` `com.apple.mobilenotes.SharingExtension`（创建备忘录） |

第三方 AI Intent：豆包 `com.bot.doubao.AskAssistantIntent`，ChatGPT `com.openai.chat.*`，Apple 智能 `com.apple.intelligence.*`。

**最可靠的方法**：不确定某个动作的参数结构时，在 Shortcuts.app 里手工搭一个只含该动作的最小快捷指令，分享出 iCloud 链接后 `decompile`，照抄它的结构。
