"""
Factory for selecting the appropriate clip processor.
"""
import logging
from typing import Any, List, Optional

from .base import ClipProcessor
from .video import VideoClipProcessor
from .image import ImageClipProcessor
from .bgm import BGMClipProcessor
from .voice import VoiceClipProcessor
from .drawtext import DrawTextClipProcessor
from .effect import EffectClipProcessor

logger = logging.getLogger(__name__)


class ProcessorFactory:
    """Registry-based factory that dispatches clips to the correct processor."""

    def __init__(self) -> None:
        self._processors: List[ClipProcessor] = [
            VideoClipProcessor(),
            ImageClipProcessor(),
            BGMClipProcessor(),
            VoiceClipProcessor(),
            DrawTextClipProcessor(),
            EffectClipProcessor(),
        ]

    def get_processor(self, clip: Any) -> Optional[ClipProcessor]:
        """
        Return the first processor that supports the given clip.

        Args:
            clip: A clip model instance.

        Returns:
            The matching ClipProcessor, or None if no processor supports the clip.
        """
        for processor in self._processors:
            if processor.supports(clip):
                return processor
        logger.warning(f"No processor found for clip type: {type(clip).__name__}")
        return None
