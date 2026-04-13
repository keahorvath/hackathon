import csv
from pathlib import Path

def read_file(file_name):
    data  = []
    try:
        with open(file_name, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row['name']
                l, w, h = int(row['length']), int(row['width']), int(row['height'])
                data.append([l,w,h])

    except FileNotFoundError:
        print(f"Erreur : Le fichier '{file_name}' est introuvable.")
    
    return data

def compute_UB(data):
    for box in data:
        box.sort()
    x_min = 1000
    x_max = 0
    y_sum = 0
    z_max = 0
    for box in data:
        if (box[0] < x_min):
            x_min = box[0]
        if box[0] > x_max:
            x_max = box[0]

        y_sum += box[1]
        if box[2] > z_max:
            z_max = box[2]
    UB1 = x_max * y_sum *z_max
    print(x_min, x_max)
    x_max = 0
    y_sum = 0
    z_max = 0
    for box in data:
        if box[0] > x_max:
            x_max = box[0]
        y_sum += box[2]
        if box[1] > z_max:
            z_max = box[1]
    UB2 = x_max * y_sum *z_max
    for box in data:
        if box[1] > x_max:
            x_max = box[1]
        y_sum += box[0]
        if box[2] > z_max:
            z_max = box[2]
    UB3 = x_max * y_sum *z_max
    return min(UB1,min(UB2, UB3))

if __name__ == "__main__":
    data = read_file("dataset/homo_0050.csv")
    print(data)
    UB = compute_UB(data)
    print(UB)
    """
    files = [f.name for f in Path('./dataset').glob('*.csv')]
    dossier = Path('./dataset') 

    for file in files:
        data = read_file("dataset/" + file)
        print(data)
        """