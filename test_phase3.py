import requests
import time
import os
import json

API_URL = "http://localhost:8000"
# API_URL = "https://cinema-ai-backend.onrender.com" # Uncomment for live test

def test_phase3():
    print("============================================================")
    print("🎬 TESTING PHASE 3: AUTO EDITING ENGINE")
    print("============================================================")

    # 1. Upload Videos (Simulating Retakes)
    video_ids = []
    video_path = "test_video.mp4"
    
    if not os.path.exists(video_path):
        print(f"Error: {video_path} not found. Run create_test_video.py first.")
        return

    for i in range(2):
        print(f"▶ Uploading take {i+1}...")
        with open(video_path, "rb") as f:
            response = requests.post(f"{API_URL}/upload", files={"file": f})
            if response.status_code == 200:
                vid = response.json()["id"]
                print(f"✓ Uploaded! ID: {vid}")
                video_ids.append(vid)
            else:
                print(f"✗ Upload failed: {response.text}")
                return

    # 2. Wait for Processing
    print("▶ Waiting for processing...")
    for vid in video_ids:
        while True:
            status_res = requests.get(f"{API_URL}/status/{vid}")
            status = status_res.json()["status"]
            print(f"  Take {vid[:4]}... Status: {status}")
            if status == "completed":
                break
            if status == "failed":
                print("✗ Processing failed!")
                return
            time.sleep(2)
    
    print("\n✓ All takes processed successfully!")

    # 3. Render Video
    print("\n▶ Requesting Render (Auto-Edit)...")
    payload = {
        "video_ids": video_ids,
        "reference_script": "This is a test script."
    }
    
    start_time = time.time()
    response = requests.post(f"{API_URL}/render", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("\n============================================================")
        print("🏆 RENDER SUCCESS")
        print("============================================================")
        print(json.dumps(result, indent=2))
        
        render_path = result.get("render_path")
        download_url = result.get("download_url")
        
        print(f"\n✓ Render Time: {time.time() - start_time:.2f}s")
        print(f"✓ Output File: {render_path}")
        print(f"✓ Download URL: {download_url}")
        
        # 4. Test Download
        if download_url:
            print(f"\n▶ Testing Download from {download_url}...")
            dl_res = requests.get(f"{API_URL}{download_url}", stream=True)
            if dl_res.status_code == 200:
                with open("downloaded_render.mp4", "wb") as f:
                    for chunk in dl_res.iter_content(chunk_size=8192):
                        f.write(chunk)
                print("✓ Downloaded 'downloaded_render.mp4' successfully!")
            else:
                print(f"✗ Download failed: {dl_res.status_code}")

    else:
        print(f"\n✗ Render failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_phase3()
