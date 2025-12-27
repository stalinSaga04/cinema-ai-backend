import requests
import time
import os
import json

API_URL = "http://localhost:8000"

def test_broll():
    print("============================================================")
    print("🎬 TESTING B-ROLL & OPTIMIZATION")
    print("============================================================")

    video_path = "test_video.mp4"
    if not os.path.exists(video_path):
        print(f"Error: {video_path} not found.")
        return

    # 1. Upload A-roll
    print("▶ Uploading A-roll...")
    with open(video_path, "rb") as f:
        res = requests.post(f"{API_URL}/upload", files={"file": f}, params={"type": "a-roll"})
        aroll_id = res.json()["id"]
        print(f"✓ A-roll ID: {aroll_id}")

    # 2. Upload B-roll
    print("▶ Uploading B-roll...")
    with open(video_path, "rb") as f:
        res = requests.post(f"{API_URL}/upload", files={"file": f}, params={"type": "b-roll"})
        broll_id = res.json()["id"]
        print(f"✓ B-roll ID: {broll_id}")

    # 3. Wait for Processing
    print("▶ Waiting for processing...")
    for vid in [aroll_id, broll_id]:
        start_wait = time.time()
        while True:
            status = requests.get(f"{API_URL}/status/{vid}").json()["status"]
            print(f"  {vid[:4]}... Status: {status}")
            if status == "completed":
                print(f"✓ Processed in {time.time() - start_wait:.2f}s")
                break
            if status == "failed":
                print("✗ Failed!")
                return
            time.sleep(2)

    # 4. Render
    print("\n▶ Requesting Render with B-roll...")
    payload = {"video_ids": [aroll_id, broll_id]}
    start_render = time.time()
    res = requests.post(f"{API_URL}/render", json=payload)
    
    if res.status_code == 200:
        result = res.json()
        print(f"✓ Rendered in {time.time() - start_render:.2f}s")
        print(f"✓ Download URL: {result['download_url']}")
        print("\nEDL Structure:")
        for clip in result["edl"]:
            print(f"  - {clip['type']}: {clip['video_id'][:4]}... ({clip['start_time']}s - {clip['end_time']}s)")
    else:
        print(f"✗ Render failed: {res.text}")

if __name__ == "__main__":
    test_broll()
