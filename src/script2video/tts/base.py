from abc import ABC, abstractmethod
from typing import Optional
from moviepy import AudioFileClip



class TTSProvider(ABC):
    """Abstract base class for TTS providers."""
    
    def get_audio_duration(self,audio_path: str) -> float:
        """
        Get audio file duration using MoviePy.

        Args:
            audio_path: Path to audio file

        Returns:
            Duration in seconds, or 0.0 if unable to determine
        """
        try:
            
            audio = AudioFileClip(audio_path)
            try:
                return audio.duration
            finally:
                audio.close()
        except Exception as e:
            raise Exception(f"Failed to get audio duration: {e}")

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        output_path: str,
        speaker: Optional[str] = None,
        speed: float = 1.0,
        emotion: Optional[str] = None,
        **kwargs
    ) -> tuple[str, float]:
        """
        Synthesize text to speech and save to file.

        Args:
            text: Text to synthesize
            output_path: Path to save audio file
            speaker: Speaker voice name
            speed: Speech speed (0.5-2.0)
            emotion: Emotion style (if supported)
            **kwargs: Additional provider-specific parameters

        Returns:
            Tuple of (audio_file_path, duration_in_seconds)
        """
        pass
