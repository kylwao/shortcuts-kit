"""Tests for the dev profile telemetry injector/stripper."""

from __future__ import annotations

from pathlib import Path

from shortcuts_src import plist_io
from shortcuts_src.profile import (
    CHECKPOINT_ACTIONS,
    DENSITY_BRANCH,
    DENSITY_FULL,
    DENSITY_HEADER_SUMMARY,
    HEADER_ACTIONS,
    SUMMARY_ACTIONS,
    TELEMETRY_MARKER,
    count_branch_checkpoints,
    inject_dev_telemetry,
    predict_injected_count,
    strip_dev_telemetry,
)

_FIXTURE = Path(__file__).parent / "fixtures" / "minimal.source.json"


def _load():
    return plist_io.loads(_FIXTURE.read_bytes())


def test_header_summary_adds_fixed_count():
    base = _load()
    injected = inject_dev_telemetry(
        base,
        shortcut_name="mini",
        category="test",
        density=DENSITY_HEADER_SUMMARY,
    )
    n_base = len(base["WFWorkflowActions"])
    n_injected = len(injected["WFWorkflowActions"])
    assert n_injected - n_base == HEADER_ACTIONS + SUMMARY_ACTIONS == 10


def test_branch_density_matches_checkpoint_math():
    base = _load()
    branches = count_branch_checkpoints(base["WFWorkflowActions"])
    injected = inject_dev_telemetry(
        base, shortcut_name="mini", category="test", density=DENSITY_BRANCH
    )
    added = len(injected["WFWorkflowActions"]) - len(base["WFWorkflowActions"])
    assert added == HEADER_ACTIONS + SUMMARY_ACTIONS + CHECKPOINT_ACTIONS * branches
    assert added == predict_injected_count(base, density=DENSITY_BRANCH)


def test_full_density_adds_two_per_original_action():
    base = _load()
    injected = inject_dev_telemetry(
        base, shortcut_name="mini", category="test", density=DENSITY_FULL
    )
    added = len(injected["WFWorkflowActions"]) - len(base["WFWorkflowActions"])
    assert added == HEADER_ACTIONS + SUMMARY_ACTIONS + CHECKPOINT_ACTIONS * len(base["WFWorkflowActions"])
    assert added == predict_injected_count(base, density=DENSITY_FULL)


def test_strip_restores_exact_original():
    base = _load()
    injected = inject_dev_telemetry(
        base, shortcut_name="mini", category="test", density=DENSITY_BRANCH
    )
    stripped = strip_dev_telemetry(injected)
    # Clean up any keys we didn't touch
    assert stripped == base, "strip should restore the original shortcut byte-for-byte"


def test_all_injected_actions_carry_marker():
    base = _load()
    injected = inject_dev_telemetry(
        base, shortcut_name="mini", category="test", density=DENSITY_FULL
    )
    # Everything not present in base must carry the marker
    base_uuids = {a["WFWorkflowActionParameters"]["UUID"] for a in base["WFWorkflowActions"]}
    for a in injected["WFWorkflowActions"]:
        params = a["WFWorkflowActionParameters"]
        uid = params.get("UUID")
        if uid and uid in base_uuids:
            continue  # original action, should NOT carry marker
        assert TELEMETRY_MARKER in params, f"injected action missing marker: {a}"


def test_no_uuid_collision_with_base():
    base = _load()
    injected = inject_dev_telemetry(
        base, shortcut_name="mini", category="test", density=DENSITY_FULL
    )
    base_uuids = {a["WFWorkflowActionParameters"]["UUID"] for a in base["WFWorkflowActions"]}
    injected_only = [
        a for a in injected["WFWorkflowActions"]
        if TELEMETRY_MARKER in a["WFWorkflowActionParameters"]
    ]
    for a in injected_only:
        uid = a["WFWorkflowActionParameters"].get("UUID")
        if uid is not None:
            assert uid not in base_uuids


def test_inject_is_idempotent_through_strip_inject():
    base = _load()
    once = inject_dev_telemetry(
        base, shortcut_name="mini", category="test", density=DENSITY_BRANCH
    )
    twice = inject_dev_telemetry(
        once, shortcut_name="mini", category="test", density=DENSITY_BRANCH
    )
    # After a second round, action counts should match (inject strips before re-injecting)
    assert len(once["WFWorkflowActions"]) == len(twice["WFWorkflowActions"])


def test_compile_dev_profile_produces_larger_bplist(tmp_path: Path):
    from shortcuts_src.compile import compile_source

    release_out = compile_source(
        str(_FIXTURE),
        out_path=str(tmp_path / "release.shortcut"),
        allow_unsigned=True,
        profile="release",
    )
    dev_out = compile_source(
        str(_FIXTURE),
        out_path=str(tmp_path / "dev.shortcut"),
        allow_unsigned=True,
        profile="dev",
        telemetry=DENSITY_BRANCH,
        category="test",
        shortcut_name="mini",
    )
    release_raw = release_out.read_bytes()
    dev_raw = dev_out.read_bytes()
    assert release_raw.startswith(b"bplist00")
    assert dev_raw.startswith(b"bplist00")
    assert len(dev_raw) > len(release_raw), "dev profile should add bytes"

    dev_obj = plist_io.loads(dev_raw)
    stripped_obj = strip_dev_telemetry(dev_obj)
    release_obj = plist_io.loads(release_raw)
    assert stripped_obj == release_obj
