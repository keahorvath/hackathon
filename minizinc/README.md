# 3D Packing with MiniZinc

This folder contains a simple MiniZinc workflow for the 3D packing model.
The file `packing.mzn` is a starter template for the exercise, not a complete model.

Files:

- `packing.mzn`: the MiniZinc model that students must complete
- `csv_2_dzn.py`: converts dimension CSV files into MiniZinc `.dzn` data
- `run_minizinc.py`: runs the full pipeline from CSV to MiniZinc output and BlockViz JSON
- `mzn_2_json.py`: converts MiniZinc output into BlockViz `.jsonl` format

## Exercise Instructions

Students are expected to edit and complete `packing.mzn`.
In particular, they should add the missing variable domains and the packing constraints needed to obtain a valid model.
The commands below assume that `packing.mzn` has already been completed.

## Full Pipeline

Run everything in one command:

```bash
python3 run_minizinc.py --model packing.mzn --instance ../dataset/hetero_0005.csv
```

This will:

- create `out/hetero_0005.dzn`
- run MiniZinc and write `out/hetero_0005.out`
- convert the solver output into `out/blockviz_hetero_0005.jsonl`

Required arguments:

- `--model`: MiniZinc model path to use. This must be an explicit valid path.
- `--instance`: CSV dataset path to solve. This must be an explicit valid path.

Optional arguments:

- `--solver`: choose the MiniZinc solver, default is `chuffed`
- `--time-limit-ms`: set the MiniZinc time limit, default is `10000`
- `--seed`: set the random seed, default is `42`
- `--dzn-output`, `--log-output`, `--json-output`: override output paths
- `--no-json`: skip BlockViz `.jsonl` generation

Each run regenerates the `.dzn`, reruns MiniZinc, and rewrites the `.out` and
`.jsonl` outputs.

Bare filenames such as `hetero_0050.csv` are rejected on purpose. Use a real
path such as `../dataset/hetero_0050.csv`.

## Details

### Generate A `.dzn` File

Run the converter with the CSV file you want to transform:

```bash
python3 csv_2_dzn.py ../dataset/hetero_0005.csv -o out/hetero_0005.dzn
```

Optional arguments:

- `-o/--output`: choose the output `.dzn` file

The script accepts CSV files with either `length,width,height` or
`length,depth,height` columns and writes MiniZinc data with `n`, `len`,
`dep`, and `hei`.

### Run An Instance

From this directory, run:

Make sure you have completed `packing.mzn` before running this command.

```bash
mkdir -p out
python3 csv_2_dzn.py ../dataset/hetero_0005.csv -o out/hetero_0005.dzn
minizinc --solver chuffed --statistics --time-limit 60000 --random-seed 42 -i --solver-statistics -f packing.mzn out/hetero_0005.dzn > out/hetero_0005.out
```

This writes the solver output to `out/hetero_0005.out`.

### Convert The Output To BlockViz Format

Run:

```bash
python3 mzn_2_json.py --input out/hetero_0005.out --dzn out/hetero_0005.dzn -o out/blockviz_hetero_0005.jsonl
```

This reads `out/hetero_0005.out` and writes `out/blockviz_hetero_0005.jsonl`.
