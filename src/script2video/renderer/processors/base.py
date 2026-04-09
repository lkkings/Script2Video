"""
Base classes for clip processors.
Defines RenderContext (shared state) and ClipProcessor (abstract base).
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional, List, Tuple

from ...models.draft import GlobalConfig
from ...tts import TTSProvider


@dataclass
class RenderContext:
    """Shared rendering state passed to all processors."""
    width: int
    height: int
    config: GlobalConfig  # GlobalConfig
    video_layers: List[Any] = field(default_factory=list)
    audio_clips: List[Any] = field(default_factory=list)
    tts_provider: Optional[TTSProvider] = None
    clips_to_close: List[Any] = field(default_factory=list)
    temp_audio_files: List[str] = field(default_factory=list)
    effect_segments: List[Tuple[float, float, Any]] = field(default_factory=list)


class ClipProcessor(ABC):
    """Abstract base class for clip processors."""

    @abstractmethod
    def supports(self, clip: Any) -> bool:
        """Return True if this processor can handle the given clip type."""
        ...

    @abstractmethod
    def process(self, clip: Any, context: RenderContext) -> None:
        """
        Process a clip and update the render context.

        Results should be appended to context.video_layers / context.audio_clips.
        Resources that need cleanup go into context.clips_to_close / context.temp_audio_files.
        """
        ...
