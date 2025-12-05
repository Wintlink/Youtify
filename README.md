# 🎵 Youtify

<div align="center">

<img src="Youtify.png" alt="Youtify Logo" width="200"/>

![Youtify](https://img.shields.io/badge/Youtify-v1.0-1DB954?style=for-the-badge&logo=spotify&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)

**Sync your playlists between Spotify and YouTube Music with one click!**

[🚀 Installation](#-installation) • [⚙️ Configuration](#️-configuration) • [📖 Usage](#-usage) • [🤝 Contributing](#-contributing)

</div>

---

## ✨ Features

- 🔄 **Bidirectional sync** - Missing tracks are added on both sides
- 🎯 **Smart detection** - Advanced algorithm to avoid duplicates (even with slightly different titles)
- 🖥️ **Modern GUI** - Simple and intuitive, no command line needed
- 💾 **Config saving** - Your credentials are stored locally
- 📊 **Real-time logging** - Track the sync progress live

## 📸 Overview

The graphical interface allows you to:

1. Configure your API credentials once
2. Paste your playlist links
3. Click "Synchronize" and you're done!

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- A Spotify Developer account
- A YouTube Music account

### Steps

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/youtify.git
cd youtify
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Launch the application**

```bash
python youtify.py
```

Or double-click on `Youtify.bat` (Windows)

## ⚙️ Configuration

### 1. Spotify API

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application
3. Note the **Client ID** and **Client Secret**
4. In the app settings, add `http://127.0.0.1:8888/callback` as Redirect URI

### 2. YouTube Music API

1. Open [YouTube Music](https://music.youtube.com) in your browser (logged in to your account)
2. Open developer tools (F12)
3. Go to the **Network** tab
4. Play a song or navigate on the site
5. Look for a request to `music.youtube.com`
6. Run this command in your terminal:

```bash
ytmusicapi browser
```

7. Follow the instructions to create the `browser.json` file

### 3. In Youtify

1. Launch the application
2. Enter your Spotify credentials
3. Specify the path to `browser.json`
4. Click "Save configuration"

## 📖 Usage

1. **Launch Youtify** (`python youtify.py` or `Youtify.bat`)

2. **Enter your playlist links:**

   - Spotify: `https://open.spotify.com/playlist/xxxxx`
   - YouTube Music: `https://music.youtube.com/playlist?list=xxxxx`

3. **Click "Load playlists"** to see the comparison

4. **Click "Synchronize"** to sync both playlists

5. **Track the progress** in the log panel

The algorithm intelligently compares titles to:

- Ignore case differences (uppercase/lowercase)
- Ignore accents (é → e)
- Ignore suffixes (Remastered, Live, Radio Edit...)
- Detect similar titles at 75%+ match

## 🛠️ How it works

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
│   │         Smart comparison                  │         │
│   │  • Title normalization                    │         │
│   │  • Levenshtein similarity algorithm       │         │
│   │  • Duplicate detection                    │         │
│   └──────────────────────────────────────────┘         │
│          │                         │                    │
│          ▼                         ▼                    │
│   ┌─────────────┐           ┌─────────────┐            │
│   │   Missing   │           │   Missing   │            │
│   │   tracks    │           │   tracks    │            │
│   │   on YTM    │           │  on Spotify │            │
│   └─────────────┘           └─────────────┘            │
│          │                         │                    │
│          ▼                         ▼                    │
│   ┌──────────────────────────────────────────┐         │
│   │          Automatic addition               │         │
│   └──────────────────────────────────────────┘         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 📁 Project structure

```
youtify/
├── youtify.py          # Main application with GUI
├── browser.json        # YouTube authentication (to create)
├── .env                # Configuration (auto-generated)
├── requirements.txt    # Python dependencies
├── Youtify.bat         # Windows launcher
├── Youtify.png         # Logo
└── README.md           # This file
```

## 🔧 Dependencies

| Package         | Version | Description                    |
| --------------- | ------- | ------------------------------ |
| `customtkinter` | ≥5.0    | Modern GUI framework           |
| `spotipy`       | ≥2.23   | Spotify API wrapper            |
| `ytmusicapi`    | ≥1.11   | YouTube Music API              |
| `python-dotenv` | ≥1.0    | Environment variables handling |

## 🤝 Contributing

Contributions are welcome!

1. Fork the project
2. Create your branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚠️ Disclaimer

This project is not affiliated with Spotify or YouTube/Google. Use it responsibly and respect the terms of service of both platforms.

## 💖 Acknowledgments

- [spotipy](https://github.com/spotipy-dev/spotipy) - Python wrapper for Spotify API
- [ytmusicapi](https://github.com/sigma67/ytmusicapi) - Unofficial YouTube Music API
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern GUI framework

---

<div align="center">

**⭐ If this project helped you, feel free to give it a star!**

</div>
