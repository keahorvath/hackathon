import argparse
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional

from csv_2_dzn import generate_dzn, resolve_csv_path
from mzn_2_json import convert_file

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = Path("out")
DEFAULT_TIME_LIMIT_MS = 10000


def _default_dzn_path(csv_path: str) -> str:
    return str(OUTPUT_DIR / Path(csv_path).with_suffix(".dzn").name)


def _default_log_path(csv_path: str) -> str:
    return str(OUTPUT_DIR / Path(csv_path).with_suffix(".out").name)


def _default_json_path(csv_path: str) -> str:
    source_path = Path(csv_path)
    return str(OUTPUT_DIR / f"blockviz_{source_path.stem}.jsonl")


def _next_available_path(path: Path) -> Path:
    if not path.exists():
        return path

    counter = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def _ensure_output_dir_ready() -> None:
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        return

    if OUTPUT_DIR.is_dir():
        return

    legacy_backup = _next_available_path(Path("out_legacy.out"))
    OUTPUT_DIR.rename(legacy_backup)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    migrated_backup = _next_available_path(OUTPUT_DIR / "legacy_out.out")
    legacy_backup.rename(migrated_backup)


def _ensure_parent_directory(path_str: str) -> None:
    parent = Path(path_str).parent
    if str(parent) in ("", "."):
        return

    try:
        if parent == OUTPUT_DIR:
            _ensure_output_dir_ready()
            return
        parent.mkdir(parents=True, exist_ok=True)
    except FileExistsError as exc:
        raise RuntimeError(
            f"Cannot create output directory '{parent}' because a file with that "
            "name already exists."
        ) from exc


def _resolve_model_path(mzn_path: str) -> Path:
    raw_path = Path(mzn_path).expanduser()
    candidates = [raw_path]
    if not raw_path.is_absolute():
        candidates.append(SCRIPT_DIR / raw_path)

    seen = set()
    for candidate in candidates:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        if candidate.exists():
            return candidate.resolve()

    attempted = ", ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(
        f"Could not find MiniZinc model '{mzn_path}'. Tried: {attempted}."
    )


def run_pipeline(
    mzn_path: str,
    csv_path: str,
    solver: str = "chuffed",
    time_limit_ms: int = DEFAULT_TIME_LIMIT_MS,
    seed: int = 42,
    dzn_output: Optional[str] = None,
    log_output: Optional[str] = None,
    json_output: Optional[str] = None,
    write_json: bool = True,
) -> Dict[str, object]:
    if shutil.which("minizinc") is None:
        raise RuntimeError("Could not find 'minizinc' in PATH.")

    csv_source = resolve_csv_path(csv_path)
    mzn_source = _resolve_model_path(mzn_path)
    dzn_path = dzn_output or _default_dzn_path(csv_path)
    log_path = log_output or _default_log_path(csv_path)
    json_path = json_output or _default_json_path(csv_path)

    _ensure_parent_directory(dzn_path)
    _ensure_parent_directory(log_path)
    if write_json:
        _ensure_parent_directory(json_path)

    generate_dzn(str(csv_source), dzn_path)

    command = [
        "minizinc",
        "--solver",
        solver,
        "--statistics",
        "--time-limit",
        str(time_limit_ms),
        "--random-seed",
        str(seed),
        "-i",
        "--solver-statistics",
        "-f",
        str(mzn_source),
        dzn_path,
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )

    Path(log_path).write_text(result.stdout, encoding="utf-8")

    if result.returncode != 0:
        raise RuntimeError(
            f"MiniZinc failed with exit code {result.returncode}. See {log_path}."
        )

    scene_count = 0
    if write_json:
        scene_count = convert_file(log_path, json_path, dzn_path)

    return {
        "dzn_path": dzn_path,
        "log_path": log_path,
        "json_path": json_path if write_json and scene_count else None,
        "scene_count": str(scene_count),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a CSV to DZN, run MiniZinc, and export BlockViz JSON."
    )
    parser.add_argument(
        "--instance",
        dest="csv_path",
        required=True,
        help=(
            "CSV dataset path. This must be an explicit existing path such as "
            "'../dataset/hetero_0005.csv'."
        ),
    )
    parser.add_argument(
        "--model",
        dest="mzn_path",
        required=True,
        help=(
            "MiniZinc model file. This must be an explicit existing path such as "
            "'packing.mzn'."
        ),
    )
    parser.add_argument(
        "--solver",
        default="chuffed",
        help="MiniZinc solver name. Defaults to 'chuffed'.",
    )
    parser.add_argument(
        "--time-limit-ms",
        type=int,
        default=DEFAULT_TIME_LIMIT_MS,
        help=(
            "Time limit passed to MiniZinc in milliseconds. "
            f"Defaults to {DEFAULT_TIME_LIMIT_MS}."
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed passed to MiniZinc. Defaults to 42.",
    )
    parser.add_argument(
        "--dzn-output",
        help="Output .dzn path. Defaults to out/<csv>.dzn.",
    )
    parser.add_argument(
        "--log-output",
        help="Output solver log path. Defaults to out/<csv>.out.",
    )
    parser.add_argument(
        "--json-output",
        help="Output BlockViz .jsonl path. Defaults to out/blockviz_<csv>.jsonl.",
    )
    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Skip BlockViz .jsonl generation.",
    )
    args = parser.parse_args()

    try:
        outputs = run_pipeline(
            args.mzn_path,
            args.csv_path,
            solver=args.solver,
            time_limit_ms=args.time_limit_ms,
            seed=args.seed,
            dzn_output=args.dzn_output,
            log_output=args.log_output,
            json_output=args.json_output,
            write_json=not args.no_json,
        )
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        raise SystemExit(str(exc))

    print(f"DZN written to {outputs['dzn_path']}")
    print(f"MiniZinc log written to {outputs['log_path']}")
    if outputs["json_path"]:
        print(f"BlockViz JSON written to {outputs['json_path']}")


if __name__ == "__main__":
    main()
