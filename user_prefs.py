"""
User Preferences - Stores per-user settings like voice selection
"""

import json
from pathlib import Path

# Available OpenAI TTS voices
VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
DEFAULT_VOICE = "alloy"

# Persistence file
PREFS_FILE = Path(__file__).parent / "user_prefs.json"


class UserPrefs:
    """Simple persistent storage for user preferences."""
    
    def __init__(self):
        self._prefs: dict[str, dict] = {}
        self._load()
    
    def _load(self) -> None:
        """Load preferences from disk."""
        if PREFS_FILE.exists():
            try:
                self._prefs = json.loads(PREFS_FILE.read_text())
            except (json.JSONDecodeError, IOError):
                self._prefs = {}
    
    def _save(self) -> None:
        """Save preferences to disk."""
        try:
            PREFS_FILE.write_text(json.dumps(self._prefs, indent=2))
        except IOError as e:
            print(f"Failed to save preferences: {e}")
    
    def get_voice(self, user_id: int) -> str:
        """Get the voice setting for a user."""
        user_key = str(user_id)
        return self._prefs.get(user_key, {}).get("voice", DEFAULT_VOICE)
    
    def set_voice(self, user_id: int, voice: str) -> bool:
        """
        Set the voice for a user.
        Returns True if successful, False if invalid voice.
        """
        if voice not in VOICES:
            return False
        
        user_key = str(user_id)
        if user_key not in self._prefs:
            self._prefs[user_key] = {}
        
        self._prefs[user_key]["voice"] = voice
        self._save()
        return True


# Global instance
user_prefs = UserPrefs()
