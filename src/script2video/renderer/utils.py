"""
Rendering utilities for Script2Video.
Helper functions for audio processing, subtitle generation, and transformations.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Any, Optional
import os


def db_to_linear(db: float) -> float:
    """Convert dB to linear scale."""
    return 10 ** (db / 20.0)


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """
    Convert hex color to RGB tuple.

    Args:
        hex_color: Hex color string (e.g., "#FF5733" or "#FFF")

    Returns:
        RGB tuple (r, g, b) with values 0-255

    Raises:
        ValueError: If hex color format is invalid
    """
    h = hex_color.lstrip("#")

    # Handle short form (#FFF -> #FFFFFF)
    if len(h) == 3:
        h = ''.join([c*2 for c in h])

    if len(h) != 6:
        raise ValueError(f"Invalid hex color format: {hex_color}. Expected #RRGGBB or #RGB")

    try:
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
    except ValueError as e:
        raise ValueError(f"Invalid hex color: {hex_color}") from e


def load_font(size: int) -> ImageFont.FreeTypeFont:
    """
    Load a suitable font for subtitle rendering.
    Tries common system fonts, falls back to default.
    """
    candidates = [
        # Windows fonts
        "C:/Windows/Fonts/msyh.ttc",  # Microsoft YaHei
        "C:/Windows/Fonts/simhei.ttf",  # SimHei
        "C:/Windows/Fonts/simsun.ttc",  # SimSun
        # Linux fonts
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        # macOS fonts
        "/System/Library/Fonts/PingFang.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]

    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except (OSError, IOError) as e:
                # Font file exists but can't be loaded, try next candidate
                continue

    # Fallback to default
    return ImageFont.load_default()


def apply_audio_fade(clip: Any, fade_in: float, fade_out: float, duration: float) -> Any:
    """
    Apply fade in/out to audio clip.

    Args:
        clip: MoviePy AudioClip
        fade_in: Fade in duration (seconds)
        fade_out: Fade out duration (seconds)
        duration: Total clip duration (seconds)

    Returns:
        Modified audio clip with fades applied
    """
    original_get_frame = clip.get_frame

    def new_audio_frame(*args):
        # Handle different MoviePy calling conventions
        if len(args) == 1:
            t = args[0]
            frame = original_get_frame(t)
        else:
            get_frame, t = args
            frame = get_frame(t)

        # Convert to numpy array
        t_arr = np.array(t, ndmin=1)
        v = np.ones_like(t_arr, dtype=float)

        # Apply fade in
        if fade_in > 0:
            mask = t_arr < fade_in
            v[mask] *= (t_arr[mask] / fade_in)

        # Apply fade out
        if fade_out > 0:
            mask = t_arr > (duration - fade_out)
            v[mask] *= np.maximum(0, (duration - t_arr[mask]) / fade_out)

        # Convert back to scalar if needed
        if np.isscalar(t):
            v = float(v[0])

        # Handle audio frame shape
        if hasattr(frame, "ndim") and frame.ndim > 1:
            v = np.reshape(v, (-1, 1))

        return frame * v

    return clip.with_updated_frame_function(new_audio_frame)

def _layout_text(text, font, width, config):
    from PIL import Image, ImageDraw

    subtitle_width = int(width * config.width_ratio)

    dummy = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy)

    def measure(t):
        try:
            bb = draw.textbbox((0, 0), t, font=font)
            return bb[2] - bb[0], bb[3] - bb[1]
        except:
            return draw.textsize(t, font=font)

    text_width, text_height = measure(text)

    # ---- 自动换行 ----
    if text_width > subtitle_width:
        words = text.split()
        lines, current = [], []

        for word in words:
            test = " ".join(current + [word])
            w, _ = measure(test)

            if w <= subtitle_width:
                current.append(word)
            else:
                if current:
                    lines.append(" ".join(current))
                current = [word]

        if current:
            lines.append(" ".join(current))

        text = "\n".join(lines)
        text_width, text_height = measure(text)

    return text, text_width, text_height

def _resolve_style(width, height, config, style):
    if style:
        font_size = int(height * style.font_size_ratio)
        color_hex = style.color
        pos_x = int(width * style.position[0])
        pos_y = int(height * style.position[1])
    else:
        font_size = int(height * config.font_size_ratio)
        color_hex = config.default_color
        pos_x = width // 2
        pos_y = int(height * config.position_y_ratio)

    return font_size, hex_to_rgb(color_hex), pos_x, pos_y

def _canvas_to_clip(canvas, start, end):
    from moviepy.video.VideoClip import ImageClip
    import numpy as np

    frame_rgb = np.array(canvas.convert("RGB"))
    alpha = np.array(canvas.getchannel("A")) / 255.0

    duration = end - start

    return (
        ImageClip(frame_rgb)
        .with_duration(duration)
        .with_start(start)
        .with_mask(
            ImageClip(alpha, is_mask=True)
            .with_duration(duration)
            .with_start(start)
        )
    )
def _render_text_canvas(
    text,
    font,
    text_width,
    text_height,
    width,
    height,
    pos_x,
    pos_y,
    color_rgb,
    subtitle_config
):
    from PIL import Image, ImageDraw
    from .constants import SUBTITLE_PADDING, SUBTITLE_SHADOW_OFFSET

    padding = SUBTITLE_PADDING

    bg_width = text_width + padding * 2
    bg_height = text_height + padding * 2

    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # 背景
    bg_alpha = int(255 * subtitle_config.background_opacity)
    bg = Image.new("RGBA", (bg_width, bg_height), (0, 0, 0, bg_alpha))

    canvas.paste(
        bg,
        (pos_x - bg_width // 2, pos_y - bg_height // 2),
        bg
    )

    draw = ImageDraw.Draw(canvas)

    text_x = pos_x - text_width // 2
    text_y = pos_y - text_height // 2

    # 主文字
    draw.text(
        (text_x, text_y),
        text,
        font=font,
        fill=(*color_rgb, 255)
    )

    return canvas

def make_subtitle_clip(
    text: str,
    start: float,
    end: float,
    width: int,
    height: int,
    subtitle_config: Any,
    style: Optional[dict] = None
) -> Any:
    """
    Create a subtitle clip (refactored, modular).
    """

    # ------------------------
    # 1. Resolve style
    # ------------------------
    font_size, color_rgb, pos_x, pos_y = _resolve_style(
        width, height, subtitle_config, style
    )

    font = load_font(font_size)

    # ------------------------
    # 2. Layout text (wrap + size)
    # ------------------------
    text, text_width, text_height = _layout_text(
        text, font, width, subtitle_config
    )

    # ------------------------
    # 3. Render to canvas
    # ------------------------
    canvas = _render_text_canvas(
        text=text,
        font=font,
        text_width=text_width,
        text_height=text_height,
        width=width,
        height=height,
        pos_x=pos_x,
        pos_y=pos_y,
        color_rgb=color_rgb,
        subtitle_config=subtitle_config
    )

    # ------------------------
    # 4. Convert to clip
    # ------------------------
    return _canvas_to_clip(canvas, start, end)