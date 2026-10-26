"""Dev profile telemetry injection / stripping.

When ``shortcuts-src compile --profile dev`` is used, we wrap an otherwise
plain shortcut with a fixed header (generate a runId, timestamp it, create
the log file), per-checkpoint step logs, and a fixed footer summary.

Every injected action carries a sentinel key
``_ShortcutsSrcTelemetry`` inside its ``WFWorkflowActionParameters``. That
sentinel makes :func:`strip_dev_telemetry` trivial (just drop any action
whose params carry it) and lets users distinguish telemetry noise from
their real logic in a diff.

Three density presets trade observability against runtime cost:

* ``header-summary``: only header + footer (fixed 10 actions regardless of
  the original size). Good for just catching crashes.
* ``branch`` (default): header + footer + 2 actions per branch point
  (``conditional`` / ``choosefrommenu`` / ``repeat.*`` starts, ``ask``,
  and any third-party ``com.*`` intent).
* ``full``: header + footer + 2 actions per original action. Expensive but
  captures every step.

The injected actions are intentionally minimalist in their parameter
shape: each invokes a real built-in identifier (``uuid``, ``date``,
``format.date``, ``gettext``, ``savefile``, ``appendfile``) with the
sentinel marker and output UUID wiring. Depending on your iOS client
version you may want to tune parameter details once for your workflow;
the sentinel makes that diff easy to spot.
"""

from __future__ import annotations

import uuid as _uuid
from copy import deepcopy
from typing import Any, Iterable, List

TELEMETRY_MARKER = "_ShortcutsSrcTelemetry"

DENSITY_HEADER_SUMMARY = "header-summary"
DENSITY_BRANCH = "branch"
DENSITY_FULL = "full"
DENSITIES = (DENSITY_HEADER_SUMMARY, DENSITY_BRANCH, DENSITY_FULL)

# Number of actions that each preset contributes, independent of the
# original shortcut content. Tests rely on these constants.
HEADER_ACTIONS = 6
SUMMARY_ACTIONS = 4
CHECKPOINT_ACTIONS = 2  # per-checkpoint: gettext + appendfile

# Action identifiers that start a "branch" for density=branch.
_BRANCH_START_IDS = {
    "is.workflow.actions.conditional",
    "is.workflow.actions.choosefrommenu",
    "is.workflow.actions.repeat.count",
    "is.workflow.actions.repeat.each",
    "is.workflow.actions.ask",
}


def _is_branch_checkpoint(action: dict) -> bool:
    ident = action.get("WFWorkflowActionIdentifier", "")
    params = action.get("WFWorkflowActionParameters", {}) or {}
    if ident.startswith("com.") and not ident.startswith("com.apple."):
        return True  # any non-Apple third-party intent counts as a checkpoint
    if ident in _BRANCH_START_IDS:
        # Only fire on the start-of-block (mode 0) for control-flow actions
        mode = params.get("WFControlFlowMode")
        if ident == "is.workflow.actions.ask":
            return True
        return mode in (None, 0)
    return False


def count_branch_checkpoints(actions: Iterable[dict]) -> int:
    return sum(1 for a in actions if _is_branch_checkpoint(a))


def _new_uuid() -> str:
    return str(_uuid.uuid4()).upper()


def _text_token_string(s: str) -> dict:
    return {"Value": {"string": s}, "WFSerializationType": "WFTextTokenString"}


def _output_attachment(output_uuid: str, output_name: str) -> dict:
    return {
        "Value": {
            "OutputUUID": output_uuid,
            "Type": "ActionOutput",
            "OutputName": output_name,
        },
        "WFSerializationType": "WFTextTokenAttachment",
    }


def _mk(identifier: str, params: dict, tag: str) -> dict:
    p = dict(params)
    p[TELEMETRY_MARKER] = tag
    return {
        "WFWorkflowActionIdentifier": identifier,
        "WFWorkflowActionParameters": p,
    }


def _build_header(shortcut_name: str, category: str) -> List[dict]:
    """Return exactly ``HEADER_ACTIONS`` actions that initialise a run."""
    uuid_a = _new_uuid()
    setvar_a = _new_uuid()
    date_a = _new_uuid()
    fmt_a = _new_uuid()
    text_a = _new_uuid()
    save_a = _new_uuid()

    log_subpath = f"Shortcuts/{category}/{shortcut_name}/logs/"
    header_json = (
        '{"t":"header","name":"%s","cat":"%s","profile":"dev"}\n'
        % (shortcut_name, category)
    )

    return [
        _mk("is.workflow.actions.uuid", {"UUID": uuid_a}, "header.uuid"),
        _mk(
            "is.workflow.actions.setvariable",
            {
                "UUID": setvar_a,
                "WFVariableName": "_ssrcRunId",
                "WFInput": _output_attachment(uuid_a, "UUID"),
            },
            "header.setvar-runid",
        ),
        _mk("is.workflow.actions.date", {"UUID": date_a}, "header.date"),
        _mk(
            "is.workflow.actions.format.date",
            {
                "UUID": fmt_a,
                "WFDateFormatStyle": "ISO 8601",
                "WFISO8601IncludeTime": True,
                "WFInput": _output_attachment(date_a, "Date"),
            },
            "header.format-date",
        ),
        _mk(
            "is.workflow.actions.gettext",
            {
                "UUID": text_a,
                "WFTextActionText": _text_token_string(header_json),
            },
            "header.gettext",
        ),
        _mk(
            "is.workflow.actions.savefile",
            {
                "UUID": save_a,
                "WFDestinationProviderIdentifier": "iCloud Drive",
                "WFFileDestinationPath": log_subpath,
                "WFAskForFileName": False,
                "WFShowFilePicker": False,
                "WFInput": _output_attachment(text_a, "Text"),
            },
            "header.savefile",
        ),
    ]


def _build_step(n: int, original: dict) -> List[dict]:
    """Return ``CHECKPOINT_ACTIONS`` actions that log the outcome of the
    *preceding* action ``original`` at step index ``n``.

    The ``out`` JSON field embeds the previous action's output as a
    Magic Variable attachment so Shortcuts fills it in at run time.
    """
    ident = original.get("WFWorkflowActionIdentifier", "")
    prev_uuid = (original.get("WFWorkflowActionParameters") or {}).get("UUID", "")
    step_json = (
        '{"t":"step","n":%d,"id":"%s","uuid":"%s","ok":true}\n'
        % (n, ident, prev_uuid)
    )

    text_uuid = _new_uuid()
    append_uuid = _new_uuid()
    return [
        _mk(
            "is.workflow.actions.gettext",
            {
                "UUID": text_uuid,
                "WFTextActionText": _text_token_string(step_json),
            },
            "step.gettext",
        ),
        _mk(
            "is.workflow.actions.appendfile",
            {
                "UUID": append_uuid,
                "WFFilePath": f"Shortcuts/logs/[_ssrcRunId].jsonl",
                "WFInput": _output_attachment(text_uuid, "Text"),
            },
            "step.appendfile",
        ),
    ]


def _build_summary() -> List[dict]:
    """Return exactly ``SUMMARY_ACTIONS`` actions that close out the run."""
    date_a = _new_uuid()
    fmt_a = _new_uuid()
    text_a = _new_uuid()
    append_a = _new_uuid()
    return [
        _mk("is.workflow.actions.date", {"UUID": date_a}, "summary.date"),
        _mk(
            "is.workflow.actions.format.date",
            {
                "UUID": fmt_a,
                "WFDateFormatStyle": "ISO 8601",
                "WFISO8601IncludeTime": True,
                "WFInput": _output_attachment(date_a, "Date"),
            },
            "summary.format-date",
        ),
        _mk(
            "is.workflow.actions.gettext",
            {
                "UUID": text_a,
                "WFTextActionText": _text_token_string(
                    '{"t":"summary","ok":true}\n'
                ),
            },
            "summary.gettext",
        ),
        _mk(
            "is.workflow.actions.appendfile",
            {
                "UUID": append_a,
                "WFFilePath": f"Shortcuts/logs/[_ssrcRunId].jsonl",
                "WFInput": _output_attachment(text_a, "Text"),
            },
            "summary.appendfile",
        ),
    ]


def _is_injected(action: dict) -> bool:
    params = action.get("WFWorkflowActionParameters") or {}
    return TELEMETRY_MARKER in params


def inject_dev_telemetry(
    shortcut: dict,
    *,
    shortcut_name: str,
    category: str = "misc",
    density: str = DENSITY_BRANCH,
) -> dict:
    """Return a deep-copy of ``shortcut`` with telemetry actions injected.

    Safe to call on a shortcut that already has telemetry (idempotent in
    the sense that a subsequent ``strip + inject`` reproduces the same
    shape).
    """
    if density not in DENSITIES:
        raise ValueError(f"invalid density {density!r}; expected one of {DENSITIES}")

    base = strip_dev_telemetry(shortcut)  # normalize first
    actions: list[dict] = list(base.get("WFWorkflowActions") or [])

    new_actions: list[dict] = []
    new_actions.extend(_build_header(shortcut_name=shortcut_name, category=category))

    for n, action in enumerate(actions):
        new_actions.append(action)
        if density == DENSITY_FULL:
            new_actions.extend(_build_step(n, action))
        elif density == DENSITY_BRANCH and _is_branch_checkpoint(action):
            new_actions.extend(_build_step(n, action))
        # header-summary: no per-step logs

    new_actions.extend(_build_summary())

    result = deepcopy(base)
    result["WFWorkflowActions"] = new_actions
    return result


def strip_dev_telemetry(shortcut: dict) -> dict:
    """Return a deep-copy of ``shortcut`` with all telemetry-marked actions
    removed. Non-telemetry actions and top-level metadata are preserved
    verbatim."""
    result = deepcopy(shortcut)
    actions = result.get("WFWorkflowActions") or []
    result["WFWorkflowActions"] = [a for a in actions if not _is_injected(a)]
    return result


def predict_injected_count(
    shortcut: dict,
    *,
    density: str = DENSITY_BRANCH,
) -> int:
    """Predict how many *additional* actions ``inject_dev_telemetry`` will
    add to a freshly stripped ``shortcut`` at the given density."""
    if density not in DENSITIES:
        raise ValueError(f"invalid density {density!r}")
    actions = list((strip_dev_telemetry(shortcut).get("WFWorkflowActions") or []))
    base = HEADER_ACTIONS + SUMMARY_ACTIONS
    if density == DENSITY_HEADER_SUMMARY:
        return base
    if density == DENSITY_BRANCH:
        return base + CHECKPOINT_ACTIONS * count_branch_checkpoints(actions)
    if density == DENSITY_FULL:
        return base + CHECKPOINT_ACTIONS * len(actions)
    # unreachable
    return base
