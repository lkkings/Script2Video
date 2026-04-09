"""
Base Pydantic models for Script2Video.
Reusable primitives for positions, transforms, time ranges, colors, and animations.
"""
from typing import Optional, Literal, Tuple
from pydantic import BaseModel, Field, field_validator
import re


class Position(BaseModel):
    """
    Coordinate position in 2D space.
    Supports both pixel coordinates (int) and normalized coordinates (0-1 float).
    """
    x: float | int = Field(..., description="X coordinate (pixels or normalized 0-1)")
    y: float | int = Field(..., description="Y coordinate (pixels or normalized 0-1)")


class Transform(BaseModel):
    """
    Spatial transformation with position, scale, and rotation.
    Used for positioning and transforming video/image clips.
    """
    position: Position = Field(..., description="Center position of the element")
    scale: float = Field(default=1.0, gt=0, description="Scale factor (must be positive)")
    rotation: float = Field(default=0.0, description="Rotation angle in degrees")


class Color(BaseModel):
    """
    Hex color representation.
    Validates hex color format (#RGB or #RRGGBB).
    """
    value: str = Field(..., description="Hex color string (e.g., #FF5733 or #FFF)")

    @field_validator("value")
    @classmethod
    def validate_hex_color(cls, v):
        """Validate hex color format."""
        if not re.match(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", v):
            raise ValueError("Invalid hex color format. Use #RGB or #RRGGBB")
        return v


# ── Animation types ─────────────────────────────────────────────────────────

AnimationEffect = Literal[
    "fade_in", "fade_out",
    "slide_left", "slide_right", "slide_up", "slide_down",
    "zoom_in", "zoom_out",
    "rotate_in", "rotate_out",
    "bounce_in",
    "none",
]


class AnimationConfig(BaseModel):
    """
    Configuration for a single animation phase (in or out).

    Example JSON:
        {"effect": "fade_in", "duration": 0.5, "easing": "ease_in_out"}
    Or shorthand string: "fade_in"  (duration defaults to 0.5s)
    """
    effect: AnimationEffect = Field(..., description="Animation effect type")
    duration: float = Field(0.5, gt=0, le=10, description="Animation duration in seconds")
    easing: Literal[
        "linear", "ease_in", "ease_out", "ease_in_out"
    ] = Field("ease_in_out", description="Easing function for the animation curve")


class Animation(BaseModel):
    """
    Animation specification for clip enter/exit transitions.

    Supports two forms in JSON:
      - Structured: {"enter": {"effect": "fade_in", "duration": 0.5}, "exit": {"effect": "zoom_out"}}
      - Shorthand:  {"enter": "fade_in", "exit": "zoom_out"}  (uses default duration/easing)
    """
    enter: Optional[AnimationConfig] = Field(
        None, description="Entry animation (played at clip start)"
    )
    exit: Optional[AnimationConfig] = Field(
        None, description="Exit animation (played at clip end)"
    )

    model_config = {"populate_by_name": True}

    @field_validator("enter", "exit", mode="before")
    @classmethod
    def _coerce_shorthand(cls, v):
        """Accept a plain string like 'fade_in' and expand to full config."""
        if isinstance(v, str):
            return {"effect": v}
        return v

class TTSConfig(BaseModel):
    speaker: str = Field(None, description="Speaker name")
    speed: float = Field(1.0, description="Speech speed")
    emotion: str = Field("neutral", description="Emotion style")


class FontStyle(BaseModel):
    """Minimal font style for subtitle clips"""

    font_family: str = Field(
        "Arial",
        description="Font family name"
    )

    font_size_ratio: float = Field(
        0.05,
        description="Font size relative to video height"
    )

    color: str = Field(
        "#FFFFFF",
        description="Text color (hex)"
    )

    position: Tuple[float, float] = Field(
        (0.5, 0.9),
        description="(x_ratio, y_ratio), e.g. bottom center"
    )
    
    # ------------------------
    # Validators（关键增强）
    # ------------------------

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str):
        if not isinstance(v, str) or not v.startswith("#") or len(v) not in (7, 9):
            raise ValueError("color must be hex format like #RRGGBB or #RRGGBBAA")
        return v

    @field_validator("position")
    @classmethod
    def validate_position(cls, v: Tuple[float, float]):
        x, y = v
        if not (0 <= x <= 1 and 0 <= y <= 1):
            raise ValueError("position values must be between 0 and 1")
        return v