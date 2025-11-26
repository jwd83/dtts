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
    
    @property
    def is_empty(self) -> bool:
        return len(self._queue) == 0
    
    @property
    def size(self) -> int:
        return len(self._queue)
    
    async def add(self, filepath: str, voice_client: discord.VoiceClient) -> None:
        """
        Add an audio file to the queue and start playback if not already playing.
        """
        async with self._lock:
            self._queue.append(filepath)
            
            # Start playback if nothing is currently playing
            if not voice_client.is_playing() and not voice_client.is_paused():
                await self._play_next(voice_client)
    
    async def _play_next(self, voice_client: discord.VoiceClient) -> None:
        """
        Play the next file in the queue.
        Called internally after adding to queue or when current audio finishes.
        """
        if not self._queue:
            self._current_file = None
            return
        
        if not voice_client.is_connected():
            # Voice client disconnected, clear queue
            await self.clear()
            return
        
        filepath = self._queue.popleft()
        self._current_file = filepath
        
        try:
            # Create audio source with FFmpeg
            source = discord.FFmpegPCMAudio(
                filepath,
                options="-loglevel quiet"
            )
            
            # Apply volume transformation (optional, default 1.0)
            source = discord.PCMVolumeTransformer(source, volume=1.0)
            
            # Create callback for when audio finishes
            def after_playing(error):
                if error:
                    print(f"Playback error: {error}")
                
                # Clean up the played file
                cleanup_file(filepath)
                
                # Schedule next track (must use asyncio since callback is sync)
                asyncio.run_coroutine_threadsafe(
                    self._play_next(voice_client),
                    voice_client.loop
                )
            
            voice_client.play(source, after=after_playing)
            
        except Exception as e:
            print(f"Error playing audio: {e}")
            cleanup_file(filepath)
            # Try to play next in queue
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
            
            return count
    
    async def stop(self, voice_client: discord.VoiceClient) -> None:
        """
        Stop playback and clear the entire queue.
        """
        await self.clear()
        
        if voice_client.is_playing():
            voice_client.stop()


# Global queue instance (one per bot)
# For multi-guild support, use a dict mapping guild_id -> TTSQueue
tts_queue = TTSQueue()
