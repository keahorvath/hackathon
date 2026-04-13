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
                data.append((l,w,h))

    except FileNotFoundError:
        print(f"Erreur : Le fichier '{file_name}' est introuvable.")
    
    return data

def compute_UB(data):
    sum_x = 0
    sum_y = 0
    sum_z = 0
    for i in range(len(data)):
        sum_x += data[i][0]
        sum_y += data[i][1]
        sum_z += data[i][2]

    return sum_x * sum_y * sum_z

if __name__ == "__main__":
    #data = read_file("dataset/random_0050.csv")
    #print(data)
    files = [f.name for f in Path('./dataset').glob('*.csv')]
    dossier = Path('./dataset') 

    for file in files:
        data = read_file("dataset/" + file)
        print(data)