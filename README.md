# Script2Video

JSON-driven non-linear video editor that converts timeline specifications into rendered videos.

## Features

- **Multi-track compositing** - Layer video, images, text, and effects on a timeline
- **TTS integration** - Text-to-speech with auto-generated subtitles (Edge TTS, Azure, DashScope)
- **Builder API** - Fluent Python API for programmatic video creation
- **JSON schema** - Declarative timeline format with scenes, tracks, and clips
- **Effects pipeline** - Blur, brightness, contrast, grayscale, vignette
- **MCP server** - Model Context Protocol integration for LLM-driven video editing

## Quick Start

### Prerequisites

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/) package manager
- FFmpeg (for video encoding)

### Installation

```bash
git clone https://github.com/lkkings/Script2Video.git
cd Script2Video
uv sync
```

### CLI Usage

```bash
# Render a video from JSON timeline
script2video --json script.json --output output.mp4

# Or run directly
python -m script2video --json script.json --output output.mp4
```

### Python API

```python
from src.script2video import VideoDraft, ImageTrackBuilder, VoiceTrackBuilder

# Create a draft (1080x1920 vertical video)
draft = VideoDraft.create(resolution=(1080, 1920), fps=30)

# Add a scene
scene = draft.add_scene(duration=10, scene_type="INTRO", key_point="Opening")

# Add image track
scene.add_track(
    ImageTrackBuilder()
    .add_clip(
        desc="Background",
        source="assets/background.png",
        start=0,
        fit_mode="cover"
    )
    .build()
)

# Add voice track (TTS with auto subtitles)
scene.add_track(
    VoiceTrackBuilder()
    .add_clip(desc="Narration", text="Welcome to my video!", start=0)
    .build()
)

# Export and render
draft.export_json("my_video.json")
draft.render("my_video.mp4")
```

## JSON Timeline Schema

```json
{
  "title": "My Video",
  "config": {
    "resolution": [1080, 1920],
    "fps": 30,
    "global_volume": 1.0,
    "tts": {
      "provider": "edge-tts",
      "default_speaker": "zh-CN-XiaoxiaoNeural"
    },
    "subtitle": {
      "font_size_ratio": 0.04,
      "default_color": "#FFFF00",
      "position_y_ratio": 0.85
    }
  },
  "scenes": [
    {
      "duration": 10.0,
      "type": "INTRO",
      "tracks": [
        {
          "type": "image",
          "clips": [{ "desc": "bg", "source": "bg.png", "start": 0, "fit_mode": "cover" }]
        },
        {
          "type": "voice",
          "clips": [{ "desc": "narration", "text": "Hello!", "start": 0 }]
        }
      ]
    }
  ]
}
```

## Track Types

| Type | Description | Key Features |
|------|-------------|--------------|
| `video` | Video clips | Transform, opacity, fit modes, source trimming |
| `image` | Static images | Transform, animations (fade_in, slide_in), fit modes |
| `bgm` | Background music | Volume (dB), fade in/out, looping |
| `voice` | TTS speech | Auto subtitle generation, multiple providers |
| `drawtext` | Text overlays | Custom fonts, colors, positioning, animations |
| `effect` | Post-processing | Blur, brightness, contrast, grayscale, vignette |

## MCP Server

Script2Video includes a Model Context Protocol server for LLM integration. See [MCP Server Guide](README_MCP.md) for details.

```bash
# Start HTTP server
uv run run_mcp_server.py

# Or stdio mode for Claude Desktop
python run_mcp_server.py stdio
```

## Project Structure

```
src/script2video/
  models/         # Pydantic data models (Draft, Scene, Track, Clips)
  api/            # Fluent builder API (VideoDraft, TrackBuilders)
  renderer/       # MoviePy-based rendering engine
  effects/        # Effect registry and implementations
  tts/            # TTS providers (Edge, Azure, DashScope)
  mcp_server.py   # MCP server implementation
```

## Technical Notes

- **Coordinates**: Pixel or normalized (0-1) values, center-anchored transforms
- **Audio volume**: Specified in dB, converted via `10^(dB/20)`
- **Timing**: All timestamps in seconds; clips use `start`/`end` + `in`/`out` for source trimming

## License

MIT
