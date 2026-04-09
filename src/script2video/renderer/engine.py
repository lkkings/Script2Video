"""
Video rendering engine for Script2Video.
Converts Draft objects into rendered video files using MoviePy.
"""
import os
import logging
from typing import Any, Optional, List
from moviepy import (
    CompositeVideoClip,
    CompositeAudioClip,
    concatenate_videoclips
)
from moviepy.video.VideoClip import VideoClip

from ..models.draft import Draft, Scene, TrackType
from .processors import ProcessorFactory, RenderContext
from .constants import DEFAULT_VIDEO_DURATION


logger = logging.getLogger(__name__)

# 如果没有 handler，需要加一个
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class VideoRenderer:
    """Main video rendering engine."""

    def __init__(self):
        """
        Initialize video renderer.

        The renderer manages the complete video rendering pipeline including
        video/image compositing, audio mixing, subtitle generation, and effects.
        """
        self.factory = ProcessorFactory()
        
    def _render_signle_scene(self,scene:Scene,context:RenderContext) -> CompositeVideoClip:
        for track in scene.tracks:
            for index,clip in enumerate(track.clips):
                try:
                    next_clip = track.clips[index+1]
                    end = next_clip.start 
                except:
                    end = scene.duration
                clip.end = end
                logger.info(f"Clip 【{track.type.name}-{clip.start}-{clip.end}】: {clip.desc}")
                
                processor = self.factory.get_processor(clip)
                if processor:
                    processor.process(clip, context)
        # Composite video layers
        logger.info("Compositing video layers...")
        composite = CompositeVideoClip(context.video_layers, size=(context.width, context.height))
        if context.effect_segments:
            logger.info(f"Apply {len(context.effect_segments)} effect ...")
            composite = self._apply_collected_effects(composite, context.effect_segments)
        # Mix audio
        if context.audio_clips:
            logger.info(f"Mixing {len(context.audio_clips)} audio tracks...")
            composite = composite.with_audio(
                CompositeAudioClip(context.audio_clips)
            )

        return composite

    def render(self, draft: Draft, output_path: str, verbose=True):
        """
        Render draft to video file.

        Args:
            draft: Draft object to render
            output_path: Path to output video file
        """
        logger.setLevel(logging.DEBUG if verbose else logging.WARNING)
        logger.info(f"Rendering: {draft.title}")
        logger.info(f"Resolution: {draft.config.resolution[0]}x{draft.config.resolution[1]}")
        logger.info(f"FPS: {draft.config.fps}")
        logger.info(f"Scenes: {len(draft.scenes)}")

        # Extract configuration
        width = draft.config.resolution[0]
        height = draft.config.resolution[1]
        fps = draft.config.fps

        total_duration = 0
        composites: List[CompositeVideoClip] = []
        all_contexts: List[RenderContext] = []
        # Process all scenes
        for scene_idx, scene in enumerate(draft.scenes):
            logger.info(f"Processing scene {scene_idx + 1}/{len(draft.scenes)}: {scene.type}")
            if len(scene.tracks) == 0:
                logger.warning(f"Scene tracks is null: {scene.type}")
                continue
            context = RenderContext(
                width=width,
                height=height,
                config=draft.config
            )
            composite = self._render_signle_scene(scene, context)
            composites.append(composite)
            all_contexts.append(context)
            duration = composite.duration
            total_duration += duration
            logger.info(f"Scene duration: {duration} s")

        final_video = concatenate_videoclips(composites, method="compose")
        logger.info(f"Video duration: {final_video.duration} ")
        # Export
        logger.info(f"Exporting to: {output_path}")
        try:
            final_video.write_videofile(
                output_path,
                fps=fps,
                codec="libx264",
                audio_codec="aac",
                preset="medium",
                ffmpeg_params=["-crf", "23"],
            )
            logger.info(f"Rendering complete: {output_path}")
        finally:
            # Close composites and final video first
            for composite in composites:
                try:
                    composite.close()
                except Exception:
                    pass
            try:
                final_video.close()
            except Exception:
                pass
            # Then cleanup underlying clips and temp files
            for ctx in all_contexts:
                self._cleanup_clips(ctx.clips_to_close, ctx.temp_audio_files)
            

    def _cleanup_clips(self, clips_to_close: List[Any], temp_audio_files: List[str]):
        """Close all tracked clips to free resources."""
        for clip in clips_to_close:
            try:
                if hasattr(clip, 'close'):
                    clip.close()
            except Exception as e:
                logger.warning(f"Failed to close clip: {e}")

        # Clean up temporary TTS audio files
        for audio_file in temp_audio_files:
            try:
                if os.path.exists(audio_file):
                    os.remove(audio_file)
                    logger.debug(f"Removed temp TTS file: {audio_file}")
            except Exception as e:
                logger.warning(f"Failed to remove temp file {audio_file}: {e}")


    def _apply_collected_effects(self, composite, effect_segments):
        """Apply collected effect clips to composite video."""
        if not effect_segments:
            return composite

        logger.info(f"Applying {len(effect_segments)} effects...")
        original_get_frame = composite.get_frame

        def new_frame(t):
            frame = original_get_frame(t)
            for start, end, effect in effect_segments:
                if start <= t < end:
                    # Create a dummy clip for the effect to process
                    dummy_clip = VideoClip(make_frame=lambda t: frame, duration=1)
                    processed_clip = effect.apply(dummy_clip)
                    frame = processed_clip.get_frame(0)
            return frame

        return composite.with_updated_frame_function(new_frame)
