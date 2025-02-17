# TinyCompagnon

TinyCompagnon est un assistant numérique. Il offre plusieurs fonctionnalités utiles dans une interface élégante et intuitive.

## Fonctionnalités

### 🕒 Horloge
- Affichage de l'heure en temps réel
- Format 24h
- Design minimaliste et élégant

### 🎵 Spotify
- Affichage de la musique en cours de lecture
- Pochette d'album
- Titre et artiste
- Barre de progression
- Nécessite un compte Spotify Premium

### ⛅ Météo
- Température actuelle
- Températures min/max
- Conditions météorologiques avec icônes
- Mise à jour automatique toutes les 30 minutes
- Données fournies par Meteoblue

### 📰 Actualités
- Dernières actualités en français
- Défilement automatique des articles toutes les 10 secondes
- Mise à jour automatique toutes les 10 minutes
- Données fournies par NewsAPI

### 🖼️ Photos
- Affichage de photos personnelles
- Upload via l'interface web

## Guide d'Installation

### Prérequis
- Raspberry Pi (testé sur Raspberry Pi 4)
- Écran tactile officiel Raspberry Pi
- Python 3.7+
- pip (gestionnaire de paquets Python)

### Installation

1. Cloner le repository :
`git clone https://github.com/devleoniiiid/TinyCompagnon.git`
`cd TinyCompagnon`


2. Créer et activer l'environnement virtuel :
# Sur Linux/Mac
`python3 -m venv venv`
`source venv/bin/activate`


# Sur Windows
`python -m venv venv`
`.\venv\Scripts\activate`


3. Installer les dépendances :
`pip install -r requirements.txt`


4. Configurer les APIs :
   - Créer un compte développeur sur [Spotify](https://developer.spotify.com/)
   - Obtenir une clé API sur [Meteoblue](https://www.meteoblue.com/en/weather-api)
   - Obtenir une clé API sur [NewsAPI](https://newsapi.org/)
   - Créer un projet sur [Google Cloud Console](https://console.cloud.google.com/) pour YouTube
   - Configurer l'[Instagram Basic Display API](https://developers.facebook.com/docs/instagram-basic-display-api/)

5. Configurer le fichier config.json avec toutes les clées API


6. Lancer l'application :
`python main.py`

7. Accéder à l'interface web de contrôle :
   - Ouvrir un navigateur
   - Aller sur `http://adresse-ip-dans-la-console:XXXX`

## Structure des Dossiers
TinyCompagnon/
├── main.py
├── config.json
├── requirements.txt
├── static/
│ ├── css/
│ ├── images/
│ │ └── Weather Icons/
│ └── js/
├── templates/
│ └── index.html
└── uploaded_photos/


## Dépendances Principales
- Flask
- Requests
- Pillow
- Spotipy
- Tkinter
- google-api-python-client
- python-dotenv

## Limites des APIs Gratuites
- NewsAPI : 100 requêtes par jour
- Meteoblue : Limite selon le plan

## Contribution
Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à proposer une pull request.

## Licence
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.