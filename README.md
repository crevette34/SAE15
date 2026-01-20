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
```
Utilisation des données
Avant de lancer l’application Flask, il est nécessaire de générer le fichier occupation_parkings_et_velos.txt utilisé pour l’affichage des graphiques.
Pour cela, il faut exécuter le script generateur_occupation.py, qui interroge régulièrement les API de Montpellier Méditerranée Métropole et enregistre les données dans deux fichiers :
```bash
occupation_parkings_et_velos.txt (format texte utilisé par l’application Flask)

occupation_parkings_et_velos.json (version structurée des données brutes)

Le script permet de définir :

la période d’échantillonnage (intervalle entre deux acquisitions, en secondes)

la durée totale d’acquisition (en secondes)

Exemple d’utilisation :

python
# acquisition toutes les 30 minutes pendant 7 jours
acquisition(1800, 604800)
Une fois la période d’échantillonnage et la durée d’acquisition réglées, lancer le script :

bash
python generateur_occupation.py
À la fin de l’acquisition, les fichiers générés seront disponibles dans le dossier du projet et pourront être utilisés directement par l’application Flask pour l’analyse et la visualisation.
```
Projet réalisé par Remi Caravaca et Florent Reus


