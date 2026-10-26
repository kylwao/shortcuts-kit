# 刚炫了啥 Bite Dance V0.7

- 动作数量：**462**
- 最低客户端版本：`3010`
- 编写客户端版本：`4528.0.4.3`

## 流程

```text
  0 │ 注释  [WFCommentActionText=刚炫了啥（Bite Dance） V0.7
基于用户手动调整的 V0.6.2。
主菜单 3 路：🍱 餐食 / 💊 固食 / 🆕 录入固食。

【V0.7 改动】
1. 计算链重写为 multiple 模式（参考用户 iCloud shortcut）：
   已录入: multi…]
  1 │ 注释  [WFCommentActionText=下方三行分别是蛋白质、脂肪、碳水化合物占总能量的比例，通常参考成人推荐比例如下。可自行调整比例，确保总数100即可。
	•	蛋白质：10%–20%
	•	脂肪：20%–30%
	•	碳水化合物：50%–65%]
  2 │ 数字  [WFNumberActionNumber=25]
  3 │ 数字  [WFNumberActionNumber=20]
  4 │ 数字  [WFNumberActionNumber=55]
  5 │ 查找健康样本
  6 │ 统计  [WFStatisticsOperation=Median]
  7 │ 四舍五入
  8 │ 如果  [WFCondition=2; WFControlFlowMode=0]
    9 │ 设为变量  [WFVariableName=EstimateRestingEnergy]
 10 │ 否则  [WFControlFlowMode=1]
   11 │ 数字  [WFNumberActionNumber=1800]
   12 │ 设为变量  [WFVariableName=EstimateRestingEnergy]
 13 │ 结束如果  [WFControlFlowMode=2]
 14 │ 查找健康样本
 15 │ 统计  [WFStatisticsOperation=Median]
 16 │ 四舍五入
 17 │ 设为变量  [WFVariableName=EstimateActiveEnergy]
 18 │ 查找健康样本
 19 │ 统计  [WFStatisticsOperation=Sum]
 20 │ 四舍五入
 21 │ 设为变量  [WFVariableName=TrueActiveEnergy]
 22 │ 如果  [WFCondition=2; WFControlFlowMode=0]
   23 │ 设为变量  [WFVariableName=ActiveEnergy]
 24 │ 否则  [WFControlFlowMode=1]
   25 │ 设为变量  [WFVariableName=ActiveEnergy]
 26 │ 结束如果  [WFControlFlowMode=2]
 27 │ 查找健康样本
 28 │ 统计  [WFStatisticsOperation=Sum]
 29 │ 四舍五入
 30 │ 如果  [WFCondition=100; WFControlFlowMode=0]
   31 │ 设为变量  [WFVariableName=DietaryEnergy]
 32 │ 否则  [WFControlFlowMode=1]
   33 │ 数字  [WFNumberActionNumber=0]
   34 │ 设为变量  [WFVariableName=DietaryEnergy]
 35 │ 结束如果  [WFControlFlowMode=2]
 36 │ 计算
 37 │ 计算  [WFMathOperation=-]
 38 │ 计算表达式
 39 │ 设为变量  [WFVariableName=Calories%]
 40 │ 重复  [WFRepeatCount=10; WFControlFlowMode=0]
   41 │ 如果  [WFCondition=2; WFControlFlowMode=0]
     42 │ 合并文本
     43 │ 设为变量  [WFVariableName=Calories1]
     44 │ 计算  [WFMathOperation=-; WFMathOperand=10]
     45 │ 设为变量  [WFVariableName=Calories%]
   46 │ 否则  [WFControlFlowMode=1]
     47 │ 合并文本
     48 │ 设为变量  [WFVariableName=Calories2]
   49 │ 结束如果  [WFControlFlowMode=2]
 50 │ 结束重复  [WFControlFlowMode=2]
 51 │ 查找健康样本
 52 │ 统计  [WFStatisticsOperation=Sum]
 53 │ 如果  [WFCondition=100; WFControlFlowMode=0]
   54 │ 计算表达式
   55 │ 四舍五入
   56 │ 设为变量  [WFVariableName=Protein%]
   57 │ 设为变量  [WFVariableName=ProteinInitial%]
 58 │ 否则  [WFControlFlowMode=1]
   59 │ 数字  [WFNumberActionNumber=0]
   60 │ 设为变量  [WFVariableName=ProteinInitial%]
 61 │ 结束如果  [WFControlFlowMode=2]
 62 │ 查找健康样本
 63 │ 统计  [WFStatisticsOperation=Sum]
 64 │ 如果  [WFCondition=100; WFControlFlowMode=0]
   65 │ 计算表达式
   66 │ 四舍五入
   67 │ 设为变量  [WFVariableName=Fat%]
   68 │ 设为变量  [WFVariableName=FatInitial%]
 69 │ 否则  [WFControlFlowMode=1]
   70 │ 数字  [WFNumberActionNumber=0]
   71 │ 设为变量  [WFVariableName=FatInitial%]
 72 │ 结束如果  [WFControlFlowMode=2]
 73 │ 查找健康样本
 74 │ 统计  [WFStatisticsOperation=Sum]
 75 │ 如果  [WFCondition=100; WFControlFlowMode=0]
   76 │ 计算表达式
   77 │ 四舍五入
   78 │ 设为变量  [WFVariableName=Carb%]
   79 │ 设为变量  [WFVariableName=CarbInitial%]
 80 │ 否则  [WFControlFlowMode=1]
   81 │ 数字  [WFNumberActionNumber=0]
   82 │ 设为变量  [WFVariableName=CarbInitial%]
 83 │ 结束如果  [WFControlFlowMode=2]
 84 │ 重复  [WFRepeatCount=5; WFControlFlowMode=0]
   85 │ 如果  [WFCondition=2; WFControlFlowMode=0]
     86 │ 合并文本
     87 │ 设为变量  [WFVariableName=Protein1]
     88 │ 计算  [WFMathOperation=-; WFMathOperand=20]
     89 │ 设为变量  [WFVariableName=Protein%]
   90 │ 否则  [WFControlFlowMode=1]
     91 │ 合并文本
     92 │ 设为变量  [WFVariableName=Protein2]
   93 │ 结束如果  [WFControlFlowMode=2]
 94 │ 结束重复  [WFControlFlowMode=2]
 95 │ 重复  [WFRepeatCount=5; WFControlFlowMode=0]
   96 │ 如果  [WFCondition=2; WFControlFlowMode=0]
     97 │ 合并文本
     98 │ 设为变量  [WFVariableName=Fat1]
     99 │ 计算  [WFMathOperation=-; WFMathOperand=20]
    100 │ 设为变量  [WFVariableName=Fat%]
  101 │ 否则  [WFControlFlowMode=1]
    102 │ 合并文本
    103 │ 设为变量  [WFVariableName=Fat2]
  104 │ 结束如果  [WFControlFlowMode=2]
105 │ 结束重复  [WFControlFlowMode=2]
106 │ 重复  [WFRepeatCount=5; WFControlFlowMode=0]
  107 │ 如果  [WFCondition=2; WFControlFlowMode=0]
    108 │ 合并文本
    109 │ 设为变量  [WFVariableName=Carb1]
    110 │ 计算  [WFMathOperation=-; WFMathOperand=20]
    111 │ 设为变量  [WFVariableName=Carb%]
  112 │ 否则  [WFControlFlowMode=1]
    113 │ 合并文本
    114 │ 设为变量  [WFVariableName=Carb2]
  115 │ 结束如果  [WFControlFlowMode=2]
116 │ 结束重复  [WFControlFlowMode=2]
117 │ 文本  [WFTextActionText=🎯预估总消耗：￼ kcal
🍽️今日已摄入：￼ kcal
🥣还可以摄入：￼ kcal
￼￼

蛋白质：￼￼  ￼%
脂    肪：￼￼  ￼%
碳    水：￼￼  ￼%

现在开始记录吧～]
118 │ 从菜单中选择  [WFMenuPrompt=￼; WFControlFlowMode=0]
119 │ 菜单项  [WFMenuItemTitle=🍱 餐食; WFControlFlowMode=1]
  120 │ 从菜单中选择  [WFMenuPrompt=￼; WFControlFlowMode=0]
  121 │ 菜单项  [WFMenuItemTitle=拍照📷; WFControlFlowMode=1]
    122 │ 拍照
    123 │ 设为变量  [WFVariableName=LogTime]
  124 │ 菜单项  [WFMenuItemTitle=相册🖼️; WFControlFlowMode=1]
    125 │ 选取照片
    126 │ 获取图像属性
    127 │ 如果  [WFControlFlowMode=0]
      128 │ 设为变量  [WFVariableName=LogTime]
    129 │ 否则  [WFControlFlowMode=1]
      130 │ 设为变量  [WFVariableName=LogTime]
    131 │ 结束如果  [WFControlFlowMode=2]
  132 │ 菜单项  [WFMenuItemTitle=不了🙂‍↔️; WFControlFlowMode=1]
    133 │ 退出快捷指令
  134 │ 结束菜单  [WFControlFlowMode=2]
  135 │ 从菜单中选择  [WFMenuPrompt=吃了多少呢？; WFControlFlowMode=0]
  136 │ 菜单项  [WFMenuItemTitle=一半; WFControlFlowMode=1]
    137 │ 数字  [WFNumberActionNumber=50]
    138 │ 设为变量  [WFVariableName=Portion]
  139 │ 菜单项  [WFMenuItemTitle=全部; WFControlFlowMode=1]
    140 │ 数字  [WFNumberActionNumber=100]
    141 │ 设为变量  [WFVariableName=Portion]
  142 │ 菜单项  [WFMenuItemTitle=其他; WFControlFlowMode=1]
    143 │ 询问输入  [WFAskActionPrompt=手动输入百分比数字（⚠️：不要加%）; WFAskActionDefaultAnswer=30]
    144 │ 设为变量  [WFVariableName=Portion]
  145 │ 结束菜单  [WFControlFlowMode=2]
  146 │ 文本  [WFTextActionText=你是一位专业的卡路里评估助手。
图片中是我吃喝的食物本身，或者食物的商品条形码。如果图片是食物本身，请根据图片，分析图中的食物是什么，并估算食物的重量单位g，用括号标明在食物名后方，如果有多个，请用逗号隔开列出。
如果图片中的是商品条形码，请根据条形码查询食物名称和相关营养信息…]
  147 │ 如果  [WFCondition=100; WFControlFlowMode=0]
    148 │ 豆包 AI 助手
    149 │ 设为变量  [WFVariableName=AIResultD]
  150 │ 否则  [WFControlFlowMode=1]
    151 │ 豆包 AI 助手
    152 │ 设为变量  [WFVariableName=AIResultD]
  153 │ 结束如果  [WFControlFlowMode=2]
  154 │ 获取字典值  [WFDictionaryKey=食物]
  155 │ 获取字典值  [WFDictionaryKey=餐型]
  156 │ 获取字典值  [WFDictionaryKey=总重量]
  157 │ 获取字典值  [WFDictionaryKey=卡路里]
  158 │ 获取字典值  [WFDictionaryKey=蛋白质]
  159 │ 获取字典值  [WFDictionaryKey=脂肪]
  160 │ 获取字典值  [WFDictionaryKey=碳水化合物]
  161 │ 文本  [WFTextActionText=👩‍🏫聪明的豆老师提供了以下内容：
食物：￼
餐型：￼
时间：￼
食物总量：￼ g
摄入比例：￼ %

热量：￼ kcal
蛋白质：￼ g
脂肪：￼ g
碳水化合物：￼ g

📝如何在Health和Calendar记录呢？]
  162 │ 从菜单中选择  [WFMenuPrompt=￼; WFControlFlowMode=0]
  163 │ 菜单项  [WFMenuItemTitle=✅直接记录; WFControlFlowMode=1]
    164 │ 设为变量  [WFVariableName=Food]
    165 │ 设为变量  [WFVariableName=Meal]
    166 │ 设为变量  [WFVariableName=Amount]
    167 │ 设为变量  [WFVariableName=Calories]
    168 │ 设为变量  [WFVariableName=Protein]
    169 │ 设为变量  [WFVariableName=Fat]
    170 │ 设为变量  [WFVariableName=Carbohydrates]
  171 │ 菜单项  [WFMenuItemTitle=🤨质疑豆老师; WFControlFlowMode=1]
    172 │ 询问输入  [WFAskActionPrompt=请输入质疑的内容]
    173 │ 文本  [WFTextActionText=￼，请重新思考我的问题。
只返回JSON，不要添加额外的代码，不要添加任何解释或文本。
{ 
"食物": "string", 
"餐型": "string", 
"总重量": number， 
"卡路里": number, 
"蛋白质": number, 
"脂肪": numb…]
    174 │ 豆包 AI 助手
    175 │ 设为变量  [WFVariableName=ResultD2]
    176 │ 获取字典值  [WFDictionaryKey=食物]
    177 │ 获取字典值  [WFDictionaryKey=餐型]
    178 │ 获取字典值  [WFDictionaryKey=总重量]
    179 │ 获取字典值  [WFDictionaryKey=卡路里]
    180 │ 获取字典值  [WFDictionaryKey=蛋白质]
    181 │ 获取字典值  [WFDictionaryKey=脂肪]
    182 │ 获取字典值  [WFDictionaryKey=碳水化合物]
    183 │ 文本  [WFTextActionText=👩‍🏫聪明的豆老师又思考了一遍，得出以下结论：
食物：￼
餐型：￼
时间：￼
食物总量：￼ g
摄入比例：￼ %

热量：￼ kcal
蛋白质：￼ g
脂肪： ￼ g
碳水化合物：￼ g

📝是否在Health和Calendar记录呢？]
    184 │ 从菜单中选择  [WFMenuPrompt=￼; WFControlFlowMode=0]
    185 │ 菜单项  [WFMenuItemTitle=🙆是; WFControlFlowMode=1]
      186 │ 设为变量  [WFVariableName=Food]
      187 │ 设为变量  [WFVariableName=Meal]
      188 │ 设为变量  [WFVariableName=Amount]
      189 │ 设为变量  [WFVariableName=Calories]
      190 │ 设为变量  [WFVariableName=Protein]
      191 │ 设为变量  [WFVariableName=Fat]
      192 │ 设为变量  [WFVariableName=Carbohydrates]
    193 │ 菜单项  [WFMenuItemTitle=🙅‍♀️否; WFControlFlowMode=1]
      194 │ 退出快捷指令
    195 │ 结束菜单  [WFControlFlowMode=2]
  196 │ 菜单项  [WFMenuItemTitle=⛔️不做记录; WFControlFlowMode=1]
    197 │ 退出快捷指令
  198 │ 结束菜单  [WFControlFlowMode=2]
199 │ 菜单项  [WFMenuItemTitle=💊 固食; WFControlFlowMode=1]
  200 │ 日期
  201 │ 设为变量  [WFVariableName=LogTime]
  202 │ 从菜单中选择  [WFMenuPrompt=选择记录方式; WFControlFlowMode=0]
  203 │ 菜单项  [WFMenuItemTitle=📒 已录入固食; WFControlFlowMode=1]
    204 │ 文本  [WFTextActionText=选择固食类型]
    205 │ 从菜单中选择  [WFMenuPrompt=￼; WFControlFlowMode=0]
    206 │ 菜单项  [WFMenuItemTitle=补剂; WFControlFlowMode=1]
      207 │ 文本  [WFTextActionText=补剂]
      208 │ 设为变量  [WFVariableName=FilterCategory]
    209 │ 菜单项  [WFMenuItemTitle=药品; WFControlFlowMode=1]
      210 │ 文本  [WFTextActionText=药品]
      211 │ 设为变量  [WFVariableName=FilterCategory]
    212 │ 菜单项  [WFMenuItemTitle=食品饮品; WFControlFlowMode=1]
      213 │ 文本  [WFTextActionText=食品饮品]
      214 │ 设为变量  [WFVariableName=FilterCategory]
    215 │ 菜单项  [WFMenuItemTitle=其它; WFControlFlowMode=1]
      216 │ 文本  [WFTextActionText=其它]
      217 │ 设为变量  [WFVariableName=FilterCategory]
    218 │ 结束菜单  [WFControlFlowMode=2]
    219 │ is.workflow.actions.filter.notes
    220 │ is.workflow.actions.choosefromlist
    221 │ 设为变量  [WFVariableName=SelectedNote]
    222 │ 设为变量  [WFVariableName=FoodJson]
    223 │ is.workflow.actions.detect.text
    224 │ 从输入获取字典
    225 │ 设为变量  [WFVariableName=FoodDict]
    226 │ 获取字典值  [WFDictionaryKey=name]
    227 │ 设为变量  [WFVariableName=FoodName]
    228 │ 获取字典值  [WFDictionaryKey=category]
    229 │ 设为变量  [WFVariableName=FoodCategory]
    230 │ 获取字典值  [WFDictionaryKey=unit]
    231 │ 设为变量  [WFVariableName=FoodUnit]
    232 │ 获取字典值  [WFDictionaryKey=per_base]
    233 │ 设为变量  [WFVariableName=FoodPerBase]
    234 │ 获取字典值  [WFDictionaryKey=per_user_base]
    235 │ 设为变量  [WFVariableName=FoodPerUserBase]
    236 │ 获取字典值  [WFDictionaryKey=default_amount]
    237 │ 设为变量  [WFVariableName=FoodDefault]
    238 │ 获取字典值  [WFDictionaryKey=per_unit_calories]
    239 │ 设为变量  [WFVariableName=FoodPerUnitCalories]
    240 │ 获取字典值  [WFDictionaryKey=per_unit_protein]
    241 │ 设为变量  [WFVariableName=FoodPerUnitProtein]
    242 │ 获取字典值  [WFDictionaryKey=per_unit_fat]
    243 │ 设为变量  [WFVariableName=FoodPerUnitFat]
    244 │ 获取字典值  [WFDictionaryKey=per_unit_carbohydrates]
    245 │ 设为变量  [WFVariableName=FoodPerUnitCarbohydrates]
    246 │ 获取字典值  [WFDictionaryKey=per_unit_sodium]
    247 │ 设为变量  [WFVariableName=FoodPerUnitSodium]
    248 │ 获取字典值  [WFDictionaryKey=per_unit_caffeine]
    249 │ 设为变量  [WFVariableName=FoodPerUnitCaffeine]
    250 │ 文本  [WFTextActionText=📒 已选中以下固食：
名称： ￼
类型：￼
单位：￼
每份 = ￼ ￼（用户定义）
默认吃：￼ 份

每 ￼ ￼ 标准营养：
  热量：￼ kcal
  蛋白质：￼ g
  脂肪：￼ g
  碳水化合物：￼ g
  钠：￼ mg
  咖啡因：￼ mg]
    251 │ 从菜单中选择  [WFMenuPrompt=￼; WFControlFlowMode=0]
    252 │ 菜单项  [WFMenuItemTitle=✅ 开吃; WFControlFlowMode=1]
    253 │ 菜单项  [WFMenuItemTitle=↔️ 换一个; WFControlFlowMode=1]
      254 │ 退出快捷指令
    255 │ 菜单项  [WFMenuItemTitle=❌ 取消; WFControlFlowMode=1]
      256 │ 退出快捷指令
    257 │ 结束菜单  [WFControlFlowMode=2]
    258 │ 询问输入  [WFAskActionPrompt=吃了几份？（每份 ￼ ￼，默认吃 ￼ 份）; WFAskActionDefaultAnswer=￼]
    259 │ 设为变量  [WFVariableName=ActualServing]
    260 │ 文本  [WFTextActionText=这一口算哪一餐？]
    261 │ 从菜单中选择  [WFMenuPrompt=￼; WFControlFlowMode=0]
    262 │ 菜单项  [WFMenuItemTitle=早餐; WFControlFlowMode=1]
      263 │ 文本  [WFTextActionText=早餐]
      264 │ 设为变量  [WFVariableName=Meal]
    265 │ 菜单项  [WFMenuItemTitle=午餐; WFControlFlowMode=1]
      266 │ 文本  [WFTextActionText=午餐]
      267 │ 设为变量  [WFVariableName=Meal]
    268 │ 菜单项  [WFMenuItemTitle=晚餐; WFControlFlowMode=1]
      269 │ 文本  [WFTextActionText=晚餐]
      270 │ 设为变量  [WFVariableName=Meal]
    271 │ 菜单项  [WFMenuItemTitle=加餐; WFControlFlowMode=1]
      272 │ 文本  [WFTextActionText=加餐]
      273 │ 设为变量  [WFVariableName=Meal]
    274 │ 结束菜单  [WFControlFlowMode=2]
    275 │ 计算  [WFMathOperation=÷]
    276 │ 计算  [WFMathOperation=×]
    277 │ 设为变量  [WFVariableName=multiple]
    278 │ 计算  [WFMathOperation=×]
    279 │ 设为变量  [WFVariableName=Calories]
    280 │ 计算  [WFMathOperation=×]
    281 │ 设为变量  [WFVariableName=Protein]
    282 │ 计算  [WFMathOperation=×]
    283 │ 设为变量  [WFVariableName=Fat]
    284 │ 计算  [WFMathOperation=×]
    285 │ 设为变量  [WFVariableName=Carbohydrates]
    286 │ 计算  [WFMathOperation=×]
    287 │ 设为变量  [WFVariableName=Amount]
    288 │ 设为变量  [WFVariableName=Food]
  289 │ 菜单项  [WFMenuItemTitle=📸 一次性记录; WFControlFlowMode=1]
    290 │ 文本  [WFTextActionText=选择图片来源]
    291 │ 从菜单中选择  [WFMenuPrompt=￼; WFControlFlowMode=0]
    292 │ 菜单项  [WFMenuItemTitle=📷 拍照; WFControlFlowMode=1]
      293 │ 拍照
      294 │ 设为变量  [WFVariableName=FoodImage]
    295 │ 菜单项  [WFMenuItemTitle=🖼️ 相册; WFControlFlowMode=1]
      296 │ 选取照片
      297 │ 设为变量  [WFVariableName=FoodImage]
    298 │ 结束菜单  [WFControlFlowMode=2]
    299 │ 文本  [WFTextActionText=你是营养成分表解析助手。
图片是一张食品 / 补剂 / 药品的营养成分表或标签。
请返回严格 JSON（不要代码块，不要解释，key 全部小写，营养字段全部扁平放在顶层）：
{
  "name": "string",
  "unit": "g|ml|粒|片",
  "per_b…]
    300 │ 豆包 AI 助手
    301 │ 设为变量  [WFVariableName=AIResultD]
    302 │ 获取字典值  [WFDictionaryKey=name]
    303 │ 设为变量  [WFVariableName=FoodName]
    304 │ 获取字典值  [WFDictionaryKey=unit]
    305 │ 设为变量  [WFVariableName=FoodUnit]
    306 │ 获取字典值  [WFDictionaryKey=per_base]
    307 │ 设为变量  [WFVariableName=FoodPerBase]
    308 │ 获取字典值  [WFDictionaryKey=per_unit_calories]
    309 │ 设为变量  [WFVariableName=FoodPerUnitCalories]
    310 │ 获取字典值  [WFDictionaryKey=per_unit_protein]
    311 │ 设为变量  [WFVariableName=FoodPerUnitProtein]
    312 │ 获取字典值  [WFDictionaryKey=per_unit_fat]
    313 │ 设为变量  [WFVariableName=FoodPerUnitFat]
    314 │ 获取字典值  [WFDictionaryKey=per_unit_carbohydrates]
    315 │ 设为变量  [WFVariableName=FoodPerUnitCarbohydrates]
    316 │ 获取字典值  [WFDictionaryKey=per_unit_sodium]
    317 │ 设为变量  [WFVariableName=FoodPerUnitSodium]
    318 │ 获取字典值  [WFDictionaryKey=per_unit_caffeine]
    319 │ 设为变量  [WFVariableName=FoodPerUnitCaffeine]
    320 │ 文本  [WFTextActionText=📸 AI 识别结果：
名称： ￼
单位：￼

每 ￼ ￼ 营养：
  热量：￼ kcal
  蛋白质：￼ g
  脂肪：￼ g
  碳水化合物：￼ g
  钠：￼ mg
  咖啡因：￼ mg]
    321 │ 从菜单中选择  [WFMenuPrompt=￼; WFControlFlowMode=0]
    322 │ 菜单项  [WFMenuItemTitle=✅ 继续记录; WFControlFlowMode=1]
    323 │ 菜单项  [WFMenuItemTitle=❌ 取消; WFControlFlowMode=1]
      324 │ 退出快捷指令
    325 │ 结束菜单  [WFControlFlowMode=2]
    326 │ 询问输入  [WFAskActionPrompt=吃了多少 ￼？（每 ￼ ￼ 营养见上）; WFAskActionDefaultAnswer=￼]
    327 │ 设为变量  [WFVariableName=ActualAmount]
    328 │ 文本  [WFTextActionText=这一口算哪一餐？]
    329 │ 从菜单中选择  [WFMenuPrompt=￼; WFControlFlowMode=0]
    330 │ 菜单项  [WFMenuItemTitle=早餐; WFControlFlowMode=1]
      331 │ 文本  [WFTextActionText=早餐]
      332 │ 设为变量  [WFVariableName=Meal]
    333 │ 菜单项  [WFMenuItemTitle=午餐; WFControlFlowMode=1]
      334 │ 文本  [WFTextActionText=午餐]
      335 │ 设为变量  [WFVariableName=Meal]
    336 │ 菜单项  [WFMenuItemTitle=晚餐; WFControlFlowMode=1]
      337 │ 文本  [WFTextActionText=晚餐]
      338 │ 设为变量  [WFVariableName=Meal]
    339 │ 菜单项  [WFMenuItemTitle=加餐; WFControlFlowMode=1]
      340 │ 文本  [WFTextActionText=加餐]
      341 │ 设为变量  [WFVariableName=Meal]
    342 │ 结束菜单  [WFControlFlowMode=2]
    343 │ 计算  [WFMathOperation=÷]
    344 │ 设为变量  [WFVariableName=multiple]
    345 │ 计算  [WFMathOperation=×]
    346 │ 设为变量  [WFVariableName=Calories]
    347 │ 计算  [WFMathOperation=×]
    348 │ 设为变量  [WFVariableName=Protein]
    349 │ 计算  [WFMathOperation=×]
    350 │ 设为变量  [WFVariableName=Fat]
    351 │ 计算  [WFMathOperation=×]
    352 │ 设为变量  [WFVariableName=Carbohydrates]
    353 │ 设为变量  [WFVariableName=Amount]
    354 │ 设为变量  [WFVariableName=Food]
  355 │ 结束菜单  [WFControlFlowMode=2]
  356 │ 文本  [WFTextActionText=￼]
  357 │ 设为变量  [WFVariableName=_Food]
  358 │ 文本  [WFTextActionText=￼]
  359 │ 设为变量  [WFVariableName=_FoodUnit]
  360 │ 文本  [WFTextActionText=食物：￼
餐型：￼
食物总量：￼ ￼

热量：￼ kcal
蛋白质：￼ g
脂肪：￼ g
碳水化合物：￼ g]
  361 │ 从菜单中选择  [WFMenuPrompt=￼; WFControlFlowMode=0]
  362 │ 菜单项  [WFMenuItemTitle=✅ 确认记录; WFControlFlowMode=1]
  363 │ 菜单项  [WFMenuItemTitle=❌ 取消; WFControlFlowMode=1]
    364 │ 退出快捷指令
  365 │ 结束菜单  [WFControlFlowMode=2]
366 │ 菜单项  [WFMenuItemTitle=🆕 录入固食; WFControlFlowMode=1]
  367 │ 文本  [WFTextActionText=选择图片来源]
  368 │ 从菜单中选择  [WFMenuPrompt=￼; WFControlFlowMode=0]
  369 │ 菜单项  [WFMenuItemTitle=📷 拍照; WFControlFlowMode=1]
    370 │ 拍照
    371 │ 设为变量  [WFVariableName=FoodImage]
  372 │ 菜单项  [WFMenuItemTitle=🖼️ 相册; WFControlFlowMode=1]
    373 │ 选取照片
    374 │ 设为变量  [WFVariableName=FoodImage]
  375 │ 结束菜单  [WFControlFlowMode=2]
  376 │ 文本  [WFTextActionText=你是营养成分表登记助手。
图片是一张食品 / 补剂 / 药品的营养成分表或包装。
请返回严格 JSON（不要代码块，不要解释，key 全部小写，营养字段全部扁平放在顶层）：
{
  "name": "string",
  "category": "补剂|药品|食品饮品|其它",…]
  377 │ 豆包 AI 助手
  378 │ 设为变量  [WFVariableName=RegistryAIResult]
  379 │ 获取字典值  [WFDictionaryKey=name]
  380 │ 设为变量  [WFVariableName=AI_Name]
  381 │ 获取字典值  [WFDictionaryKey=category]
  382 │ 设为变量  [WFVariableName=AI_Category]
  383 │ 获取字典值  [WFDictionaryKey=unit]
  384 │ 设为变量  [WFVariableName=AI_Unit]
  385 │ 获取字典值  [WFDictionaryKey=per_base]
  386 │ 设为变量  [WFVariableName=AI_PerBase]
  387 │ 获取字典值  [WFDictionaryKey=default_amount]
  388 │ 设为变量  [WFVariableName=AI_DefaultAmount]
  389 │ 获取字典值  [WFDictionaryKey=per_unit_calories]
  390 │ 设为变量  [WFVariableName=AI_PerUnitCalories]
  391 │ 获取字典值  [WFDictionaryKey=per_unit_protein]
  392 │ 设为变量  [WFVariableName=AI_PerUnitProtein]
  393 │ 获取字典值  [WFDictionaryKey=per_unit_fat]
  394 │ 设为变量  [WFVariableName=AI_PerUnitFat]
  395 │ 获取字典值  [WFDictionaryKey=per_unit_carbohydrates]
  396 │ 设为变量  [WFVariableName=AI_PerUnitCarbohydrates]
  397 │ 获取字典值  [WFDictionaryKey=per_unit_sodium]
  398 │ 设为变量  [WFVariableName=AI_PerUnitSodium]
  399 │ 获取字典值  [WFDictionaryKey=per_unit_caffeine]
  400 │ 设为变量  [WFVariableName=AI_PerUnitCaffeine]
  401 │ 文本  [WFTextActionText=📝 识别到以下固食：
名称： ￼
类型：￼
单位：￼
标准每份：￼ ￼
AI 建议默认吃：￼ 份

每 ￼ ￼ 的营养：
  热量：￼ kcal
  蛋白质：￼ g
  脂肪：￼ g
  碳水化合物：￼ g
  钠：￼ mg
  咖啡因：￼ mg]
  402 │ 从菜单中选择  [WFMenuPrompt=￼; WFControlFlowMode=0]
  403 │ 菜单项  [WFMenuItemTitle=✅ 继续录入; WFControlFlowMode=1]
  404 │ 菜单项  [WFMenuItemTitle=❌ 取消; WFControlFlowMode=1]
    405 │ 退出快捷指令
  406 │ 结束菜单  [WFControlFlowMode=2]
  407 │ 询问输入  [WFAskActionPrompt=固食显示名; WFAskActionDefaultAnswer=￼]
  408 │ 设为变量  [WFVariableName=NewName]
  409 │ 文本  [WFTextActionText=选择类型（AI 识别：￼）]
  410 │ 从菜单中选择  [WFMenuPrompt=￼; WFControlFlowMode=0]
  411 │ 菜单项  [WFMenuItemTitle=补剂; WFControlFlowMode=1]
    412 │ 文本  [WFTextActionText=补剂]
    413 │ 设为变量  [WFVariableName=NewCategory]
  414 │ 菜单项  [WFMenuItemTitle=药品; WFControlFlowMode=1]
    415 │ 文本  [WFTextActionText=药品]
    416 │ 设为变量  [WFVariableName=NewCategory]
  417 │ 菜单项  [WFMenuItemTitle=食品饮品; WFControlFlowMode=1]
    418 │ 文本  [WFTextActionText=食品饮品]
    419 │ 设为变量  [WFVariableName=NewCategory]
  420 │ 菜单项  [WFMenuItemTitle=其它; WFControlFlowMode=1]
    421 │ 文本  [WFTextActionText=其它]
    422 │ 设为变量  [WFVariableName=NewCategory]
  423 │ 结束菜单  [WFControlFlowMode=2]
  424 │ 文本  [WFTextActionText=选择基准单位（AI 识别：￼）]
  425 │ 从菜单中选择  [WFMenuPrompt=￼; WFControlFlowMode=0]
  426 │ 菜单项  [WFMenuItemTitle=g; WFControlFlowMode=1]
    427 │ 文本  [WFTextActionText=g]
    428 │ 设为变量  [WFVariableName=NewUnit]
  429 │ 菜单项  [WFMenuItemTitle=ml; WFControlFlowMode=1]
    430 │ 文本  [WFTextActionText=ml]
    431 │ 设为变量  [WFVariableName=NewUnit]
  432 │ 菜单项  [WFMenuItemTitle=粒; WFControlFlowMode=1]
    433 │ 文本  [WFTextActionText=粒]
    434 │ 设为变量  [WFVariableName=NewUnit]
  435 │ 菜单项  [WFMenuItemTitle=片; WFControlFlowMode=1]
    436 │ 文本  [WFTextActionText=片]
    437 │ 设为变量  [WFVariableName=NewUnit]
  438 │ 结束菜单  [WFControlFlowMode=2]
  439 │ 设为变量  [WFVariableName=NewPerBase]
  440 │ 询问输入  [WFAskActionPrompt=你定义的「一份」有多大 ￼？（默认 = 标准每份 ￼；例如一整盒 1200）; WFAskActionDefaultAnswer=￼]
  441 │ 设为变量  [WFVariableName=NewPerUserBase]
  442 │ 询问输入  [WFAskActionPrompt=默认吃几份（可小数如 0.75）; WFAskActionDefaultAnswer=￼]
  443 │ 设为变量  [WFVariableName=NewDefaultAmount]
  444 │ 设为变量  [WFVariableName=NewPerUnitCalories]
  445 │ 设为变量  [WFVariableName=NewPerUnitProtein]
  446 │ 设为变量  [WFVariableName=NewPerUnitFat]
  447 │ 设为变量  [WFVariableName=NewPerUnitCarbohydrates]
  448 │ 设为变量  [WFVariableName=NewPerUnitSodium]
  449 │ 设为变量  [WFVariableName=NewPerUnitCaffeine]
  450 │ 文本  [WFTextActionText=[￼]￼

{
  "name": "￼",
  "category": "￼",
  "unit": "￼",
  "per_base": ￼,
  "per_user_base": ￼,
  "default_amount": ￼,
  "per_unit_calories…]
  451 │ com.apple.mobilenotes.SharingExtension
  452 │ 显示结果  [Text=✅ 已创建备忘录：[￼]￼

已自动归档到「固食档案」文件夹。下次用「📒 已录入固食」就能直接选到。]
  453 │ 退出快捷指令
454 │ 结束菜单  [WFControlFlowMode=2]
455 │ 记录健康样本
456 │ 记录健康样本
457 │ 记录健康样本
458 │ 记录健康样本
459 │ 调整日期
460 │ 添加日历事件
461 │ 显示结果  [Text=OK啦～]
```

## 关键长文本

### #0 · WFCommentActionText

```
刚炫了啥（Bite Dance） V0.7
基于用户手动调整的 V0.6.2。
主菜单 3 路：🍱 餐食 / 💊 固食 / 🆕 录入固食。

【V0.7 改动】
1. 计算链重写为 multiple 模式（参考用户 iCloud shortcut）：
   已录入: multiple = PerUserBase ÷ PerBase × ActualServing
   一次性: multiple = ActualAmount ÷ PerBase
   actual_X = per_unit_X × multiple
   math 用显式 WFInput 做左操作数，不依赖隐式 previous output。
2. 固食两条分支共享计算结果展示（确认/取消），
   移到固食子菜单结束后。Food/FoodUnit 预转纯文本。

【首次使用前置】
1. 备忘录 App 创建「固食档案」文件夹。
2. 健康权限全部允许。
3. 下载豆包并登陆。
```

### #1 · WFCommentActionText

```
下方三行分别是蛋白质、脂肪、碳水化合物占总能量的比例，通常参考成人推荐比例如下。可自行调整比例，确保总数100即可。
	•	蛋白质：10%–20%
	•	脂肪：20%–30%
	•	碳水化合物：50%–65%
```

### #117 · WFTextActionText

```
🎯预估总消耗：￼ kcal
🍽️今日已摄入：￼ kcal
🥣还可以摄入：￼ kcal
￼￼

蛋白质：￼￼  ￼%
脂    肪：￼￼  ￼%
碳    水：￼￼  ￼%

现在开始记录吧～
```

### #146 · WFTextActionText

```
你是一位专业的卡路里评估助手。
图片中是我吃喝的食物本身，或者食物的商品条形码。如果图片是食物本身，请根据图片，分析图中的食物是什么，并估算食物的重量单位g，用括号标明在食物名后方，如果有多个，请用逗号隔开列出。
如果图片中的是商品条形码，请根据条形码查询食物名称和相关营养信息。
同时，依据我吃东西的时间￼，判断类型是早餐、午餐、晚餐，或者是加餐。
并且，依据估算的食物总重量（单位g）和我摄入的比例￼%，估算我摄入的总卡路里（单位kcal），总蛋白质（单位g），总脂肪（单位g），总碳水化合物（单位g）。
请以 JSON 格式返回，不要添加任何解释或文本。
{ 
"食物": "string", 
"餐型": "string", 
"总重量": number， 
"卡路里": number, 
"蛋白质": number, 
"脂肪": number, 
"碳水化合物": number 
}
范例如下：
{ 
"食物": "牛油果鸡蛋培根三明治（300g），咖啡加奶（200g）", 
"餐型": "早餐", 
"总重量": 500， 
"卡路里": 560, 
"蛋白质": 17, 
"脂肪": 36, 
"碳水化合物": 30 
}
```

### #161 · WFTextActionText

```
👩‍🏫聪明的豆老师提供了以下内容：
食物：￼
餐型：￼
时间：￼
食物总量：￼ g
摄入比例：￼ %

热量：￼ kcal
蛋白质：￼ g
脂肪：￼ g
碳水化合物：￼ g

📝如何在Health和Calendar记录呢？
```

### #173 · WFTextActionText

```
￼，请重新思考我的问题。
只返回JSON，不要添加额外的代码，不要添加任何解释或文本。
{ 
"食物": "string", 
"餐型": "string", 
"总重量": number， 
"卡路里": number, 
"蛋白质": number, 
"脂肪": number, 
"碳水化合物": number 
}
范例如下：
{ 
"食物": "牛油果鸡蛋培根三明治（300g），咖啡加奶（200g）", 
"餐型": "早餐", 
"总重量": 500， 
"卡路里": 560, 
"蛋白质": 17, 
"脂肪": 36, 
"碳水化合物": 30 
}
```

### #183 · WFTextActionText

```
👩‍🏫聪明的豆老师又思考了一遍，得出以下结论：
食物：￼
餐型：￼
时间：￼
食物总量：￼ g
摄入比例：￼ %

热量：￼ kcal
蛋白质：￼ g
脂肪： ￼ g
碳水化合物：￼ g

📝是否在Health和Calendar记录呢？
```

### #250 · WFTextActionText

```
📒 已选中以下固食：
名称： ￼
类型：￼
单位：￼
每份 = ￼ ￼（用户定义）
默认吃：￼ 份

每 ￼ ￼ 标准营养：
  热量：￼ kcal
  蛋白质：￼ g
  脂肪：￼ g
  碳水化合物：￼ g
  钠：￼ mg
  咖啡因：￼ mg
```

### #299 · WFTextActionText

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

### #320 · WFTextActionText

```
📸 AI 识别结果：
名称： ￼
单位：￼

每 ￼ ￼ 营养：
  热量：￼ kcal
  蛋白质：￼ g
  脂肪：￼ g
  碳水化合物：￼ g
  钠：￼ mg
  咖啡因：￼ mg
```

### #376 · WFTextActionText

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

### #401 · WFTextActionText

```
📝 识别到以下固食：
名称： ￼
类型：￼
单位：￼
标准每份：￼ ￼
AI 建议默认吃：￼ 份

每 ￼ ￼ 的营养：
  热量：￼ kcal
  蛋白质：￼ g
  脂肪：￼ g
  碳水化合物：￼ g
  钠：￼ mg
  咖啡因：￼ mg
```

### #450 · WFTextActionText

```
[￼]￼

{
  "name": "￼",
  "category": "￼",
  "unit": "￼",
  "per_base": ￼,
  "per_user_base": ￼,
  "default_amount": ￼,
  "per_unit_calories": ￼,
  "per_unit_protein": ￼,
  "per_unit_fat": ￼,
  "per_unit_carbohydrates": ￼,
  "per_unit_sodium": ￼,
  "per_unit_caffeine": ￼
}
```
