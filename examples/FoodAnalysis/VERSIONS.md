# FoodAnalysis · 版本说明

> 「刚炫了啥（Bite Dance）」系列快捷指令的开发档案。AI 提示词统一在 [`AI_PROMPTS.md`](AI_PROMPTS.md)。

## 项目简介

- **目标**：用豆包 AI 识别食物照片 / 营养成分表 / 补剂标签，自动计算热量与营养素，写入 Apple Health + Calendar。
- **技术栈**：Apple Shortcuts + 豆包 AI（`com.bot.doubao.AskAssistantIntent`）+ HealthKit + Calendar + Notes（固食持久化）。
- **反编译工具**：本仓库的 `shortcuts-src`（`shortcuts-src decompile` / `compile`）。
- **公开范围**：本示例只公开当前版本 `V0.7`；下表中的 V0.1 到 V0.6 仅保留变更记录，源码未公开。

## 版本矩阵

| 版本 | 动作数 | 状态 | 主要改动 |
| --- | --- | --- | --- |
| `V0.1` | 204 | 归档 | 原作者「吃吃喝喝 2.1.dola」首次反编译。 |
| `V0.2` | 204 | 归档 | 纯转录基线，只改名。 |
| `V0.3` | 357 | 归档 | 重命名；三路主菜单（餐食 / 固食 / 录入固食）；`fixed_foods.json` + 备忘录双存储。iOS 26 上 `getfile`/`savefile` 丢失，不可用。 |
| `V0.4` | 餐食 203 / 固食 175 | 归档 | 拆成两个 shortcut；固食改用每食 1 条备忘录 + `filter.notes`；编译改 `plutil` 管线。 |
| `V0.5~V0.5.8` | 418→465 | 归档 | V0.4 合并回单 shortcut。经历 8 个 patch 修复 iOS 26 的 Dictionary Value 类型问题（详见「V0.5.x 经验教训」）。 |
| `V0.6` | 480 | 归档 | 基于用户手动修正的 V0.5.8。修已录入 filter.notes schema（完整 iOS 26 Enumeration）；两条计算链 gettext 类型强转修 HealthKit 写 0；已录入加 detect.text → detect.dictionary 转 Note Body；展示文本全改 ActionOutput 引用。 |
| **`V0.7`** | **462** | **当前** | 基于用户手动调整的 V0.6.2。计算链重写为 multiple 模式（math 显式 WFInput，不用 gettext coerce）；固食两条分支共享结果展示（确认/取消）移到固食子菜单结束后。 |

## 目录结构

```
FoodAnalysis/
├── VERSIONS.md
├── AI_PROMPTS.md
└── V0.7/                   # 当前
    ├── 刚炫了啥 Bite Dance V0.7.source.json
    ├── 刚炫了啥 Bite Dance V0.7.source.xml
    ├── 刚炫了啥 Bite Dance V0.7.flow.md
    └── 刚炫了啥 Bite Dance V0.7.meta.json
```

签名产物用 `shortcuts-src compile "V0.7/刚炫了啥 Bite Dance V0.7.source.json"` 在本地生成，不入仓。

> `*.source.json` / `*.source.xml` 互为规范来源；`flow.md` / `meta.json` 只读。

---

## 流程概览

### 能量基线（动作 0–117）

沿用 V0.1：静息能量 7 天中位数（兜底 1800 kcal）+ 活跃能量 + 当日摄入 → 剩余摄入比例 + 三大营养素动态百分比。

### 主菜单（动作 #118）

| 菜单项 | 分支 |
| --- | --- |
| 🍱 餐食 | AI 识图估算 → 确认/质疑 → HealthKit + Calendar |
| 💊 固食 | 📒 已录入 / 📸 一次性 → 计算 → HealthKit + Calendar |
| 🆕 录入固食 | AI 读营养标 → 用户确认 → 备忘录存档到「固食档案」 |

### 备忘录 JSON schema（V0.5.2 起，12 个扁平字段）

```json
{
  "name": "山姆韩式烤肉",
  "category": "食品饮品",
  "unit": "g",
  "per_base": 100,
  "per_user_base": 1200,
  "default_amount": 0.75,
  "per_unit_calories": 189.7,
  "per_unit_protein": 9.7,
  "per_unit_fat": 14.0,
  "per_unit_carbohydrates": 6.4,
  "per_unit_sodium": 459,
  "per_unit_caffeine": 0
}
```

### 计算公式

**能量基线**（动作 #0-#38）：
```
TotalEnergyBudget = EstimateRestingEnergy + ActiveEnergy
RemainingBudget   = TotalEnergyBudget - DietaryEnergy
Calories%         = DietaryEnergy / TotalEnergyBudget × 100
```
- `EstimateRestingEnergy`：过去 7 天静息能量中位数（兜底 1800 kcal）
- `ActiveEnergy`：今日活跃能量（无数据时用 7 天中位数）
- `DietaryEnergy`：今日已摄入膳食能量

**三大营养素上限百分比**（动作 #51-#82）：
```
Protein% = 蛋白质已摄入_g × 40000 / (TotalEnergyBudget × ProteinNum)
Fat%     = 脂肪已摄入_g   × 90000 / (TotalEnergyBudget × FatNum)
Carb%    = 碳水已摄入_g   × 40000 / (TotalEnergyBudget × CarbNum)
```
常量 40000 = 4 kcal/g × 100 × 100；90000 = 9 kcal/g × 100 × 100。
ProteinNum/FatNum/CarbNum 默认 25/20/55（动作 #2-#4 可调，总和 100）。

| 营养素 | 上限（克） | 示例（2500 kcal） |
|---|---|---|
| 蛋白质 | `Budget × 25% / 4` | 156 g |
| 脂肪 | `Budget × 20% / 9` | 56 g |
| 碳水 | `Budget × 55% / 4` | 344 g |

**固食摄入计算**（动作 #275+ / #343+）：
```
已录入: multiple = per_user_base ÷ per_base × ActualServing
一次性: multiple = ActualAmount ÷ per_base
通用:   actual_X = per_unit_X × multiple
```

HealthKit 写入 4 条：Calories / Protein / Fat / Carbohydrates。Sodium / Caffeine 只入备忘录。

---

## V0.5.x 经验教训（iOS 26）

V0.5.1~V0.5.8 迭代了 8 个 patch，总结 3 个核心坑：

1. **`showResult` 控制豆包 output 类型**：`true` → Dictionary（gvf 可取 key），`false` → Text（gvf 报错）。`isTTSEnabled` 单独控制 TTS。V0.5.1 误改 `showResult=false` 导致 6 个版本全线失败，V0.5.7 改回 `true` 才修好。
2. **Dictionary Value 类型无法自动 coerce**：gvf 产出的 Dictionary Value 在 `Variable` 引用时——gettext 渲染字符串为空、math 计算为 0、SharingExtension 渲染为 Attachment.txt。**解法**：统一用 `ActionOutput`（OutputUUID + OutputName）替代 `Variable`（VariableName）引用。
3. **iOS 26 的 `detect.dictionary` 不可靠**：V0.5.3~V0.5.5 尝试各种 detect.dictionary 中转模式均失败。最终回到 V0.3 餐食同款：gvf 带显式 WFInput + CustomOutputName，不带 WFGetDictionaryValueType。

---

## V0.7 改动记录

> 基线：用户在 Shortcuts.app 里手动调整后分享的 V0.6.2。

**V0.6 系列累积修复**（V0.6 → V0.6.1 → V0.6.2，已合并到基线）：
- 已录入固食 filter.notes 改完整 iOS 26 schema（Enumeration + AppIntentDescriptor）。
- 计算链：`getvariable` 改 `gettext` 做 Dictionary Value → text 强转；math 操作数预转换纯文本变量。
- 已录入：Note Body 解析加 `detect.text` → `detect.dictionary` 两步（Note Body 是富文本，不能直接 detect.dictionary）。
- 展示文本 14 个附件全改 ActionOutput 引用。

**V0.7 改动**：
1. **计算链重写为 multiple 模式**（参考用户 iCloud shortcut）：
   - 已录入：`multiple = PerUserBase ÷ PerBase × ActualServing`，`actual_X = per_unit_X × multiple`
   - 一次性：`multiple = ActualAmount ÷ PerBase`，`actual_X = per_unit_X × multiple`
   - math 全部用显式 `WFInput`（左操作数）+ `WFMathOperand`（右操作数），不依赖隐式 previous output，不用 gettext 做数值类型转换。
2. **共享固食结果展示**：从一次性分支内移到固食子菜单结束后，已录入/一次性两条分支共享。Food/FoodUnit 预转纯文本（gettext coerce）。
3. 动作数 480 → 462。

**V0.8 TODO**
1. 注释不放版本信息，放简单的计算方法
2. 录入固食：命名方式调整 `${name}[${类型}]`将类型放在后面，便于筛选的时候太长看不到食物名字
3. 吃固食：
  已录入：筛选的时候没有按照类型分类，出了全部结果
  已录入：选择完固食之后，[换一个]逻辑还是空的
4. 吃完固食之后，是否可以默认弹出健康页 
5. 初始化蛋白质、脂肪、碳水 帮忙确认总和超过 100%是否可行 