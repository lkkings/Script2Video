"""
Clip processors package.
Each processor handles one clip type and writes results into a shared RenderContext.
"""
from .base import RenderContext, ClipProcessor
from .factory import ProcessorFactory
from .video import VideoClipProcessor
from .image import ImageClipProcessor
from .bgm import BGMClipProcessor
from .voice import VoiceClipProcessor
from .drawtext import DrawTextClipProcessor
from .effect import EffectClipProcessor

__all__ = [
    "RenderContext",
    "ClipProcessor",
    "ProcessorFactory",
    "VideoClipProcessor",
    "ImageClipProcessor",
    "BGMClipProcessor",
    "VoiceClipProcessor",
    "DrawTextClipProcessor",
    "EffectClipProcessor",
]
