# ============================================================
# JARVIS - Media Controls Module
# ============================================================

import pyautogui


class MediaControls:
    """System media and volume controls via keyboard shortcuts."""

    @staticmethod
    def play_pause():
        """Toggle play/pause."""
        try:
            pyautogui.press("playpause")
            return True, "Toggling play pause, sir."
        except Exception as e:
            return False, f"Media control failed: {e}"

    @staticmethod
    def next_track():
        """Skip to next track."""
        try:
            pyautogui.press("nexttrack")
            return True, "Next track, sir."
        except Exception as e:
            return False, f"Next track failed: {e}"

    @staticmethod
    def previous_track():
        """Go to previous track."""
        try:
            pyautogui.press("prevtrack")
            return True, "Previous track, sir."
        except Exception as e:
            return False, f"Previous track failed: {e}"

    @staticmethod
    def volume_up(steps=5):
        """Increase system volume."""
        try:
            for _ in range(steps):
                pyautogui.press("volumeup")
            return True, "Volume increased, sir."
        except Exception as e:
            return False, f"Volume up failed: {e}"

    @staticmethod
    def volume_down(steps=5):
        """Decrease system volume."""
        try:
            for _ in range(steps):
                pyautogui.press("volumedown")
            return True, "Volume decreased, sir."
        except Exception as e:
            return False, f"Volume down failed: {e}"

    @staticmethod
    def mute():
        """Mute/unmute system volume."""
        try:
            pyautogui.press("volumemute")
            return True, "Volume muted, sir."
        except Exception as e:
            return False, f"Mute failed: {e}"

    @staticmethod
    def play_music():
        """Open Spotify and play (best effort)."""
        try:
            import os
            os.startfile("spotify")
            return True, "Opening Spotify for music, sir."
        except Exception:
            try:
                pyautogui.press("playpause")
                return True, "Playing music, sir."
            except Exception as e:
                return False, f"Could not play music: {e}"

    @staticmethod
    def spotify_play_track(song_name):
        """Search and play a track via Spotify API."""
        try:
            import spotipy
            from spotipy.oauth2 import SpotifyOAuth
            import config
            
            if not getattr(config, 'SPOTIPY_CLIENT_ID', None) or not getattr(config, 'SPOTIPY_CLIENT_SECRET', None):
                return False, "Spotify API credentials are not set in config, sir."
                
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=config.SPOTIPY_CLIENT_ID,
                client_secret=config.SPOTIPY_CLIENT_SECRET,
                redirect_uri=config.SPOTIPY_REDIRECT_URI,
                scope="user-modify-playback-state user-read-playback-state"
            ))
            
            results = sp.search(q=song_name, limit=1, type='track')
            if results['tracks']['items']:
                track_uri = results['tracks']['items'][0]['uri']
                track_name = results['tracks']['items'][0]['name']
                artist = results['tracks']['items'][0]['artists'][0]['name']
                
                devices = sp.devices()
                if not devices['devices']:
                    return False, "No active Spotify devices found. Please open Spotify on your device first, sir."
                
                sp.start_playback(uris=[track_uri])
                return True, f"Playing {track_name} by {artist} on Spotify, sir."
            return False, f"Could not find the song {song_name} on Spotify, sir."
        except ImportError:
            return False, "Spotipy library not installed, sir. Run pip install spotipy."
        except Exception as e:
            return False, f"Spotify playback failed: {e}"
