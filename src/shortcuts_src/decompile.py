"""decompile: iCloud URL / .shortcut / .plist / .json  ->  editable source."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from . import aea, icloud, plist_io
from .flow import metadata_json, render_flow


_UNSAFE_NAME = re.compile(r'[\\/:"*?<>|\x00-\x1f]+')


def _safe_name(name: str, fallback: str = "shortcut") -> str:
    cleaned = _UNSAFE_NAME.sub("_", name).strip().strip(".")
    return cleaned or fallback


@dataclass
class DecompileResult:
    name: str
    files: dict[str, Optional[Path]]
    shortcut: dict


def _load_bytes_from(source: str) -> tuple[bytes, Optional[str], str]:
    """Return (raw bplist bytes, display_name, origin_label)."""
    if icloud.is_icloud_shortcut_url(source):
        record, data = icloud.fetch_unsigned_bplist(source)
        if plist_io.sniff_format(data) == "aea":
            data = aea.decrypt_bytes(data)
        return data, record.name, f"iCloud:{record.record_id}"

    path = Path(source).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"no such file: {path}")
    data = path.read_bytes()
    fmt = plist_io.sniff_format(data)
    if fmt == "aea":
        data = aea.decrypt_bytes(data)
    elif fmt not in ("bplist", "xml", "json"):
        raise ValueError(
            f"{path}: could not identify format (expected bplist / XML plist / JSON / AEA). "
            "If this is a .shortcut from iCloud, pass the iCloud share URL instead."
        )
    return data, path.stem, f"file:{path}"


def decompile_input(
    source: str,
    *,
    out_dir: Optional[str] = None,
    fmt: str = "both",
    name: Optional[str] = None,
    emit_flow: bool = True,
    keep_bplist: bool = False,
) -> DecompileResult:
    """Main decompile entry point.

    Parameters
    ----------
    source : str
        Either an iCloud share URL or a local file path.
    out_dir : str, optional
        Directory to write outputs into. Defaults to the input's parent
        directory, or the current directory for URL inputs.
    fmt : {'xml', 'json', 'both'}
        Which canonical format(s) to emit.
    name : str, optional
        Override the output base name.
    emit_flow : bool
        Emit ``<name>.flow.md`` (default True).
    keep_bplist : bool
        Also write the raw unsigned bplist to ``<name>.bplist``.
    """
    data, inferred_name, origin = _load_bytes_from(source)
    shortcut = plist_io.loads(data)
    if not isinstance(shortcut, dict):
        raise ValueError("shortcut source did not deserialize to a dict (unexpected root type)")

    base_name = _safe_name(name or inferred_name or "shortcut")

    if out_dir is None:
        if origin.startswith("file:"):
            out_path = Path(origin.split(":", 1)[1]).expanduser().parent
        else:
            out_path = Path.cwd()
    else:
        out_path = Path(out_dir).expanduser()
    out_path.mkdir(parents=True, exist_ok=True)

    files: dict[str, Optional[Path]] = {
        "xml": None,
        "json": None,
        "flow.md": None,
        "meta.json": None,
        "bplist": None,
    }

    if fmt in ("xml", "both"):
        files["xml"] = plist_io.write_bytes(out_path / f"{base_name}.source.xml", plist_io.dump_xml(shortcut))
    if fmt in ("json", "both"):
        files["json"] = plist_io.write_bytes(out_path / f"{base_name}.source.json", plist_io.dump_json(shortcut))

    if emit_flow:
        shortcut_for_render = dict(shortcut)
        shortcut_for_render.setdefault("_workflowName", base_name)
        md = render_flow(shortcut_for_render).encode("utf-8")
        files["flow.md"] = plist_io.write_bytes(out_path / f"{base_name}.flow.md", md)

    files["meta.json"] = plist_io.write_bytes(out_path / f"{base_name}.meta.json", metadata_json(shortcut))

    if keep_bplist:
        files["bplist"] = plist_io.write_bytes(out_path / f"{base_name}.bplist", data)

    return DecompileResult(name=base_name, files=files, shortcut=shortcut)


def inspect_input(source: str) -> list[str]:
    """Return a short list of summary lines describing the input."""
    data, inferred_name, origin = _load_bytes_from(source)
    shortcut = plist_io.loads(data)
    actions = shortcut.get("WFWorkflowActions") or []
    summary: list[str] = [
        f"name:   {inferred_name}",
        f"origin: {origin}",
        f"actions: {len(actions)}",
    ]
    min_client = shortcut.get("WFWorkflowMinimumClientVersionString")
    if min_client:
        summary.append(f"minClient: {min_client}")
    client = shortcut.get("WFWorkflowClientVersion")
    if client:
        summary.append(f"client:    {client}")
    types = shortcut.get("WFWorkflowTypes")
    if types:
        summary.append(f"types:     {', '.join(types)}")
    for act in actions:
        if act.get("WFWorkflowActionIdentifier") == "is.workflow.actions.comment":
            from .flow import _as_inline_string  # late import: internal helper
            comment = _as_inline_string((act.get("WFWorkflowActionParameters") or {}).get("WFCommentActionText"), max_len=160)
            if comment:
                summary.append(f"comment:   {comment}")
            break
    return summary
