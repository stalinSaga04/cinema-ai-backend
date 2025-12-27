# Phase 2: Retake Matching Guide

The "Brain" can now compare multiple takes of the same scene and tell you which one is best.

## 🚀 How to Use

### 1. Upload Your Takes
First, upload each video take individually using the standard upload process.
You will get a `video_id` for each take.

Example:
- Take 1: `id_123`
- Take 2: `id_456`
- Take 3: `id_789`

### 2. Compare Them
Send a POST request to `/compare` with the list of IDs.

**Endpoint**: `POST https://cinema-ai-backend.onrender.com/compare`

**Body**:
```json
{
  "video_ids": ["id_123", "id_456", "id_789"],
  "reference_script": "To be or not to be, that is the question."
}
```
*(Note: `reference_script` is optional. If omitted, it compares takes against each other.)*

### 3. Get Ranked Results
The API returns a ranked list:

```json
{
  "best_take_id": "id_123",
  "rankings": [
    {
      "rank": 1,
      "video_id": "id_123",
      "total_score": 0.92,
      "metrics": {
        "script_adherence": 1.0,
        "audio_quality": 0.8,
        "emotion_intensity": 0.9
      }
    },
    {
      "rank": 2,
      "video_id": "id_456",
      "total_score": 0.75,
      ...
    }
  ]
}
```

## 🧠 How Scoring Works
- **Script Adherence (40%)**: Did they say the right lines?
- **Audio Quality (30%)**: Is it clear? (Baseline score for now)
- **Emotion Intensity (30%)**: How expressive was the acting?
