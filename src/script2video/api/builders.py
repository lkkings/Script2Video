"""
Builder helpers for creating tracks and clips programmatically.
"""
from typing import Optional,Generic,List,Any
from abc import ABC, abstractmethod
from ..models.draft import Track,TrackType
from ..models.clips import (
    ClipType,
    VideoClip,
    ImageClip,
    BGMClip,
    VoiceClip,
    DrawTextClip,
    EffectClip,
)

_CLIP_TYPE_MAP = {
    VideoClip: TrackType.VIDEO,
    ImageClip: TrackType.IMAGE,
    BGMClip: TrackType.BGM,
    VoiceClip: TrackType.VOICE,
    DrawTextClip: TrackType.DRAWTEXT,
    EffectClip: TrackType.EFFECT,
}

class TrackBuilder(ABC,Generic[ClipType]):
    """
    Chainable builder for creating tracks.

    Every clip method accepts **kwargs that are forwarded directly to the
    underlying Pydantic model, so all model fields are always available.
    """
    type: TrackType = None

    def __init__(self):
        self._clips: List[ClipType] = []
        self._desc: Optional[str] = None

    def desc(self, desc: str) -> "TrackBuilder[ClipType]":
        """Set track description."""
        self._desc = desc
        return self
    


    @abstractmethod
    def add_clip(self,*args: Any, **kwargs: Any) -> "TrackBuilder[ClipType]":
        raise NotImplementedError("TrackBuild need implement add_clip method")
    

    def build(self) -> Track:
        """
        Build the track.

        Raises:
            ValueError: If no clips were added
        """
        return Track(type=self.type,desc=self._desc, clips=self._clips)


class VideoTrackBuilder(TrackBuilder[VideoClip]):
    type = TrackType.VIDEO
    def add_clip(self,desc:str,source:str,start:float,in_time:float,opacity:float=1.0,fit_mode="cover",animation:Optional[dict]=None,transform:Optional[dict]=None,volume:float=0):
        data = dict(
            desc=desc,source=source, start=start, in_time=in_time,
            opacity=opacity, fit_mode=fit_mode,volume=volume
        )
        if transform is not None:
            data["transform"] = transform
        if animation is not None:
            data["animation"] = animation
        self._clips.append(VideoClip(**data))
        return self

class ImageTrackBuilder(TrackBuilder[ImageClip]):
    type = TrackType.IMAGE
    def add_clip(self,desc:str,source:str,start:float,opacity:float=1.0,fit_mode="cover",animation:Optional[dict]=None,transform:Optional[dict]=None):
        data = dict(
            desc=desc,source=source, start=start,
            opacity=opacity, fit_mode=fit_mode,
        )
        if transform is not None:
            data["transform"] = transform
        if animation is not None:
            data["animation"] = animation
        self._clips.append(ImageClip(**data))
        return self

class VoiceTrackBuilder(TrackBuilder[VoiceClip]):
    type = TrackType.VOICE
    def add_clip(self,desc:str,text:str,start:float,tts_config:Optional[dict]=None,volume:float=0,add_subtitle=True):
        data = dict(
            desc=desc,text=text, start=start,
            volume=volume, add_subtitle=add_subtitle,
        )
        if tts_config is not None:
            data["tts_config"] = tts_config
        self._clips.append(VoiceClip(**data))
        return self

class BGMTrackBuilder(TrackBuilder[BGMClip]):
    type = TrackType.BGM
    def add_clip(self,desc:str,source:str,start:float,end:float,fade_in:float=0,fade_out:float=0,volume:float=0,loop:bool=False):
        data = dict(
            desc=desc,source=source, start=start,end=end,loop=loop,
            volume=volume, fade_in=fade_in,fade_out=fade_out,
        )
        self._clips.append(BGMClip(**data))
        return self


class DrawTextTrackBuilder(TrackBuilder[DrawTextClip]):
    type = TrackType.DRAWTEXT
    def add_clip(self,desc:str,text:str,start:float,end:float,style:Optional[dict]=None,animation:Optional[dict]=None):
        data = dict(
            desc=desc,text=text,start=start,end=end
        )
        if style is not None:
            data["style"] = style
        if animation is not None:
            data["animation"] = animation
        self._clips.append(DrawTextClip(**data))
        return self

class EffectTrackBuilder(TrackBuilder[EffectClip]):
    type = TrackType.EFFECT
    def add_clip(self,desc:str,effect_type:str,start:float,end:float,style:Optional[dict]=None,animation:Optional[dict]=None,params:Optional[dict]=None):
        data = dict(
            desc=desc,effect_type=effect_type, start=start,end=end
        )
        if style is not None:
            data["style"] = style
        if animation is not None:
            data["animation"] = animation
        clip = EffectClip(**data)
        if params is not None:
            clip.set_params()
        self._clips.append(clip)
        return self

