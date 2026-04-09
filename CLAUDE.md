# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Script2Video is a JSON-driven non-linear video editor that converts timeline specifications into rendered videos. The system uses a track-based architecture where multiple media types (video, audio, images, subtitles, effects) are composited together.

## Core Architecture

**Timeline Structure**: The project uses a JSON schema (`script.json`) that defines:
- Global config: resolution, fps, volume
- Scenes with multiple tracks
- Each track contains clips with timing and parameters

**Track Types**:
- `video`: Video file clips with transform (position, scale, rotation), opacity, fit modes
- `image`: Static images with transforms and animations
- `bgm`: Audio layers with volume (dB), fade in/out, looping
- `voice`: TTS-generated speech with auto-subtitle generation
- `drawtext`: Text overlays with styling and positioning
- `effect`: Post-processing filters (blur, brightness, contrast, grayscale, vignette)

**Reference Implementation**: The README.md contains a complete Python implementation using MoviePy that demonstrates the rendering pipeline: parse timeline → build effects → composite video layers → add subtitles → apply effects → mix audio → export.

## Development Commands

This is a Python project managed with `uv` (requires Python >=3.13):

```bash
# Install dependencies (when added to pyproject.toml)
uv sync

# Run the video editor (reference implementation)
python video_editor.py --json script.json --output output.mp4
```

## Key Technical Details

**Coordinate System**: Positions use pixel coordinates or normalized (0-1) values depending on context. Transform positions are center-anchored.

**Audio Volume**: Specified in dB (e.g., -12 dB for background music). Converted to linear scale via `10^(dB/20)`.

**Timing**: All timestamps in seconds. Clips define `start`/`end` on timeline, plus `in`/`out` for source trimming.

**Style References**: Text clips can use `style_ref` to reference predefined styles instead of inline styling.
