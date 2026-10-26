"""Ingest dev-profile JSONL logs from iCloud Drive (or any directory).

The iOS dev-profile shortcut writes one JSON object per line to a log
file rooted at::

    iCloud Drive/Shortcuts/<category>/<name>/logs/<runId>.jsonl

On macOS those files appear under::

    ~/Library/Mobile Documents/com~apple~CloudDocs/Shortcuts/...

As a secondary source we also accept logs that the user manually
exported to the project tree under any folder named ``debuglog`` (e.g.
``MyShortcuts/FoodAnalysis/V0.2/debuglog/<runId>.jsonl``). This is
useful when iCloud sync is offline or when the user AirDrop'd the log
from the phone.

Files ending in ``.jsonl`` or ``.log`` are both accepted. Parsing is
line-granular and tolerant: a bad line is dropped, a good run keeps
going.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional

_ICLOUD_ROOT = Path(
    "~/Library/Mobile Documents/com~apple~CloudDocs/Shortcuts"
).expanduser()
_LOG_EXTS = (".jsonl", ".log")
_DEBUGLOG_DIRNAME = "debuglog"
# Action params carry a UUID; this pattern finds it in a raw source.json text.
_UUID_LINE_RE = re.compile(r'"UUID"\s*:\s*"([0-9A-Fa-f-]+)"')


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class Step:
    n: int
    identifier: str
    uuid: str
    ok: bool = True
    out: Optional[str] = None
    ts: Optional[str] = None
    source_index: Optional[int] = None      # set by cross_reference
    source_line: Optional[int] = None       # set by cross_reference


@dataclass
class Run:
    run_id: str
    shortcut_name: str
    category: str
    source_file: Path
    started_at: Optional[str] = None
    steps: list[Step] = field(default_factory=list)
    summary: Optional[dict] = None
    aborted: bool = False
    corrupt: bool = False
    first_fail_step: Optional[int] = None

    @property
    def ok(self) -> bool:
        return self.summary is not None and not self.aborted and not self.corrupt


# ---------------------------------------------------------------------------
# Location helpers
# ---------------------------------------------------------------------------


def default_icloud_root() -> Path:
    """Return the macOS path where iCloud Drive exposes Shortcuts logs."""
    return _ICLOUD_ROOT


def discover_project_debuglogs(project_root: Path) -> list[Path]:
    """Find all ``debuglog`` directories under ``project_root``."""
    if not project_root.exists():
        return []
    return sorted({p.resolve() for p in project_root.rglob(_DEBUGLOG_DIRNAME) if p.is_dir()})


def default_log_roots(project_root: Optional[Path] = None) -> list[Path]:
    """Return the list of roots ``ingest-logs`` scans when called with no args.

    Order: iCloud Drive first (auto-sync source), then any ``debuglog``
    directory found under ``project_root`` (manual upload source).
    """
    roots: list[Path] = []
    if _ICLOUD_ROOT.exists():
        roots.append(_ICLOUD_ROOT)
    if project_root is not None:
        roots.extend(discover_project_debuglogs(project_root))
    return roots


def _iter_log_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in _LOG_EXTS:
            yield p


def _ensure_downloaded(path: Path) -> Path:
    """Trigger iCloud Drive's Files On-Demand download if ``path`` is a
    placeholder, and return the resolved local path.

    iCloud Drive stores not-yet-downloaded files as ``.icloud`` stub
    files with a leading dot. We call ``brctl download`` best-effort.
    """
    if shutil.which("brctl") is None:
        return path
    try:
        subprocess.run(
            ["brctl", "download", str(path.parent)],
            capture_output=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        pass
    return path


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def _parse_jsonl(path: Path) -> list[dict]:
    """Parse a JSONL file tolerantly. Return a list of decoded objects."""
    out: list[dict] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return out
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            out.append(obj)
    return out


def parse_run(path: Path) -> Run:
    """Read one log file and return its Run."""
    objs = _parse_jsonl(path)
    if not objs:
        return Run(
            run_id=path.stem,
            shortcut_name="<unknown>",
            category="<unknown>",
            source_file=path,
            corrupt=True,
        )

    header = objs[0] if objs[0].get("t") == "header" else None
    if header is None:
        return Run(
            run_id=path.stem,
            shortcut_name="<unknown>",
            category="<unknown>",
            source_file=path,
            corrupt=True,
        )

    run = Run(
        run_id=header.get("runId") or path.stem,
        shortcut_name=header.get("name", path.stem),
        category=header.get("cat", "<unknown>"),
        source_file=path,
        started_at=header.get("ts"),
    )
    for obj in objs[1:]:
        t = obj.get("t")
        if t == "step":
            run.steps.append(
                Step(
                    n=int(obj.get("n", -1)),
                    identifier=obj.get("id", ""),
                    uuid=obj.get("uuid", ""),
                    ok=bool(obj.get("ok", True)),
                    out=obj.get("out"),
                    ts=obj.get("ts"),
                )
            )
        elif t == "summary":
            run.summary = obj
    if run.summary is None:
        run.aborted = True
        run.first_fail_step = (run.steps[-1].n + 1) if run.steps else 0
    else:
        # if any step reported ok=false, the first one is the failure
        for s in run.steps:
            if not s.ok:
                run.first_fail_step = s.n
                break
    return run


def read_runs(
    roots: Iterable[Path],
    *,
    since: Optional[_dt.date] = None,
    download_icloud: bool = True,
) -> list[Run]:
    """Scan each root for log files, download missing iCloud placeholders,
    and return a list of parsed Runs sorted by path."""
    runs: list[Run] = []
    seen: set[Path] = set()
    for root in roots:
        root = Path(root).expanduser()
        if download_icloud and str(root).startswith(str(_ICLOUD_ROOT)):
            _ensure_downloaded(root)
        for f in _iter_log_files(root):
            key = f.resolve()
            if key in seen:
                continue
            seen.add(key)
            if since is not None:
                try:
                    mtime = _dt.date.fromtimestamp(f.stat().st_mtime)
                except OSError:
                    mtime = None
                if mtime is not None and mtime < since:
                    continue
            runs.append(parse_run(f))
    runs.sort(key=lambda r: str(r.source_file))
    return runs


# ---------------------------------------------------------------------------
# Cross reference with source.json
# ---------------------------------------------------------------------------


def _build_uuid_index(source_text: str) -> dict[str, int]:
    """Return a mapping ``uuid -> line_number`` found in the JSON source."""
    index: dict[str, int] = {}
    for lineno, line in enumerate(source_text.splitlines(), start=1):
        for m in _UUID_LINE_RE.finditer(line):
            uid = m.group(1).upper()
            index.setdefault(uid, lineno)
    return index


def _action_index_by_uuid(shortcut: dict) -> dict[str, int]:
    out: dict[str, int] = {}
    for i, act in enumerate(shortcut.get("WFWorkflowActions") or []):
        uid = (act.get("WFWorkflowActionParameters") or {}).get("UUID")
        if uid:
            out[str(uid).upper()] = i
    return out


def cross_reference(runs: list[Run], source_path: Optional[Path]) -> list[Run]:
    """Enrich each step with its index + line number in the source file."""
    if source_path is None:
        return runs
    try:
        source_text = Path(source_path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return runs
    from . import plist_io
    try:
        shortcut = plist_io.loads(source_text.encode("utf-8"))
    except Exception:
        return runs
    uuid_to_index = _action_index_by_uuid(shortcut if isinstance(shortcut, dict) else {})
    uuid_to_line = _build_uuid_index(source_text)
    for run in runs:
        for step in run.steps:
            key = (step.uuid or "").upper()
            if key and key in uuid_to_index:
                step.source_index = uuid_to_index[key]
            if key and key in uuid_to_line:
                step.source_line = uuid_to_line[key]
    return runs


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------


def render_report(runs: list[Run], *, source_path: Optional[Path] = None) -> str:
    """Render a Markdown diagnostic report."""
    total = len(runs)
    failed = sum(1 for r in runs if not r.ok)
    corrupt = sum(1 for r in runs if r.corrupt)

    buf: list[str] = []
    title = runs[0].shortcut_name if runs else "<no runs>"
    buf.append(f"# {title} · 日志汇总 ({total} 次运行, {failed} 次失败, {corrupt} 份损坏)")
    buf.append("")
    if source_path is not None:
        buf.append(f"- 源文件：`{source_path}`")
    buf.append(f"- 扫描时间：{_dt.datetime.now().isoformat(timespec='seconds')}")
    buf.append("")

    if not runs:
        buf.append("_没有日志可供聚合。_")
        return "\n".join(buf) + "\n"

    for run in runs:
        status = "OK" if run.ok else ("CORRUPT" if run.corrupt else "ABORTED / FAILED")
        buf.append(f"## Run `{run.run_id[:8]}…` · {run.started_at or '?'} · {status}")
        buf.append("")
        buf.append(f"- 源文件：`{run.source_file}`")
        buf.append(f"- 动作步数：{len(run.steps)}")
        if run.first_fail_step is not None:
            step = next((s for s in run.steps if s.n == run.first_fail_step), None)
            buf.append(f"- 首次失败：step #{run.first_fail_step}")
            if step is not None:
                where = ""
                if step.source_line is not None:
                    where = f" ({source_path}:{step.source_line})"
                buf.append(f"  - {step.identifier} · UUID {step.uuid}{where}")
                if step.out:
                    truncated = step.out.replace("\n", " ")[:200]
                    buf.append(f"  - out: `{truncated}`")
        if run.corrupt:
            buf.append("- _该日志文件无法解析（缺少 header 或全部为 invalid JSON）_")
        elif run.aborted:
            buf.append("- _运行异常终止：日志末尾缺少 summary 行_")

        if run.steps:
            buf.append("")
            buf.append("<details><summary>完整 step 轨迹</summary>")
            buf.append("")
            buf.append("| # | action id | uuid | ok | out | src |")
            buf.append("|---|---|---|---|---|---|")
            for s in run.steps:
                out_txt = (s.out or "").replace("\n", " ").replace("|", "\\|")[:80]
                src_cell = (
                    f"L{s.source_line}" if s.source_line is not None
                    else (f"#{s.source_index}" if s.source_index is not None else "")
                )
                buf.append(
                    f"| {s.n} | `{s.identifier}` | `{s.uuid[:8]}…` | {'Y' if s.ok else 'N'} | `{out_txt}` | {src_cell} |"
                )
            buf.append("")
            buf.append("</details>")
        buf.append("")

    return "\n".join(buf).rstrip() + "\n"


# ---------------------------------------------------------------------------
# High-level entry point
# ---------------------------------------------------------------------------


def ingest(
    log_dirs: Optional[Iterable[Path]] = None,
    *,
    source: Optional[Path] = None,
    project_root: Optional[Path] = None,
    since: Optional[_dt.date] = None,
    only_failed: bool = False,
) -> tuple[list[Run], str]:
    """Top-level helper that combines discovery + parsing + rendering.

    Returns ``(runs, markdown_report)``.
    """
    if log_dirs is None or not list(log_dirs):
        log_dirs = default_log_roots(project_root)
    runs = read_runs(list(log_dirs), since=since)
    if source is not None:
        runs = cross_reference(runs, Path(source))
    if only_failed:
        runs = [r for r in runs if not r.ok]
    report = render_report(runs, source_path=Path(source) if source else None)
    return runs, report
