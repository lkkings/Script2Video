"""
Abstract base class for video effects.
"""
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field
from moviepy.video.VideoClip import VideoClip


class EffectParams(BaseModel):
    """Base class for effect parameters."""
    intensity: float = Field(0.5, ge=0, le=1, description="Effect intensity (0-1)")


class BaseEffect(ABC):
    """Abstract base class for all video effects."""

    def __init__(self, params: dict[str, Any]):
        """Initialize effect with parameters."""
        self.params = self._validate_params(params)

    def _validate_params(self, params: dict[str, Any]) -> EffectParams:
        """Validate and convert params dict to EffectParams."""
        return EffectParams(**params)

    @abstractmethod
    def apply(self, clip: VideoClip) -> Any:
        """
        Apply effect to video clip.

        Args:
            clip: MoviePy VideoClip to apply effect to

        Returns:
            Modified VideoClip with effect applied
        """
        pass
