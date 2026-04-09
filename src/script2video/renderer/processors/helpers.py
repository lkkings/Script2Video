"""
Shared helper functions used by multiple clip processors.
Moved from engine.py: _ease, _apply_fit_mode, _apply_animation.
"""
import math
from typing import Optional

import numpy as np

from ...models.base import AnimationConfig


# ── Easing functions ────────────────────────────────────────────────────────

def _ease(t: float, easing: str) -> float:
    """Map progress t (0-1) through an easing curve."""
    t = max(0.0, min(1.0, t))
    if easing == "linear":
        return t
    if easing == "ease_in":
        return t * t
    if easing == "ease_out":
        return 1.0 - (1.0 - t) ** 2
    # ease_in_out (default)
    return 3 * t * t - 2 * t * t * t


# ── Fit-mode helper ─────────────────────────────────────────────────────────

def _apply_fit_mode(clip, fit_mode: str, canvas_w: int, canvas_h: int):
    """
    Resize clip to fit the canvas according to fit_mode.

    cover   - scale up to fill canvas, crop overflow (no black bars)
    contain - scale down so the whole clip is visible (may have black bars)
    fill    - stretch to exact canvas size (may distort)
    """
    cw, ch = clip.w, clip.h
    if cw == 0 or ch == 0:
        return clip

    if fit_mode == "fill":
        return clip.resized((canvas_w, canvas_h))

    src_ratio = cw / ch
    dst_ratio = canvas_w / canvas_h

    if fit_mode == "cover":
        # Scale so the *smaller* dimension matches the canvas
        if src_ratio < dst_ratio:
            scale = canvas_w / cw
        else:
            scale = canvas_h / ch
    else:  # contain
        # Scale so the *larger* dimension matches the canvas
        if src_ratio > dst_ratio:
            scale = canvas_w / cw
        else:
            scale = canvas_h / ch

    new_w = int(cw * scale)
    new_h = int(ch * scale)
    clip = clip.resized((new_w, new_h))

    if fit_mode == "cover":
        # Crop to canvas size (center crop)
        x_off = (new_w - canvas_w) // 2
        y_off = (new_h - canvas_h) // 2
        clip = clip.cropped(x1=x_off, y1=y_off, x2=x_off + canvas_w, y2=y_off + canvas_h)

    return clip


# ── Animation applicator ───────────────────────────────────────────────────

def _apply_animation(clip, animation, clip_duration: float, canvas_w: int, canvas_h: int):
    """
    Wrap a MoviePy clip so its enter/exit animations modify opacity and position per-frame.
    """
    if animation is None:
        return clip
    enter: Optional[AnimationConfig] = animation.enter
    exit_: Optional[AnimationConfig] = animation.exit
    if enter is None and exit_ is None:
        return clip

    # Snapshot the base position (may be a tuple or a lambda)
    base_pos = clip.pos
    if callable(base_pos):
        _base_pos_fn = base_pos
    else:
        _base_pos_fn = lambda t: base_pos

    base_opacity = clip.opacity if hasattr(clip, 'opacity') and clip.opacity is not None else 1.0

    clip_w, clip_h = clip.w, clip.h

    def _pos_and_opacity(t):
        """Return (dx, dy, opacity_multiplier) for the given local time."""
        dx, dy, op = 0, 0, 1.0

        # ── enter animation ──
        if enter is not None and t < enter.duration:
            p = _ease(t / enter.duration, enter.easing)  # 0 -> 1

            eff = enter.effect
            if eff == "fade_in":
                op *= p
            elif eff == "slide_left":
                dx = int(canvas_w * (1.0 - p))
            elif eff == "slide_right":
                dx = int(-canvas_w * (1.0 - p))
            elif eff == "slide_up":
                dy = int(canvas_h * (1.0 - p))
            elif eff == "slide_down":
                dy = int(-canvas_h * (1.0 - p))
            elif eff == "zoom_in":
                op *= p  # fade while growing - actual scale is below
            elif eff == "zoom_out":
                op *= p
            elif eff == "rotate_in":
                op *= p
            elif eff == "bounce_in":
                # overshoot ease
                bounce = 1.0 + 0.3 * math.sin(p * math.pi)
                op *= min(p * 2, 1.0)
                dx = int(canvas_w * (1.0 - bounce) * (1.0 - p))

        # ── exit animation ──
        time_left = clip_duration - t
        if exit_ is not None and time_left < exit_.duration and exit_.duration > 0:
            p = _ease(time_left / exit_.duration, exit_.easing)  # 1 -> 0

            eff = exit_.effect
            if eff == "fade_out":
                op *= p
            elif eff == "slide_left":
                dx = int(-canvas_w * (1.0 - p))
            elif eff == "slide_right":
                dx = int(canvas_w * (1.0 - p))
            elif eff == "slide_up":
                dy = int(-canvas_h * (1.0 - p))
            elif eff == "slide_down":
                dy = int(canvas_h * (1.0 - p))
            elif eff == "zoom_in":
                op *= p
            elif eff == "zoom_out":
                op *= p
            elif eff == "rotate_out":
                op *= p

        return dx, dy, op

    # ── wrap position ──
    def animated_pos(t):
        bx, by = _base_pos_fn(t)
        dx, dy, _ = _pos_and_opacity(t)
        return (bx + dx, by + dy)

    clip = clip.with_position(animated_pos)

    # ── wrap opacity via frame function ──
    original_get_frame = clip.get_frame

    def animated_frame(t):
        frame = original_get_frame(t)
        _, _, op_mult = _pos_and_opacity(t)
        final_op = base_opacity * op_mult
        if final_op >= 1.0:
            return frame
        if final_op <= 0.0:
            return np.zeros_like(frame)
        return (frame.astype(np.float32) * final_op).astype(np.uint8)

    clip = clip.with_updated_frame_function(animated_frame)

    return clip
