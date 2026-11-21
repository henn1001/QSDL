#!/usr/bin/env python3
"""Generate and compile every Spring smoke case with bounded concurrency."""

from __future__ import annotations

import argparse
import fnmatch
import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Case:
    """One schema input and its isolated generated project paths."""

    case_id: str
    schema: Path
    output: Path
    config: Path
    log: Path


@dataclass(frozen=True)
class CaseResult:
    """Result captured from one generation/compilation worker."""

    case_id: str
    status: str
    log: Path


def positive_int(value: str) -> int:
    """Parse a positive integer for the worker count."""
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a positive integer") from error
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def discover_cases(root: Path, log_root: Path) -> list[Case]:
    """Discover case entrypoints and resolve their config and output paths."""
    cases_root = root
    shared_config = root / "spring-smoke-config.json"
    schemas = sorted(
        schema for schema in root.glob("*/**/schema.qsdl")
        if not schema.is_relative_to(root / "00-pet-store")
    )

    cases = []
    for schema in schemas:
        case_id = schema.relative_to(cases_root).parent.as_posix()
        case_config = schema.parent / "config.json"
        safe_case_id = case_id.replace("/", "__")
        cases.append(
            Case(
                case_id=case_id,
                schema=schema,
                output=root.parent / "xtmp" / "examples-spring-smoke" / "srcgen" / case_id,
                config=case_config if case_config.is_file() else shared_config,
                log=log_root / f"{safe_case_id}.log",
            )
        )
    return cases


def run_case(root: Path, case: Case) -> CaseResult:
    """Generate and compile one case, writing all command output to its log."""
    case.output.parent.mkdir(parents=True, exist_ok=True)
    case.log.parent.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(case.output, ignore_errors=True)

    try:
        with case.log.open("w", encoding="utf-8") as log:
            log.write(f"schema: {case.schema}\n")
            log.write(f"output: {case.output}\n")
            log.write(f"config: {case.config}\n\n")

            generation = subprocess.run(
                [
                    "uv",
                    "run",
                    "qsdl",
                    "generate",
                    "spring",
                    "-i",
                    str(case.schema),
                    "-c",
                    str(case.config),
                    "-o",
                    str(case.output),
                ],
                cwd=root.parent,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=False,
            )
            if generation.returncode != 0:
                log.write(f"\nqsdl exit code: {generation.returncode}\n")
                return CaseResult(case.case_id, "generation", case.log)

            compilation = subprocess.run(
                ["mvn", "-q", "compile"],
                cwd=case.output,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=False,
            )
            if compilation.returncode != 0:
                log.write(f"\nmvn exit code: {compilation.returncode}\n")
                return CaseResult(case.case_id, "compilation", case.log)

            return CaseResult(case.case_id, "ok", case.log)
    except Exception as error:  # noqa: BLE001 - keep one worker failure from hiding other cases.
        with case.log.open("a", encoding="utf-8") as log:
            log.write(f"\ninternal runner error: {error}\n")
        return CaseResult(case.case_id, "internal", case.log)


def build_parser(default_jobs: int) -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-j",
        "--jobs",
        type=positive_int,
        default=default_jobs,
        help="maximum number of concurrent cases (default: %(default)s)",
    )
    parser.add_argument(
        "--case",
        dest="case_patterns",
        action="append",
        metavar="GLOB",
        help="run cases matching this glob; repeat for multiple patterns",
    )
    parser.add_argument("--list", action="store_true", help="list available cases without running them")
    return parser


def select_cases(cases: list[Case], patterns: list[str] | None) -> list[Case]:
    """Select cases whose IDs match at least one requested glob pattern."""
    if not patterns:
        return cases
    return [case for case in cases if any(fnmatch.fnmatchcase(case.case_id, pattern) for pattern in patterns)]


def main() -> int:
    """Run all discovered cases and return a process exit code."""
    root = Path(__file__).resolve().parent
    try:
        default_jobs = positive_int(os.environ.get("SMOKE_JOBS", "2"))
    except argparse.ArgumentTypeError as error:
        print(f"SMOKE_JOBS {error}")
        return 2

    args = build_parser(default_jobs).parse_args()
    work_root = root.parent / "xtmp" / "examples-spring-smoke"
    log_root = work_root / ".smoke-logs"
    all_cases = discover_cases(root, log_root)
    if not all_cases:
        print("No case schemas found under examples/<category>/<case>/")
        return 2

    cases = select_cases(all_cases, args.case_patterns)
    if not cases:
        patterns = ", ".join(args.case_patterns or [])
        print(f"No cases matched: {patterns}")
        return 2

    if args.list:
        for case in cases:
            print(case.case_id)
        return 0

    shutil.rmtree(work_root / "srcgen", ignore_errors=True)
    shutil.rmtree(log_root, ignore_errors=True)
    (work_root / "srcgen").mkdir(parents=True)
    log_root.mkdir()

    worker_count = min(args.jobs, len(cases))
    for case in cases:
        print(f"\n==> {case.case_id} (starting; {worker_count} worker(s) max)")
        print(f"    schema: {case.schema.relative_to(root)}")
        print(f"    output: {case.output.relative_to(root.parent)}")

    results: dict[str, CaseResult] = {}
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = {executor.submit(run_case, root, case): case for case in cases}
        for future in as_completed(futures):
            case = futures[future]
            try:
                result = future.result()
            except Exception as error:  # noqa: BLE001 - defensive guard around worker execution.
                result = CaseResult(case.case_id, "internal", case.log)
                case.log.write_text(f"internal runner error: {error}\n", encoding="utf-8")
            results[result.case_id] = result
            print(f"<== {result.case_id}: {result.status.upper()}")

    failures = [results[case.case_id] for case in cases if results[case.case_id].status != "ok"]
    print(f"\n==> Summary: {len(cases)} cases, {len(failures)} failures")
    if not failures:
        return 0

    print("Failed cases:")
    for result in failures:
        print(f"  - {result.case_id} ({result.status})")
        print(f"    log: {result.log.relative_to(root.parent)}")
        if result.log.is_file():
            lines = result.log.read_text(encoding="utf-8", errors="replace").splitlines()
            print("    last 40 log lines:")
            for line in lines[-40:]:
                print(f"      {line}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
