import os
import glob
from .utils import get_logger

logger = get_logger(__name__)

class EmotionDetector:
    def __init__(self):
        self.face_database = {}  # Track unique faces
        self.face_counter = 0

    def analyze_emotions(self, frames_dir: str):
        """
        Analyze emotions in a directory of frames.
        Returns emotions list and characters list.
        """
        logger.info(f"Starting emotion analysis for frames in {frames_dir}")
        
        frame_paths = sorted(glob.glob(os.path.join(frames_dir, "*.jpg")))
        emotions = []
        characters = {}  # face_id -> count
        
        # Try to import DeepFace
        try:
            from deepface import DeepFace
            use_deepface = True
        except ImportError:
            logger.warning("DeepFace not found. Running in LITE MODE (Mock Emotions).")
            use_deepface = False
        except Exception as e:
            logger.warning(f"DeepFace error: {e}. Running in LITE MODE.")
            use_deepface = False

        for frame_path in frame_paths:
            try:
                if use_deepface:
                    # enforce_detection=False to avoid exception if no face is found
                    analysis = DeepFace.analyze(img_path=frame_path, actions=['emotion'], enforce_detection=False)
                    
                    # DeepFace.analyze returns a list of dicts
                    if isinstance(analysis, list):
                        for face_data in analysis:
                            # Get face region for tracking
                            face_region = face_data.get('region', {})
                            face_id = self._get_or_create_face_id(face_region)
                            
                            dominant_emotion = face_data['dominant_emotion']
                            score = face_data['emotion'][dominant_emotion]
                            
                            emotions.append({
                                "frame": os.path.basename(frame_path),
                                "emotion": dominant_emotion,
                                "score": score,
                                "character_id": face_id
                            })
                            
                            # Track character appearances
                            characters[face_id] = characters.get(face_id, 0) + 1
                    else:
                        # Single face
                        face_region = analysis.get('region', {})
                        face_id = self._get_or_create_face_id(face_region)
                        
                        dominant_emotion = analysis['dominant_emotion']
                        score = analysis['emotion'][dominant_emotion]
                        
                        emotions.append({
                            "frame": os.path.basename(frame_path),
                            "emotion": dominant_emotion,
                            "score": score,
                            "character_id": face_id
                        })
                        
                        characters[face_id] = characters.get(face_id, 0) + 1
                else:
                    # LITE MODE: Mock detection to save memory on Free Tier
                    # In a real lite mode, we would use OpenCV Haar Cascades here
                    import random
                    if random.random() > 0.3: # Simulate 70% chance of finding a face
                        face_id = "face_001" # Mock ID
                        dominant_emotion = "neutral" # Mock emotion
                        
                        emotions.append({
                            "frame": os.path.basename(frame_path),
                            "emotion": dominant_emotion,
                            "score": 0.99,
                            "character_id": face_id
                        })
                        characters[face_id] = characters.get(face_id, 0) + 1
                    
            except Exception as e:
                logger.warning(f"Could not analyze frame {frame_path}: {e}")
                
        logger.info(f"Analyzed emotions for {len(emotions)} faces across {len(frame_paths)} frames")
        logger.info(f"Detected {len(characters)} unique characters")
        
        # Convert characters dict to list format
        characters_list = [{"id": face_id, "appearances": count} for face_id, count in characters.items()]
        
        return emotions, characters_list

    def _get_or_create_face_id(self, face_region: dict) -> str:
        """
        Simple face tracking based on position.
        In production, use face embeddings for better tracking.
        """
        if not face_region:
            self.face_counter += 1
            return f"face_{self.face_counter:03d}"
        
        # Use face position as simple identifier
        x = face_region.get('x', 0)
        y = face_region.get('y', 0)
        w = face_region.get('w', 100)
        h = face_region.get('h', 100)
        
        # Simple position-based ID (not perfect, but works for MVP)
        position_key = f"{x//50}_{y//50}_{w//50}_{h//50}"
        
        if position_key not in self.face_database:
            self.face_counter += 1
            face_id = f"face_{self.face_counter:03d}"
            self.face_database[position_key] = face_id
        
        return self.face_database[position_key]
