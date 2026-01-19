import requests
import time
from datetime import datetime
import json

url_parking = "https://portail-api-data.montpellier3m.fr/offstreetparking?limit=1000"
url_velo = "https://portail-api-data.montpellier3m.fr/bikestation?limit=1000"

fichier_json = "occupation_parkings_et_velos.json"
fichier_texte = "occupation_parkings_et_velos.txt"


def recupere_data(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            print("Erreur HTTP :", r.status_code)
    except Exception as e:
        print("Erreur :", e)
    return None


def sauvegarder(parkings_data, velo_data):
    maintenant = datetime.now()
    date_actuelle = maintenant.strftime("%d/%m/%Y")
    heure_actuelle = maintenant.strftime("%H:%M:%S")

    # JSON
    with open(fichier_json, "w", encoding="utf-8") as fjson:
        json.dump(
            {"parkings": parkings_data, "velos": velo_data},
            fjson,
            indent=4,
            ensure_ascii=False
        )

    # TXT
    with open(fichier_texte, "a", encoding="utf-8") as ftxt:

        if parkings_data:
            for item in parkings_data:
                nom = item.get("name", {}).get("value", "Non spécifié")
                libres = int(float(item.get("availableSpotNumber", {}).get("value", 0)))
                total = item.get("totalSpotNumber", {}).get("value", 0)
                ftxt.write(f"Parking voiture | {nom} | {date_actuelle} {heure_actuelle} | {libres}/{total}\n")

        if velo_data:
            for item in velo_data:
                nom = item.get("address", {}).get("value", {}).get("streetAddress", "Non spécifié")
                libres = int(float(item.get("freeSlotNumber", {}).get("value", 0)))
                total = item.get("totalSlotNumber", {}).get("value", 0)
                ftxt.write(f"Parking vélo | {nom} | {date_actuelle} {heure_actuelle} | {libres}/{total}\n")


def acquisition(Te, duree_acquisition):
    print("Début acquisition...")
    temps_initial = time.time()

    while time.time() - temps_initial < duree_acquisition:

        parkings = recupere_data(url_parking)
        velos = recupere_data(url_velo)

        if parkings or velos:
            sauvegarder(parkings, velos)
            print("Données enregistrées :", datetime.now().strftime("%H:%M:%S"))
        else:
            print("Aucune donnée récupérée.")

        time.sleep(Te)

    print("Fin acquisition.")
    

if __name__ == "__main__":
    acquisition(1800, 604800) # 30 intervale et 7 jours total