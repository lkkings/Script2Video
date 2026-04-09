"""
Script2Video - JSON-driven non-linear video editor.

This package provides a complete system for converting video scripts (JSON)
into rendered videos with Pydantic models, effects, and a fluent API.
"""
from .models.draft import Draft, Scene, Track, GlobalConfig
from .models.clips import (
    VideoClip,
    ImageClip,
    BGMClip,
    VoiceClip,
    DrawTextClip,
    EffectClip,
)
from .models.base import Position, Transform, Color, Animation, AnimationConfig
from .effects import BaseEffect, get_effect, EFFECT_REGISTRY
from .api.draft import VideoDraft
from .api.builders import ImageTrackBuilder,VideoTrackBuilder,VoiceTrackBuilder,BGMTrackBuilder,DrawTextTrackBuilder,EffectTrackBuilder

__version__ = "0.1.0"

__all__ = [
    # Draft models
    "Draft",
    "Scene",
    "Track",
    "GlobalConfig",
    # Clip models
    "VideoClip",
    "ImageClip",
    "BGMClip",
    "VoiceClip",
    "DrawTextClip",
    "EffectClip",
    # Base models
    "Position",
    "Transform",
    "Color",
    "Animation",
    "AnimationConfig",
    # Effects
    "BaseEffect",
    "get_effect",
    "EFFECT_REGISTRY",
    # API
    "VideoDraft",
    "ImageTrackBuilder",
    "VideoTrackBuilder",
    "VoiceTrackBuilder",
    "BGMTrackBuilder",
    "DrawTextTrackBuilder",
    "EffectTrackBuilder"
]