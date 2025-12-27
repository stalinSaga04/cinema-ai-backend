from .utils import get_logger

logger = get_logger(__name__)

class EDLGenerator:
    def __init__(self):
        pass

    def generate_edl(self, comparison_result: dict) -> list:
        """
        Generate an Edit Decision List (EDL) from comparison results.
        PRD 9. Video Editing Rules - Deterministic cutting.
        """
        logger.info("Generating EDL from comparison result")
        
        edl = []
        
        best_take_id = comparison_result.get("best_take_id")
        if not best_take_id:
            logger.error("No best_take_id found in comparison result")
            return []
            
        # Get full data for the best take to access scenes and emotions
        best_take_data = next((r for r in comparison_result.get("rankings", []) if r["video_id"] == best_take_id), None)
        
        # In a real system, we'd pass the full analysis result here.
        # For MVP, we'll assume the comparison_result has been enriched or we fetch it.
        # Since we don't have the full scenes list here, we'll use a simplified version.
        
        # For MVP: 
        # 1. Start with the best A-roll take.
        # 2. Use the whole take, but mark it with metadata for the renderer.
        
        # In a more advanced MVP, we'd iterate through scenes:
        # for scene in best_take_scenes:
        #     duration = scene['end'] - scene['start']
        #     if scene['motion_score'] > 10: duration = min(duration, 3.0)
        #     ...
        
        edl.append({
            "video_id": best_take_id,
            "start_time": 0.0,
            "end_time": None,
            "type": "a-roll",
            "motion_score": best_take_data.get("metrics", {}).get("motion_score", 5.0),
            "has_face": best_take_data.get("metrics", {}).get("emotion_intensity", 0) > 0
        })
            
        logger.info(f"Generated EDL with {len(edl)} clips")
        return edl
