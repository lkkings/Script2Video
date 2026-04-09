"""
Effect system with registry and factory function.
"""
from .base import BaseEffect, EffectParams
from .builtin import (
    BlurEffect,
    BrightnessEffect,
    ContrastEffect,
    GrayscaleEffect,
    VignetteEffect,
)


EFFECT_REGISTRY = {
    "blur": BlurEffect,
    "brightness": BrightnessEffect,
    "contrast": ContrastEffect,
    "grayscale": GrayscaleEffect,
    "vignette": VignetteEffect,
}


def get_effect(name: str, params: dict) -> BaseEffect:
    """
    Factory function to create effect instances.

    Args:
        name: Effect type name (blur, brightness, contrast, grayscale, vignette)
        params: Effect parameters dict

    Returns:
        Instantiated effect object

    Raises:
        ValueError: If effect name is not recognized
    """
    effect_class = EFFECT_REGISTRY.get(name)
    if not effect_class:
        raise ValueError(
            f"Unknown effect: {name}. Available effects: {', '.join(EFFECT_REGISTRY.keys())}"
        )
    return effect_class(params)


__all__ = [
    "BaseEffect",
    "EffectParams",
    "BlurEffect",
    "BrightnessEffect",
    "ContrastEffect",
    "GrayscaleEffect",
    "VignetteEffect",
    "EFFECT_REGISTRY",
    "get_effect",
]
