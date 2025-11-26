SOTA Discord TTS Bot

1. Project Overview

Goal: Create a Discord bot using Python that joins a voice channel and reads incoming text messages from a specific text channel aloud using high-quality, neural-network-based Text-to-Speech.

Key Features:

!join / !leave commands to control bot presence.

Automatic queue system (to handle multiple messages coming in simultaneously).

"State of the Art" TTS integration (OpenAI API or ElevenLabs).

Automatic temporary file cleanup.

Character limit filtering (to prevent spam).

2. Technology Stack

Language: Python 3.10+

Discord Library: discord.py (specifically commands extension).

Audio Handling: FFmpeg (Required for Discord audio streaming).

TTS Provider: - Primary Option: OpenAI API (tts-1 model) - Fast, cheap, very realistic.

Secondary Option: ElevenLabs API - Best expressiveness, more expensive.

Environment Management: python-dotenv for API keys.

3. Architecture Design

A. The Event Loop

User sends message: Bot detects on_message event.

Filter: Ignore bots, ignore commands (start with !), ignore messages if bot is not in VC.

Process: Send text to TTS Service -> Get Audio Bytes -> Save to temp file.

Queue: Add file path to a playback queue.

Playback: Background task monitors queue -> Plays audio -> Deletes file after playing.

B. Directory Structure

discord-tts-bot/
├── .env                # API Keys (Discord Token, OpenAI Key)
├── requirements.txt    # Dependencies
├── main.py             # Entry point and Discord event handlers
├── tts_handler.py      # Module to interface with OpenAI/ElevenLabs
└── audio_queue.py      # Logic to manage the playlist FIFO queue


4. Implementation Steps

Phase 1: Setup & Authorization

[ ] Create Application in Discord Developer Portal.

[ ] Crucial: Enable "Message Content Intent" in the Bot tab (required to read messages).

[ ] Generate Bot Token.

[ ] Get OpenAI API Key.

[ ] Install local dependencies: pip install discord.py openai python-dotenv.

[ ] Install system dependency: FFmpeg (must be in system PATH).

Phase 2: Basic Bot Connectivity

[ ] Create main.py.

[ ] Implement !join command (connects to ctx.author.voice.channel).

[ ] Implement !leave command.

[ ] Verify bot can join/leave and permissions are correct.

Phase 3: The TTS Engine (tts_handler.py)

[ ] Create a function generate_speech(text, filename).

[ ] Initialize OpenAI client.

[ ] implementations:

Sanitize text (remove emojis/urls).

Call API: client.audio.speech.create.

Stream response to a local .mp3 or .opus file.

Phase 4: The Queue System (audio_queue.py)

Discord bots cannot play two audio sources at once. A blocking queue is required.

[ ] Create TTSQueue class.

[ ] Logic:

Check if voice_client.is_playing().

If yes: Add new audio file to list.

If no: Play immediately.

[ ] Implement an after_playing callback function in discord.py to trigger the next song in the queue and delete the old file.

Phase 5: Integration

[ ] Wire on_message in main.py to trigger the tts_handler.

[ ] Ensure the bot only speaks in the text channel where the command was run (to avoid global spam).

[ ] Add error handling (e.g., user disconnects while bot is speaking).

5. Risk Management & Limits

Cost Control: SOTA APIs are paid. Implement a character limit per message (e.g., max 200 chars).

Spam: Add a cooldown or a !shutup command to clear the current queue.

Privacy: Ensure the bot does not log or store text data, only processes it for audio.

6. Future Enhancements

[ ] Different voices for different users (mapping UserID to specific VoiceIDs).

[ ] Soundboard effects.

[ ] "Now Playing" status updates.