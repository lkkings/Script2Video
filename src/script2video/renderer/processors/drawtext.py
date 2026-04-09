"""
Processor for drawtext (subtitle/text overlay) clips.
"""
import logging
from typing import Any

from ...models.clips import DrawTextClip
from ..utils import make_subtitle_clip
from .base import ClipProcessor, RenderContext
from .helpers import _apply_animation

logger = logging.getLogger(__name__)


class DrawTextClipProcessor(ClipProcessor):
    """Processes drawtext/subtitle track clips."""

    def supports(self, clip: Any) -> bool:
        return isinstance(clip, DrawTextClip)

    def process(self, clip: DrawTextClip, context: RenderContext) -> None:
        logger.info(f"Processing drawtext clip: {clip.text}...")

        sc = make_subtitle_clip(
            text=clip.text,
            start=clip.start,
            end=clip.end,
            width=context.width,
            height=context.height,
            subtitle_config=context.config.subtitle,
            style=clip.style
        )
        duration = clip.end - clip.start
        sc = _apply_animation(sc, clip.animation, duration, context.width, context.height)
        context.video_layers.append(sc)
