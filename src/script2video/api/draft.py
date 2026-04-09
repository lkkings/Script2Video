"""
VideoDraft API for programmatic video editing.
"""
from typing import Optional,List
from ..models.draft import Draft, Scene, Track, GlobalConfig


class VideoDraft:
    """Fluent API for programmatic video editing."""

    def __init__(self, draft: Draft):
        """Initialize with a draft."""
        self._draft = draft

    @classmethod
    def create(
        cls,
        resolution: tuple[int, int],
        fps: int = 30,
        title: str = "Untitled",
        tags: List[str] = []
    ) -> "VideoDraft":
        """
        Create new video draft.

        Args:
            resolution: Video resolution as (width, height)
            fps: Frames per second (default: 30)
            title: Video title (default: "Untitled")

        Returns:
            New VideoDraft instance
        """
        config = GlobalConfig(
            resolution=resolution,
            fps=fps
        )
        draft = Draft(title=title, config=config,tags=tags)
        return cls(draft)

    @classmethod
    def from_json(cls, json_path: str) -> "VideoDraft":
        """
        Load draft from JSON file.

        Args:
            json_path: Path to JSON file

        Returns:
            VideoDraft instance loaded from file
        """
        return cls(Draft.from_json(json_path))

    def add_scene(
        self,
        duration: float,
        scene_type: str = "DEFAULT",
        key_point: Optional[str] = None,
        emotion: Optional[str] = None,
    ) -> Scene:
        """
        Add new scene to draft.

        Args:
            duration: Scene duration
            scene_type: Scene type (e.g., HOOK, INTRO, OUTRO)
            key_point: Key narrative point
            emotion: Emotional tone

        Returns:
            The created Scene object
        """
        scene = Scene(duration=duration,type=scene_type, key_point=key_point, emotion=emotion)
        self._draft.scenes.append(scene)
        return scene
    
    @property
    def scenes(self) -> List[Scene]:
        return self._draft.scenes

    def get_scene(self, index: int) -> Optional[Scene]:
        """
        Get scene by index.

        Args:
            index: Scene index

        Returns:
            Scene object or None if index out of range
        """
        if 0 <= index < len(self._draft.scenes):
            return self._draft.scenes[index]
        return None

    def remove_scene(self, index: int) -> bool:
        """
        Remove scene by index.

        Args:
            index: Scene index

        Returns:
            True if removed, False if index out of range
        """
        if 0 <= index < len(self._draft.scenes):
            self._draft.scenes.pop(index)
            return True
        return False

    def add_track(self, scene_index: int, track: Track) -> bool:
        """
        Add track to scene.

        Args:
            scene_index: Index of scene to add track to
            track: Track object to add

        Returns:
            True if added, False if scene index out of range
        """
        scene = self.get_scene(scene_index)
        if scene:
            scene.tracks.append(track)
            return True
        return False

    def remove_track(self, scene_index: int, track_index: int) -> bool:
        """
        Remove track from scene.

        Args:
            scene_index: Index of scene
            track_index: Index of track within scene

        Returns:
            True if removed, False if indices out of range
        """
        scene = self.get_scene(scene_index)
        if scene and 0 <= track_index < len(scene.tracks):
            scene.tracks.pop(track_index)
            return True
        return False

    def export_json(self, output_path: str):
        """
        Export draft to JSON file.

        Args:
            output_path: Path to output JSON file
        """
        self._draft.to_json(output_path)

    def render(self, output_path: str,verbose=True):
        """
        Render video to file.

        Args:
            output_path: Path to output video file
        """
        from ..renderer.engine import VideoRenderer
        renderer = VideoRenderer()
        renderer.render(self._draft, output_path,verbose=verbose)

    @property
    def draft(self) -> Draft:
        """Get the underlying draft object."""
        return self._draft
