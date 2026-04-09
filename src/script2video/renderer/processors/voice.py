"""
Processor for voice/TTS clips.
"""
import asyncio
import logging
import tempfile
from typing import Any
import re

from moviepy import AudioFileClip

from ...models.clips import VoiceClip
from ...tts import get_tts_provider
from ..utils import db_to_linear, make_subtitle_clip
from .base import ClipProcessor, RenderContext

logger = logging.getLogger(__name__)


class VoiceClipProcessor(ClipProcessor):
    """Processes voice/TTS track clips."""

    def supports(self, clip: Any) -> bool:
        return isinstance(clip, VoiceClip)

    def process(self, clip: VoiceClip, context: RenderContext) -> None:
        logger.info(f"Processing voice clip: {clip.text[:50]}...")

        config = context.config

        # Initialize TTS provider (once, lazily)
        if context.tts_provider is None:
            try:
                provider_name = config.tts.provider
                logger.info(f"Initializing TTS provider: {provider_name}")
                context.tts_provider = get_tts_provider(provider_name, **config.tts.params)
            except Exception as e:
                raise Exception(f"Failed to initialize TTS provider: {e}")

        # Synthesize speech
        try:
            # Create temp file for TTS audio
            tmp = tempfile.NamedTemporaryFile(
                suffix=".mp3", delete=False, prefix="tts_"
            )
            audio_path = tmp.name
            tmp.close()
            # Get TTS config from clip, falling back to defaults
            speaker = clip.tts_config.speaker
            speed = clip.tts_config.speed or config.tts.default_speed
            emotion = clip.tts_config.emotion or config.tts.default_emotion
            # NOTE: asyncio.run() must not be called from within a running loop.
            # If you need to call render() from async code, use run_in_executor.
            audio_path, duration = asyncio.run(
                context.tts_provider.synthesize(
                    text=clip.text,
                    output_path=audio_path,
                    speaker=speaker,
                    speed=speed,
                    emotion=emotion
                )
            )

            context.temp_audio_files.append(audio_path)

            # Load audio and add to clips
            ac = AudioFileClip(audio_path)
            context.clips_to_close.append(ac)

            ac = ac.with_volume_scaled(db_to_linear(clip.volume))
            context.audio_clips.append(ac.with_start(clip.start))

            logger.info(f"TTS synthesis successful: {duration:.2f}s")

        except Exception as e:
            raise Exception(f"TTS synthesis failed: {e}")
        if clip.add_subtitle:
            # Always create subtitle for the voice clip
            segments = re.split(r'[,.，。！？；\s]+', clip.text)
            segments = [s for s in segments if s.strip()] # 过滤空字符串
            
            total_chars = sum(len(s) for s in segments)
            current_time = clip.start
            for seg in segments:
                seg_duration = (len(seg) / total_chars) * duration
                subtitle_clip = make_subtitle_clip(
                    text=seg,
                    start=current_time,
                    end=current_time + seg_duration,
                    width=context.width,
                    height=context.height,
                    subtitle_config=config.subtitle,
                    style=None
                )
                context.video_layers.append(subtitle_clip)
                current_time += seg_duration
