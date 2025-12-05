"""
Youtify - Synchronisation bidirectionnelle Spotify <-> YouTube Music
Interface graphique moderne avec CustomTkinter
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
import os
import re
import unicodedata
from dotenv import load_dotenv, set_key
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from ytmusicapi import YTMusic

# Configuration du thème
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# Constantes
ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")
SIMILARITY_THRESHOLD = 0.75

# Couleurs personnalisées
SPOTIFY_GREEN = "#1DB954"
SPOTIFY_GREEN_HOVER = "#1ed760"
YOUTUBE_RED = "#FF0000"
YOUTUBE_RED_DARK = "#CC0000"
DARK_BG = "#1a1a2e"
CARD_BG = "#16213e"
CARD_BG_LIGHT = "#1f3460"
ACCENT_BLUE = "#4361ee"


class YoutifyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuration de la fenêtre
        self.title("🎵 Youtify")
        self.geometry("1100x800")
        self.configure(fg_color=DARK_BG)
        self.resizable(True, True)
        self.minsize(900, 700)
        
        # Variables
        self.spotify_client = None
        self.youtube_client = None
        self.is_syncing = False
        self.spotify_tracks = []
        self.youtube_tracks = []
        
        # Charger les variables d'environnement existantes
        load_dotenv(ENV_FILE)
        
        # Créer l'interface
        self.create_widgets()
        self.load_saved_config()
    
    def create_widgets(self):
        """Crée tous les widgets de l'interface."""
        
        # === HEADER ===
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=80)
        header_frame.pack(fill="x", padx=30, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        # Logo et titre
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.pack(side="left")
        
        title_label = ctk.CTkLabel(
            title_container, 
            text="🎵 Youtify",
            font=ctk.CTkFont(family="Segoe UI", size=42, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(side="left")
        
        subtitle_label = ctk.CTkLabel(
            title_container,
            text="  Sync your music everywhere",
            font=ctk.CTkFont(size=16),
            text_color="#888888"
        )
        subtitle_label.pack(side="left", padx=(10, 0), pady=(12, 0))
        
        # Bouton config
        self.config_btn = ctk.CTkButton(
            header_frame,
            text="⚙️ Configuration",
            command=self.toggle_config,
            width=140,
            height=35,
            fg_color=CARD_BG,
            hover_color=CARD_BG_LIGHT,
            corner_radius=8
        )
        self.config_btn.pack(side="right")
        
        # === CONFIG PANEL (caché par défaut) ===
        self.config_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=15)
        self.config_visible = False
        
        config_inner = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        config_inner.pack(fill="x", padx=20, pady=15)
        
        # Titre config
        ctk.CTkLabel(
            config_inner,
            text="🔐 Configuration API",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(0, 15))
        
        # Grid pour les entrées
        entries_frame = ctk.CTkFrame(config_inner, fg_color="transparent")
        entries_frame.pack(fill="x")
        
        # Spotify
        spotify_config = ctk.CTkFrame(entries_frame, fg_color=CARD_BG_LIGHT, corner_radius=10)
        spotify_config.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(spotify_config, text="🟢 Spotify", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.spotify_id_entry = ctk.CTkEntry(spotify_config, placeholder_text="Client ID", height=35)
        self.spotify_id_entry.pack(fill="x", padx=15, pady=5)
        
        self.spotify_secret_entry = ctk.CTkEntry(spotify_config, placeholder_text="Client Secret", show="•", height=35)
        self.spotify_secret_entry.pack(fill="x", padx=15, pady=(5, 15))
        
        # YouTube
        youtube_config = ctk.CTkFrame(entries_frame, fg_color=CARD_BG_LIGHT, corner_radius=10)
        youtube_config.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(youtube_config, text="🔴 YouTube Music", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.youtube_auth_entry = ctk.CTkEntry(youtube_config, placeholder_text="Chemin vers browser.json", height=35)
        self.youtube_auth_entry.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(youtube_config, text="", height=35).pack(fill="x", padx=15, pady=(5, 15))  # Spacer
        
        # Bouton sauvegarder
        ctk.CTkButton(
            config_inner,
            text="💾 Sauvegarder",
            command=self.save_config,
            width=150,
            height=35,
            fg_color=ACCENT_BLUE,
            hover_color="#5a73f0"
        ).pack(pady=(15, 0))
        
        # === MAIN CONTENT ===
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        # === PLAYLIST INPUTS ===
        input_frame = ctk.CTkFrame(main_frame, fg_color=CARD_BG, corner_radius=15, height=120)
        input_frame.pack(fill="x", pady=(0, 15))
        input_frame.pack_propagate(False)
        
        input_inner = ctk.CTkFrame(input_frame, fg_color="transparent")
        input_inner.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Spotify input
        spotify_input_frame = ctk.CTkFrame(input_inner, fg_color="transparent")
        spotify_input_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        spotify_label_frame = ctk.CTkFrame(spotify_input_frame, fg_color="transparent")
        spotify_label_frame.pack(fill="x")
        ctk.CTkLabel(spotify_label_frame, text="🟢", font=ctk.CTkFont(size=24)).pack(side="left")
        ctk.CTkLabel(spotify_label_frame, text=" Playlist Spotify", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        self.spotify_playlist_entry = ctk.CTkEntry(
            spotify_input_frame,
            placeholder_text="https://open.spotify.com/playlist/...",
            height=45,
            corner_radius=10,
            border_color=SPOTIFY_GREEN,
            border_width=2
        )
        self.spotify_playlist_entry.pack(fill="x", pady=(10, 0))
        
        # Séparateur
        sep_frame = ctk.CTkFrame(input_inner, fg_color="transparent", width=60)
        sep_frame.pack(side="left")
        sep_frame.pack_propagate(False)
        
        ctk.CTkLabel(sep_frame, text="⟷", font=ctk.CTkFont(size=30), text_color="#666").pack(expand=True)
        
        # YouTube input
        youtube_input_frame = ctk.CTkFrame(input_inner, fg_color="transparent")
        youtube_input_frame.pack(side="left", fill="both", expand=True, padx=(15, 0))
        
        youtube_label_frame = ctk.CTkFrame(youtube_input_frame, fg_color="transparent")
        youtube_label_frame.pack(fill="x")
        ctk.CTkLabel(youtube_label_frame, text="🔴", font=ctk.CTkFont(size=24)).pack(side="left")
        ctk.CTkLabel(youtube_label_frame, text=" Playlist YouTube Music", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        self.youtube_playlist_entry = ctk.CTkEntry(
            youtube_input_frame,
            placeholder_text="https://music.youtube.com/playlist?list=...",
            height=45,
            corner_radius=10,
            border_color=YOUTUBE_RED,
            border_width=2
        )
        self.youtube_playlist_entry.pack(fill="x", pady=(10, 0))
        
        # === PLAYLISTS COMPARISON ===
        comparison_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        comparison_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Spotify tracks panel
        spotify_panel = ctk.CTkFrame(comparison_frame, fg_color=CARD_BG, corner_radius=15)
        spotify_panel.pack(side="left", fill="both", expand=True, padx=(0, 8))
        
        spotify_header = ctk.CTkFrame(spotify_panel, fg_color=SPOTIFY_GREEN, corner_radius=10, height=50)
        spotify_header.pack(fill="x", padx=10, pady=10)
        spotify_header.pack_propagate(False)
        
        self.spotify_header_label = ctk.CTkLabel(
            spotify_header,
            text="🟢 SPOTIFY • 0 morceaux",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#000000"
        )
        self.spotify_header_label.pack(expand=True)
        
        self.spotify_list = ctk.CTkTextbox(
            spotify_panel,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=CARD_BG_LIGHT,
            corner_radius=10
        )
        self.spotify_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.spotify_list.insert("1.0", "Entrez un lien de playlist Spotify\net cliquez sur Charger...")
        self.spotify_list.configure(state="disabled")
        
        # YouTube tracks panel
        youtube_panel = ctk.CTkFrame(comparison_frame, fg_color=CARD_BG, corner_radius=15)
        youtube_panel.pack(side="left", fill="both", expand=True, padx=(8, 0))
        
        youtube_header = ctk.CTkFrame(youtube_panel, fg_color=YOUTUBE_RED, corner_radius=10, height=50)
        youtube_header.pack(fill="x", padx=10, pady=10)
        youtube_header.pack_propagate(False)
        
        self.youtube_header_label = ctk.CTkLabel(
            youtube_header,
            text="🔴 YOUTUBE MUSIC • 0 morceaux",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        )
        self.youtube_header_label.pack(expand=True)
        
        self.youtube_list = ctk.CTkTextbox(
            youtube_panel,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=CARD_BG_LIGHT,
            corner_radius=10
        )
        self.youtube_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.youtube_list.insert("1.0", "Entrez un lien de playlist YouTube\net cliquez sur Charger...")
        self.youtube_list.configure(state="disabled")
        
        # === ACTION BUTTONS ===
        action_frame = ctk.CTkFrame(main_frame, fg_color=CARD_BG, corner_radius=15, height=80)
        action_frame.pack(fill="x", pady=(0, 10))
        action_frame.pack_propagate(False)
        
        action_inner = ctk.CTkFrame(action_frame, fg_color="transparent")
        action_inner.pack(expand=True)
        
        # Bouton charger
        self.load_btn = ctk.CTkButton(
            action_inner,
            text="📥 Charger les playlists",
            command=self.load_playlists,
            width=200,
            height=50,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=ACCENT_BLUE,
            hover_color="#5a73f0",
            corner_radius=10
        )
        self.load_btn.pack(side="left", padx=10)
        
        # Bouton sync
        self.sync_button = ctk.CTkButton(
            action_inner,
            text="🔄 Synchroniser",
            command=self.start_sync,
            width=200,
            height=50,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=SPOTIFY_GREEN,
            hover_color=SPOTIFY_GREEN_HOVER,
            corner_radius=10
        )
        self.sync_button.pack(side="left", padx=10)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(action_inner, width=200, height=15, corner_radius=5)
        self.progress_bar.pack(side="left", padx=20)
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            action_inner,
            text="Prêt",
            font=ctk.CTkFont(size=13),
            text_color="#888888"
        )
        self.status_label.pack(side="left", padx=10)
        
        # === LOG PANEL ===
        log_frame = ctk.CTkFrame(main_frame, fg_color=CARD_BG, corner_radius=15, height=120)
        log_frame.pack(fill="x")
        log_frame.pack_propagate(False)
        
        log_header = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_header.pack(fill="x", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(log_header, text="📋 Journal des opérations", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
        
        ctk.CTkButton(
            log_header,
            text="Effacer",
            command=self.clear_log,
            width=60,
            height=25,
            fg_color=CARD_BG_LIGHT,
            hover_color="#2a4a7a",
            font=ctk.CTkFont(size=11)
        ).pack(side="right")
        
        self.log_textbox = ctk.CTkTextbox(
            log_frame,
            height=70,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=CARD_BG_LIGHT,
            corner_radius=8
        )
        self.log_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 10))
    
    def toggle_config(self):
        """Affiche/cache le panneau de configuration."""
        if self.config_visible:
            self.config_frame.pack_forget()
            self.config_visible = False
            self.config_btn.configure(text="⚙️ Configuration")
        else:
            self.config_frame.pack(fill="x", padx=30, pady=(0, 10), after=self.winfo_children()[0])
            self.config_visible = True
            self.config_btn.configure(text="✕ Fermer")
    
    def clear_log(self):
        """Efface le journal."""
        self.log_textbox.delete("1.0", "end")
    
    def log(self, message):
        """Ajoute un message au journal."""
        self.log_textbox.insert("end", f"{message}\n")
        self.log_textbox.see("end")
        self.update()
    
    def update_status(self, text, color="#888888"):
        """Met à jour le label de statut."""
        self.status_label.configure(text=text, text_color=color)
        self.update()
    
    def load_saved_config(self):
        """Charge la configuration sauvegardée."""
        self.spotify_id_entry.insert(0, os.getenv("SPOTIFY_CLIENT_ID", ""))
        self.spotify_secret_entry.insert(0, os.getenv("SPOTIFY_CLIENT_SECRET", ""))
        self.youtube_auth_entry.insert(0, os.getenv("YOUTUBE_AUTH_FILE", "browser.json"))
    
    def save_config(self):
        """Sauvegarde la configuration dans le fichier .env."""
        try:
            if not os.path.exists(ENV_FILE):
                with open(ENV_FILE, "w") as f:
                    f.write("")
            
            set_key(ENV_FILE, "SPOTIFY_CLIENT_ID", self.spotify_id_entry.get())
            set_key(ENV_FILE, "SPOTIFY_CLIENT_SECRET", self.spotify_secret_entry.get())
            set_key(ENV_FILE, "YOUTUBE_AUTH_FILE", self.youtube_auth_entry.get())
            
            self.log("✅ Configuration sauvegardée")
            self.update_status("Configuration sauvegardée", SPOTIFY_GREEN)
        except Exception as e:
            self.log(f"❌ Erreur: {e}")
            messagebox.showerror("Erreur", f"Impossible de sauvegarder: {e}")
    
    def extract_spotify_id(self, url):
        if "spotify.com" in url:
            match = re.search(r'playlist/([a-zA-Z0-9]+)', url)
            if match:
                return match.group(1)
        return url.split("?")[0]
    
    def extract_youtube_id(self, url):
        if "youtube.com" in url or "music.youtube.com" in url:
            match = re.search(r'list=([a-zA-Z0-9_-]+)', url)
            if match:
                return match.group(1)
        return url.split("?")[0].split("&")[0]
    
    def normalize_string(self, s):
        if not s:
            return ""
        s = s.lower().strip()
        s = unicodedata.normalize('NFKD', s)
        s = ''.join(c for c in s if not unicodedata.combining(c))
        patterns = [
            r'\s*-\s*remaster(ed)?\s*\d*', r'\s*\(remaster(ed)?\s*\d*\)',
            r'\s*-\s*live.*$', r'\s*\(live.*?\)', r'\s*-\s*radio edit',
            r'\s*\(feat\..*?\)', r'\s*\(ft\..*?\)', r'\s*feat\..*$', r'\s*ft\..*$'
        ]
        for pattern in patterns:
            s = re.sub(pattern, '', s, flags=re.IGNORECASE)
        s = re.sub(r'[^\w\s]', '', s)
        s = re.sub(r'\s+', ' ', s)
        return s.strip()
    
    def normalize_artist(self, artist):
        if not artist:
            return ""
        artist = self.normalize_string(artist)
        for sep in [' & ', ' and ', ' x ', ' vs ', ', ']:
            if sep in artist:
                artist = artist.split(sep)[0]
                break
        return artist.strip()
    
    def levenshtein_ratio(self, s1, s2):
        if not s1 or not s2:
            return 0.0
        if s1 == s2:
            return 1.0
        len1, len2 = len(s1), len(s2)
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if s1[i-1] == s2[j-1] else 1
                matrix[i][j] = min(matrix[i-1][j] + 1, matrix[i][j-1] + 1, matrix[i-1][j-1] + cost)
        return 1.0 - (matrix[len1][len2] / max(len1, len2))
    
    def tracks_match(self, track1, track2):
        name1, name2 = self.normalize_string(track1['name']), self.normalize_string(track2['name'])
        artist1, artist2 = self.normalize_artist(track1['artist']), self.normalize_artist(track2['artist'])
        if name1 == name2 and artist1 == artist2:
            return True
        name_ratio = self.levenshtein_ratio(name1, name2)
        artist_ratio = self.levenshtein_ratio(artist1, artist2)
        if name_ratio >= SIMILARITY_THRESHOLD and artist_ratio >= 0.6:
            return True
        if len(name1) >= 3 and len(name2) >= 3:
            if (name1 in name2 or name2 in name1) and artist_ratio >= 0.5:
                return True
        return False
    
    def get_spotify_tracks(self, playlist_url):
        playlist_id = self.extract_spotify_id(playlist_url)
        tracks = []
        offset = 0
        while True:
            results = self.spotify_client.playlist_tracks(playlist_id, offset=offset, limit=100)
            items = results.get('items', [])
            if not items:
                break
            for item in items:
                track = item.get('track')
                if track and track.get('name'):
                    tracks.append({
                        "name": track['name'],
                        "artist": track['artists'][0]['name'] if track.get('artists') else "Unknown",
                    })
            if not results.get('next'):
                break
            offset += 100
        return tracks
    
    def get_youtube_tracks(self, playlist_id):
        playlist = self.youtube_client.get_playlist(playlist_id, limit=None)
        tracks = []
        for track in playlist.get('tracks', []):
            if track and track.get('title'):
                tracks.append({
                    "name": track['title'],
                    "artist": track['artists'][0]['name'] if track.get('artists') else "Unknown",
                })
        return tracks
    
    def find_missing_tracks(self, source, target):
        missing = []
        for s_track in source:
            found = any(self.tracks_match(s_track, t_track) for t_track in target)
            if not found:
                missing.append(s_track)
        return missing
    
    def update_track_list(self, textbox, tracks, header_label, platform, missing=None):
        """Met à jour la liste des morceaux avec coloration."""
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        
        missing_names = set()
        if missing:
            missing_names = {(t['name'], t['artist']) for t in missing}
        
        for i, track in enumerate(tracks, 1):
            is_missing = (track['name'], track['artist']) in missing_names
            prefix = "⚡ " if is_missing else "   "
            line = f"{prefix}{i:3}. {track['name'][:40]:<40} • {track['artist'][:25]}\n"
            textbox.insert("end", line)
        
        textbox.configure(state="disabled")
        
        # Update header
        count = len(tracks)
        missing_count = len(missing) if missing else 0
        if platform == "spotify":
            text = f"🟢 SPOTIFY • {count} morceaux"
            if missing_count > 0:
                text += f" (+{missing_count} à ajouter)"
            header_label.configure(text=text)
        else:
            text = f"🔴 YOUTUBE MUSIC • {count} morceaux"
            if missing_count > 0:
                text += f" (+{missing_count} à ajouter)"
            header_label.configure(text=text)
    
    def load_playlists(self):
        """Charge les playlists sans synchroniser."""
        if not self.spotify_id_entry.get() or not self.spotify_secret_entry.get():
            messagebox.showerror("Erreur", "Configurez vos identifiants Spotify d'abord !")
            self.toggle_config()
            return
        
        if not self.spotify_playlist_entry.get() or not self.youtube_playlist_entry.get():
            messagebox.showerror("Erreur", "Entrez les liens des deux playlists !")
            return
        
        self.load_btn.configure(state="disabled", text="⏳ Chargement...")
        thread = threading.Thread(target=self._load_playlists_thread, daemon=True)
        thread.start()
    
    def _load_playlists_thread(self):
        try:
            self.update_status("Connexion à Spotify...", ACCENT_BLUE)
            self.progress_bar.set(0.1)
            
            self.spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=self.spotify_id_entry.get(),
                client_secret=self.spotify_secret_entry.get(),
                redirect_uri="http://127.0.0.1:8888/callback",
                scope="playlist-read-private playlist-modify-public playlist-modify-private"
            ))
            self.log("✅ Spotify connecté")
            
            self.update_status("Connexion à YouTube Music...", ACCENT_BLUE)
            self.progress_bar.set(0.2)
            
            auth_file = self.youtube_auth_entry.get()
            if not os.path.isabs(auth_file):
                auth_file = os.path.join(os.path.dirname(__file__), auth_file)
            self.youtube_client = YTMusic(auth_file)
            self.log("✅ YouTube Music connecté")
            
            self.update_status("Chargement Spotify...", SPOTIFY_GREEN)
            self.progress_bar.set(0.4)
            
            self.spotify_tracks = self.get_spotify_tracks(self.spotify_playlist_entry.get())
            self.log(f"📗 Spotify: {len(self.spotify_tracks)} morceaux")
            
            self.update_status("Chargement YouTube...", YOUTUBE_RED)
            self.progress_bar.set(0.6)
            
            youtube_id = self.extract_youtube_id(self.youtube_playlist_entry.get())
            self.youtube_tracks = self.get_youtube_tracks(youtube_id)
            self.log(f"📕 YouTube: {len(self.youtube_tracks)} morceaux")
            
            self.update_status("Analyse des différences...", ACCENT_BLUE)
            self.progress_bar.set(0.8)
            
            missing_on_youtube = self.find_missing_tracks(self.spotify_tracks, self.youtube_tracks)
            missing_on_spotify = self.find_missing_tracks(self.youtube_tracks, self.spotify_tracks)
            
            self.log(f"🔄 {len(missing_on_youtube)} → YouTube | {len(missing_on_spotify)} → Spotify")
            
            # Mise à jour des listes
            self.update_track_list(self.spotify_list, self.spotify_tracks, self.spotify_header_label, "spotify", missing_on_spotify)
            self.update_track_list(self.youtube_list, self.youtube_tracks, self.youtube_header_label, "youtube", missing_on_youtube)
            
            self.progress_bar.set(1.0)
            
            if not missing_on_youtube and not missing_on_spotify:
                self.update_status("✨ Playlists synchronisées !", SPOTIFY_GREEN)
            else:
                self.update_status(f"Prêt à synchroniser ({len(missing_on_youtube) + len(missing_on_spotify)} morceaux)", SPOTIFY_GREEN)
            
        except Exception as e:
            self.log(f"❌ Erreur: {e}")
            self.update_status("Erreur", YOUTUBE_RED)
            messagebox.showerror("Erreur", str(e))
        finally:
            self.load_btn.configure(state="normal", text="📥 Charger les playlists")
    
    def start_sync(self):
        if self.is_syncing:
            return
        
        if not self.spotify_tracks or not self.youtube_tracks:
            messagebox.showinfo("Info", "Chargez d'abord les playlists !")
            return
        
        self.is_syncing = True
        self.sync_button.configure(state="disabled", text="⏳ Synchronisation...")
        thread = threading.Thread(target=self._sync_thread, daemon=True)
        thread.start()
    
    def _sync_thread(self):
        try:
            youtube_id = self.extract_youtube_id(self.youtube_playlist_entry.get())
            spotify_id = self.extract_spotify_id(self.spotify_playlist_entry.get())
            
            missing_on_youtube = self.find_missing_tracks(self.spotify_tracks, self.youtube_tracks)
            missing_on_spotify = self.find_missing_tracks(self.youtube_tracks, self.spotify_tracks)
            
            total = len(missing_on_youtube) + len(missing_on_spotify)
            if total == 0:
                self.update_status("✨ Déjà synchronisé !", SPOTIFY_GREEN)
                return
            
            done = 0
            
            # Sync vers YouTube
            if missing_on_youtube:
                self.log(f"\n➡️ Ajout de {len(missing_on_youtube)} morceaux sur YouTube...")
                for track in missing_on_youtube:
                    try:
                        query = f"{track['name']} {track['artist']}"
                        results = self.youtube_client.search(query, filter="songs", limit=1)
                        if results:
                            self.youtube_client.add_playlist_items(youtube_id, [results[0]['videoId']])
                            self.log(f"   ✅ {track['name'][:35]} - {track['artist'][:20]}")
                        else:
                            self.log(f"   ⚠️ Non trouvé: {track['name'][:35]}")
                    except Exception as e:
                        self.log(f"   ❌ {track['name'][:35]}")
                    done += 1
                    self.progress_bar.set(done / total)
                    self.update_status(f"YouTube: {done}/{total}", YOUTUBE_RED)
            
            # Sync vers Spotify
            if missing_on_spotify:
                self.log(f"\n➡️ Ajout de {len(missing_on_spotify)} morceaux sur Spotify...")
                track_ids = []
                for track in missing_on_spotify:
                    try:
                        query = f"{track['name']} {track['artist']}"
                        result = self.spotify_client.search(q=query, type='track', limit=1)
                        if result['tracks']['items']:
                            track_ids.append(result['tracks']['items'][0]['id'])
                            self.log(f"   ✅ {track['name'][:35]} - {track['artist'][:20]}")
                        else:
                            self.log(f"   ⚠️ Non trouvé: {track['name'][:35]}")
                    except:
                        self.log(f"   ❌ {track['name'][:35]}")
                    done += 1
                    self.progress_bar.set(done / total)
                    self.update_status(f"Spotify: {done}/{total}", SPOTIFY_GREEN)
                
                if track_ids:
                    # Spotify limite à 100 tracks par requête
                    for i in range(0, len(track_ids), 100):
                        self.spotify_client.playlist_add_items(spotify_id, track_ids[i:i+100])
            
            self.progress_bar.set(1.0)
            self.log("\n" + "=" * 50)
            self.log("✨ Synchronisation terminée !")
            self.update_status("✨ Synchronisation terminée !", SPOTIFY_GREEN)
            
            # Recharger les playlists
            self._load_playlists_thread()
            
        except Exception as e:
            self.log(f"❌ Erreur: {e}")
            self.update_status("Erreur", YOUTUBE_RED)
        finally:
            self.is_syncing = False
            self.sync_button.configure(state="normal", text="🔄 Synchroniser")


if __name__ == "__main__":
    app = YoutifyApp()
    app.mainloop()
