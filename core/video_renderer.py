import os
from .utils import get_logger, ensure_directory

logger = get_logger(__name__)

class VideoRenderer:
    def __init__(self, output_dir: str = "outputs/renders", uploads_dir: str = "uploads"):
        self.output_dir = output_dir
        self.uploads_dir = uploads_dir
        ensure_directory(output_dir)

    def render_video(self, edl: list, output_filename: str = "final_render.mp4", bg_music_path: str = None, is_paid: bool = False) -> str:
        """
        Render video based on EDL.
        PRD 12. Free Tier vs Paid Tier rules.
        
        Args:
            edl: List of clip dictionaries from EDLGenerator.
            output_filename: Name of the output file.
            is_paid: True if the user has a paid subscription, False otherwise.
            
        Returns:
            Path to the rendered video file.
        """
        # Lazy import to avoid startup crash on Render Free Tier
        try:
            from moviepy.editor import VideoFileClip, concatenate_videoclips
        except ImportError:
            from moviepy import VideoFileClip, concatenate_videoclips

        logger.info(f"Starting video render with {len(edl)} clips")
        
        clips = []
        
        try:
            for clip_data in edl:
                video_id = clip_data.get("video_id")
                
                # Resolve file path
                # We assume the file is in the uploads directory with a known extension
                # In a real app, we'd query the DB for the filename.
                # Here we'll try common extensions.
                video_path = None
                for ext in [".mp4", ".mov", ".avi", ".mkv"]:
                    path = os.path.join(self.uploads_dir, f"{video_id}{ext}")
                    if os.path.exists(path):
                        video_path = path
                        break
                
                if not video_path:
                    logger.info(f"Clip {video_id} not found locally. Attempting to download from Supabase...")
                    # Try to download from Supabase Storage
                    # We assume the file is in 'videos' bucket under 'uploads/{video_id}.mp4'
                    # In a real app, we'd store the extension in the DB.
                    local_path = os.path.join(self.uploads_dir, f"{video_id}.mp4")
                    
                    from .storage import Storage
                    storage = Storage()
                    if storage.download_file("videos", f"uploads/{video_id}.mp4", local_path):
                        video_path = local_path
                    else:
                        logger.warning(f"Could not find or download source video for ID {video_id}")
                        continue
                    
                logger.info(f"Loading clip from {video_path}")
                clip = VideoFileClip(video_path)
                
                # Handle start/end times if specified
                start = clip_data.get("start_time", 0.0)
                end = clip_data.get("end_time")
                
                if end is None:
                    end = clip.duration
                    
                # Sanity check
                if start < 0: start = 0
                if end > clip.duration: end = clip.duration
                if start >= end:
                    logger.warning(f"Invalid clip duration: start={start}, end={end}")
                    clip.close()
                    continue
                
                # MoviePy 2.0+ uses 'subclipped', older versions use 'subclip'
                if hasattr(clip, 'subclipped'):
                    subclip = clip.subclipped(start, end)
                else:
                    subclip = clip.subclip(start, end)
                
                clips.append(subclip)
            
            if not clips:
                logger.error("No valid clips to render")
                return None
                
            logger.info("Concatenating clips...")
            final_video = concatenate_videoclips(clips)
            
            # PRD 12. Free Tier - 720p
            # PRD 8. Camera Policy - Light stabilization & Soft clarity
            # PRD 10. Audio Rules - Normalization
            
            output_path = os.path.join(self.output_dir, output_filename)
            
            logger.info(f"Writing video to {output_path} with PRD compliance filters")
            
            # PRD 10. Audio Rules - Normalization, Music Loop, Ducking
            # [0:a] is the narrator voice (final_video.audio)
            # [1:a] would be the background music
            
            if bg_music_path and os.path.exists(bg_music_path):
                logger.info(f"Applying background music with ducking: {bg_music_path}")
                # We use complex_filter for ducking
                # 1. Loop the music: stream_loop -1
                # 2. Sidechaincompress: music volume drops when voice is active
                # 3. Mix: amix
                
                # Note: MoviePy handles the narrator audio as the primary stream.
                # To add a second stream and duck it, it's easier to do it via ffmpeg_params
                # but we need to pass the second input. MoviePy's write_videofile doesn't easily
                # support multiple inputs in ffmpeg_params.
                
                # Alternative: Use MoviePy to mix the audio, then use FFmpeg for the final normalization.
                from moviepy.editor import AudioFileClip, afx
                
                voice_audio = final_video.audio
                bg_audio = AudioFileClip(bg_music_path)
                
                # Loop music to match video duration
                bg_audio = bg_audio.loop(duration=final_video.duration)
                
                # Simple ducking: lower bg volume
                # For a true sidechain effect in MoviePy, we'd need more complex logic.
                # For MVP, we'll lower bg volume to 15% and voice to 100%
                bg_audio = bg_audio.volumex(0.15)
                
                from moviepy.editor import CompositeAudioClip
                final_audio = CompositeAudioClip([voice_audio, bg_audio])
                final_video.audio = final_audio
            
            # PRD-MONETIZATION: Duration Caps & Preview Compression
            # Free: 60s (Compressed), Paid: 300s (5m) (Truncated if needed)
            if not is_paid:
                if final_video.duration > 60:
                    logger.info(f"Applying Preview Compression for draft (Original: {final_video.duration}s)")
                    # Sample 12 segments of 5s each, spaced evenly
                    num_segments = 12
                    segment_duration = 5.0
                    total_preview_duration = num_segments * segment_duration
                    
                    # Calculate spacing
                    # We want to cover the whole video, so we space the start of each segment
                    # across (duration - segment_duration)
                    spacing = (final_video.duration - segment_duration) / (num_segments - 1)
                    
                    preview_clips = []
                    for i in range(num_segments):
                        start = i * spacing
                        end = start + segment_duration
                        
                        if hasattr(final_video, 'subclipped'):
                            seg = final_video.subclipped(start, end)
                        else:
                            seg = final_video.subclip(start, end)
                        preview_clips.append(seg)
                    
                    old_final = final_video
                    final_video = concatenate_videoclips(preview_clips)
                    old_final.close() # Release original
                else:
                    logger.info("Draft duration is under 60s, no compression needed.")
            else:
                # Paid Tier: Truncate to 5m if it exceeds
                if final_video.duration > 300:
                    logger.info(f"Trimming final video to 300s duration cap (Original: {final_video.duration}s)")
                    if hasattr(final_video, 'subclipped'):
                        final_video = final_video.subclipped(0, 300)
                    else:
                        final_video = final_video.subclip(0, 300)

            # PRD-MONETIZATION: Watermark (Free only)
            vf_filters = "scale=-1:720,unsharp=3:3:1.5"
            if not is_paid:
                # Check if drawtext is available
                import subprocess
                try:
                    # More robust check: look for ' drawtext ' in filters list
                    result = subprocess.run(["ffmpeg", "-filters"], capture_output=True, text=True)
                    filters_list = result.stdout.splitlines()
                    has_drawtext = any(" drawtext " in line for line in filters_list)
                    
                    if has_drawtext:
                        vf_filters += ",drawtext=text='Cinema AI':x=W-tw-10:y=H-th-10:fontsize=24:fontcolor=white@0.5"
                    else:
                        logger.warning("FFmpeg 'drawtext' filter not found in filters list. Skipping watermark.")
                except Exception as e:
                    logger.warning(f"Could not check FFmpeg filters: {e}")

            ffmpeg_params = ["-vf", vf_filters]
            if final_video.audio:
                ffmpeg_params.extend(["-af", "loudnorm"])
            else:
                logger.info("No audio track detected, skipping 'loudnorm' filter.")
            
            final_video.write_videofile(
                output_path, 
                codec="libx264", 
                audio_codec="aac",
                preset="ultrafast",
                fps=24,
                threads=4,
                ffmpeg_params=ffmpeg_params,
                logger=None
            )
            
            # Close clips to release resources
            final_video.close()
            for clip in clips:
                clip.close()
                
            logger.info("Render complete!")
            return output_path
            
        except Exception as e:
            logger.error(f"Error during rendering: {e}")
            # Cleanup
            for clip in clips:
                try: clip.close()
                except: pass
            raise
