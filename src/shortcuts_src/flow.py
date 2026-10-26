"""Render a human-readable Markdown view of a shortcut's action list.

The generated flow is strictly *informational* — round-tripping source
code is done via the XML / JSON representations, not this Markdown
view.

We walk ``WFWorkflowActions`` and:

* indent inside control-flow blocks (``conditional``, ``repeat.*``,
  ``choosefrommenu``) by tracking ``WFControlFlowMode`` (0 = start, 1 =
  else / case, 2 = end).
* surface the strings that actually tell a human what the step does —
  comment bodies, ``WFTextActionText``, menu prompts, menu item titles,
  ``WFAskActionPrompt``, Doubao ``CustomQuestion``, etc.
"""

from __future__ import annotations

import json
from typing import Any, Iterable

from .names import display_name

# Keys whose *string value* is interesting enough to inline in the flow.
_STRING_FIELDS: tuple[str, ...] = (
    "WFCommentActionText",
    "WFTextActionText",
    "WFVariableName",
    "WFMenuPrompt",
    "WFAskActionPrompt",
    "WFAskActionDefaultAnswer",
    "WFMenuItemTitle",
    "WFInputText",
    "CustomQuestion",
    "CustomText",
    "Prompt",
    "Text",
    "WFShowAlertActionTitle",
    "WFShowAlertActionMessage",
    "WFNotificationActionTitle",
    "WFNotificationActionBody",
    "WFURLActionURL",
    "WFDictionaryKey",
    "WFDictionaryValue",
    "WFMathOperation",
    "WFStatisticsOperation",
    "WFRoundMode",
    "WFCalculateExpression",
)

# Keys whose *scalar value* (number / bool) is interesting.
_SCALAR_FIELDS: tuple[str, ...] = (
    "WFNumberActionNumber",
    "WFScalarNumber",
    "WFRepeatCount",
    "WFDelayTime",
    "WFCondition",
    "WFControlFlowMode",
    "WFMathOperand",
    "WFDuplicateCount",
)


def _unwrap_value(value: Any) -> Any:
    """Peel off Shortcuts' ``{'Value': {...}, 'WFSerializationType': ...}`` wrapper."""
    if isinstance(value, dict) and "Value" in value and "WFSerializationType" in value:
        return value["Value"]
    return value


def _as_inline_string(value: Any, *, max_len: int = 140) -> str | None:
    v = _unwrap_value(value)
    if isinstance(v, str):
        s = v
    elif isinstance(v, (int, float, bool)):
        s = str(v)
    elif isinstance(v, dict):
        if "string" in v and isinstance(v["string"], str):
            s = v["string"]
        elif "Value" in v:
            return _as_inline_string(v["Value"], max_len=max_len)
        else:
            return None
    else:
        return None
    s = s.replace("\r\n", "\n").strip("\n")
    if not s:
        return None
    if len(s) > max_len:
        s = s[: max_len - 1] + "…"
    return s


def _extract_highlights(identifier: str, params: dict) -> list[tuple[str, str]]:
    """Return a list of (label, value) pairs worth including beside a step."""
    hits: list[tuple[str, str]] = []
    for key in _STRING_FIELDS + _SCALAR_FIELDS:
        if key not in params:
            continue
        s = _as_inline_string(params[key])
        if s is None:
            continue
        hits.append((key, s))
    # Menu items rendered as a single joined string
    items = params.get("WFMenuItems")
    if isinstance(items, list) and items:
        names = []
        for it in items:
            if isinstance(it, dict):
                label = _as_inline_string(it.get("WFValue") or it.get("WFMenuItemTitle"))
                if label:
                    names.append(label)
        if names:
            hits.append(("WFMenuItems", " | ".join(names)))
    # Doubao intents expose the user prompt under various keys; try a few.
    if identifier.startswith("com.bot.doubao."):
        for key in ("CustomQuestion", "question", "Question"):
            if key in params:
                s = _as_inline_string(params[key])
                if s:
                    hits.append((key, s))
                    break
    return hits


def _control_flow_label(identifier: str, mode: int | None) -> str:
    if identifier == "is.workflow.actions.conditional":
        return {0: "如果", 1: "否则", 2: "结束如果"}.get(mode, "如果")
    if identifier.startswith("is.workflow.actions.repeat"):
        return {0: "重复", 1: "重复（继续）", 2: "结束重复"}.get(mode, "重复")
    if identifier == "is.workflow.actions.choosefrommenu":
        return {0: "从菜单中选择", 1: "菜单项", 2: "结束菜单"}.get(mode, "从菜单中选择")
    return display_name(identifier)


def render_flow(shortcut: dict, *, pretty_json_highlights: bool = False) -> str:
    """Render a ``WFWorkflow`` dict as Markdown. Pure function, no IO."""
    name = shortcut.get("_workflowName") or shortcut.get("name") or "shortcut"
    actions: list[dict] = shortcut.get("WFWorkflowActions") or []

    buf: list[str] = []
    buf.append(f"# {name}")
    buf.append("")
    buf.append(f"- 动作数量：**{len(actions)}**")
    min_client = shortcut.get("WFWorkflowMinimumClientVersionString") or shortcut.get("WFWorkflowMinimumClientVersion")
    if min_client:
        buf.append(f"- 最低客户端版本：`{min_client}`")
    client = shortcut.get("WFWorkflowClientVersion")
    if client:
        buf.append(f"- 编写客户端版本：`{client}`")
    types = shortcut.get("WFWorkflowTypes")
    if types:
        buf.append(f"- 入口类型：{', '.join(f'`{t}`' for t in types)}")
    buf.append("")
    buf.append("## 流程")
    buf.append("")
    buf.append("```text")

    indent = 0
    for idx, act in enumerate(actions):
        identifier = act.get("WFWorkflowActionIdentifier", "")
        params = act.get("WFWorkflowActionParameters", {}) or {}
        mode = params.get("WFControlFlowMode") if isinstance(params.get("WFControlFlowMode"), int) else None

        is_control_flow = identifier in (
            "is.workflow.actions.conditional",
            "is.workflow.actions.choosefrommenu",
        ) or identifier.startswith("is.workflow.actions.repeat")

        label = _control_flow_label(identifier, mode) if is_control_flow else display_name(identifier)

        if is_control_flow and mode == 2:
            indent = max(0, indent - 1)
        depth = indent if not (is_control_flow and mode == 1) else max(0, indent - 1)

        highlights = _extract_highlights(identifier, params)
        base = f"{'  ' * depth}{idx:3d} │ {label}"
        if highlights:
            extras = "; ".join(f"{k}={v!r}" if pretty_json_highlights else f"{k}={v}" for k, v in highlights)
            buf.append(f"{base}  [{extras}]")
        else:
            buf.append(base)

        if is_control_flow and mode == 0:
            indent += 1

    buf.append("```")
    buf.append("")

    # Appendix: full text of long comments / prompts / AI questions
    extras: list[tuple[int, str, str]] = []
    for idx, act in enumerate(actions):
        params = act.get("WFWorkflowActionParameters", {}) or {}
        for key in ("WFCommentActionText", "WFTextActionText", "WFAskActionPrompt", "CustomQuestion"):
            if key not in params:
                continue
            s = _as_inline_string(params[key], max_len=10_000)
            if s and len(s) > 60:
                extras.append((idx, key, s))
    if extras:
        buf.append("## 关键长文本")
        buf.append("")
        for idx, key, body in extras:
            buf.append(f"### #{idx} · {key}")
            buf.append("")
            buf.append("```")
            buf.append(body)
            buf.append("```")
            buf.append("")
    return "\n".join(buf).rstrip() + "\n"


def extract_metadata(shortcut: dict) -> dict:
    """Pick out a small metadata dict suitable for ``<name>.meta.json``."""
    keys = (
        "WFWorkflowClientVersion",
        "WFWorkflowMinimumClientVersion",
        "WFWorkflowMinimumClientVersionString",
        "WFWorkflowIcon",
        "WFWorkflowTypes",
        "WFWorkflowInputContentItemClasses",
        "WFWorkflowOutputContentItemClasses",
        "WFWorkflowImportQuestions",
        "WFWorkflowHasOutputFallback",
        "WFWorkflowHasShortcutInputVariables",
        "WFQuickActionSurfaces",
    )
    meta: dict[str, Any] = {k: shortcut[k] for k in keys if k in shortcut}
    actions: Iterable[dict] = shortcut.get("WFWorkflowActions") or ()
    meta["WFWorkflowActionCount"] = sum(1 for _ in actions)
    # Best-effort: pull the very first comment as a "description"
    for act in shortcut.get("WFWorkflowActions") or ():
        if act.get("WFWorkflowActionIdentifier") == "is.workflow.actions.comment":
            params = act.get("WFWorkflowActionParameters") or {}
            text = _as_inline_string(params.get("WFCommentActionText"), max_len=10_000)
            if text:
                meta["_firstComment"] = text
            break
    return meta


def metadata_json(shortcut: dict) -> bytes:
    meta = extract_metadata(shortcut)
    # Rewrap bytes (icon color is fine as int, nothing else is bytes-ish)
    return (json.dumps(meta, ensure_ascii=False, indent=2, default=str) + "\n").encode("utf-8")
