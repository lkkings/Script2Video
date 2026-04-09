"""
Processor for effect clips.
Collects effects into context.effect_segments for deferred application.
"""
import logging
from typing import Any

from ...models.clips import EffectClip
from ...effects import get_effect
from .base import ClipProcessor, RenderContext

logger = logging.getLogger(__name__)


class EffectClipProcessor(ClipProcessor):
    """Collects effect clips into context for later application."""

    def supports(self, clip: Any) -> bool:
        return isinstance(clip, EffectClip)

    def process(self, clip: EffectClip, context: RenderContext) -> None:
        try:
            params = getattr(clip, "params", {})
            effect = get_effect(clip.effect_type, params)
            context.effect_segments.append((clip.start, clip.end, effect))
        except Exception as e:
            logger.warning(f"Failed to create effect {clip.effect_type}: {e}")
