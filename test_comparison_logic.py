import unittest
from core.retake_matcher import RetakeMatcher

class TestRetakeMatcher(unittest.TestCase):
    def setUp(self):
        self.matcher = RetakeMatcher()
        
        # Mock Data
        self.take_1 = {
            "video_id": "take_1",
            "transcript": "To be or not to be, that is the question.",
            "emotion_map": [{"score": 0.9, "emotion": "sad"}, {"score": 0.8, "emotion": "neutral"}]
        }
        
        self.take_2 = {
            "video_id": "take_2",
            "transcript": "To be or not to be, that is the...", # Incomplete
            "emotion_map": [{"score": 0.5, "emotion": "neutral"}]
        }
        
        self.take_3 = {
            "video_id": "take_3",
            "transcript": "I want a hamburger.", # Wrong lines
            "emotion_map": [{"score": 0.9, "emotion": "happy"}]
        }

    def test_compare_takes_with_script(self):
        script = "To be or not to be, that is the question."
        takes = [self.take_1, self.take_2, self.take_3]
        
        result = self.matcher.compare_takes(takes, reference_script=script)
        
        rankings = result["rankings"]
        
        # Take 1 should be first (Perfect match, good emotion)
        self.assertEqual(rankings[0]["video_id"], "take_1")
        self.assertEqual(rankings[0]["metrics"]["script_adherence"], 1.0)
        
        # Take 3 should be last (Wrong lines)
        self.assertEqual(rankings[-1]["video_id"], "take_3")
        
        print("\nTest With Script Results:")
        for r in rankings:
            print(f"Rank {rankings.index(r)+1}: {r['video_id']} - Score: {r['total_score']}")

    def test_compare_takes_no_script(self):
        # Without script, we assume transcript existence = good
        takes = [self.take_1, self.take_2]
        
        result = self.matcher.compare_takes(takes)
        rankings = result["rankings"]
        
        # Take 1 should still win due to better emotion score
        self.assertEqual(rankings[0]["video_id"], "take_1")
        
        print("\nTest No Script Results:")
        for r in rankings:
            print(f"Rank {rankings.index(r)+1}: {r['video_id']} - Score: {r['total_score']}")

if __name__ == "__main__":
    unittest.main()
