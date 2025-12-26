import os
from .utils import get_logger, ensure_directory

logger = get_logger(__name__)

class VideoRenderer:
    def __init__(self, output_dir: str = "outputs/renders", uploads_dir: str = "uploads"):
        self.output_dir = output_dir
        self.uploads_dir = uploads_dir
        ensure_directory(output_dir)

    def render_video(self, edl: list, output_filename: str = "final_render.mp4") -> str:
        """
        Render the final video based on the EDL.
        
        Args:
            edl: List of clip dictionaries from EDLGenerator.
            output_filename: Name of the output file.
            
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
                    logger.warning(f"Could not find source video for ID {video_id}")
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
            
            output_path = os.path.join(self.output_dir, output_filename)
            
            logger.info(f"Writing video to {output_path}")
            # Use 'medium' preset for speed, 'libx264' for compatibility
            final_video.write_videofile(
                output_path, 
                codec="libx264", 
                audio_codec="aac",
                preset="medium",
                fps=24,
                threads=4,
                logger=None # Disable moviepy's internal logger to keep stdout clean
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
