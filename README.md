# Discord TTS Bot

A Discord bot that reads text messages aloud in voice channels using OpenAI's neural text-to-speech.

## Features

- `!join` - Bot joins your voice channel and listens to all text channels
- `!leave` - Bot leaves the voice channel
- `!skip` - Skip the current message being read
- `!shutup` / `!stop` / `!clear` - Stop playback and clear the queue
- `!voice` - Set your preferred TTS voice (per-user preference)
- Speaker announcements (e.g., "Alice says: hello") when different users speak

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
   Create a `.env` file with the following:
   ```bash
   DISCORD_TOKEN=your_discord_bot_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Discord Bot Setup**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application and bot
   - Enable **Message Content Intent** in the Bot settings
   - Copy the bot token to your `.env` file
   - Invite the bot with these permissions: `Connect`, `Speak`, `Read Messages/View Channels`, `Send Messages`

## Running

```bash
uv run main.py
```

On first run, an invite link will be printed to the console for easy bot invitation.

## Usage

1. Join a voice channel in Discord
2. In any text channel, type `!join`
3. Send messages — the bot will read them aloud
4. Use `!leave` when done

## Commands

| Command | Description |
|---------|-------------|
| `!join` | Join your voice channel |
| `!leave` | Leave the voice channel |
| `!skip` | Skip current message |
| `!shutup` / `!stop` / `!clear` | Stop playback and clear queue |
| `!voice [name]` | Set your voice (or list options) |

## Available Voices

- `alloy` (default)
- `echo`
- `fable`
- `onyx`
- `nova`
- `shimmer`

Voice preferences are saved per-user and persist across sessions.
