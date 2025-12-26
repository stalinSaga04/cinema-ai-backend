import logging
from difflib import SequenceMatcher
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetakeMatcher:
    """
    Compares multiple video takes to identify the best one.
    """

    def __init__(self):
        pass

    def compare_takes(self, takes_data: List[Dict[str, Any]], reference_script: str = None) -> Dict[str, Any]:
        """
        Compare a list of processed video results.
        
        Args:
            takes_data: List of result dicts (from BrainController.get_result)
            reference_script: Optional script text to compare against. 
                              If None, the first take's transcript is used as reference 
                              (or we just compare them to each other).
        
        Returns:
            Dict containing the 'best_take_id' and a list of 'rankings'.
        """
        logger.info(f"Comparing {len(takes_data)} takes")
        
        rankings = []
        
        # If no reference script is provided, we can't score "script adherence" accurately 
        # unless we assume one take is the "master". 
        # For now, let's score based on intrinsic qualities (audio, emotion) 
        # and if a script is provided, we use it.
        
        for take in takes_data:
            video_id = take.get("video_id", "unknown")
            transcript = take.get("transcript", "")
            
            # 1. Script Adherence Score (0.0 - 1.0)
            script_score = 0.0
            if reference_script:
                script_score = self._calculate_similarity(reference_script, transcript)
            elif len(transcript) > 0:
                # If no reference, we assume having *some* speech is better than none
                script_score = 1.0 
            
            # 2. Audio Quality Score (0.0 - 1.0)
            # Currently we don't have raw audio metrics in the JSON result (like dB levels).
            # We can infer quality from the confidence of the transcription if available,
            # or just placeholder it for now until we add audio metrics to AudioExtractor.
            # For Phase 2 MVP, we'll give a baseline score.
            audio_score = 0.8 
            
            # 3. Emotion Intensity Score (0.0 - 1.0)
            emotion_score = self._calculate_emotion_score(take.get("emotion_map", []))
            
            # Total Weighted Score
            # Weights: Script (40%), Audio (30%), Emotion (30%)
            total_score = (script_score * 0.4) + (audio_score * 0.3) + (emotion_score * 0.3)
            
            rankings.append({
                "video_id": video_id,
                "total_score": round(total_score, 2),
                "metrics": {
                    "script_adherence": round(script_score, 2),
                    "audio_quality": round(audio_score, 2),
                    "emotion_intensity": round(emotion_score, 2)
                },
                "transcript_preview": transcript[:50] + "..." if len(transcript) > 50 else transcript
            })
            
        # Sort by total score descending
        rankings.sort(key=lambda x: x["total_score"], reverse=True)
        
        best_take_id = rankings[0]["video_id"] if rankings else None
        
        return {
            "best_take_id": best_take_id,
            "rankings": rankings
        }

    def _calculate_similarity(self, a: str, b: str) -> float:
        """Calculates similarity ratio between two strings (0.0 to 1.0)."""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def _calculate_emotion_score(self, emotion_map: List[Dict]) -> float:
        """
        Calculates a score based on emotion intensity and variety.
        Higher score for more expressive takes.
        """
        if not emotion_map:
            return 0.0
            
        # 1. Average Confidence/Intensity
        total_confidence = sum(e.get("score", 0) for e in emotion_map)
        avg_confidence = total_confidence / len(emotion_map) if emotion_map else 0
        
        # 2. Variety (Bonus for showing different emotions)
        unique_emotions = set(e.get("emotion") for e in emotion_map)
        variety_bonus = min(len(unique_emotions) * 0.1, 0.3) # Max 0.3 bonus
        
        final_score = min(avg_confidence + variety_bonus, 1.0)
        return final_score
