from docplex.cp import model as cp
import csv
import json
import random
import os
import argparse


def read_file(file_name):
    data = []
    try:
        with open(file_name, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row['name']
                l, w, h = int(row['length']), int(row['width']), int(row['height'])
                data.append((l, w, h))

    except FileNotFoundError:
        print(f"Erreur : Le fichier '{file_name}' est introuvable.")

    return data


def get_ub(data: list[tuple[int, int, int]]):
    max_vals = [max(v) for v in data]
    return sum(max_vals)


def solve_3d_packing(item_dims, ub_L=1000, ub_W=3000, ub_H=3000, time_limit=600):
    EXECFILE = '/apps/CPLEX_Studio2211/cpoptimizer/bin/x86-64_linux/cpoptimizer'
    mdl = cp.CpoModel("3d_packing_min_volume")

    n = len(item_dims)

    # 6 rotations for each box
    rots = []
    for dx, dy, dz in item_dims:
        rots.append([
            (dx, dy, dz),
            (dx, dz, dy),
            (dy, dx, dz),
            (dy, dz, dx),
            (dz, dx, dy),
            (dz, dy, dx),
        ])

    # Orientation choice
    ori = [mdl.integer_var(0, 5, name=f"ori_{i}") for i in range(n)]

    # Chosen dimensions
    bx = [cp.element([rots[i][k][0] for k in range(6)], ori[i]) for i in range(n)]
    by = [cp.element([rots[i][k][1] for k in range(6)], ori[i]) for i in range(n)]
    bz = [cp.element([rots[i][k][2] for k in range(6)], ori[i]) for i in range(n)]

    # Positions
    x = [mdl.integer_var(0, ub_L, name=f"x_{i}") for i in range(n)]
    y = [mdl.integer_var(0, ub_W, name=f"y_{i}") for i in range(n)]
    z = [mdl.integer_var(0, ub_H, name=f"z_{i}") for i in range(n)]

    # Container dimensions
    L = mdl.integer_var(0, ub_L, name="L")
    W = mdl.integer_var(0, ub_W, name="W")
    H = mdl.integer_var(0, ub_H, name="H")

    # Fit inside container
    for i in range(n):
        mdl.add(x[i] + bx[i] <= L)
        mdl.add(y[i] + by[i] <= W)
        mdl.add(z[i] + bz[i] <= H)

    # 3D non-overlap
    for i in range(n):
        for j in range(i + 1, n):
            mdl.add(
                (x[i] + bx[i] <= x[j]) |
                (x[j] + bx[j] <= x[i]) |
                (y[i] + by[i] <= y[j]) |
                (y[j] + by[j] <= y[i]) |
                (z[i] + bz[i] <= z[j]) |
                (z[j] + bz[j] <= z[i])
            )
    # Symmetry breaking
    # after bx, by, bz are defined
    sx = sum(bx)
    sy = sum(by)
    sz = sum(bz)

    mdl.add(sx >= sy)
    mdl.add(sy >= sz)

    mdl.add(L >= W)
    mdl.add(W >= H)

    # Minimize container volume
    mdl.add(mdl.minimize(L + W + H))

    sol = mdl.solve(execfile=EXECFILE, TimeLimit=time_limit)  # , LogVerbosity="Quiet")
    return sol, x, y, z, ori, rots


def export_solution(sol, x, y, z, ori, rots):
    boxes = []

    n = len(x)

    for i in range(n):
        xi = sol.get_value(x[i])
        yi = sol.get_value(y[i])
        zi = sol.get_value(z[i])

        o = sol.get_value(ori[i])
        dx, dy, dz = rots[i][o]

        color = [
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        ]

        boxes.append({
            "position": [xi, yi, zi],
            "size": [dx, dy, dz],
            "color": color
        })

    result = {"boxes": boxes, "text": "Text\n"}

    return result


def main_cluster(job_id: int):
    folder_path = "./dataset"
    csv_files = [
        os.path.splitext(f)[0]
        for f in os.listdir(folder_path)
        if f.endswith(".csv")
    ]
    print(csv_files)

    file_name = csv_files[job_id]
    print(file_name)
    data = read_file(f"./dataset/{file_name}.csv")
    print(data)
    ub = get_ub(data)
    print("ub = ", ub)
    sol, x, y, z, ori, rots = solve_3d_packing(data, ub, ub, ub, time_limit=144000)
    res = export_solution(sol, x, y, z, ori, rots)
    print(res)
    with open(f"./solutions/{file_name}.json", "w") as f:
        json.dump(res, f)  # , separators=(',', ':'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="cluster gives job_id")
    parser.add_argument("job_id", type=int, help="job_id that will use to start corresponding problem")
    args = parser.parse_args()
    job_id = args.job_id
    main_cluster(job_id)