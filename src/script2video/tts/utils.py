from moviepy import AudioFileClip

def get_audio_duration(audio_path: str) -> float:
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