from .base import TTSProvider
from .edge import EdgeTTSProvider
from .azure import AzureTTSProvider
from .dashscope import DashScopeTTSProvider


def get_tts_provider(provider_name: str = "edge-tts", **kwargs) -> TTSProvider:
    """
    Factory function to create TTS provider instances.

    Args:
        provider_name: Provider name ("edge-tts", "azure", etc.)
        **kwargs: Provider-specific initialization parameters

    Returns:
        TTSProvider instance

    Raises:
        ValueError: If provider name is not recognized
    """
    providers = {
        "edge-tts": EdgeTTSProvider,
        "azure": AzureTTSProvider,
        "dashscope": DashScopeTTSProvider
    }

    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(
            f"Unknown TTS provider: {provider_name}. "
            f"Available providers: {', '.join(providers.keys())}"
        )

    return provider_class(**kwargs)

__all__ = [
    "EdgeTTSProvider",
    "AzureTTSProvider",
    "get_tts_provider"
]
