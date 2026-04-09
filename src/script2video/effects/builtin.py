"""
Built-in video effects: blur, brightness, contrast, grayscale, vignette.
"""
from typing import Any

from moviepy.video.VideoClip import VideoClip
from PIL import Image, ImageFilter
import numpy as np

from .base import BaseEffect


class BlurEffect(BaseEffect):
    """Gaussian blur effect."""

    def apply(self, clip:VideoClip) -> Any:
        """Apply blur effect to clip."""
        radius = max(1, int(self.params.intensity * 20))

        def blur_frame(frame):
            return np.array(
                Image.fromarray(frame).filter(ImageFilter.GaussianBlur(radius=radius))
            )

        return clip.fl_image(blur_frame)


class BrightnessEffect(BaseEffect):
    """Brightness adjustment effect."""

    def apply(self, clip: Any) -> Any:
        """Apply brightness effect to clip."""
        factor = 1.0 + self.params.intensity

        def adjust_brightness(frame):
            return np.clip(frame.astype(np.float32) * factor, 0, 255).astype(np.uint8)

        return clip.fl_image(adjust_brightness)


class ContrastEffect(BaseEffect):
    """Contrast adjustment effect."""

    def apply(self, clip: Any) -> Any:
        """Apply contrast effect to clip."""
        factor = 1.0 + self.params.intensity

        def adjust_contrast(frame):
            adjusted = (frame.astype(np.float32) - 128) * factor + 128
            return np.clip(adjusted, 0, 255).astype(np.uint8)

        return clip.fl_image(adjust_contrast)


class GrayscaleEffect(BaseEffect):
    """Grayscale conversion effect."""

    def apply(self, clip: Any) -> Any:
        """Apply grayscale effect to clip."""
        def to_grayscale(frame):
            return np.array(
                Image.fromarray(frame).convert("L").convert("RGB")
            )

        return clip.fl_image(to_grayscale)


class VignetteEffect(BaseEffect):
    """Vignette darkening effect."""

    def apply(self, clip: Any) -> Any:
        """Apply vignette effect to clip."""
        cache = {}
        intensity = self.params.intensity

        def apply_vignette(frame):
            h, w = frame.shape[:2]
            if (h, w) not in cache:
                cx, cy = w / 2, h / 2
                Y, X = np.ogrid[:h, :w]
                dist = np.sqrt((X - cx)**2 + (Y - cy)**2)
                max_dist = np.sqrt(cx**2 + cy**2)
                mask = np.clip(1 - intensity * (dist / max_dist)**2, 0, 1)
                cache[(h, w)] = mask[..., np.newaxis]

            return np.clip(
                frame.astype(np.float32) * cache[(h, w)], 0, 255
            ).astype(np.uint8)

        return clip.fl_image(apply_vignette)
