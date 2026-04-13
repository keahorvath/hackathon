import argparse
import csv
from pathlib import Path
from typing import List, Optional


def resolve_csv_path(csv_path: str) -> Path:
    resolved_path = Path(csv_path).expanduser()
    if resolved_path.exists() and resolved_path.is_file():
        return resolved_path

    raise FileNotFoundError(
        f"Could not find CSV input '{csv_path}'. "
        "Pass an explicit existing path such as '../dataset/hetero_0050.csv'."
    )


def _pick_depth_column(fieldnames: List[str]) -> str:
    for candidate in ("width", "depth"):
        if candidate in fieldnames:
            return candidate
    raise ValueError(
        "CSV must contain either a 'width' column or a 'depth' column."
    )


def _to_int(value: str, column_name: str, row_number: int) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Invalid value {value!r} in column '{column_name}' at row {row_number}."
        ) from exc


def read_box_dimensions(csv_path: str) -> tuple[List[int], List[int], List[int]]:
    source_path = resolve_csv_path(csv_path)

    with source_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames or []

        missing = {"length", "height"} - set(fieldnames)
        if missing:
            missing_list = ", ".join(sorted(missing))
            raise ValueError(f"CSV is missing required column(s): {missing_list}.")

        depth_column = _pick_depth_column(fieldnames)

        length_values: List[int] = []
        depth_values: List[int] = []
        height_values: List[int] = []

        for row_index, row in enumerate(reader, start=2):
            if not row["length"] or not row[depth_column] or not row["height"]:
                continue

            length_values.append(_to_int(row["length"], "length", row_index))
            depth_values.append(_to_int(row[depth_column], depth_column, row_index))
            height_values.append(_to_int(row["height"], "height", row_index))

    return length_values, depth_values, height_values


def build_dzn_content(
    length_values: List[int],
    depth_values: List[int],
    height_values: List[int],
) -> str:
    n = len(length_values)
    return (
        f"n = {n};\n"
        f"len = {length_values};\n"
        f"dep = {depth_values};\n"
        f"hei = {height_values};\n"
    )


def generate_dzn(
    csv_path: str,
    output_path: Optional[str] = None,
) -> str:
    """
    Convert a CSV file into MiniZinc .dzn data with:
        n = ...;
        len = [...];
        dep = [...];
        hei = [...];

    Supported CSV schemas:
    - length, width, height
    - length, depth, height
    """

    if output_path is None:
        output_path = str(Path(csv_path).with_suffix(".dzn"))

    length_values, depth_values, height_values = read_box_dimensions(csv_path)
    dzn_content = build_dzn_content(length_values, depth_values, height_values)

    Path(output_path).write_text(dzn_content, encoding="utf-8")
    return dzn_content


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a CSV file of box dimensions into a MiniZinc .dzn file."
    )
    parser.add_argument(
        "csv_path",
        help=(
            "Input CSV file path. Examples: '../dataset/hetero_0005.csv' "
            "or '/full/path/to/hetero_0005.csv'."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_path",
        help="Output .dzn file. Defaults to the CSV filename with a .dzn extension.",
    )
    args = parser.parse_args()

    try:
        print(generate_dzn(args.csv_path, args.output_path))
    except (FileNotFoundError, ValueError) as exc:
        raise SystemExit(str(exc))


if __name__ == "__main__":
    main()
