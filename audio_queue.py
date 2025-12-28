"""
Audio Queue - Manages FIFO playback for Discord voice client
"""

import asyncio
from collections import deque
from typing import Callable

import discord

from tts_handler import cleanup_file


class TTSQueue:
    """
    Manages a queue of audio files to be played through Discord voice client.
    Ensures only one audio source plays at a time.
    """

    def __init__(self):
        self._queue: deque[str] = deque()
        self._lock = asyncio.Lock()
        self._current_file: str | None = None
        self._last_speaker_id: int | None = None

    @property
    def is_empty(self) -> bool:
        return len(self._queue) == 0

    @property
    def size(self) -> int:
        return len(self._queue)

    async def add(self, filepath: str, voice_client: discord.VoiceClient, speaker_id: int | None = None) -> None:
        """
        Add an audio file to the queue and start playback if not already playing.
        """
        async with self._lock:
            self._queue.append(filepath)
            if speaker_id is not None:
                self._last_speaker_id = speaker_id

            # Start playback if nothing is currently playing
            if not voice_client.is_playing() and not voice_client.is_paused():
                await self._play_next(voice_client)

    async def _play_next(self, voice_client: discord.VoiceClient) -> None:
        """
        Play the next file in the queue. Must be called with lock held.
        """
        if not self._queue:
            self._current_file = None
            return

        if not voice_client.is_connected():
            return

        # Don't start if already playing
        if voice_client.is_playing() or voice_client.is_paused():
            return

        filepath = self._queue.popleft()
        self._current_file = filepath

        # Create callback for when audio finishes
        def after_playing(error):
            if error:
                print(f"Playback error: {error}")

            # Clean up the played file
            cleanup_file(filepath)

            # Schedule next track with lock
            asyncio.run_coroutine_threadsafe(
                self._on_playback_finished(voice_client),
                voice_client.loop
            )

        try:
            source = discord.FFmpegOpusAudio(filepath)
            voice_client.play(source, after=after_playing)
        except Exception as e:
            print(f"Error playing audio: {e}")
            cleanup_file(filepath)
            # Schedule retry on the event loop to avoid blocking
            asyncio.run_coroutine_threadsafe(self._play_next(voice_client), voice_client.loop)

    async def _on_playback_finished(self, voice_client: discord.VoiceClient) -> None:
        """
        Called when playback finishes to start the next track.
        """
        async with self._lock:
            await self._play_next(voice_client)

    async def skip(self, voice_client: discord.VoiceClient) -> bool:
        """
        Skip the currently playing audio.
        Returns True if something was skipped.
        """
        if voice_client.is_playing():
            voice_client.stop()  # This triggers the after callback
            return True
        return False

    async def clear(self) -> int:
        """
        Clear all pending items from the queue (does not stop current playback).
        Returns the number of items cleared.
        """
        async with self._lock:
            count = len(self._queue)

            # Clean up all queued files
            while self._queue:
                filepath = self._queue.popleft()
                cleanup_file(filepath)

            self._last_speaker_id = None
            return count

    def should_announce_speaker(self, speaker_id: int) -> bool:
        """
        Check if we should announce this speaker (different from last).
        """
        return self._last_speaker_id != speaker_id

    async def stop(self, voice_client: discord.VoiceClient) -> None:
        """
        Stop playback and clear the entire queue.
        """
        await self.clear()

        if voice_client.is_playing():
            voice_client.stop()


# Per-guild queue manager for multi-server support
class TTSQueueManager:
    """
    Manages separate TTS queues for each Discord guild.
    """

    def __init__(self):
        self._queues: dict[int, TTSQueue] = {}

    def get_queue(self, guild_id: int) -> TTSQueue:
        """Get or create a queue for the specified guild."""
        if guild_id not in self._queues:
            self._queues[guild_id] = TTSQueue()
        return self._queues[guild_id]

    async def stop(self, guild_id: int, voice_client: discord.VoiceClient) -> None:
        """Stop playback for a specific guild."""
        if guild_id in self._queues:
            await self._queues[guild_id].stop(voice_client)
            del self._queues[guild_id]

    async def clear(self, guild_id: int) -> int:
        """Clear queue for a specific guild without removing it."""
        if guild_id in self._queues:
            return await self._queues[guild_id].clear()
        return 0


# Global queue manager instance (supports multiple guilds)
tts_queue_manager = TTSQueueManager()
