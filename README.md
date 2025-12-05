# 🎵 Youtify

<div align="center">

<img src="Youtify.png" alt="Youtify Logo" width="200"/>

![Youtify Logo](https://img.shields.io/badge/Youtify-v1.0-1DB954?style=for-the-badge&logo=spotify&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

**Synchronisez vos playlists entre Spotify et YouTube Music en un clic !**

[🚀 Installation](#-installation) • [⚙️ Configuration](#️-configuration) • [📖 Utilisation](#-utilisation) • [🤝 Contribuer](#-contribuer)

</div>

---

## ✨ Fonctionnalités

- 🔄 **Synchronisation bidirectionnelle** - Les morceaux manquants sont ajoutés des deux côtés
- 🎯 **Détection intelligente** - Algorithme avancé pour éviter les doublons (même avec des titres légèrement différents)
- 🖥️ **Interface graphique moderne** - Simple et intuitive, pas besoin de ligne de commande
- 💾 **Sauvegarde de configuration** - Vos identifiants sont stockés localement
- 📊 **Journal en temps réel** - Suivez la progression de la synchronisation

## 📸 Aperçu

L'interface graphique vous permet de :

1. Configurer vos identifiants API une seule fois
2. Coller les liens de vos playlists
3. Cliquer sur "Synchroniser" et c'est parti !

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- Un compte Spotify Developer
- Un compte YouTube Music

### Étapes

1. **Clonez le repository**

```bash
git clone https://github.com/votre-nom/youtify.git
cd youtify
```

2. **Installez les dépendances**

```bash
pip install -r requirements.txt
```

3. **Lancez l'application**

```bash
python youtify.py
```

Ou double-cliquez sur `Youtify.bat` (Windows)

## ⚙️ Configuration

### 1. Spotify API

1. Allez sur [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Créez une nouvelle application
3. Notez le **Client ID** et **Client Secret**
4. Dans les paramètres de l'app, ajoutez `http://127.0.0.1:8888/callback` comme Redirect URI

### 2. YouTube Music API

1. Ouvrez [YouTube Music](https://music.youtube.com) dans votre navigateur (connecté à votre compte)
2. Ouvrez les outils de développement (F12)
3. Allez dans l'onglet **Network** (Réseau)
4. Jouez une chanson ou naviguez sur le site
5. Cherchez une requête vers `music.youtube.com`
6. Exécutez cette commande dans votre terminal :

```bash
ytmusicapi browser
```

7. Suivez les instructions pour créer le fichier `browser.json`

### 3. Dans Youtify

1. Lancez l'application
2. Entrez vos identifiants Spotify
3. Indiquez le chemin vers `browser.json`
4. Cliquez sur "Sauvegarder la configuration"

## 📖 Utilisation

1. **Lancez Youtify** (`python youtify.py` ou `Youtify.bat`)

2. **Entrez les liens de vos playlists :**

   - Spotify : `https://open.spotify.com/playlist/xxxxx`
   - YouTube Music : `https://music.youtube.com/playlist?list=xxxxx`

3. **Cliquez sur "Synchroniser"**

4. **Suivez la progression** dans le journal

L'algorithme compare intelligemment les titres pour :

- Ignorer les différences de casse (majuscules/minuscules)
- Ignorer les accents (é → e)
- Ignorer les suffixes (Remastered, Live, Radio Edit...)
- Détecter les titres similaires à 75%+

## 🛠️ Comment ça fonctionne

```
┌─────────────────────────────────────────────────────────┐
│                      YOUTIFY                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ┌──────────────┐          ┌──────────────┐           │
│   │   SPOTIFY    │◄────────►│ YOUTUBE MUSIC │           │
│   │   Playlist   │   Sync   │   Playlist    │           │
│   └──────────────┘          └──────────────┘           │
│          │                         │                    │
│          ▼                         ▼                    │
│   ┌──────────────────────────────────────────┐         │
│   │         Comparaison intelligente          │         │
│   │  • Normalisation des titres               │         │
│   │  • Algorithme de similarité Levenshtein   │         │
│   │  • Détection des doublons                 │         │
│   └──────────────────────────────────────────┘         │
│          │                         │                    │
│          ▼                         ▼                    │
│   ┌─────────────┐           ┌─────────────┐            │
│   │  Morceaux   │           │  Morceaux   │            │
│   │  manquants  │           │  manquants  │            │
│   │  sur YTM    │           │  sur Spotify│            │
│   └─────────────┘           └─────────────┘            │
│          │                         │                    │
│          ▼                         ▼                    │
│   ┌──────────────────────────────────────────┐         │
│   │          Ajout automatique                │         │
│   └──────────────────────────────────────────┘         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 📁 Structure du projet

```
youtify/
├── youtify.py          # Application principale avec GUI
├── browser.json        # Authentification YouTube (à créer)
├── .env                # Configuration (généré automatiquement)
├── requirements.txt    # Dépendances Python
├── Youtify.bat         # Lanceur Windows
├── LICENSE             # Licence MIT
└── README.md           # Ce fichier
```

## 🔧 Dépendances

| Package         | Version | Description                           |
| --------------- | ------- | ------------------------------------- |
| `customtkinter` | ≥5.0    | Interface graphique moderne           |
| `spotipy`       | ≥2.23   | API Spotify                           |
| `ytmusicapi`    | ≥1.11   | API YouTube Music                     |
| `python-dotenv` | ≥1.0    | Gestion des variables d'environnement |

## 🤝 Contribuer

Les contributions sont les bienvenues !

1. Forkez le projet
2. Créez votre branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Pushez (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Licence

Distribué sous licence MIT. Voir `LICENSE` pour plus d'informations.

## ⚠️ Avertissement

Ce projet n'est pas affilié à Spotify ou YouTube/Google. Utilisez-le de manière responsable et respectez les conditions d'utilisation des deux plateformes.

## 💖 Remerciements

- [spotipy](https://github.com/spotipy-dev/spotipy) - Wrapper Python pour l'API Spotify
- [ytmusicapi](https://github.com/sigma67/ytmusicapi) - API non-officielle YouTube Music
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Interface graphique moderne

---

<div align="center">

**⭐ Si ce projet vous a aidé, n'hésitez pas à lui donner une étoile !**

Made with ❤️

</div>
