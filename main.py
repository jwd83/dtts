"""
Discord TTS Bot - Main Entry Point
Reads text messages aloud in voice channels using OpenAI TTS.
"""

import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from audio_queue import tts_queue
from tts_handler import generate_speech, cleanup_all
from user_prefs import user_prefs, VOICES

# Load environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN not found in environment variables")

# Bot setup with required intents
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content
intents.voice_states = True     # Required for voice channel events

bot = commands.Bot(command_prefix="!", intents=intents)



@bot.event
async def on_ready():
    print(f"✓ Logged in as {bot.user}")
    print(f"✓ Connected to {len(bot.guilds)} guild(s)")
    
    # Cleanup any leftover temp files from previous sessions
    cleanup_all()


@bot.command(name="join")
async def join(ctx: commands.Context):
    """Join the voice channel of the user who sent the command."""
    
    # Check if user is in a voice channel
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ You need to be in a voice channel first!")
        return
    
    channel = ctx.author.voice.channel
    
    # Check if bot is already in a voice channel in this guild
    if ctx.voice_client:
        if ctx.voice_client.channel == channel:
            await ctx.send("✓ Already in your channel!")
            return
        # Move to the new channel
        await ctx.voice_client.move_to(channel)
    else:
        # Connect to the voice channel
        try:
            await channel.connect()
        except Exception as e:
            await ctx.send(f"❌ Failed to join: {e}")
            return
    
    await ctx.send(f"✓ Joined **{channel.name}** — I'll read messages from all text channels!")


@bot.command(name="leave")
async def leave(ctx: commands.Context):
    """Leave the voice channel."""
    
    if not ctx.voice_client:
        await ctx.send("❌ I'm not in a voice channel!")
        return
    
    # Clear the queue and disconnect
    await tts_queue.stop(ctx.voice_client)
    await ctx.voice_client.disconnect()
    
    await ctx.send("👋 Left the voice channel!")


@bot.command(name="skip")
async def skip(ctx: commands.Context):
    """Skip the currently playing message."""
    
    if not ctx.voice_client:
        await ctx.send("❌ I'm not in a voice channel!")
        return
    
    skipped = await tts_queue.skip(ctx.voice_client)
    
    if skipped:
        await ctx.send("⏭️ Skipped!")
    else:
        await ctx.send("Nothing is playing.")


@bot.command(name="shutup", aliases=["clear", "stop"])
async def shutup(ctx: commands.Context):
    """Stop playback and clear the queue."""
    
    if not ctx.voice_client:
        await ctx.send("❌ I'm not in a voice channel!")
        return
    
    await tts_queue.stop(ctx.voice_client)
    await ctx.send("🤐 Queue cleared!")


@bot.command(name="voice")
async def voice(ctx: commands.Context, voice_name: str | None = None):
    """Set your TTS voice. Usage: !voice <name> or !voice to see options."""
    
    current = user_prefs.get_voice(ctx.author.id)
    
    if voice_name is None:
        voices_list = ", ".join(f"**{v}**" if v == current else v for v in VOICES)
        await ctx.send(f"Available voices: {voices_list}\nUsage: `!voice <name>`")
        return
    
    voice_name = voice_name.lower()
    
    if user_prefs.set_voice(ctx.author.id, voice_name):
        await ctx.send(f"✓ Voice set to **{voice_name}**")
    else:
        await ctx.send(f"❌ Unknown voice. Options: {', '.join(VOICES)}")


@bot.event
async def on_message(message: discord.Message):
    """Process incoming messages for TTS."""
    
    # Always process commands first
    await bot.process_commands(message)
    
    # Ignore messages from bots (including self)
    if message.author.bot:
        return
    
    # Ignore if no guild (DMs)
    if not message.guild:
        return
    
    # Check if bot is in a voice channel in this guild
    voice_client = message.guild.voice_client
    if not voice_client or not voice_client.is_connected():
        return
    
    # Ignore command messages
    if message.content.startswith("!"):
        return
    
    # Ignore empty messages (e.g., image-only)
    if not message.content.strip():
        return
    
    # Generate TTS audio with user's preferred voice
    voice = user_prefs.get_voice(message.author.id)
    audio_path = await generate_speech(message.content, voice=voice)
    
    if audio_path:
        await tts_queue.add(audio_path, voice_client)


@bot.event
async def on_voice_state_update(
    member: discord.Member,
    before: discord.VoiceState,
    after: discord.VoiceState
):
    """Handle voice state changes (e.g., bot gets disconnected)."""
    
    # Check if it's the bot that changed state
    if member != bot.user:
        return
    
    # Bot was disconnected from voice
    if before.channel and not after.channel:
        # Clean up
        await tts_queue.clear()


# Error handling
@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands silently
    
    await ctx.send(f"❌ Error: {error}")


if __name__ == "__main__":
    print("Starting Discord TTS Bot...")
    bot.run(DISCORD_TOKEN)
