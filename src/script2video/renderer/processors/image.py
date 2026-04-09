"""
Processor for image clips.
"""
import os
import logging
from typing import Any

from moviepy.video.VideoClip import ImageClip

from ...models.clips import ImageClip as ImageClipModel
from .base import ClipProcessor, RenderContext
from .helpers import _apply_fit_mode, _apply_animation

logger = logging.getLogger(__name__)


class ImageClipProcessor(ClipProcessor):
    """Processes image track clips."""

    def supports(self, clip: Any) -> bool:
        return isinstance(clip, ImageClipModel)

    def process(self, clip: ImageClipModel, context: RenderContext) -> None:
        if not os.path.exists(clip.source):
            raise FileNotFoundError(f"Image file not found: {clip.source}")
        logger.info(f"Processing image clip: {clip.source}...")

        width, height = context.width, context.height
        duration = clip.end - clip.start
        ic = ImageClip(clip.source).with_duration(duration)

        # Apply fit_mode
        ic = _apply_fit_mode(ic, clip.fit_mode, width, height)

        # Apply transform
        if clip.transform:
            if clip.transform.scale != 1.0:
                ic = ic.resized(clip.transform.scale)

            if clip.transform.rotation != 0:
                ic = ic.rotated(clip.transform.rotation, expand=True)

            pos_x = clip.transform.position.x
            pos_y = clip.transform.position.y

            if 0 <= pos_x <= 1:
                pos_x = int(pos_x * width)
            if 0 <= pos_y <= 1:
                pos_y = int(pos_y * height)

            px = int(pos_x - ic.w // 2)
            py = int(pos_y - ic.h // 2)
            ic = ic.with_position((px, py))
        else:
            px = (width - ic.w) // 2
            py = (height - ic.h) // 2
            ic = ic.with_position((px, py))

        if clip.opacity < 1.0:
            ic = ic.with_opacity(clip.opacity)

        ic = ic.with_start(clip.start)

        # Apply animation
        ic = _apply_animation(ic, clip.animation, duration, width, height)

        context.video_layers.append(ic)
