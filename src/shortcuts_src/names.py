"""Action identifier -> short display name map.

Intentionally small (~70 entries) — just the actions most commonly seen
in user-authored workflows. The flow renderer falls back to the raw
identifier when an entry is missing, so adding to this table is an
incremental improvement, not a correctness requirement.
"""

from __future__ import annotations

ACTION_NAMES: dict[str, str] = {
    # Comments / text / numbers
    "is.workflow.actions.comment": "注释",
    "is.workflow.actions.number": "数字",
    "is.workflow.actions.text": "文本",
    "is.workflow.actions.gettext": "文本",
    # Variables
    "is.workflow.actions.setvariable": "设为变量",
    "is.workflow.actions.getvariable": "获取变量",
    "is.workflow.actions.appendvariable": "添加到变量",
    # Control flow
    "is.workflow.actions.conditional": "如果",
    "is.workflow.actions.repeat.count": "重复",
    "is.workflow.actions.repeat.each": "遍历",
    "is.workflow.actions.choosefrommenu": "从菜单中选择",
    "is.workflow.actions.exit": "退出快捷指令",
    "is.workflow.actions.waittoreturn": "等待返回",
    "is.workflow.actions.delay": "延迟",
    "is.workflow.actions.nothing": "空操作",
    # Math / formatting
    "is.workflow.actions.math": "计算",
    "is.workflow.actions.calculateexpression": "计算表达式",
    "is.workflow.actions.round": "四舍五入",
    "is.workflow.actions.statistics": "统计",
    "is.workflow.actions.format.number": "格式化数字",
    "is.workflow.actions.format.date": "格式化日期",
    "is.workflow.actions.gettimebetweendates": "两个日期之间",
    # Text manipulation
    "is.workflow.actions.text.combine": "合并文本",
    "is.workflow.actions.text.split": "拆分文本",
    "is.workflow.actions.text.replace": "替换文本",
    "is.workflow.actions.text.match": "匹配文本",
    "is.workflow.actions.getvalueforkey": "获取字典值",
    "is.workflow.actions.setvalueforkey": "设置字典值",
    "is.workflow.actions.detect.dictionary": "从输入获取字典",
    "is.workflow.actions.getdictionaryvalue": "获取字典值",
    "is.workflow.actions.dictionary": "字典",
    "is.workflow.actions.list": "列表",
    "is.workflow.actions.getitemfromlist": "获取列表中的项",
    "is.workflow.actions.count": "计数",
    # Health
    "is.workflow.actions.filter.health.quantity": "查找健康样本",
    "is.workflow.actions.health.quantity.log": "记录健康样本",
    # Input / UI
    "is.workflow.actions.ask": "询问输入",
    "is.workflow.actions.alert": "显示提醒",
    "is.workflow.actions.showresult": "显示结果",
    "is.workflow.actions.notification": "显示通知",
    "is.workflow.actions.speak": "朗读文字",
    # Media
    "is.workflow.actions.takephoto": "拍照",
    "is.workflow.actions.selectphoto": "选取照片",
    "is.workflow.actions.properties.images": "获取图像属性",
    "is.workflow.actions.recordvideo": "录制视频",
    "is.workflow.actions.recordaudio": "录制音频",
    "is.workflow.actions.savetophotoalbum": "存储到相簿",
    # Files / URL
    "is.workflow.actions.getfile": "获取文件",
    "is.workflow.actions.savefile": "存储文件",
    "is.workflow.actions.appendfile": "追加到文件",
    "is.workflow.actions.url": "URL",
    "is.workflow.actions.downloadurl": "获取 URL 内容",
    "is.workflow.actions.openurl": "打开 URL",
    "is.workflow.actions.openx-callback": "打开 X-Callback URL",
    "is.workflow.actions.getheadersfromurl": "获取 URL 标头",
    "is.workflow.actions.getcomponentsofurl": "获取 URL 的组件",
    # Networking
    "is.workflow.actions.qrcode.generate": "生成二维码",
    "is.workflow.actions.detect.qrcode": "扫描二维码",
    # Calendar / Reminders
    "is.workflow.actions.addnewevent": "添加日历事件",
    "is.workflow.actions.addnewreminder": "添加提醒事项",
    "is.workflow.actions.adjustdate": "调整日期",
    "is.workflow.actions.date": "日期",
    # Sharing / misc
    "is.workflow.actions.share": "共享",
    "is.workflow.actions.copytoclipboard": "拷贝到剪贴板",
    "is.workflow.actions.getclipboard": "获取剪贴板",
    # Scripting / Runtime
    "is.workflow.actions.runjavascript": "运行 JavaScript",
    "is.workflow.actions.runjavascriptonwebpage": "在网页上运行 JavaScript",
    "is.workflow.actions.runworkflow": "运行快捷指令",
    "is.workflow.actions.dictate": "听写文字",
    # 3rd-party AI
    "com.bot.doubao.AskAssistantIntent": "豆包 AI 助手",
    "com.openai.chat.ChatGPTIntent": "ChatGPT",
    "com.apple.intelligence.ChatGPTIntent": "Apple 智能 ChatGPT",
}


def display_name(identifier: str) -> str:
    """Return a short display name for an action identifier."""
    return ACTION_NAMES.get(identifier, identifier)
