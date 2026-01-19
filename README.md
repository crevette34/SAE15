# SAE15 — Analyse et visualisation des données de stationnement

Ce projet est une application web développée avec Flask permettant de visualiser les données d’occupation des parkings et des stations vélo.  
L’interface offre plusieurs outils d’analyse : sélection de capteurs, choix de modèles de graphiques, filtrage temporel et génération d’une heatmap.

## Fonctionnalités

- Choix du type de données : parkings ou stations vélo
- Sélection multiple avec boutons "Tout sélectionner" et "Tout désélectionner"
- Filtrage par période (12h, 1 jour, 2 jours, 7 jours, 14 jours, 30 jours, tout)
- Sélection du modèle de graphique
- Affichage dynamique des résultats dans une iframe
- Heatmap générée à partir des données brutes

## Structure du projet

├── app.py                                    # Application Flask principale
├── heatmap_popup.py        # Script de génération de la heatmap
├── requirement.txt                  # Liste des dépendances Python
├── data/
│   └── occupation_parkings_et_velos.txt
├── static/
│   └── site.css                        # Feuille de style de l’interface
├── templates/
│   └── index.html                    # Interface utilisateur

Code

## Installation

1. Cloner le dépôt :

```bash
git clone https://github.com/crevette34/SAE15.git
cd SAE15
Créer un environnement virtuel :

bash
python -m venv venv
Activer l’environnement virtuel :

Windows :

bash
venv\Scripts\activate
Installer les dépendances :

bash
pip install -r requirement.txt
Lancement de l’application
bash
python app.py
Puis ouvrir le navigateur à l’adresse :

Code
http://localhost:5000
Données utilisées
Le fichier occupation_parkings_et_velos.txt contient les données brutes issues des capteurs.
Les scripts Python se chargent de parser, filtrer et visualiser ces données selon les choix de l’utilisateur.


Projet réalisé par Remi Caravaca et Florent Reus
