"""check: structural validation of a shortcut before compiling.

Catches what hand or AI edits of ``source.json`` tend to break: duplicate
action UUIDs, control-flow blocks that do not pair up by
``GroupingIdentifier``, and ``ActionOutput`` references to actions that do
not exist or come later. Business logic and type inference are out of scope.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterator, Optional

from . import plist_io
from .decompile import _load_bytes_from

_ACTION_PREFIX = "is.workflow.actions."
# One match per action, in action order, in both canonical JSON and XML plist sources.
_ACTION_LINE_RE = re.compile(r'"WFWorkflowActionIdentifier"\s*:|<key>WFWorkflowActionIdentifier</key>')


@dataclass
class Finding:
    severity: str  # "error" | "warning"
    code: str
    index: int
    identifier: str
    message: str
    uuid: Optional[str] = None
    line: Optional[int] = None


@dataclass
class CheckResult:
    name: str
    action_count: int
    findings: list[Finding] = field(default_factory=list)

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "warning"]


def _params(action: dict) -> dict:
    params = action.get("WFWorkflowActionParameters")
    return params if isinstance(params, dict) else {}


def _uuid(action: dict) -> Optional[str]:
    uid = _params(action).get("UUID")
    return str(uid).upper() if uid else None


def _finding(severity: str, code: str, index: int, action: dict, message: str) -> Finding:
    return Finding(
        severity=severity,
        code=code,
        index=index,
        identifier=str(action.get("WFWorkflowActionIdentifier", "")),
        message=message,
        uuid=_uuid(action),
    )


def _short(identifier: str) -> str:
    return identifier[len(_ACTION_PREFIX):] if identifier.startswith(_ACTION_PREFIX) else identifier


def _check_uuids(actions: list) -> tuple[list[Finding], dict[str, int]]:
    findings: list[Finding] = []
    first_index: dict[str, int] = {}
    for index, action in enumerate(actions):
        uid = _uuid(action)
        if uid is None:
            continue
        if uid in first_index:
            findings.append(
                _finding("error", "duplicate-uuid", index, action, f"UUID {uid} is already used by #{first_index[uid]}")
            )
        else:
            first_index[uid] = index
    return findings, first_index


def _check_control_flow(actions: list) -> list[Finding]:
    findings: list[Finding] = []
    open_blocks: list[tuple[str, int]] = []
    opened_at: dict[str, int] = {}
    for index, action in enumerate(actions):
        params = _params(action)
        if "WFControlFlowMode" not in params:
            continue
        mode = params["WFControlFlowMode"]
        if type(mode) is not int or mode not in (0, 1, 2):
            findings.append(
                _finding("error", "invalid-control-flow-mode", index, action, f"WFControlFlowMode must be 0, 1 or 2, got {mode!r}")
            )
            continue
        if not params.get("GroupingIdentifier"):
            findings.append(_finding("error", "missing-grouping-id", index, action, "control-flow action has no GroupingIdentifier"))
            continue
        group = str(params["GroupingIdentifier"]).upper()

        if mode == 0:
            if group in opened_at:
                findings.append(
                    _finding(
                        "error", "reused-grouping-id", index, action,
                        f"GroupingIdentifier {group} already belongs to the block opened at #{opened_at[group]}",
                    )
                )
            else:
                opened_at[group] = index
            open_blocks.append((group, index))
            continue

        depth = next((d for d in range(len(open_blocks) - 1, -1, -1) if open_blocks[d][0] == group), None)
        if depth is None:
            code = "branch-outside-block" if mode == 1 else "end-without-start"
            findings.append(_finding("error", code, index, action, f"no open block has GroupingIdentifier {group}"))
            continue
        start = open_blocks[depth][1]
        if depth != len(open_blocks) - 1:
            findings.append(
                _finding(
                    "error", "interleaved-block", index, action,
                    f"the block opened at #{open_blocks[-1][1]} is still open inside the block opened at #{start}",
                )
            )
        expected = str(actions[start].get("WFWorkflowActionIdentifier", ""))
        if action.get("WFWorkflowActionIdentifier") != expected:
            findings.append(
                _finding("error", "identifier-mismatch", index, action, f"the block opened at #{start} is {_short(expected)}")
            )
        if mode == 2:
            del open_blocks[depth]

    for group, start in open_blocks:
        findings.append(
            _finding("error", "unclosed-block", start, actions[start], f"block {group} is never closed (no mode 2 action)")
        )
    return findings


def _output_refs(value: Any) -> Iterator[dict]:
    if isinstance(value, dict):
        if "OutputUUID" in value:
            yield value
        for child in value.values():
            yield from _output_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from _output_refs(child)


def _check_references(actions: list, uuid_index: dict[str, int]) -> list[Finding]:
    findings: list[Finding] = []
    for index, action in enumerate(actions):
        for ref in _output_refs(_params(action)):
            uid = str(ref["OutputUUID"]).upper()
            label = f"output {ref.get('OutputName')!r} ({uid})"
            target = uuid_index.get(uid)
            if target is None:
                findings.append(
                    _finding(
                        "warning", "dangling-ref", index, action,
                        f"{label} matches no action; harmless only if this field is unused",
                    )
                )
            elif target >= index:
                where = "this action itself" if target == index else f"later action #{target}"
                findings.append(_finding("warning", "forward-ref", index, action, f"{label} comes from {where}"))
    return findings


def check_workflow(shortcut: dict) -> list[Finding]:
    """Return findings ordered by action index; any ``error`` means the shortcut is structurally broken."""
    actions = shortcut.get("WFWorkflowActions") or []
    findings, uuid_index = _check_uuids(actions)
    findings += _check_control_flow(actions)
    findings += _check_references(actions, uuid_index)
    findings.sort(key=lambda f: f.index)
    return findings


def _action_lines(data: bytes, count: int) -> Optional[list[int]]:
    if plist_io.sniff_format(data) not in ("json", "xml"):
        return None
    text = data.decode("utf-8", errors="replace")
    starts = [m.start() for m in _ACTION_LINE_RE.finditer(text)]
    if len(starts) != count:
        return None
    lines: list[int] = []
    line, last = 1, 0
    for start in starts:
        line += text.count("\n", last, start)
        lines.append(line)
        last = start
    return lines


def check_input(source: str) -> CheckResult:
    """Check an iCloud URL or local shortcut file; JSON / XML sources also get line numbers."""
    data, name, _origin = _load_bytes_from(source)
    shortcut = plist_io.loads(data)
    if not isinstance(shortcut, dict):
        raise ValueError("shortcut source did not deserialize to a dict (unexpected root type)")
    actions = shortcut.get("WFWorkflowActions") or []
    findings = check_workflow(shortcut)
    lines = _action_lines(data, len(actions))
    if lines is not None:
        for finding in findings:
            finding.line = lines[finding.index]
    return CheckResult(name=name or "shortcut", action_count=len(actions), findings=findings)


def _plural(count: int, noun: str) -> str:
    return f"{count} {noun}" + ("" if count == 1 else "s")


def report_lines(result: CheckResult) -> list[str]:
    out: list[str] = []
    for f in result.findings:
        where = f" L{f.line}" if f.line is not None else ""
        out.append(f"{f.severity} #{f.index}{where} {_short(f.identifier)} [{f.code}] {f.message}")
    out.append(
        f"{result.name}: {_plural(len(result.errors), 'error')}, "
        f"{_plural(len(result.warnings), 'warning')}, {result.action_count} actions"
    )
    return out
