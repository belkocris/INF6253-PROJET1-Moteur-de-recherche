# INF6253-WEB SEMANTIQUE - Projet1 - Moteur de recherche
Implémentation d'un moteur classique, un moteur RDFa enrichi et un moteur SPARQL basé sur un graphe RDF. L’objectif principal est d’illustrer l’évolution progressive des technologies du web 1.0 au web sémantique

# Projet Web Sémantique (Partie 1)
Université du Québec en Outaouais — Hiver 2026

## 🎯 Description du projet

Ce projet a été réalisé dans le cadre du cours **INF6253 – Web sémantique**.

Il vise à :

- extraire et transformer des données en graphes RDF ;
- enrichir les données via des règles et de l’inférence ;
- exécuter des requêtes **SPARQL** ;
- exposer le tout via une petite application web (Flask).

Le projet combine **Python**, **RDF/RDFS/OWL**, **SPARQL** et une interface web simple.

---

## 🗂️ Structure du projet

```text
INF6253-PROJET-P1/
│
├── database/                 # Données sources ou RDF générés
│
├── pages_html/               # Pages HTML originales
├── pages_html_enrichies/     # Pages HTML annotées / enrichies
│
├── sources/                  # Scripts Python d'extraction et d'enrichissement
│   ├── extract.py
│   ├── extract_enrichi.py
│   ├── extract_sparql.py
│
├── static/                   # Fichiers statiques pour l'application web
│   ├── script.js
│   ├── style.css
│
├── templates/                # Templates HTML (Flask)
│   ├── search.html
│
├── app.py                    # Application web (Flask)
│
└── README.md                 # Documentation du projet

```

## 🛠️ Technologies utilisées
 
- Python 3
- Flask
- RDF / RDFS / OWL
- SPARQL
- HTML / CSS / JavaScript
- (optionnel) BeautifulSoup ou équivalent pour l’extraction HTML


## ▶️ Installation et exécution
1. Cloner le dépôt

git clone https://github.com/belkocris/INF6253-PROJET-P1.git
cd INF6253-PROJET-P1

2. Créer et activer un environnement virtuel
python -m venv .venv

## macOS / Linux
source .venv/bin/activate

## Windows
.venv\Scripts\activate

Puis ouvrir dans un navigateur :
http://localhost:5000

## 🔍 Fonctionnalités principales
- Extraction de données à partir de pages HTML (pages_html/) ;
- Génération de versions enrichies (pages_html_enrichies/) ;
- Construction de graphes RDF et exécution de requêtes SPARQL (extract_sparql.py) ;
- Interface web de recherche et d’affichage (app.py, templates/search.html, static/).

## 👨‍🎓 Auteur
### Christian Belibi Kouoh  
DESS en Data Science et Intelligence Artificielle
Université du Québec en Outaouais (UQO)
