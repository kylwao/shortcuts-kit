"""Command-line entry point."""

from __future__ import annotations

import argparse
import datetime as _dt
import sys
from pathlib import Path

from . import __version__
from .check import check_input, report_lines
from .compile import compile_source
from .decompile import decompile_input, inspect_input
from .ingest import ingest


def _add_decompile(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "decompile",
        help="Fetch / open a shortcut and emit XML + JSON source plus a Markdown flow view.",
    )
    p.add_argument(
        "input",
        help="iCloud share URL (https://www.icloud.com/shortcuts/<id>) or path to a .shortcut / .plist / .xml / .json file.",
    )
    p.add_argument(
        "-o", "--out",
        default=None,
        help="Output directory (default: alongside input or current directory).",
    )
    p.add_argument(
        "--format",
        choices=["xml", "json", "both"],
        default="both",
        help="Which canonical source format to emit (default: both).",
    )
    p.add_argument(
        "--name",
        default=None,
        help="Override the base name used for output files.",
    )
    p.add_argument(
        "--no-flow",
        action="store_true",
        help="Skip generating the Markdown flow view.",
    )
    p.add_argument(
        "--keep-bplist",
        action="store_true",
        help="Also save the raw binary plist (.bplist) alongside source files.",
    )
    p.set_defaults(func=_run_decompile)


def _add_compile(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "compile",
        help="Compile an edited XML / JSON source file back to a signed .shortcut.",
    )
    p.add_argument(
        "input",
        help="Path to the edited source file (.xml / .json / .plist).",
    )
    p.add_argument(
        "-o", "--out",
        default=None,
        help="Output path for the signed .shortcut file (default: <name>.signed.shortcut next to input).",
    )
    p.add_argument(
        "--mode",
        choices=["anyone", "people-who-know-me"],
        default="anyone",
        help="Signing mode passed to `shortcuts sign` (default: anyone).",
    )
    p.add_argument(
        "--keep-unsigned",
        action="store_true",
        help="Also keep the intermediate unsigned binary plist as <out>.unsigned.shortcut.",
    )
    p.add_argument(
        "--allow-unsigned",
        action="store_true",
        help="Skip signing and just emit the unsigned .shortcut (use only if `shortcuts` CLI is unavailable).",
    )
    p.add_argument(
        "--profile",
        choices=["release", "dev"],
        default="release",
        help="Compilation profile. 'release' (default) emits exactly the source; 'dev' injects telemetry logging actions that write JSONL logs to iCloud Drive for later ingestion.",
    )
    p.add_argument(
        "--telemetry",
        choices=["header-summary", "branch", "full"],
        default="branch",
        help="Telemetry density (only meaningful under --profile dev). Default: branch.",
    )
    p.add_argument(
        "--category",
        default=None,
        help="Category name used in the log file path. Default: inferred from the source path (e.g. 'FoodAnalysis').",
    )
    p.set_defaults(func=_run_compile)


def _add_inspect(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "inspect",
        help="Print a short summary of the shortcut (metadata, action count, first comment).",
    )
    p.add_argument("input", help="iCloud URL or local shortcut/plist file.")
    p.set_defaults(func=_run_inspect)


def _add_check(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "check",
        help="Validate structure before compiling: duplicate UUIDs, unpaired control flow, broken output references.",
    )
    p.add_argument(
        "input",
        help="iCloud URL or local .shortcut / .plist / .xml / .json file. JSON and XML sources get line numbers.",
    )
    p.set_defaults(func=_run_check)


def _add_ingest_logs(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "ingest-logs",
        help="Aggregate iOS dev-profile JSONL logs into a Markdown diagnostic report.",
    )
    p.add_argument(
        "log_dirs",
        nargs="*",
        help=(
            "One or more directories to scan (recursively). "
            "If none are given, shortcuts-src scans iCloud Drive "
            "(~/Library/Mobile Documents/com~apple~CloudDocs/Shortcuts/) plus any "
            "'debuglog' folder discovered under --project-root."
        ),
    )
    p.add_argument(
        "--source",
        default=None,
        help="Path to the source.json file used to generate the dev-profile build. "
             "When provided, each step is mapped back to its action index / line number.",
    )
    p.add_argument(
        "--project-root",
        default=None,
        help="Project root under which to auto-discover '<...>/debuglog/' folders as manual upload sources. "
             "Default: current working directory.",
    )
    p.add_argument(
        "-o", "--out",
        default=None,
        help="Write the Markdown report to this file. Default: stdout.",
    )
    p.add_argument(
        "--since",
        default=None,
        help="Only include log files modified on or after this date (YYYY-MM-DD).",
    )
    p.add_argument(
        "--only-failed",
        action="store_true",
        help="Keep only runs that did not produce a summary line or that reported ok=false.",
    )
    p.set_defaults(func=_run_ingest_logs)


def _run_decompile(args: argparse.Namespace) -> int:
    out = decompile_input(
        args.input,
        out_dir=args.out,
        fmt=args.format,
        name=args.name,
        emit_flow=not args.no_flow,
        keep_bplist=args.keep_bplist,
    )
    print(f"Decompiled: {out.name}")
    for label, path in out.files.items():
        if path is not None:
            print(f"  {label:<10} -> {path}")
    return 0


def _run_compile(args: argparse.Namespace) -> int:
    out_path = compile_source(
        args.input,
        out_path=args.out,
        mode=args.mode,
        keep_unsigned=args.keep_unsigned,
        allow_unsigned=args.allow_unsigned,
        profile=args.profile,
        telemetry=args.telemetry,
        category=args.category,
    )
    print(f"Compiled: {out_path}")
    if args.profile == "dev":
        print(
            f"\nDev profile injected (telemetry={args.telemetry}).\n"
            "On first run, iOS will ask for iCloud Drive write permission.\n"
            "Logs will appear under iCloud Drive/Shortcuts/<category>/<name>/logs/<runId>.jsonl\n"
            "and sync back to Mac at ~/Library/Mobile Documents/com~apple~CloudDocs/Shortcuts/.../logs/\n"
            "Run `shortcuts-src ingest-logs` after a few iOS runs to get a diagnostic report."
        )
    if not args.allow_unsigned:
        print(
            "\nNext step: open the file in Shortcuts.app to import it, then use\n"
            "  Share -> Copy iCloud Link\n"
            "to obtain a sharable https://www.icloud.com/shortcuts/... URL.\n"
            "(Apple does not expose a programmatic API for that last step.)"
        )
    return 0


def _run_inspect(args: argparse.Namespace) -> int:
    summary = inspect_input(args.input)
    for line in summary:
        print(line)
    return 0


def _run_check(args: argparse.Namespace) -> int:
    result = check_input(args.input)
    for line in report_lines(result):
        print(line)
    return 1 if result.errors else 0


def _run_ingest_logs(args: argparse.Namespace) -> int:
    since = None
    if args.since:
        try:
            since = _dt.date.fromisoformat(args.since)
        except ValueError as exc:
            raise SystemExit(f"error: --since must be YYYY-MM-DD ({exc})")

    log_dirs = [Path(d).expanduser() for d in args.log_dirs] if args.log_dirs else None
    project_root = Path(args.project_root).expanduser() if args.project_root else Path.cwd()
    source = Path(args.source).expanduser() if args.source else None

    runs, report = ingest(
        log_dirs=log_dirs,
        source=source,
        project_root=project_root,
        since=since,
        only_failed=args.only_failed,
    )

    if args.out:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"Report written to {out}")
    else:
        sys.stdout.write(report)

    if not runs:
        print("(no runs found)", file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shortcuts-src",
        description="Decompile and compile Apple Shortcuts between .shortcut binaries and editable XML/JSON source.",
    )
    parser.add_argument("--version", action="version", version=f"shortcuts-src {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    _add_decompile(sub)
    _add_compile(sub)
    _add_inspect(sub)
    _add_check(sub)
    _add_ingest_logs(sub)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except SystemExit:
        raise
    except Exception as exc:  # surface a clean error without traceback for CLI users
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
