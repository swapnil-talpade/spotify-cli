"""Spotify Controller module for interacting with Spotify API"""

import os
import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import Optional, List

from ..utils.llm_helper import LLMHelper


class SpotifyController:
    def __init__(self):
        """Initialize Spotify controller with authentication"""
        # You need to set these environment variables or replace with your values
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = os.getenv(
            "SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8080/callback"
        )

        if not self.client_id or not self.client_secret:
            print(
                "❌ Error: Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables"
            )
            sys.exit(1)

        # Set up Spotify API with required scopes
        scope = "user-read-playback-state,user-modify-playback-state,user-read-currently-playing,playlist-read-private,user-library-read"

        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=scope,
            )
        )
        self.llm = LLMHelper()

    def get_devices(self) -> List[dict]:
        """Get available Spotify devices"""
        try:
            devices = self.sp.devices()
            return devices.get("devices", [])
        except Exception as e:
            print(f"❌ Error getting devices: {e}")
            return []

    def show_devices(self):
        """Display available devices"""
        devices = self.get_devices()
        if not devices:
            print(
                "❌ No devices found. Make sure Spotify is open on at least one device."
            )
            return

        print("🎵 Available devices:")
        for i, device in enumerate(devices):
            status = "🟢 Active" if device["is_active"] else "⚫ Inactive"
            print(f"  {i+1}. {device['name']} ({device['type']}) - {status}")

    def search_track(self, query: str, limit: int = 10) -> Optional[list]:
        """Search for tracks"""
        try:
            results = self.sp.search(q=query, type="track", limit=limit)
            return results["tracks"]["items"]
        except Exception as e:
            print(f"❌ Error searching: {e}")
            return None

    def play_track(self, track_uri: str, device_id: Optional[str] = None):
        """Play a specific track"""
        try:
            devices = self.get_devices()
            if not devices:
                print("❌ No Spotify devices found! Please:")
                print("  1. Open Spotify on your computer/phone")
                print("  2. Run 'devices' command to verify it's detected")
                print("  3. Try playing music again")
                return

            self.sp.start_playback(uris=[track_uri], device_id=device_id)
            print("▶️  Playing track...")
        except Exception as e:
            print(f"❌ Error playing track: {e}")

    def enhance_search_query(self, user_input: str) -> str:
        """Enhance search query using LLM"""
        prompt = f"""<system>You are a music recommendation system. You MUST respond with ONLY a song name and artist in the exact format 'Song Name - Artist'. No explanation, no options, no additional text.</system>

    Convert this request into a single specific song:
    Request: {user_input}
    Format: Song Name - Artist
    
    Examples:
    Request: something chill
    Response: Weightless - Marconi Union
    
    Request: workout music
    Response: Eye of the Tiger - Survivor
    
    Request: {user_input}
    Response:"""

        enhanced = self.llm.generate(prompt)
        # Clean up any potential extra whitespace or newlines
        if enhanced:
            enhanced = enhanced.strip()
            # If response doesn't match expected format, fall back to original query
            if " - " not in enhanced or len(enhanced.split(" - ")) != 2:
                return user_input
        return enhanced if enhanced else user_input

    def search_and_play(self, query: str):
        """Search for a track and play it"""
        # Enhance the query first
        enhanced_query = self.enhance_search_query(query)
        if enhanced_query != query:
            print(f"🤖 Enhanced search: '{enhanced_query}'")

        tracks = self.search_track(enhanced_query, limit=5)
        if not tracks:
            print("❌ No tracks found")
            return

        print(f"🔍 Search results for '{enhanced_query}':")
        for i, track in enumerate(tracks):
            artists = ", ".join([artist["name"] for artist in track["artists"]])
            print(f"  {i+1}. {track['name']} - {artists}")

        try:
            choice = input("\nEnter number to play (or press Enter for #1): ").strip()
            index = 0 if not choice else int(choice) - 1

            if 0 <= index < len(tracks):
                selected_track = tracks[index]
                print(
                    f"🎵 Selected: {selected_track['name']} - {', '.join([artist['name'] for artist in selected_track['artists']])}"
                )
                self.play_track(selected_track["uri"])
            else:
                print("❌ Invalid selection")
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Cancelled")

    def pause(self):
        """Pause playback"""
        try:
            self.sp.pause_playback()
            print("⏸️  Paused")
        except Exception as e:
            print(f"❌ Error pausing: {e}")

    def resume(self):
        """Resume playback"""
        try:
            self.sp.start_playback()
            print("▶️  Resumed")
        except Exception as e:
            print(f"❌ Error resuming: {e}")

    def next_track(self):
        """Skip to next track"""
        try:
            self.sp.next_track()
            print("⏭️  Next track")
        except Exception as e:
            print(f"❌ Error skipping: {e}")

    def previous_track(self):
        """Go to previous track"""
        try:
            self.sp.previous_track()
            print("⏮️  Previous track")
        except Exception as e:
            print(f"❌ Error going back: {e}")

    def current_track(self):
        """Show currently playing track"""
        try:
            current = self.sp.current_playback()
            if not current or not current.get("item"):
                print("❌ Nothing currently playing")
                return

            track = current["item"]
            artists = ", ".join([artist["name"] for artist in track["artists"]])
            progress = current.get("progress_ms", 0) // 1000
            duration = track.get("duration_ms", 0) // 1000
            is_playing = current.get("is_playing", False)

            status = "▶️ Playing" if is_playing else "⏸️ Paused"
            print(f"{status}: {track['name']} - {artists}")
            print(
                f"⏱️  {progress//60}:{progress%60:02d} / {duration//60}:{duration%60:02d}"
            )

        except Exception as e:
            print(f"❌ Error getting current track: {e}")

    def set_volume(self, volume: int):
        """Set playback volume (0-100)"""
        try:
            volume = max(0, min(100, volume))  # Clamp between 0-100
            self.sp.volume(volume)
            print(f"🔊 Volume set to {volume}%")
        except Exception as e:
            print(f"❌ Error setting volume: {e}")

    def play_best_match(self, query: str):
        """Play the best matching track without user interaction"""
        tracks = self.search_track(query, limit=1)
        if not tracks:
            print("❌ No tracks found")
            return

        track = tracks[0]
        print(
            f"▶️ Playing: {track['name']} - {', '.join([artist['name'] for artist in track['artists']])}"
        )
        self.play_track(track["uri"])
