"""
Youtify - Bidirectional Spotify <-> YouTube Music sync
Modern GUI with CustomTkinter
"""

import sys
import os

# Hide console window on Windows
if sys.platform == 'win32':
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

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

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")
SIMILARITY_THRESHOLD = 0.75
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
        
        self.title("🎵 Youtify")
        self.geometry("1100x800")
        self.configure(fg_color=DARK_BG)
        self.resizable(True, True)
        self.minsize(900, 700)
        
        self.spotify_client = None
        self.youtube_client = None
        self.is_syncing = False
        self.spotify_tracks = []
        self.youtube_tracks = []
        
        load_dotenv(ENV_FILE)
        self.create_widgets()
        self.load_saved_config()
    
    def create_widgets(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=80)
        header_frame.pack(fill="x", padx=30, pady=(20, 10))
        header_frame.pack_propagate(False)
        
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
        
        # Config panel
        self.config_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=15)
        self.config_visible = False
        
        config_inner = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        config_inner.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            config_inner,
            text="🔐 Configuration API",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(0, 15))
        
        entries_frame = ctk.CTkFrame(config_inner, fg_color="transparent")
        entries_frame.pack(fill="x")
        
        spotify_config = ctk.CTkFrame(entries_frame, fg_color=CARD_BG_LIGHT, corner_radius=10)
        spotify_config.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(spotify_config, text="🟢 Spotify", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.spotify_id_entry = ctk.CTkEntry(spotify_config, placeholder_text="Client ID", height=35)
        self.spotify_id_entry.pack(fill="x", padx=15, pady=5)
        
        self.spotify_secret_entry = ctk.CTkEntry(spotify_config, placeholder_text="Client Secret", show="•", height=35)
        self.spotify_secret_entry.pack(fill="x", padx=15, pady=(5, 15))
        
        youtube_config = ctk.CTkFrame(entries_frame, fg_color=CARD_BG_LIGHT, corner_radius=10)
        youtube_config.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(youtube_config, text="🔴 YouTube Music", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.youtube_auth_entry = ctk.CTkEntry(youtube_config, placeholder_text="Path to browser.json", height=35)
        self.youtube_auth_entry.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(youtube_config, text="", height=35).pack(fill="x", padx=15, pady=(5, 15))
        
        ctk.CTkButton(
            config_inner,
            text="💾 Save",
            command=self.save_config,
            width=150,
            height=35,
            fg_color=ACCENT_BLUE,
            hover_color="#5a73f0"
        ).pack(pady=(15, 0))
        
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        input_frame = ctk.CTkFrame(main_frame, fg_color=CARD_BG, corner_radius=15, height=120)
        input_frame.pack(fill="x", pady=(0, 15))
        input_frame.pack_propagate(False)
        
        input_inner = ctk.CTkFrame(input_frame, fg_color="transparent")
        input_inner.pack(fill="both", expand=True, padx=20, pady=15)
        
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
        
        sep_frame = ctk.CTkFrame(input_inner, fg_color="transparent", width=60)
        sep_frame.pack(side="left")
        sep_frame.pack_propagate(False)
        
        ctk.CTkLabel(sep_frame, text="⟷", font=ctk.CTkFont(size=30), text_color="#666").pack(expand=True)
        
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
        
        comparison_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        comparison_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        spotify_panel = ctk.CTkFrame(comparison_frame, fg_color=CARD_BG, corner_radius=15)
        spotify_panel.pack(side="left", fill="both", expand=True, padx=(0, 8))
        
        spotify_header = ctk.CTkFrame(spotify_panel, fg_color=SPOTIFY_GREEN, corner_radius=10, height=50)
        spotify_header.pack(fill="x", padx=10, pady=10)
        spotify_header.pack_propagate(False)
        
        self.spotify_header_label = ctk.CTkLabel(
            spotify_header,
            text="🟢 SPOTIFY • 0 tracks",
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
        self.spotify_list.insert("1.0", "Enter a Spotify playlist link\nand click Load...")
        self.spotify_list.configure(state="disabled")
        
        youtube_panel = ctk.CTkFrame(comparison_frame, fg_color=CARD_BG, corner_radius=15)
        youtube_panel.pack(side="left", fill="both", expand=True, padx=(8, 0))
        
        youtube_header = ctk.CTkFrame(youtube_panel, fg_color=YOUTUBE_RED, corner_radius=10, height=50)
        youtube_header.pack(fill="x", padx=10, pady=10)
        youtube_header.pack_propagate(False)
        
        self.youtube_header_label = ctk.CTkLabel(
            youtube_header,
            text="🔴 YOUTUBE MUSIC • 0 tracks",
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
        self.youtube_list.insert("1.0", "Enter a YouTube playlist link\nand click Load...")
        self.youtube_list.configure(state="disabled")
        
        action_frame = ctk.CTkFrame(main_frame, fg_color=CARD_BG, corner_radius=15, height=80)
        action_frame.pack(fill="x", pady=(0, 10))
        action_frame.pack_propagate(False)
        
        action_inner = ctk.CTkFrame(action_frame, fg_color="transparent")
        action_inner.pack(expand=True)
        
        self.load_btn = ctk.CTkButton(
            action_inner,
            text="📥 Load playlists",
            command=self.load_playlists,
            width=200,
            height=50,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=ACCENT_BLUE,
            hover_color="#5a73f0",
            corner_radius=10
        )
        self.load_btn.pack(side="left", padx=10)
        
        self.sync_button = ctk.CTkButton(
            action_inner,
            text="🔄 Sync",
            command=self.start_sync,
            width=200,
            height=50,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=SPOTIFY_GREEN,
            hover_color=SPOTIFY_GREEN_HOVER,
            corner_radius=10
        )
        self.sync_button.pack(side="left", padx=10)
        
        self.progress_bar = ctk.CTkProgressBar(action_inner, width=200, height=15, corner_radius=5)
        self.progress_bar.pack(side="left", padx=20)
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(
            action_inner,
            text="Ready",
            font=ctk.CTkFont(size=13),
            text_color="#888888"
        )
        self.status_label.pack(side="left", padx=10)
        
        log_frame = ctk.CTkFrame(main_frame, fg_color=CARD_BG, corner_radius=15, height=120)
        log_frame.pack(fill="x")
        log_frame.pack_propagate(False)
        
        log_header = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_header.pack(fill="x", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(log_header, text="📋 Log", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
        
        ctk.CTkButton(
            log_header,
            text="Clear",
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
        if self.config_visible:
            self.config_frame.pack_forget()
            self.config_visible = False
            self.config_btn.configure(text="⚙️ Configuration")
        else:
            self.config_frame.pack(fill="x", padx=30, pady=(0, 10), after=self.winfo_children()[0])
            self.config_visible = True
            self.config_btn.configure(text="✕ Close")
    
    def clear_log(self):
        self.log_textbox.delete("1.0", "end")
    
    def log(self, message):
        self.log_textbox.insert("end", f"{message}\n")
        self.log_textbox.see("end")
        self.update()
    
    def update_status(self, text, color="#888888"):
        self.status_label.configure(text=text, text_color=color)
        self.update()
    
    def load_saved_config(self):
        self.spotify_id_entry.insert(0, os.getenv("SPOTIFY_CLIENT_ID", ""))
        self.spotify_secret_entry.insert(0, os.getenv("SPOTIFY_CLIENT_SECRET", ""))
        self.youtube_auth_entry.insert(0, os.getenv("YOUTUBE_AUTH_FILE", "browser.json"))
    
    def save_config(self):
        try:
            if not os.path.exists(ENV_FILE):
                with open(ENV_FILE, "w") as f:
                    f.write("")
            
            set_key(ENV_FILE, "SPOTIFY_CLIENT_ID", self.spotify_id_entry.get())
            set_key(ENV_FILE, "SPOTIFY_CLIENT_SECRET", self.spotify_secret_entry.get())
            set_key(ENV_FILE, "YOUTUBE_AUTH_FILE", self.youtube_auth_entry.get())
            
            self.log("✅ Configuration saved")
            self.update_status("Configuration saved", SPOTIFY_GREEN)
        except Exception as e:
            self.log(f"❌ Error: {e}")
            messagebox.showerror("Error", f"Unable to save: {e}")
    
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
        if not track1 or not track2:
            return False
        name1 = self.normalize_string(track1.get('name', '') or '')
        name2 = self.normalize_string(track2.get('name', '') or '')
        artist1 = self.normalize_artist(track1.get('artist', '') or '')
        artist2 = self.normalize_artist(track2.get('artist', '') or '')
        if not name1 or not name2:
            return False
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
                    artist = "Unknown"
                    artists = track.get('artists')
                    if artists and len(artists) > 0 and artists[0]:
                        artist = artists[0].get('name', 'Unknown') or 'Unknown'
                    tracks.append({
                        "name": track['name'],
                        "artist": artist,
                    })
            if not results.get('next'):
                break
            offset += 100
        return tracks
    
    def get_youtube_tracks(self, playlist_id):
        # Custom pagination to handle YouTube Music's new continuation format
        from ytmusicapi.navigation import nav, TWO_COLUMN_RENDERER, SECTION, CONTENT
        from ytmusicapi.parsers.playlists import parse_playlist_items
        
        browse_id = "VL" + playlist_id if not playlist_id.startswith("VL") else playlist_id
        body = {"browseId": browse_id}
        
        response = self.youtube_client._send_request("browse", body)
        
        # Get initial tracks
        section_list = nav(response, [*TWO_COLUMN_RENDERER, "secondaryContents", *SECTION])
        content_data = nav(section_list, [*CONTENT, "musicPlaylistShelfRenderer"])
        
        all_raw_tracks = []
        if "contents" in content_data:
            contents = content_data["contents"]
            
            # Parse initial tracks (excluding continuation item)
            track_items = [c for c in contents if "musicResponsiveListItemRenderer" in c]
            all_raw_tracks.extend(parse_playlist_items(track_items))
            
            # Check for continuation and fetch more
            while contents:
                last_item = contents[-1] if contents else None
                if not last_item or "continuationItemRenderer" not in last_item:
                    break
                
                # Extract continuation token - handle both formats
                cont_renderer = last_item.get("continuationItemRenderer", {})
                cont_endpoint = cont_renderer.get("continuationEndpoint", {})
                
                token = None
                
                # Format 1: Direct continuationCommand (used in continuation responses)
                if "continuationCommand" in cont_endpoint:
                    token = cont_endpoint["continuationCommand"].get("token")
                
                # Format 2: Nested in commandExecutorCommand (used in initial response)
                if not token:
                    commands = cont_endpoint.get("commandExecutorCommand", {}).get("commands", [])
                    for cmd in commands:
                        if "continuationCommand" in cmd:
                            token = cmd["continuationCommand"].get("token")
                            break
                
                if not token:
                    break
                
                # Fetch next batch
                cont_response = self.youtube_client._send_request("browse", {"continuation": token})
                cont_items = nav(cont_response, ["onResponseReceivedActions", 0, "appendContinuationItemsAction", "continuationItems"], True)
                
                if not cont_items:
                    break
                
                # Parse new tracks
                track_items = [c for c in cont_items if "musicResponsiveListItemRenderer" in c]
                if not track_items:
                    break
                    
                all_raw_tracks.extend(parse_playlist_items(track_items))
                contents = cont_items
        
        # Convert to our format
        tracks = []
        for track in all_raw_tracks:
            if track and track.get('title'):
                artist = "Unknown"
                artists = track.get('artists')
                if artists and len(artists) > 0 and artists[0]:
                    artist = artists[0].get('name', 'Unknown') or 'Unknown'
                tracks.append({
                    "name": track['title'],
                    "artist": artist,
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
        
        count = len(tracks)
        missing_count = len(missing) if missing else 0
        if platform == "spotify":
            text = f"🟢 SPOTIFY • {count} tracks"
            if missing_count > 0:
                text += f" (+{missing_count} to add)"
            header_label.configure(text=text)
        else:
            text = f"🔴 YOUTUBE MUSIC • {count} tracks"
            if missing_count > 0:
                text += f" (+{missing_count} to add)"
            header_label.configure(text=text)
    
    def load_playlists(self):
        if not self.spotify_id_entry.get() or not self.spotify_secret_entry.get():
            messagebox.showerror("Error", "Configure your Spotify credentials first!")
            self.toggle_config()
            return
        
        if not self.spotify_playlist_entry.get() or not self.youtube_playlist_entry.get():
            messagebox.showerror("Error", "Enter both playlist links!")
            return
        
        self.load_btn.configure(state="disabled", text="⏳ Loading...")
        thread = threading.Thread(target=self._load_playlists_thread, daemon=True)
        thread.start()
    
    def _load_playlists_thread(self):
        try:
            self.update_status("Connecting to Spotify...", ACCENT_BLUE)
            self.progress_bar.set(0.1)
            
            self.spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=self.spotify_id_entry.get(),
                client_secret=self.spotify_secret_entry.get(),
                redirect_uri="http://127.0.0.1:8888/callback",
                scope="playlist-read-private playlist-modify-public playlist-modify-private"
            ))
            self.log("✅ Spotify connected")
            
            self.update_status("Connecting to YouTube Music...", ACCENT_BLUE)
            self.progress_bar.set(0.2)
            
            auth_file = self.youtube_auth_entry.get()
            if not os.path.isabs(auth_file):
                auth_file = os.path.join(os.path.dirname(__file__), auth_file)
            self.youtube_client = YTMusic(auth_file)
            self.log("✅ YouTube Music connected")
            
            self.update_status("Loading Spotify...", SPOTIFY_GREEN)
            self.progress_bar.set(0.4)
            
            self.spotify_tracks = self.get_spotify_tracks(self.spotify_playlist_entry.get())
            self.log(f"📗 Spotify: {len(self.spotify_tracks)} tracks")
            
            self.update_status("Loading YouTube...", YOUTUBE_RED)
            self.progress_bar.set(0.6)
            
            youtube_id = self.extract_youtube_id(self.youtube_playlist_entry.get())
            self.youtube_tracks = self.get_youtube_tracks(youtube_id)
            self.log(f"📕 YouTube: {len(self.youtube_tracks)} tracks")
            
            self.update_status("Analyzing differences...", ACCENT_BLUE)
            self.progress_bar.set(0.8)
            
            missing_on_youtube = self.find_missing_tracks(self.spotify_tracks, self.youtube_tracks)
            missing_on_spotify = self.find_missing_tracks(self.youtube_tracks, self.spotify_tracks)
            
            self.log(f"🔄 {len(missing_on_youtube)} → YouTube | {len(missing_on_spotify)} → Spotify")
            
            self.update_track_list(self.spotify_list, self.spotify_tracks, self.spotify_header_label, "spotify", missing_on_spotify)
            self.update_track_list(self.youtube_list, self.youtube_tracks, self.youtube_header_label, "youtube", missing_on_youtube)
            
            self.progress_bar.set(1.0)
            
            if not missing_on_youtube and not missing_on_spotify:
                self.update_status("✨ Playlists synced!", SPOTIFY_GREEN)
            else:
                self.update_status(f"Ready to sync ({len(missing_on_youtube) + len(missing_on_spotify)} tracks)", SPOTIFY_GREEN)
            
        except Exception as e:
            self.log(f"❌ Error: {e}")
            self.update_status("Error", YOUTUBE_RED)
            messagebox.showerror("Error", str(e))
        finally:
            self.load_btn.configure(state="normal", text="📥 Load playlists")
    
    def start_sync(self):
        if self.is_syncing:
            return
        
        if not self.spotify_tracks or not self.youtube_tracks:
            messagebox.showinfo("Info", "Load playlists first!")
            return
        
        self.is_syncing = True
        self.sync_button.configure(state="disabled", text="⏳ Syncing...")
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
                self.update_status("✨ Already synced!", SPOTIFY_GREEN)
                return
            
            done = 0
            
            if missing_on_youtube:
                self.log(f"\n➡️ Adding {len(missing_on_youtube)} tracks to YouTube...")
                for track in missing_on_youtube:
                    try:
                        query = f"{track['name']} {track['artist']}"
                        results = self.youtube_client.search(query, filter="songs", limit=1)
                        if results:
                            self.youtube_client.add_playlist_items(youtube_id, [results[0]['videoId']])
                            self.log(f"   ✅ {track['name'][:35]} - {track['artist'][:20]}")
                        else:
                            self.log(f"   ⚠️ Not found: {track['name'][:35]}")
                    except Exception as e:
                        self.log(f"   ❌ {track['name'][:35]}")
                    done += 1
                    self.progress_bar.set(done / total)
                    self.update_status(f"YouTube: {done}/{total}", YOUTUBE_RED)
            
            if missing_on_spotify:
                self.log(f"\n➡️ Adding {len(missing_on_spotify)} tracks to Spotify...")
                track_ids = []
                for track in missing_on_spotify:
                    try:
                        query = f"{track['name']} {track['artist']}"
                        result = self.spotify_client.search(q=query, type='track', limit=1)
                        if result['tracks']['items']:
                            track_ids.append(result['tracks']['items'][0]['id'])
                            self.log(f"   ✅ {track['name'][:35]} - {track['artist'][:20]}")
                        else:
                            self.log(f"   ⚠️ Not found: {track['name'][:35]}")
                    except:
                        self.log(f"   ❌ {track['name'][:35]}")
                    done += 1
                    self.progress_bar.set(done / total)
                    self.update_status(f"Spotify: {done}/{total}", SPOTIFY_GREEN)
                
                if track_ids:
                    for i in range(0, len(track_ids), 100):
                        self.spotify_client.playlist_add_items(spotify_id, track_ids[i:i+100])
            
            self.progress_bar.set(1.0)
            self.log("\n" + "=" * 50)
            self.log("✨ Sync completed!")
            self.update_status("✨ Sync completed!", SPOTIFY_GREEN)
            
            self._load_playlists_thread()
            
        except Exception as e:
            self.log(f"❌ Error: {e}")
            self.update_status("Error", YOUTUBE_RED)
        finally:
            self.is_syncing = False
            self.sync_button.configure(state="normal", text="🔄 Sync")


if __name__ == "__main__":
    app = YoutifyApp()
    app.mainloop()
