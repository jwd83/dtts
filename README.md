# Discord TTS Bot

A Discord bot that reads text messages aloud in voice channels using OpenAI's neural text-to-speech.

## Features

- `!join` - Bot joins your voice channel and listens to the text channel
- `!leave` - Bot leaves the voice channel
- `!skip` - Skip the current message being read
- `!shutup` / `!stop` / `!clear` - Stop playback and clear the queue

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- FFmpeg installed and in PATH
- Discord Bot Token (with Message Content Intent enabled)
- OpenAI API Key

## Setup

1. **Install FFmpeg** (if not already installed):
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt install ffmpeg
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your tokens
   ```

4. **Discord Bot Setup**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application and bot
   - Enable **Message Content Intent** in the Bot settings
   - Copy the bot token to your `.env` file
   - Invite the bot with these permissions: `Connect`, `Speak`, `Read Messages/View Channels`

## Running

```bash
uv run main.py
```

## Usage

1. Join a voice channel in Discord
2. In a text channel, type `!join`
3. Send messages in that text channel — the bot will read them aloud
4. Use `!leave` when done

## Configuration

Edit `tts_handler.py` to customize:

- `MAX_CHARS` - Maximum characters per message (default: 200)
- `VOICE` - OpenAI voice: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`
- `MODEL` - `tts-1` (faster) or `tts-1-hd` (higher quality)
