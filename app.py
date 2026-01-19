import os
from datetime import datetime
from io import BytesIO

from flask import Flask, render_template, request, send_file, render_template_string
from markupsafe import Markup

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import numpy as np

import mpld3
from mpld3 import plugins

import plotly.figure_factory as ff
import plotly.graph_objects as go


# -----------------------
# CONFIG
# -----------------------
DATA_DIR = "data"
F_TXT = os.path.join(DATA_DIR, "occupation_parkings_et_velos.txt")

app = Flask(__name__, template_folder="templates")

# -----------------------
# CHARGEMENT DES DONNÉES
# -----------------------
def charger_depuis_fichier(fichier):

    evolution_places_parking = {}
    evolution_places_velo = {}
    evolution_totaux_parking = {}
    evolution_totaux_velo = {}

    temps_initial = None

    if not os.path.exists(fichier):
        return {}, {}, {}, {}, datetime.now().timestamp()

    with open(fichier, "r", encoding="utf-8") as f:
        for ligne in f:
            try:
                type_p, nom, date_str, dispo = [x.strip() for x in ligne.split("|")]

                dt = datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")
                timestamp = dt.timestamp()

                if temps_initial is None:
                    temps_initial = timestamp

                temps_ecoule = timestamp - temps_initial

                libres, total = dispo.split("/")
                libres = int(float(libres))
                total = int(float(total))

                if "voiture" in type_p.lower():
                    evolution_totaux_parking[nom] = total
                    evolution_places_parking.setdefault(nom, []).append((temps_ecoule, libres))

                elif "velo" in type_p.lower() or "vélo" in type_p.lower():
                    evolution_totaux_velo[nom] = total
                    evolution_places_velo.setdefault(nom, []).append((temps_ecoule, libres))

            except:
                continue

    if temps_initial is None:
        temps_initial = datetime.now().timestamp()

    return (evolution_places_parking,
            evolution_places_velo,
            evolution_totaux_parking,
            evolution_totaux_velo,
            temps_initial)


# -----------------------
# FONCTIONS DE TRACÉ
# -----------------------

def filtrer_par_duree(evo, duree):
    """Filtre les données selon la durée en secondes."""
    if duree is None:
        return evo

    evo_filtre = {}
    now = max(max(t for t, _ in data) for data in evo.values())

    for nom, data in evo.items():
        evo_filtre[nom] = [(t, v) for (t, v) in data if now - t <= duree]

    return evo_filtre


def tracer_courbes_par_lots(evolution_places, titre_base, temps_initial, selection=None):

    fig = plt.figure(figsize=(12, 8))

    noms = selection if selection else evolution_places.keys()

    for nom in noms:
        if nom not in evolution_places:
            continue
        data = evolution_places[nom]
        temps = [datetime.fromtimestamp(t[0] + temps_initial) for t in data]
        places = [t[1] for t in data]
        plt.plot(temps, places, label=nom)

    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M\n%d/%m'))
    plt.title(titre_base)
    plt.xlabel("Temps")
    plt.ylabel("Places disponibles")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(True)
    plt.tight_layout()

    return fig


def tracer_pourcentage_par_lots(evolution_places, evolution_totaux, titre_base, temps_initial, selection=None):

    fig = plt.figure(figsize=(12, 8))

    noms = selection if selection else evolution_places.keys()

    for nom in noms:
        if nom not in evolution_places:
            continue

        data = evolution_places[nom]
        total_places = evolution_totaux.get(nom, None)
        if not total_places or total_places == 0:
            continue

        temps = [datetime.fromtimestamp(t[0] + temps_initial) for t in data]
        libres = [t[1] for t in data]
        pourcentage = [(v / total_places) * 100 for v in libres]

        plt.plot(temps, pourcentage, label=nom)

    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M\n%d/%m'))
    plt.title(titre_base)
    plt.xlabel("Temps")
    plt.ylabel("Disponibilité (%)")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(True)
    plt.tight_layout()

    return fig


def tracer_moyennes_par_lots(evolution_places, evolution_totaux, titre_base, selection=None):

    fig = plt.figure(figsize=(12, 8))

    noms = selection if selection else evolution_places.keys()

    moyennes = []
    labels = []

    for nom in noms:
        if nom not in evolution_places:
            continue

        data = evolution_places[nom]
        total_places = evolution_totaux.get(nom, 0)
        if total_places == 0:
            continue

        libres = [t[1] for t in data]
        moyenne_libres = sum(libres) / len(libres)
        moyenne_prises = total_places - moyenne_libres

        moyennes.append(moyenne_prises)
        labels.append(nom)

    plt.bar(labels, moyennes)
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Moyenne places prises")
    plt.title(titre_base)
    plt.tight_layout()

    return fig


def tracer_moyennes_pourcentage_par_lots(evolution_places, evolution_totaux, titre_base, selection=None):

    fig = plt.figure(figsize=(12, 8))

    noms = selection if selection else evolution_places.keys()

    moyennes = []
    ecarts = []
    labels = []

    for nom in noms:
        if nom not in evolution_places:
            continue

        data = evolution_places[nom]
        total_places = evolution_totaux.get(nom, 0)
        if total_places == 0:
            continue

        libres = [t[1] for t in data]
        pourcentages = [(v / total_places) * 100 for v in libres]

        moyenne_pourcentage = sum(pourcentages) / len(pourcentages)
        ecart_type = np.std(pourcentages)

        moyennes.append(moyenne_pourcentage)
        ecarts.append(ecart_type)
        labels.append(nom)

    x = np.arange(len(labels))
    plt.bar(x, moyennes, yerr=ecarts, capsize=5)

    plt.xticks(x, labels, rotation=45, ha="right")
    plt.ylabel("Moyenne disponibilité (%)")
    plt.title(titre_base)
    plt.tight_layout()

    return fig


def tracer_moyenne_globale(evolution_places, evolution_totaux, titre_base, temps_initial):

    fig = plt.figure(figsize=(12, 6))

    if not evolution_places:
        plt.text(0.5, 0.5, "Aucune donnée", ha="center", va="center")
        plt.axis("off")
        return fig

    premier = next(iter(evolution_places))
    temps = [datetime.fromtimestamp(t[0] + temps_initial) for t in evolution_places[premier]]

    moyennes = []

    for i in range(len(temps)):
        valeurs = []
        for nom, data in evolution_places.items():
            if i >= len(data):
                continue
            libres = data[i][1]
            total = evolution_totaux.get(nom, 0)
            if total > 0:
                valeurs.append((libres / total) * 100)

        moyennes.append(sum(valeurs) / len(valeurs) if valeurs else 0)

    plt.plot(temps, moyennes, color="blue", linewidth=2)
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M\n%d/%m'))
    plt.title(titre_base)
    plt.xlabel("Temps")
    plt.ylabel("Disponibilité moyenne (%)")
    plt.grid(True)
    plt.tight_layout()

    return fig


# -----------------------
# HEATMAP
# -----------------------

def tracer_heatmap(evo_parking, evo_velo):

    fig = plt.figure(figsize=(12, 10))

    all_names = list(evo_parking.keys()) + list(evo_velo.keys())
    all_data = list(evo_parking.values()) + list(evo_velo.values())

    if len(all_data) < 2:
        plt.text(0.5, 0.5, "Pas assez de données", ha="center", va="center")
        plt.axis("off")
        return fig

    longueur = min(len(serie) for serie in all_data)
    matrix = np.zeros((longueur, len(all_data)))

    for j, serie in enumerate(all_data):
        matrix[:, j] = [point[1] for point in serie[:longueur]]

    corr = np.corrcoef(matrix.T)

    plt.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    plt.colorbar()

    plt.xticks(range(len(all_names)), all_names, rotation=45, ha="right")
    plt.yticks(range(len(all_names)), all_names)

    plt.title("Heatmap de corrélation (voitures + vélos)")
    plt.tight_layout()

    return fig


# -----------------------
# ROUTES FLASK
# -----------------------

@app.route("/")
def index():
    evo_parking, evo_velo, _, _, _ = charger_depuis_fichier(F_TXT)
    return render_template(
        "index.html",
        parkings=sorted(evo_parking.keys()),
        velos=sorted(evo_velo.keys()),
        models=[
            "courbes",
            "pourcentage",
            "moyennes",
            "moyennes_pourcentage",
            "moyenne_globale"
        ]
    )


@app.route("/graph")
def graph():

    type_ = request.args.get("type")
    model = request.args.get("model")
    selection = request.args.getlist("select")
    duree = request.args.get("duree")

    # Durées en secondes
    durees_map = {
        "12h": 43200,
        "1j": 86400,
        "2j": 172800,
        "7j": 604800,
        "14j": 1209600,
        "30j": 2592000,
        "tout": None
    }

    duree_sec = durees_map.get(duree, None)

    evo_parking, evo_velo, tot_parking, tot_velo, temps_initial = charger_depuis_fichier(F_TXT)

    if type_ == "parking":
        evo = evo_parking
        tot = tot_parking
    else:
        evo = evo_velo
        tot = tot_velo

    # Filtrage par durée
    evo = filtrer_par_duree(evo, duree_sec)

    # Si aucune case cochée → tout sélectionner
    if not selection:
        selection = list(evo.keys())

    # Sélection du modèle
    if model == "courbes":
        fig = tracer_courbes_par_lots(evo, "Courbes", temps_initial, selection)

    elif model == "pourcentage":
        fig = tracer_pourcentage_par_lots(evo, tot, "Pourcentage", temps_initial, selection)

    elif model == "moyennes":
        fig = tracer_moyennes_par_lots(evo, tot, "Moyennes", selection)

    elif model == "moyennes_pourcentage":
        fig = tracer_moyennes_pourcentage_par_lots(evo, tot, "Moyennes %", selection)

    elif model == "moyenne_globale":
        fig = tracer_moyenne_globale(evo, tot, "Moyenne globale", temps_initial)

    else:
        return "Modèle inconnu"

    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)

    return send_file(buf, mimetype="image/png")


@app.route("/heatmap")
def heatmap():

    evo_parking, evo_velo, _, _, _ = charger_depuis_fichier(F_TXT)

    all_names = list(evo_velo.keys()) + list(evo_parking.keys())
    all_data = list(evo_velo.values()) + list(evo_parking.values())

    if len(all_data) < 2:
        return "<h2>Pas assez de données</h2>"

    longueur = min(len(s) for s in all_data)
    matrix = np.array([
        [point[1] for point in serie[:longueur]]
        for serie in all_data
    ])

    corr = np.corrcoef(matrix)



    fig = go.Figure(data=go.Heatmap(
        z=corr,
        x=all_names,
        y=all_names,
        colorscale="RdBu_r",
        zmin=-1,
        zmax=1,
        showscale=True
    ))


    fig.update_layout(
        title="Heatmap de corrélation (voitures + vélos)",
        height=900,
        width=1100
    )

    return fig.to_html(full_html=False)



if __name__ == "__main__":
    app.run(port=3000, debug=True)
