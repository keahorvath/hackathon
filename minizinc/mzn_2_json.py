import argparse
import json
import random
import re
from pathlib import Path
from typing import Dict, List, Optional

BOX_RE = re.compile(r"box\s+\d+:\s*x=(\d+)\s*y=(\d+)\s*z=(\d+)", re.IGNORECASE)
CAP_RE = re.compile(r"^([XYZV])\s*=\s*(\d+)\s*$", re.IGNORECASE)
BOUNDARY_RE = re.compile(r"^(----------|==========)$")
ARRAY_RE = re.compile(r"^(len|dep|hei)\s*=\s*\[(.*?)\]\s*;\s*$", re.IGNORECASE)


def _parse_int_list(raw_values: str) -> List[int]:
    values = [value.strip() for value in raw_values.split(",") if value.strip()]
    return [int(value) for value in values]


def load_box_sizes_from_dzn(dzn_path: str) -> List[List[int]]:
    arrays: Dict[str, List[int]] = {}
    lines = Path(dzn_path).read_text(encoding="utf-8").splitlines()

    for raw_line in lines:
        line = raw_line.strip()
        match = ARRAY_RE.match(line)
        if not match:
            continue

        key, values = match.groups()
        arrays[key.lower()] = _parse_int_list(values)

    missing = {"len", "dep", "hei"} - set(arrays)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"DZN is missing required array(s): {missing_list}.")

    if not (len(arrays["len"]) == len(arrays["dep"]) == len(arrays["hei"])):
        raise ValueError("DZN arrays len, dep, and hei must have the same size.")

    return [
        [length, depth, height]
        for length, depth, height in zip(
            arrays["len"], arrays["dep"], arrays["hei"]
        )
    ]


def _parse_solution_block(lines: List[str]) -> Optional[Dict[str, object]]:
    caps: Dict[str, int] = {}
    boxes: List[List[int]] = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("%"):
            continue

        cap_match = CAP_RE.match(line)
        if cap_match:
            key, value = cap_match.groups()
            caps[key.upper()] = int(value)
            continue

        box_match = BOX_RE.match(line)
        if box_match:
            x, y, z = map(int, box_match.groups())
            boxes.append([x, y, z])

    if not boxes:
        return None

    if not all(key in caps for key in ("X", "Y", "Z", "V")):
        print(f"Skipping incomplete solution with {len(boxes)} boxes.")
        return None

    return {
        "boxes_raw": boxes,
        "X": caps["X"],
        "Y": caps["Y"],
        "Z": caps["Z"],
        "V": caps["V"],
    }


def parse_solutions(text: str) -> List[Dict[str, object]]:
    solutions: List[Dict[str, object]] = []
    current_block: List[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if BOUNDARY_RE.match(line):
            solution = _parse_solution_block(current_block)
            if solution is not None:
                solutions.append(solution)
            current_block = []
            continue

        current_block.append(raw_line)

    solution = _parse_solution_block(current_block)
    if solution is not None:
        solutions.append(solution)

    return solutions


def generate_unique_colors(n: int, seed: int = 42) -> List[List[int]]:
    random.seed(seed)
    used = set()
    colors: List[List[int]] = []

    while len(colors) < n:
        color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )
        if color not in used:
            used.add(color)
            colors.append(list(color))

    return colors


def build_output_objects(
    parsed_solutions: List[Dict[str, object]],
    colors: List[List[int]],
    box_sizes: Optional[List[List[int]]] = None,
) -> List[Dict[str, object]]:
    output = []

    for index, solution in enumerate(parsed_solutions, start=1):
        positions = solution["boxes_raw"]

        if box_sizes is None:
            sizes = [[solution["X"], solution["Y"], solution["Z"]]] * len(positions)
        else:
            if len(positions) != len(box_sizes):
                raise ValueError(
                    "The number of boxes in the solver output does not match the DZN."
                )
            sizes = box_sizes

        boxes = []
        for position, size, color in zip(positions, sizes, colors):
            boxes.append(
                {
                    "position": position,
                    "size": size,
                    "color": color,
                }
            )

        output.append(
            {
                "boxes": boxes,
                "text": f"Scene {index}\\nV = {solution['V']}",
            }
        )

    return output


def convert_file(
    input_path: str,
    output_path: str,
    dzn_path: Optional[str] = None,
) -> int:
    text = Path(input_path).read_text(encoding="utf-8")
    parsed_solutions = parse_solutions(text)

    if not parsed_solutions:
        print("No complete solutions found.")
        return 0

    box_sizes = load_box_sizes_from_dzn(dzn_path) if dzn_path else None

    counts = [len(solution["boxes_raw"]) for solution in parsed_solutions]
    print("Boxes per solution:", counts)

    if box_sizes is not None and any(count != len(box_sizes) for count in counts):
        raise ValueError(
            "The number of boxes in the solver output does not match the DZN."
        )

    max_boxes = len(box_sizes) if box_sizes is not None else max(counts)
    print("Generating", max_boxes, "unique fixed colors...")

    colors = generate_unique_colors(max_boxes, seed=42)
    output_objects = build_output_objects(parsed_solutions, colors, box_sizes)

    with Path(output_path).open("w", encoding="utf-8") as output_file:
        for output_object in output_objects:
            output_file.write(json.dumps(output_object, ensure_ascii=False) + "\n")

    print(f"Written {len(output_objects)} solutions to {output_path}")
    return len(output_objects)


def _default_output_path(input_path: str) -> str:
    source_path = Path(input_path)
    return str(source_path.with_name(f"blockviz_{source_path.stem}.jsonl"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert MiniZinc solver output into BlockViz .jsonl scenes."
    )
    parser.add_argument(
        "--input",
        dest="input_path",
        required=True,
        help="MiniZinc solver output file to convert.",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_path",
        help="Output .jsonl file. Defaults to blockviz_<input>.jsonl.",
    )
    parser.add_argument(
        "--dzn",
        dest="dzn_path",
        help="Optional .dzn file used to recover the real size of each box.",
    )
    args = parser.parse_args()

    output_path = args.output_path or _default_output_path(args.input_path)
    convert_file(args.input_path, output_path, args.dzn_path)


if __name__ == "__main__":
    main()
