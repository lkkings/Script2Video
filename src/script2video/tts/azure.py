import os
import html
import logging
import asyncio
from typing import Optional

from .base import TTSProvider

logger = logging.getLogger(__name__)

class AzureTTSProvider(TTSProvider):
    """Azure Cognitive Services TTS provider."""

    def __init__(self, api_key: Optional[str] = None, region: Optional[str] = None):
        """
        Initialize Azure TTS provider.

        Args:
            api_key: Azure API key (or from AZURE_TTS_KEY env var)
            region: Azure region (or from AZURE_TTS_REGION env var)
        """
        self.api_key = api_key or os.getenv("AZURE_TTS_KEY")
        self.region = region or os.getenv("AZURE_TTS_REGION", "eastus")

        if not self.api_key:
            raise ValueError(
                "Azure API key not provided. Set AZURE_TTS_KEY environment variable "
                "or pass api_key parameter."
            )

        try:
            import azure.cognitiveservices.speech as speechsdk
            self.speechsdk = speechsdk
        except ImportError:
            raise ImportError(
                "azure-cognitiveservices-speech is not installed. "
                "Install it with: pip install azure-cognitiveservices-speech"
            )

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
        Synthesize text using Azure TTS.

        The Azure SDK's speak_ssml_async().get() is a blocking call,
        so we run it in an executor to avoid blocking the event loop.

        Args:
            text: Text to synthesize
            output_path: Path to save audio file
            speaker: Voice name (e.g., "zh-CN-XiaoxiaoNeural")
            speed: Speech speed (0.5-2.0)
            emotion: Emotion style (e.g., "cheerful", "sad")
            **kwargs: Additional parameters

        Returns:
            Tuple of (audio_file_path, duration_in_seconds)
        """
        if not speaker:
            speaker = "zh-CN-XiaoxiaoNeural"

        speech_config = self.speechsdk.SpeechConfig(
            subscription=self.api_key,
            region=self.region
        )
        speech_config.speech_synthesis_voice_name = speaker
        speech_config.set_speech_synthesis_output_format(
            self.speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )

        audio_config = self.speechsdk.audio.AudioOutputConfig(filename=output_path)
        synthesizer = self.speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )

        ssml = self._build_ssml(text, speaker, speed, emotion)

        logger.info(f"Synthesizing with Azure TTS: speaker={speaker}, speed={speed}")

        # Run blocking SDK call in executor to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        future = synthesizer.speak_ssml_async(ssml)
        result = await loop.run_in_executor(None, future.get)

        if result.reason == self.speechsdk.ResultReason.SynthesizingAudioCompleted:
            duration = self.get_audio_duration(output_path)
            logger.info(f"Azure TTS synthesis complete: {output_path} ({duration:.2f}s)")
            return output_path, duration
        else:
            error_msg = f"Azure TTS failed: {result.reason}"
            if result.reason == self.speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                error_msg += f" - {cancellation.reason}: {cancellation.error_details}"
            raise RuntimeError(error_msg)

    def _build_ssml(
        self,
        text: str,
        speaker: str,
        speed: float,
        emotion: Optional[str]
    ) -> str:
        """Build SSML markup for Azure TTS with proper escaping."""
        rate = f"{int((speed - 1.0) * 100):+d}%"
        safe_text = html.escape(text)
        safe_speaker = html.escape(speaker, quote=True)

        ssml = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
        ssml += f'xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="zh-CN">'
        ssml += f'<voice name="{safe_speaker}">'

        if emotion:
            safe_emotion = html.escape(emotion, quote=True)
            ssml += f'<mstts:express-as style="{safe_emotion}">'

        ssml += f'<prosody rate="{rate}">{safe_text}</prosody>'

        if emotion:
            ssml += '</mstts:express-as>'

        ssml += '</voice></speak>'
        return ssml

