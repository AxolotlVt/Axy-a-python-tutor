"""axy/spotify.py  clean, lazy-loaded, returns dicts"""
# ==============================================================================
# Copyright (c) 2026 Axo. All rights reserved.
# 
# This software is proprietary and confidential.
# Unauthorized copying, distribution, modification, or use of this file,
# via any medium, is strictly prohibited without the express written 
# consent of the developer.
# 
# AXY - Local Python Mentor
# ==============================================================================
import os
import json
from cryptography.fernet import Fernet
import spotipy
import re
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from .paths import (
    get_spotify_cache_path,
    get_spotify_key_path,
    get_spotify_secret_path,
)

# Only import what we need from the main package
# ===============================
# === ADD MESSAGE (CORRECTED RELATIVE IMPORT) ====
# ===============================
def _add(text, sender="axy"):
    # Fix: Use relative import to find the sibling 'utils' package
    from .utils.speak import Speak 
    Speak(text, sender)

# ===============================
# ENCRYPTION & CONFIG
# ===============================
KEY_PATH = get_spotify_key_path()
SECRET_PATH = get_spotify_secret_path()
CACHE_PATH = get_spotify_cache_path()


def _load_spotify_secret():
    """Lazily load the encrypted Spotify secret and return the client_secret string.

    Raises FileNotFoundError or other IO/decrypt errors with explanatory messages.
    """
    # First prefer environment variable for runtime secrets (safer for CI/containers)
    env_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")
    if env_secret:
        return env_secret

    if not (os.path.exists(KEY_PATH) and os.path.exists(SECRET_PATH)):
        _add("Spotify configuration files are missing. Please check Axy data folder.")
        raise FileNotFoundError("Missing spotify_key.key or spotify_secret.enc")

    try:
        with open(KEY_PATH, "rb") as kf:
            key = kf.read()
        fernet = Fernet(key)
    except Exception:
        _add("Failed to read Spotify key file.")
        raise

    try:
        with open(SECRET_PATH, "rb") as sf:
            enc = sf.read()
        decrypted = fernet.decrypt(enc).decode()
        payload = json.loads(decrypted)
        return payload["client_secret"]
    except Exception:
        _add("Failed to read or decrypt Spotify secret file.")
        raise


_SPOTIPY_CLIENT_SECRET = None

SPOTIPY_CLIENT_ID = "431ade58e5b24018b9d6b50e7e2f17f6"
SPOTIPY_REDIRECT_URI = "http://127.0.0.1:8888/callback"

# ===============================
# SPOTIPY (lazy)
# ===============================
_spotify_client = None

def get_spotify():
    """Lazy-initialize and return the Spotify client."""
    global _spotify_client
    if _spotify_client is None:
        _add("Authenticating with Spotify...")
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        global _SPOTIPY_CLIENT_SECRET
        if _SPOTIPY_CLIENT_SECRET is None:
            _SPOTIPY_CLIENT_SECRET = _load_spotify_secret()

        _spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=_SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope="user-modify-playback-state,user-read-playback-state",
            cache_path=str(CACHE_PATH),
            open_browser=False
        ))
    return _spotify_client

def get_clean_search_query(user_input: str) -> str:
    text = user_input.strip().lower()
    
    # 1. Define all noise words
    noise_words = set([
        "play", "on", "in", "spotify", "the", "song", "music",
        "by", "from", "reproduce", "lanzar", "jugar", "el", "la", "de",
    ])
    
    # 2. Split the string into words, filter out noise, and rejoin
    words = text.split()
    
    # Filter out any word found in the noise_words set
    filtered_words = [word for word in words if word not in noise_words]
    
    # Rejoin the remaining words to form the query
    clean_query = " ".join(filtered_words)
    
    # Final cleanup (remove excess spaces and punctuation)
    clean_query = re.sub(r"[^a-z0-9\s]", " ", clean_query).strip()
    clean_query = re.sub(r"\s+", " ", clean_query).strip()
    
    return clean_query or "lofi beats"

def search_and_play(song_name: str) -> dict:
    """Core function – does the real work, provides feedback, and returns structured data."""
    song_name = get_clean_search_query(song_name)
    sp = get_spotify()
    
    # Pre-define the result dictionary for clean returns
    result = {}
    
    try:
        results = sp.search(q=song_name, type="track", limit=1)["tracks"]["items"]
        if not results:
            result = {"error": "not_found", "message": f"Sorry, I couldn't find any track for {song_name}."}
            _add(result["message"])
            return result
            
        track = results[0]
        devices = sp.devices()["devices"]
        if not devices:
            result = {"error": "no_device", "message": "I found the song, but I couldn't find an active Spotify device to play it on."}
            _add(result["message"])
            return result
            
        sp.start_playback(device_id=devices[0]["id"], uris=[track["uri"]])
        
        # Success path
        result = {
            "status": "playing",
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "message": f"Now playing {track['name']} by {track['artists'][0]['name']}."
        }
        _add(result["message"])
        return result
        
    except spotipy.exceptions.SpotifyException as e:
        if "NO_ACTIVE_DEVICE" in str(e):
            result = {"error": "no_device", "message": "Spotify error: No active device found. Please start playback manually first."}
            
        else:
            result = {"error": "auth_error", "message": f"A Spotify authentication or API error occurred: {str(e)}"}
            
        _add(result["message"])
        return result
        
    except Exception as e:
        result = {"error": "unexpected", "message": f"An unexpected error occurred in Spotify module: {e}"}
        _add(result["message"])
        return result

# === GRACEFUL CHECK + FRIENDLY FEEDBACK ===

SPOTIFY_READY = False
SPOTIFY_ERROR_MESSAGE = None

if not KEY_PATH.exists():
    SPOTIFY_ERROR_MESSAGE = (
        "Spotify isn't connected — missing 'spotify_key.key' in the data folder. "
        "This file is needed for secure authentication."
    )
elif not SECRET_PATH.exists():
    SPOTIFY_ERROR_MESSAGE = (
        "Spotify isn't connected — missing 'spotify_secret.enc' in the data folder. "
        "This encrypted file holds the client secret."
    )
else:
    try:
        # Try to load and decrypt — catch bad key or corrupted file
        from cryptography.fernet import Fernet
        fernet = Fernet(KEY_PATH.read_bytes())
        decrypted = fernet.decrypt(SECRET_PATH.read_bytes())
        import json
        json.loads(decrypted)  # basic validation
        SPOTIFY_READY = True
    except Exception as e:
        SPOTIFY_ERROR_MESSAGE = (
            f"Spotify config is broken: {str(e)}. "
            "Try regenerating the key and encrypted secret."
        )

# If not ready, we'll use this to inform the user via chat
if SPOTIFY_ERROR_MESSAGE:
    # Auto-inform Axy on first load (optional, but nice)
    from .utils.speak import Speak  # careful with relative import
    Speak(SPOTIFY_ERROR_MESSAGE)  # this will show in chat at startup

# What this module exports
__all__ = ["get_spotify", "search_and_play"]
