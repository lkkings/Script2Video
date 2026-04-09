"""
Processor for BGM (background music) clips.
"""
import os
import logging
from typing import Any

from moviepy import AudioFileClip, concatenate_audioclips

from ...models.clips import BGMClip
from ..utils import db_to_linear, apply_audio_fade
from .base import ClipProcessor, RenderContext

logger = logging.getLogger(__name__)


class BGMClipProcessor(ClipProcessor):
    """Processes BGM track clips."""

    def supports(self, clip: Any) -> bool:
        return isinstance(clip, BGMClip)

    def process(self, clip: BGMClip, context: RenderContext) -> None:
        if not os.path.exists(clip.source):
            raise FileNotFoundError(f"Audio file not found: {clip.source}")
        logger.info(f"Processing bgm clip: {clip.source}...")

        duration = clip.end - clip.start
        raw = AudioFileClip(clip.source)

        # Loop if needed
        if clip.loop and raw.duration < duration:
            num_loops = int(duration // raw.duration) + 2
            raw = concatenate_audioclips([raw] * num_loops)

        ac = raw.subclipped(0, duration)

        # Apply volume
        ac = ac.with_volume_scaled(db_to_linear(clip.volume))

        # Apply fades
        if clip.fade_in > 0 or clip.fade_out > 0:
            ac = apply_audio_fade(ac, clip.fade_in, clip.fade_out, duration)

        context.audio_clips.append(ac.with_start(clip.start))
