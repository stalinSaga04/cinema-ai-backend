# How to View Cinema AI Results

Since the Frontend UI (Phase 6) is not built yet, you can view results using the provided scripts.

## 1. Generate Results
Run the test pipeline to upload a video and get the analysis JSON:

```bash
python3 test_pipeline.py test_video.mp4
```

This will:
1. Upload the video to your live backend
2. Wait for processing
3. Save the result as `results_<video_id>.json`

## 2. Visualize Results
Use the viewer script to see a formatted report:

```bash
python3 view_results.py results_<video_id>.json
```

## 3. Example Output
```text
============================================================
🎬 CINEMA AI ANALYSIS RESULTS
============================================================

📝 TRANSCRIPT:
--------------------
"Hello world, this is a test video..."

🎬 SCENES:
--------------------
Start      | End       
-----------------------
00:00:00   | 00:00:05  
00:00:05   | 00:00:12  

😊 EMOTIONS:
--------------------
Time       | Emotion         | Character 
----------------------------------------
00:00:02   | happy           | face_001  
00:00:07   | neutral         | face_001  
```

## 4. Raw JSON
You can also open the `.json` file directly in any text editor to see the raw data structure used by the frontend.
