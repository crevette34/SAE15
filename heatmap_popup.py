import matplotlib
matplotlib.use("TkAgg")   # IMPORTANT : active les fenêtres interactives

import matplotlib.pyplot as plt
import numpy as np
from app import charger_depuis_fichier, F_TXT

evo_parking, evo_velo, _, _, _ = charger_depuis_fichier(F_TXT)

all_names = list(evo_velo.keys()) + list(evo_parking.keys())
all_data = list(evo_velo.values()) + list(evo_parking.values())

if len(all_data) > 1:
    longueur = len(all_data[0])
    if all(len(serie) == longueur for serie in all_data):
        matrix = np.zeros((longueur, len(all_data)))
        for j, serie in enumerate(all_data):
            matrix[:, j] = [point[1] for point in serie]

        corr = np.corrcoef(matrix.T)

        fig = plt.figure(figsize=(12, 10), dpi=300)
        plt.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
        plt.colorbar()

        plt.xticks(range(len(all_names)), all_names, rotation=45, ha="right")
        plt.yticks(range(len(all_names)), all_names)

        plt.title("Heatmap de corrélation réelle (voitures + vélos)")
        plt.tight_layout()

        plt.show()
    else:
        print("Longueurs différentes entre séries, heatmap impossible.")
else:
    print("Pas assez de données pour générer la heatmap.")
