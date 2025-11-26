"""
TTS Handler - Interfaces with OpenAI's Text-to-Speech API
"""

import os
import re
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configuration
MAX_CHARS = 200  # Character limit per message
VOICE = "alloy"  # Options: alloy, echo, fable, onyx, nova, shimmer
MODEL = "tts-1"  # Options: tts-1 (faster), tts-1-hd (higher quality)

# Temp directory for audio files
TEMP_DIR = Path(tempfile.gettempdir()) / "discord_tts"
TEMP_DIR.mkdir(exist_ok=True)


def sanitize_text(text: str) -> str:
    """
    Clean text for TTS processing.
    Removes URLs, emoji, and excessive whitespace.
    """
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    
    # Remove Discord mentions (<@123456>, <#channel>, <@&role>)
    text = re.sub(r'<[@#&!]?\d+>', '', text)
    
    # Remove custom Discord emojis (<:name:id> or <a:name:id>)
    text = re.sub(r'<a?:\w+:\d+>', '', text)
    
    # Remove standard emoji (basic pattern for common emoji ranges)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    text = emoji_pattern.sub('', text)
    
    # Collapse multiple spaces/newlines into single space
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def validate_text(text: str) -> tuple[bool, str]:
    """
    Validate text before sending to TTS.
    Returns (is_valid, error_message or cleaned_text).
    """
    cleaned = sanitize_text(text)
    
    if not cleaned:
        return False, "Message is empty after sanitization."
    
    if len(cleaned) > MAX_CHARS:
        return False, f"Message too long ({len(cleaned)}/{MAX_CHARS} chars)."
    
    return True, cleaned


async def generate_speech(text: str, filename: str | None = None) -> str | None:
    """
    Generate speech audio from text using OpenAI's TTS API.
    
    Args:
        text: The text to convert to speech
        filename: Optional custom filename (without extension)
    
    Returns:
        Path to the generated audio file, or None on error
    """
    is_valid, result = validate_text(text)
    
    if not is_valid:
        print(f"TTS validation failed: {result}")
        return None
    
    cleaned_text = result
    
    # Generate unique filename if not provided
    if filename is None:
        import uuid
        filename = f"tts_{uuid.uuid4().hex[:8]}"
    
    output_path = TEMP_DIR / f"{filename}.mp3"
    
    try:
        response = client.audio.speech.create(
            model=MODEL,
            voice=VOICE,
            input=cleaned_text,
        )
        
        # Stream to file
        response.stream_to_file(str(output_path))
        
        return str(output_path)
    
    except Exception as e:
        print(f"TTS generation error: {e}")
        return None


def cleanup_file(filepath: str) -> None:
    """Safely delete a temporary audio file."""
    try:
        Path(filepath).unlink(missing_ok=True)
    except Exception as e:
        print(f"Failed to cleanup {filepath}: {e}")


def cleanup_all() -> None:
    """Remove all temporary TTS files."""
    try:
        for file in TEMP_DIR.glob("tts_*.mp3"):
            file.unlink(missing_ok=True)
    except Exception as e:
        print(f"Failed to cleanup temp directory: {e}")
