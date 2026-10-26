# FoodAnalysis · AI 调用场景与提示词档案

> 「刚炫了啥（Bite Dance）」所有 AI 调用的唯一真源。修改提示词应先改本文件，再同步到 source.json。

## 概览

| ID | 触发分支 | 豆包 Intent UUID | 输入 | 输出契约 |
| --- | --- | --- | --- | --- |
| AI-01a | 餐食 · 拍照 | `22AA63BF-C5C5-4C7B-9BED-9431E73BC4DF` | 拍照照片 + `LogTime` + `Portion%` | 7 字段 JSON（食物/餐型/总重量/卡路里/蛋白质/脂肪/碳水化合物） |
| AI-01b | 餐食 · 相册 | `E1E3380C-FCA4-48F6-85C5-DA371C00AD38` | 相册照片 + `LogTime` + `Portion%` | 同 AI-01a |
| AI-02 | 餐食 · 质疑重问 | `539C3700-A178-45BF-AA38-532054E4293C` | 用户质疑文本 | 同 AI-01 |
| AI-03 | 固食 · 一次性记录 | `1A3C588F-DEA7-45F3-BB5F-5C31B87F99FF` | 营养成分表照片 | 9 字段 JSON（扁平 schema） |
| AI-04 | 录入固食 | `3EE429FD-E780-429D-87C3-2CECFD44AD9E` | 营养成分表照片 | 11 字段 JSON（扁平 schema） |

> **iOS 26 关键经验**：
> - 豆包 `showResult` 必须 `true` 才能返回 Dictionary 类型（`false` 返回 Text → gvf 报错）。`isTTSEnabled=false` 单独控制 TTS。
> - gvf 产出的 Dictionary Value 在 `Variable` 引用时无法自动 coerce（gettext 空串、math 得 0、SE 得 Attachment.txt）。**统一用 `ActionOutput` 引用**。
> - gvf 必须带 `CustomOutputName`，不带 `WFGetDictionaryValueType`。

---

## AI-01 · 餐食首轮分析（拍照 / 相册）

**输出契约**：
```json
{
  "食物": "string",
  "餐型": "string",
  "总重量": "number",
  "卡路里": "number",
  "蛋白质": "number",
  "脂肪": "number",
  "碳水化合物": "number"
}
```

**提示词**：
```
你是一位专业的卡路里评估助手。
图片中是我吃喝的食物本身，或者食物的商品条形码。如果图片是食物本身，请根据图片，分析图中的食物是什么，并估算食物的重量单位g，用括号标明在食物名后方，如果有多个，请用逗号隔开列出。
如果图片中的是商品条形码，请根据条形码查询食物名称和相关营养信息。
同时，依据我吃东西的时间{LogTime}，判断类型是早餐、午餐、晚餐，或者是加餐。
并且，依据估算的食物总重量（单位g）和我摄入的比例{Portion}%，估算我摄入的总卡路里（单位kcal），总蛋白质（单位g），总脂肪（单位g），总碳水化合物（单位g）。
请以 JSON 格式返回，不要添加任何解释或文本。
{
  "食物": "string",
  "餐型": "string",
  "总重量": number,
  "卡路里": number,
  "蛋白质": number,
  "脂肪": number,
  "碳水化合物": number
}
范例如下：
{
  "食物": "牛油果鸡蛋培根三明治（300g），咖啡加奶（200g）",
  "餐型": "早餐",
  "总重量": 500,
  "卡路里": 560,
  "蛋白质": 17,
  "脂肪": 36,
  "碳水化合物": 30
}
```

---

## AI-02 · 餐食质疑重问

**提示词**：
```
{用户质疑文本}，请重新思考我的问题。
只返回JSON，不要添加额外的代码，不要添加任何解释或文本。
{ 同 AI-01 schema }
```

---

## AI-03 · 固食 · 一次性记录

**输出契约**（V0.5.2 起扁平 schema）：
```json
{
  "name": "string",
  "unit": "g|ml|粒|片",
  "per_base": 100,
  "per_unit_calories": "number",
  "per_unit_protein": "number",
  "per_unit_fat": "number",
  "per_unit_carbohydrates": "number",
  "per_unit_sodium": "number",
  "per_unit_caffeine": "number"
}
```

**提示词**：
```
你是营养成分表解析助手。
图片是一张食品 / 补剂 / 药品的营养成分表或标签。
请返回严格 JSON（不要代码块，不要解释，key 全部小写，营养字段全部扁平放在顶层）：
{
  "name": "string",
  "unit": "g|ml|粒|片",
  "per_base": 100,
  "per_unit_calories": number,
  "per_unit_protein": number,
  "per_unit_fat": number,
  "per_unit_carbohydrates": number,
  "per_unit_sodium": number,
  "per_unit_caffeine": number
}
字段说明:
- per_base: 标签上"每份 = N 个 unit"的 N，通常 100 (g/ml) 或 1 (粒/片)。
- per_unit_*: 每 per_base 个 unit 里含多少 X。单位对齐 Apple Health（calories=kcal, protein/fat/carbohydrates=g, sodium/caffeine=mg）。
- 未知或不适用填 0。
```

---

## AI-04 · 录入固食

**输出契约**（V0.5.2 起扁平 schema）：
```json
{
  "name": "string",
  "category": "补剂|药品|食品饮品|其它",
  "unit": "g|ml|粒|片",
  "per_base": 100,
  "default_amount": 1,
  "per_unit_calories": "number",
  "per_unit_protein": "number",
  "per_unit_fat": "number",
  "per_unit_carbohydrates": "number",
  "per_unit_sodium": "number",
  "per_unit_caffeine": "number"
}
```

**提示词**：
```
你是营养成分表登记助手。
图片是一张食品 / 补剂 / 药品的营养成分表或包装。
请返回严格 JSON（不要代码块，不要解释，key 全部小写，营养字段全部扁平放在顶层）：
{
  "name": "string",
  "category": "补剂|药品|食品饮品|其它",
  "unit": "g|ml|粒|片",
  "per_base": 100,
  "default_amount": 1,
  "per_unit_calories": number,
  "per_unit_protein": number,
  "per_unit_fat": number,
  "per_unit_carbohydrates": number,
  "per_unit_sodium": number,
  "per_unit_caffeine": number
}
字段说明:
- per_base: 标签上"每份 = N 个 unit"的 N，通常 100 (g/ml) 或 1 (粒/片)。
- default_amount: 建议默认吃几份，通常 1，可小数。
- per_unit_*: 每 per_base 个 unit 里含多少 X。单位对齐 Apple Health。
```

---

## 变更记录

| 日期 | 版本 | 变更 |
| --- | --- | --- |
| 2026-04-17 | V0.3 | 建档；AI-01a/b/02 沿用 V0.2，新增 AI-03/04。 |
| 2026-04-18 | V0.4 | `fixed_foods.json` → 备忘录方案；字段去 `_mg` 后缀。 |
| 2026-04-20 | V0.5 | 合并回单 shortcut；AI-03/04 schema 不变。 |
| 2026-04-20 | V0.5.1~V0.5.2 | `base` → `per_base`；`per_unit` 展平为 6 个顶层字段；新增 `per_user_base`。 |
| 2026-04-21 | V0.5.3~V0.5.8 | 修 iOS 26 Dictionary Value 类型问题（详见 `VERSIONS.md` 经验教训）。提示词不变。 |
| 2026-04-21 | V0.6 | filter.notes 改完整 schema；计算链 Variable→ActionOutput 修 HealthKit 写 0；一次性新增结果展示。提示词不变。 |
