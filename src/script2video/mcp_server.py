"""
MCP Server for Script2Video - JSON-driven video editing service.

This server exposes video editing capabilities through the Model Context Protocol,
allowing LLMs to create and render videos programmatically.
"""
from mcp.server.fastmcp import FastMCP
from typing import Optional, List, Dict, Any
from pathlib import Path

from .api.draft import VideoDraft
from .api.builders import (
    ImageTrackBuilder,
    VideoTrackBuilder,
    VoiceTrackBuilder,
    BGMTrackBuilder,
    DrawTextTrackBuilder,
    EffectTrackBuilder
)

# Create MCP server
mcp = FastMCP("Script2Video")

# Global state to store drafts (in production, use proper storage)
_drafts: Dict[str, VideoDraft] = {}


@mcp.tool()
def create_draft(
    resolution_width: int = 1920,
    resolution_height: int = 1080,
    fps: int = 30,
    title: str = "Untitled Video"
) -> Dict[str, Any]:
    """
    Create a new video draft with specified configuration.

    Args:
        resolution_width: Video width in pixels (default: 1920)
        resolution_height: Video height in pixels (default: 1080)
        fps: Frames per second (default: 30)
        title: Video title (default: "Untitled Video")

    Returns:
        Dict with draft_id and configuration details
    """
    draft = VideoDraft.create(
        resolution=(resolution_width, resolution_height),
        fps=fps,
        title=title
    )
    draft_id = title.replace(" ", "_").lower()
    _drafts[draft_id] = draft

    return {
        "draft_id": draft_id,
        "title": title,
        "resolution": {"width": resolution_width, "height": resolution_height},
        "fps": fps,
        "message": f"Draft '{title}' created successfully"
    }


@mcp.tool()
def add_scene(
    draft_id: str,
    duration: float,
    scene_type: str = "DEFAULT",
    key_point: Optional[str] = None,
    emotion: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add a new scene to an existing draft.

    Args:
        draft_id: ID of the draft to add scene to
        duration: Scene duration in seconds
        scene_type: Scene type (e.g., HOOK, INTRO, OUTRO, DEFAULT)
        key_point: Key narrative point of the scene
        emotion: Emotional tone (e.g., 积极, 专业, 热情)

    Returns:
        Dict with scene index and details
    """
    if draft_id not in _drafts:
        return {"error": f"Draft '{draft_id}' not found"}

    draft = _drafts[draft_id]
    scene = draft.add_scene(
        duration=duration,
        scene_type=scene_type,
        key_point=key_point,
        emotion=emotion
    )

    scene_index = len(draft.scenes) - 1
    return {
        "draft_id": draft_id,
        "scene_index": scene_index,
        "scene_type": scene_type,
        "duration": duration,
        "message": f"Scene {scene_index} added to draft '{draft_id}'"
    }


@mcp.tool()
def add_image_track(
    draft_id: str,
    scene_index: int,
    clips: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Add an image track with clips to a scene.

    Args:
        draft_id: ID of the draft
        scene_index: Index of the scene to add track to
        clips: List of image clip configurations, each with:
            - desc: Clip description/prompt
            - source: Image file path
            - start: Start time in seconds
            - opacity: Opacity (0-1, default: 1.0)
            - fit_mode: "cover", "contain", or "fill" (default: "cover")
            - transform: Optional dict with position {x, y}, scale, rotation
            - animation: Optional dict with enter/exit animations

    Returns:
        Dict with track details
    """
    if draft_id not in _drafts:
        return {"error": f"Draft '{draft_id}' not found"}

    draft = _drafts[draft_id]
    scene = draft.get_scene(scene_index)
    if not scene:
        return {"error": f"Scene {scene_index} not found"}

    builder = ImageTrackBuilder()
    for clip_data in clips:
        builder.add_clip(**clip_data)

    track = builder.build()
    scene.add_track(track)

    return {
        "draft_id": draft_id,
        "scene_index": scene_index,
        "track_type": "image",
        "clips_count": len(clips),
        "message": f"Image track with {len(clips)} clips added"
    }


@mcp.tool()
def add_video_track(
    draft_id: str,
    scene_index: int,
    clips: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Add a video track with clips to a scene.

    Args:
        draft_id: ID of the draft
        scene_index: Index of the scene
        clips: List of video clip configurations, each with:
            - desc: Clip description
            - source: Video file path
            - start: Start time in seconds
            - in_time: Start time within source video
            - opacity: Opacity (0-1, default: 1.0)
            - fit_mode: "cover", "contain", or "fill"
            - volume: Volume in dB (default: 0)
            - transform: Optional transform dict
            - animation: Optional animation dict

    Returns:
        Dict with track details
    """
    if draft_id not in _drafts:
        return {"error": f"Draft '{draft_id}' not found"}

    draft = _drafts[draft_id]
    scene = draft.get_scene(scene_index)
    if not scene:
        return {"error": f"Scene {scene_index} not found"}

    builder = VideoTrackBuilder()
    for clip_data in clips:
        builder.add_clip(**clip_data)

    track = builder.build()
    scene.add_track(track)

    return {
        "draft_id": draft_id,
        "scene_index": scene_index,
        "track_type": "video",
        "clips_count": len(clips),
        "message": f"Video track with {len(clips)} clips added"
    }


@mcp.tool()
def add_voice_track(
    draft_id: str,
    scene_index: int,
    clips: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Add a voice/TTS track with clips to a scene.

    Args:
        draft_id: ID of the draft
        scene_index: Index of the scene
        clips: List of voice clip configurations, each with:
            - desc: Voice style description
            - text: Text to synthesize (≤10 Chinese characters)
            - start: Start time in seconds
            - tts_config: Optional TTS config dict
            - volume: Volume in dB (default: 0)
            - add_subtitle: Whether to add subtitle (default: True)

    Returns:
        Dict with track details
    """
    if draft_id not in _drafts:
        return {"error": f"Draft '{draft_id}' not found"}

    draft = _drafts[draft_id]
    scene = draft.get_scene(scene_index)
    if not scene:
        return {"error": f"Scene {scene_index} not found"}

    builder = VoiceTrackBuilder()
    for clip_data in clips:
        builder.add_clip(**clip_data)

    track = builder.build()
    scene.add_track(track)

    return {
        "draft_id": draft_id,
        "scene_index": scene_index,
        "track_type": "voice",
        "clips_count": len(clips),
        "message": f"Voice track with {len(clips)} clips added"
    }


@mcp.tool()
def add_bgm_track(
    draft_id: str,
    scene_index: int,
    clips: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Add a background music track with clips to a scene.

    Args:
        draft_id: ID of the draft
        scene_index: Index of the scene
        clips: List of BGM clip configurations, each with:
            - desc: Music description
            - source: Audio file path
            - start: Start time in seconds
            - end: End time in seconds
            - volume: Volume in dB (default: -12)
            - fade_in: Fade in duration (default: 0)
            - fade_out: Fade out duration (default: 0)
            - loop: Whether to loop (default: False)

    Returns:
        Dict with track details
    """
    if draft_id not in _drafts:
        return {"error": f"Draft '{draft_id}' not found"}

    draft = _drafts[draft_id]
    scene = draft.get_scene(scene_index)
    if not scene:
        return {"error": f"Scene {scene_index} not found"}

    builder = BGMTrackBuilder()
    for clip_data in clips:
        builder.add_clip(**clip_data)

    track = builder.build()
    scene.add_track(track)

    return {
        "draft_id": draft_id,
        "scene_index": scene_index,
        "track_type": "bgm",
        "clips_count": len(clips),
        "message": f"BGM track with {len(clips)} clips added"
    }


@mcp.tool()
def add_text_track(
    draft_id: str,
    scene_index: int,
    clips: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Add a text overlay track with clips to a scene.

    Args:
        draft_id: ID of the draft
        scene_index: Index of the scene
        clips: List of text clip configurations, each with:
            - desc: Text purpose description
            - text: Text content (1-5 words)
            - start: Start time in seconds
            - end: End time in seconds
            - style: Optional style dict (font, size, color, position)
            - animation: Optional animation dict

    Returns:
        Dict with track details
    """
    if draft_id not in _drafts:
        return {"error": f"Draft '{draft_id}' not found"}

    draft = _drafts[draft_id]
    scene = draft.get_scene(scene_index)
    if not scene:
        return {"error": f"Scene {scene_index} not found"}

    builder = DrawTextTrackBuilder()
    for clip_data in clips:
        builder.add_clip(**clip_data)

    track = builder.build()
    scene.add_track(track)

    return {
        "draft_id": draft_id,
        "scene_index": scene_index,
        "track_type": "drawtext",
        "clips_count": len(clips),
        "message": f"Text track with {len(clips)} clips added"
    }


@mcp.tool()
def add_effect_track(
    draft_id: str,
    scene_index: int,
    clips: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Add a visual effect track with clips to a scene.

    Args:
        draft_id: ID of the draft
        scene_index: Index of the scene
        clips: List of effect clip configurations, each with:
            - desc: Effect description
            - effect_type: "blur", "brightness", "contrast", "grayscale", "vignette"
            - start: Start time in seconds
            - end: End time in seconds
            - params: Optional effect parameters dict

    Returns:
        Dict with track details
    """
    if draft_id not in _drafts:
        return {"error": f"Draft '{draft_id}' not found"}

    draft = _drafts[draft_id]
    scene = draft.get_scene(scene_index)
    if not scene:
        return {"error": f"Scene {scene_index} not found"}

    builder = EffectTrackBuilder()
    for clip_data in clips:
        builder.add_clip(**clip_data)

    track = builder.build()
    scene.add_track(track)

    return {
        "draft_id": draft_id,
        "scene_index": scene_index,
        "track_type": "effect",
        "clips_count": len(clips),
        "message": f"Effect track with {len(clips)} clips added"
    }


@mcp.tool()
def export_json(
    draft_id: str,
    output_path: str
) -> Dict[str, Any]:
    """
    Export draft to JSON file.

    Args:
        draft_id: ID of the draft to export
        output_path: Path to output JSON file

    Returns:
        Dict with export status
    """
    if draft_id not in _drafts:
        return {"error": f"Draft '{draft_id}' not found"}

    draft = _drafts[draft_id]
    try:
        draft.export_json(output_path)
        return {
            "draft_id": draft_id,
            "output_path": output_path,
            "message": f"Draft exported to {output_path}"
        }
    except Exception as e:
        return {"error": f"Export failed: {str(e)}"}


@mcp.tool()
def render_video(
    draft_id: str,
    output_path: str,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Render draft to video file.

    Args:
        draft_id: ID of the draft to render
        output_path: Path to output video file (e.g., output.mp4)
        verbose: Whether to show detailed rendering logs (default: True)

    Returns:
        Dict with render status
    """
    if draft_id not in _drafts:
        return {"error": f"Draft '{draft_id}' not found"}

    draft = _drafts[draft_id]
    try:
        draft.render(output_path, verbose=verbose)
        return {
            "draft_id": draft_id,
            "output_path": output_path,
            "message": f"Video rendered successfully to {output_path}"
        }
    except Exception as e:
        return {"error": f"Render failed: {str(e)}"}


@mcp.tool()
def load_from_json(
    json_path: str,
    draft_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Load a draft from JSON file.

    Args:
        json_path: Path to JSON file
        draft_id: Optional custom draft ID (defaults to filename)

    Returns:
        Dict with loaded draft details
    """
    try:
        draft = VideoDraft.from_json(json_path)
        if draft_id is None:
            draft_id = Path(json_path).stem

        _drafts[draft_id] = draft

        return {
            "draft_id": draft_id,
            "title": draft.draft.title,
            "scenes_count": len(draft.scenes),
            "message": f"Draft loaded from {json_path}"
        }
    except Exception as e:
        return {"error": f"Load failed: {str(e)}"}


@mcp.tool()
def list_drafts() -> Dict[str, Any]:
    """
    List all active drafts in memory.

    Returns:
        Dict with list of draft IDs and their details
    """
    drafts_info = []
    for draft_id, draft in _drafts.items():
        drafts_info.append({
            "draft_id": draft_id,
            "title": draft.draft.title,
            "scenes_count": len(draft.scenes),
            "resolution": draft.draft.config.resolution,
            "fps": draft.draft.config.fps
        })

    return {
        "drafts": drafts_info,
        "total_count": len(drafts_info)
    }


@mcp.tool()
def get_draft_info(draft_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a draft.

    Args:
        draft_id: ID of the draft

    Returns:
        Dict with draft details including scenes and tracks
    """
    if draft_id not in _drafts:
        return {"error": f"Draft '{draft_id}' not found"}

    draft = _drafts[draft_id]
    scenes_info = []

    for idx, scene in enumerate(draft.scenes):
        tracks_info = []
        for track in scene.tracks:
            tracks_info.append({
                "type": track.type.value,
                "clips_count": len(track.clips)
            })

        scenes_info.append({
            "index": idx,
            "type": scene.type,
            "duration": scene.duration,
            "key_point": scene.key_point,
            "emotion": scene.emotion,
            "tracks": tracks_info
        })

    return {
        "draft_id": draft_id,
        "title": draft.draft.title,
        "resolution": {
            "width": draft.draft.config.resolution[0],
            "height": draft.draft.config.resolution[1]
        },
        "fps": draft.draft.config.fps,
        "scenes": scenes_info
    }


# Run the server
if __name__ == "__main__":
    import sys

    # Default to streamable HTTP transport
    transport = "streamable-http"
    host = "127.0.0.1"
    port = 8000

    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "stdio":
            transport = "stdio"

    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        print(f"Starting Script2Video MCP Server on {host}:{port}")
        mcp.run(transport="streamable-http", host=host, port=port, json_response=True)
