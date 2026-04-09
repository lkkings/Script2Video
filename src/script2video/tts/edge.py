import os
import html
import logging
import asyncio
from typing import Optional

from .base import TTSProvider

logger = logging.getLogger(__name__)



class EdgeTTSProvider(TTSProvider):
    """EdgeTTS provider using Microsoft Edge's online TTS service."""

    def __init__(self):
        """Initialize EdgeTTS provider."""
        try:
            import edge_tts
            self.edge_tts = edge_tts
        except ImportError:
            raise ImportError(
                "edge-tts is not installed. Install it with: pip install edge-tts"
            )

    async def synthesize(
        self,
        text: str,
        output_path: str,
        speaker: Optional[str] = None,
        speed: float = 1.0,
        emotion: Optional[str] = None,
        **kwargs
    ) -> tuple[str, float]:
        """
        Synthesize text using EdgeTTS.

        Args:
            text: Text to synthesize
            output_path: Path to save audio file
            speaker: Voice name (e.g., "zh-CN-XiaoxiaoNeural")
            speed: Speech speed (0.5-2.0)
            emotion: Emotion style (ignored by EdgeTTS)
            **kwargs: Additional parameters

        Returns:
            Tuple of (audio_file_path, duration_in_seconds)
        """
        if not speaker:
            speaker = "zh-CN-XiaoxiaoNeural"

        # Convert speed to rate string (EdgeTTS uses percentage)
        rate = f"{int((speed - 1.0) * 100):+d}%"

        logger.info(f"Synthesizing with EdgeTTS: speaker={speaker}, rate={rate}")

        communicate = self.edge_tts.Communicate(text, speaker, rate=rate)
        await communicate.save(output_path)

        duration = self.get_audio_duration(output_path)

        logger.info(f"TTS synthesis complete: {output_path} ({duration:.2f}s)")
        return output_path, duration
