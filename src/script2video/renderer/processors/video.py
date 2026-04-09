"""
Processor for video clips.
"""
import os
import logging
from typing import Any

from moviepy import VideoFileClip

from ...models.clips import VideoClip as VideoClipModel
from .base import ClipProcessor, RenderContext
from .helpers import _apply_fit_mode, _apply_animation
from ..utils import db_to_linear

logger = logging.getLogger(__name__)


class VideoClipProcessor(ClipProcessor):
    """Processes video track clips."""

    def supports(self, clip: Any) -> bool:
        return isinstance(clip, VideoClipModel)

    def process(self, clip: VideoClipModel, context: RenderContext) -> None:
        if not os.path.exists(clip.source):
            raise FileNotFoundError(f"Video file not found: {clip.source}")
        logger.info(f"Processing video clip: {clip.source}...")

        # Load video
        clip_in = clip.in_time if clip.in_time is not None else 0
        duration = clip.end - clip.start
        clip_out = clip_in + duration
        
        vc: VideoFileClip = VideoFileClip(clip.source).subclipped(clip_in, clip_out)
        context.clips_to_close.append(vc)

        width, height = context.width, context.height

        # Apply fit_mode before any manual transform
        vc = _apply_fit_mode(vc, clip.fit_mode, width, height)

        # Apply transform (overrides position/scale from fit_mode if provided)
        if clip.transform:
            if clip.transform.scale != 1.0:
                vc = vc.resized(clip.transform.scale)

            if clip.transform.rotation != 0:
                vc = vc.rotated(clip.transform.rotation, expand=True)

            pos_x = clip.transform.position.x
            pos_y = clip.transform.position.y

            if 0 <= pos_x <= 1:
                pos_x = int(pos_x * width)
            if 0 <= pos_y <= 1:
                pos_y = int(pos_y * height)

            px = int(pos_x - vc.w // 2)
            py = int(pos_y - vc.h // 2)
            vc = vc.with_position((px, py))
        else:
            # Center in canvas by default (after fit_mode)
            px = (width - vc.w) // 2
            py = (height - vc.h) // 2
            vc = vc.with_position((px, py))

        if clip.opacity < 1.0:
            vc = vc.with_opacity(clip.opacity)

        vc = vc.with_start(clip.start).with_duration(duration)

        # Apply animation
        vc = _apply_animation(vc, clip.animation, duration, width, height)

        context.video_layers.append(vc)

        # Extract audio if present
        if vc.audio and clip.volume is not None:
            context.audio_clips.append(vc.audio.with_start(clip.start).with_duration(duration).with_volume_scaled(db_to_linear(clip.volume)))
