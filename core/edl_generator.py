from .utils import get_logger

logger = get_logger(__name__)

class EDLGenerator:
    def __init__(self):
        pass

    def generate_edl(self, comparison_result: dict) -> list:
        """
        Generate an Edit Decision List (EDL) from comparison results.
        
        Args:
            comparison_result: The output from RetakeMatcher.compare_takes()
            
        Returns:
            List of dicts representing clips to stitch:
            [
                {
                    "video_id": "uuid",
                    "start_time": 0.0,
                    "end_time": 10.5,
                    "source_path": "/path/to/video.mp4" 
                },
                ...
            ]
        """
        logger.info("Generating EDL from comparison result")
        
        edl = []
        
        # 1. Identify the Best Take
        # For MVP, we simply take the "best_take_id" and use it for the whole duration.
        # In the future, we will stitch scene-by-scene.
        
        best_take_id = comparison_result.get("best_take_id")
        if not best_take_id:
            logger.error("No best_take_id found in comparison result")
            return []
            
        # Find the ranking details for the best take to get metadata if needed
        best_take_data = next((r for r in comparison_result.get("rankings", []) if r["video_id"] == best_take_id), None)
        
        if best_take_data:
            # We need the source path. 
            # Note: The comparison result currently doesn't have the full path, 
            # so the caller (BrainController) might need to enrich this or we pass it in.
            # For now, we will just return the video_id and let the renderer resolve the path.
            
            # TODO: Get actual duration from metadata. For now, we assume full length.
            # We will rely on the renderer to know the duration or we should pass it.
            
            clip_entry = {
                "video_id": best_take_id,
                "start_time": 0.0,
                "end_time": None, # None means "until end"
                "type": "video"
            }
            edl.append(clip_entry)
            
        logger.info(f"Generated EDL with {len(edl)} clips")
        return edl
