"""
NEXUS - Streaming Response Handler
Handles token-by-token streaming of AI responses with animated typing effect.
"""

import time
import asyncio
from typing import AsyncGenerator, Callable, Optional
from core.logger import Logger


class StreamingResponse:
    """
    Manages streaming AI responses with progressive rendering.
    Supports both sync and async streaming with typing animation.
    """

    def __init__(self, typing_speed: float = 0.01, chunk_size: int = 1):
        self.logger = Logger().get_logger("StreamingResponse")
        self.typing_speed = typing_speed
        self.chunk_size = chunk_size
        self._full_response = ""
        self._is_complete = False
        self._callbacks = []

    def on_chunk(self, callback: Callable[[str], None]):
        """Register a callback for each chunk."""
        self._callbacks.append(callback)

    async def stream_async(self, generator) -> AsyncGenerator[str, None]:
        """Stream tokens from an async generator with callbacks."""
        self._full_response = ""
        self._is_complete = False
        buffer = ""

        async for token in generator:
            if token:
                buffer += token
                self._full_response += token
                if len(buffer) >= self.chunk_size:
                    for callback in self._callbacks:
                        try:
                            callback(buffer)
                        except Exception as e:
                            self.logger.error(f"Stream callback error: {e}")
                    yield buffer
                    buffer = ""
                    await asyncio.sleep(self.typing_speed)

        if buffer:
            for callback in self._callbacks:
                try:
                    callback(buffer)
                except Exception:
                    pass
            yield buffer

        self._is_complete = True

    def stream_sync(self, generator) -> str:
        """Stream tokens from a sync generator with callbacks."""
        self._full_response = ""
        self._is_complete = False
        buffer = ""

        for token in generator:
            if token:
                buffer += token
                self._full_response += token
                if len(buffer) >= self.chunk_size:
                    for callback in self._callbacks:
                        try:
                            callback(buffer)
                        except Exception as e:
                            self.logger.error(f"Stream callback error: {e}")
                    buffer = ""
                    time.sleep(self.typing_speed)

        if buffer:
            for callback in self._callbacks:
                try:
                    callback(buffer)
                except Exception:
                    pass

        self._is_complete = True
        return self._full_response

    @property
    def full_response(self) -> str:
        return self._full_response

    @property
    def is_complete(self) -> bool:
        return self._is_complete

    def reset(self):
        """Reset the streaming state."""
        self._full_response = ""
        self._is_complete = False
        self._callbacks.clear()


class TypingAnimation:
    """Provides typing animation for terminal output."""

    ANIMATION_CHARS = ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]

    def __init__(self):
        self._frame = 0

    def next_frame(self) -> str:
        char = self.ANIMATION_CHARS[self._frame % len(self.ANIMATION_CHARS)]
        self._frame += 1
        return char

    def reset(self):
        self._frame = 0
