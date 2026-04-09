"""
Clip models for Script2Video.
Defines all clip types: video, image, bgm, voice, drawtext, effect.
"""
from optparse import Option
from typing import Optional, Literal, TypeVar
from pydantic import BaseModel, Field
from .base import Transform, Animation,TTSConfig,FontStyle



class BaseClip(BaseModel):
    desc: str = Field(
        ...,
        description="Clip desc"
    )
    
    start: float = Field(
        ...,
        ge=0,
        description="Start time of the effect on the timeline (in seconds)"
    )
    
    end: float = Field(
        0,
        ge=0,
        description="End time of the effect on the timeline (in seconds); must be greater than start"
    )

ClipType = TypeVar("T", bound=BaseClip)


class VideoClip(BaseClip):
    """Represents a video clip with source media, timeline placement, and visual properties."""
    
    source: str = Field(
        ..., 
        description="File path of the source video asset"
    )
    
    in_time: Optional[float] = Field(
        None, 
        ge=0, 
        description="Start time within the source video (in seconds); defaults to beginning if not set"
    )
    
    volume: Optional[float] = Field(
        0,
        description="Playback gain in decibels (dB); 0 is original volume"
    )
    
    transform: Optional[Transform] = Field(
        None, 
        description="Spatial transformation applied to the clip (e.g., position, scale, rotation)"
    )
    
    opacity: float = Field(
        1.0, 
        ge=0, 
        le=1, 
        description="Opacity of the clip where 0 is fully transparent and 1 is fully opaque"
    )
    
    fit_mode: Literal["cover", "contain", "fill"] = Field(
        "cover", 
        description="Scaling behavior of the video within its frame: cover (crop to fill), contain (fit with letterboxing), or fill (stretch to fit)"
    )
    
    animation: Optional[Animation] = Field(
        None, 
        description="Optional enter and/or exit animation applied to the clip"
    )

class ImageClip(BaseClip):
    """Represents a static image clip placed on the timeline with optional transformations and animations."""
    source: str = Field(
        ..., 
        description="File path or URI of the source image asset"
    )
    
    transform: Optional[Transform] = Field(
        None, 
        description="Spatial transformation applied to the image (e.g., position, scale, rotation)"
    )
    
    opacity: float = Field(
        1.0, 
        ge=0, 
        le=1, 
        description="Opacity of the image where 0 is fully transparent and 1 is fully opaque"
    )
    
    animation: Optional[Animation] = Field(
        None, 
        description="Optional enter and/or exit animation applied to the image"
    )
    
    fit_mode: Literal["cover", "contain", "fill"] = Field(
        "cover", 
        description="Scaling behavior of the image within its frame: cover (crop to fill), contain (fit with letterboxing), or fill (stretch to fit)"
    )

class BGMClip(BaseClip):
    """Represents a background music clip placed on the timeline with volume and playback controls."""
    desc: str = Field(
        ...,
        description="Background music description. Use short phrases to describe mood, tempo, and style (e.g., upbeat, fast tempo, corporate). No sentences"
    )
    
    source: str = Field(
        ..., 
        description="File path or URI of the source audio asset"
    )
    
    volume: float = Field(
        -12, 
        description="Playback gain in decibels (dB); negative values attenuate volume, 0 represents original level"
    )
    
    fade_in: float = Field(
        0, 
        ge=0, 
        description="Duration of the fade-in effect at the beginning of the clip (in seconds)"
    )
    
    fade_out: float = Field(
        0, 
        ge=0, 
        description="Duration of the fade-out effect at the end of the clip (in seconds)"
    )
    
    loop: bool = Field(
        False, 
        description="Whether the audio should loop to fill the entire clip duration if the source is shorter"
    )
    
class VoiceClip(BaseClip):
    """Represents a character voice-over clip generated via TTS."""
    desc: str = Field(
        ...,
        description="Voice style prompt. Describe speaker role, tone, and emotion in short phrases (no sentences)"
    )

    
    text: str = Field(
        ...,
        description="Character voice line. MUST be ≤10 Chinese characters, NO punctuation, spoken style only"
    )
    
    tts_config: TTSConfig = Field(
        default_factory=TTSConfig,
        description="TTS settings including speaker, speed, and emotion"
    )
    
    volume: float = Field(
        0,
        description="Playback gain in decibels (dB); 0 is original volume"
    )
    
    add_subtitle: bool = Field(True)
    
class DrawTextClip(BaseClip):
    """Represents a text overlay clip rendered on the timeline."""
    desc: str = Field(
        ...,
        description="Highlight caption prompt. Use short phrases to emphasize key points, appear at key moments, and avoid covering main subjects"
    )
    
    text: str = Field(
        ...,
        description="Stylized highlight caption (bullet-style text). Keep it very short (1–5 words), show only at key emphasis moments, and position it to avoid blocking important content such as faces or main visuals"
    )
    
    style: FontStyle = Field(
        default_factory=FontStyle,
        description="Text styling options including font, size, color, and alignment"
    )
    
    animation: Optional[Animation] = Field(
        None,
        description="Optional enter and/or exit animation applied to the text"
    )


class EffectClip(BaseClip):
    """Represents a visual effect applied over a time range on the timeline."""
    
    effect_type: Literal["blur", "brightness", "contrast", "grayscale", "vignette"] = Field(
        ...,
        description="Visual effect type to apply (e.g., blur, brightness adjustment, contrast enhancement, grayscale, vignette)"
    )
    
    
    _params:dict = {}
    
    def set_params(self,params:dict):
        self._params = params
        
    @property
    def params(self):
        return self._params
        