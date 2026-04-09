"""
Timeline models for Script2Video.
Defines Track, Scene, GlobalConfig, and Timeline with JSON serialization.
"""
from typing import Optional, List, Tuple, Generic
from pydantic import BaseModel, Field
from enum import Enum
from .clips import ClipType

class TrackType(str, Enum):
    VIDEO = "video"
    IMAGE = "image"
    BGM = "bgm"
    VOICE = "voice"
    DRAWTEXT = "drawtext"
    EFFECT = "effect"

class Track(BaseModel,Generic[ClipType]):
    """Track containing clips of a specific type."""
    type: TrackType = Field(..., description="Type of clips in this track")
    desc: Optional[str] = Field(None, description="Track description")
    clips: List[ClipType] = Field(
        default_factory=list, description="List of clips in this track"
    )
    

class Scene(BaseModel):
    """Scene containing multiple tracks."""
    duration: float =  Field(..., description="Scene duration")
    type: str = Field(..., description="Scene type (e.g., HOOK, INTRO, OUTRO)")
    key_point: Optional[str] = Field(None, description="Key narrative point of the scene")
    emotion: Optional[str] = Field(None, description="Emotional tone of the scene")
    tracks: List[Track] = Field(default_factory=list, description="List of tracks in this scene")
    
    def add_track(self,track:Track) -> "Scene":
        self.tracks.append(track)
        return self


class TTSConfig(BaseModel):
    """TTS (Text-to-Speech) configuration."""
    provider: str = Field("edge-tts", description="TTS provider (edge-tts, azure, etc.)")
    default_speaker: str = Field("zh-CN-XiaoxiaoNeural", description="Default speaker voice")
    default_speed: float = Field(1.0, gt=0, le=2, description="Default speech speed (0.5-2.0)")
    default_emotion: Optional[str] = Field(None, description="Default emotion style")
    
    _params:dict = {}
    
    def set_params(self,params:dict):
        self._params = params
        
    @property
    def params(self):
        return self._params
        
    

class SubtitleConfig(BaseModel):
    """Subtitle display configuration."""
    width_ratio: float = Field(0.8, gt=0, le=1, description="Subtitle width as ratio of video width (0-1)")
    font_size_ratio: float = Field(0.04, gt=0, le=0.2, description="Font size as ratio of video height")
    default_color: str = Field("#FFFF00", description="Default subtitle color (hex)")
    background_opacity: float = Field(0.7, ge=0, le=1, description="Background opacity (0-1)")
    position_y_ratio: float = Field(0.85, ge=0, le=1, description="Vertical position as ratio of height")


class GlobalConfig(BaseModel):
    """Global video configuration."""
    resolution: Tuple = Field((1920,1080), description="Video resolution with 'w' and 'h'")
    fps: int = Field(30, gt=0, description="Frames per second")
    global_volume: float = Field(1.0, ge=0, le=1, description="Master volume (0-1)")
    tts: TTSConfig = Field(default_factory=TTSConfig, description="TTS configuration")
    subtitle: SubtitleConfig = Field(default_factory=SubtitleConfig, description="Subtitle configuration")


class Draft(BaseModel):
    """Complete video timeline with all scenes and configuration."""
    title: str = Field(..., description="Video title")
    tags: list[str] = Field(default_factory=list, description="Video tags for categorization")
    config: GlobalConfig = Field(..., description="Global video configuration")
    scenes: list[Scene] = Field(default_factory=list, description="List of scenes in the video")

    @classmethod
    def from_json(cls, json_path: str) -> "Draft":
        """
        Load timeline from JSON file.

        Args:
            json_path: Path to JSON file

        Returns:
            Draft instance

        Raises:
            ValueError: If file cannot be read or JSON is invalid
        """
        import json

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Pydantic can handle nested dict structures automatically
            # Just pass the entire data dict to the constructor
            return cls(**data)

        except (IOError, OSError) as e:
            raise ValueError(f"Failed to read file {json_path}: {e}") from e
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {json_path}: {e}") from e
        except Exception as e:
            raise ValueError(f"Failed to parse Draft from {json_path}: {e}") from e

    def to_json(self, json_path: str):
        """
        Save timeline to JSON file.

        Args:
            json_path: Path to output JSON file

        Raises:
            ValueError: If file cannot be written
        """
        import json
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.model_dump(), f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            raise ValueError(f"Failed to write file {json_path}: {e}") from e
