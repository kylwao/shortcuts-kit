# 已知平台坑

动作行为不符合预期时先查这里。新坑按文末格式追加，流程见 [contributing-upstream.md](contributing-upstream.md)。

## 目录

- P001 豆包 Intent 的 `showResult` 决定输出类型
- P002 字典取值结果用 `Variable` 引用时无法自动转换类型
- P003 `getvalueforkey` 的推荐写法
- P004 `detect.dictionary` 在 iOS 26 上不可靠
- P005 备忘录正文是富文本，不能直接转字典
- P006 iOS 26 上 `getfile` / `savefile` 持久化不可用
- P007 `math` 依赖隐式上一步输出容易算错
- P008 `filter.notes` 需要完整的 iOS 26 schema

---

### P001 豆包 Intent 的 `showResult` 决定输出类型

- 环境：iOS 26，`com.bot.doubao.AskAssistantIntent`
- 现象：后续 `getvalueforkey` 报错，取不到 JSON 字段。
- 原因：`showResult=true` 时输出是 Dictionary；`showResult=false` 时输出是 Text。语音播报由 `isTTSEnabled` 单独控制，和 `showResult` 无关。
- 解法：需要按 key 取值时，保持 `showResult=true`；不想播报就设 `isTTSEnabled=false`。
- 来源：FoodAnalysis V0.5.1 到 V0.5.7（误改为 `false` 后连续 6 个版本失败）

### P002 字典取值结果用 `Variable` 引用时无法自动转换类型

- 环境：iOS 26
- 现象：`getvalueforkey` 的结果被 `setvariable` 存成变量后，再用 `{"Type": "Variable"}` 引用：`gettext` 渲染为空字符串，`math` 计算结果为 0，备忘录 SharingExtension 渲染成 `Attachment.txt`，HealthKit 写入 0。
- 原因：Dictionary Value 类型在 `Variable` 引用路径上不会被自动转换。
- 解法：统一改用 `{"Type": "ActionOutput", "OutputUUID": ..., "OutputName": ...}` 直接引用产出该值的动作。
- 来源：FoodAnalysis V0.5.x、V0.6

### P003 `getvalueforkey` 的推荐写法

- 环境：iOS 26
- 现象：取值结果类型不稳定，或下游无法识别。
- 解法：显式给出 `WFInput`（指向字典来源）并设置 `CustomOutputName`；**不要**设置 `WFGetDictionaryValueType`。
- 来源：FoodAnalysis V0.5.8（回到 V0.3 餐食分支的写法后修复）

### P004 `detect.dictionary` 在 iOS 26 上不可靠

- 环境：iOS 26
- 现象：用 `detect.dictionary` 中转 AI 返回的结果时，各种组合都取不到值。
- 解法：AI 输出直接接 `getvalueforkey`（见 P001、P003），不经过 `detect.dictionary`。例外见 P005。
- 来源：FoodAnalysis V0.5.3 到 V0.5.5

### P005 备忘录正文是富文本，不能直接转字典

- 环境：iOS 26，`filter.notes` 取出的 Note Body
- 现象：对 Note Body 直接 `detect.dictionary` 失败。
- 解法：先 `detect.text` 转成纯文本，再 `detect.dictionary`。
- 来源：FoodAnalysis V0.6

### P006 iOS 26 上 `getfile` / `savefile` 持久化不可用

- 环境：iOS 26
- 现象：用 iCloud Drive 里的 JSON 文件持久化数据时，文件读写结果丢失。
- 解法：改用备忘录持久化（每条记录一条备忘录，放在专用文件夹，用 `filter.notes` 查询）。
- 备注：`--profile dev` 的遥测仍然使用 `savefile` / `appendfile` 写日志；如果真机上没有日志回流，先怀疑这一条。
- 来源：FoodAnalysis V0.3 到 V0.4

### P007 `math` 依赖隐式上一步输出容易算错

- 环境：iOS 26
- 现象：计算链中途插入动作后结果错乱，或类型转换失败导致结果为 0。
- 解法：每个 `math` 都显式设置 `WFInput`（左操作数）和 `WFMathOperand`（右操作数）；不依赖隐式的上一步输出，也不用 `gettext` 做数值类型转换。
- 来源：FoodAnalysis V0.7

### P008 `filter.notes` 需要完整的 iOS 26 schema

- 环境：iOS 26
- 现象：手写或简化过的 `filter.notes` 筛选条件不生效，查不到目标备忘录。
- 解法：在 Shortcuts.app 里手工配置一次筛选，`decompile` 出来后照抄完整结构（包括 Enumeration 和 AppIntentDescriptor）。
- 来源：FoodAnalysis V0.6

---

## 新条目格式

```markdown
### P<三位编号> <一句话标题>

- 环境：iOS/macOS 版本，涉及的动作 ID
- 现象：用户能观察到什么
- 原因：已确认的原因；不确定就写「推测」
- 解法：具体做法，最好附最小 JSON 片段
- 来源：<项目类型>（脱敏，不写私人项目名或路径）
```
