import requests
import time
import os
import json

API_URL = "https://cinema-ai-backend.onrender.com"
VIDEO_FILE = "test_video.mp4"

def upload_video(path):
    print(f"▶ Uploading {path}...")
    with open(path, "rb") as f:
        response = requests.post(f"{API_URL}/upload", files={"file": f})
    if response.status_code == 200:
        vid = response.json()["id"]
        print(f"✓ Uploaded! ID: {vid}")
        return vid
    else:
        print(f"✗ Upload failed: {response.text}")
        return None

def wait_for_processing(video_id):
    print(f"▶ Waiting for processing {video_id}...")
    for _ in range(60): # Wait up to 5 mins (free tier is slow)
        try:
            response = requests.get(f"{API_URL}/status/{video_id}", timeout=10)
            if response.status_code == 200:
                status = response.json()["status"]
                print(f"  Status: {status}")
                if status == "completed":
                    return True
                if status == "failed":
                    return False
        except:
            pass
        time.sleep(5)
    return False

def main():
    if not os.path.exists(VIDEO_FILE):
        print(f"Error: {VIDEO_FILE} not found.")
        return

    print("="*60)
    print("🎬 TESTING PHASE 2: RETAKE MATCHING")
    print("="*60)

    # 1. Upload "Take 1"
    id1 = upload_video(VIDEO_FILE)
    
    # 2. Upload "Take 2" (Same video for test)
    id2 = upload_video(VIDEO_FILE)

    if not id1 or not id2:
        return

    # 3. Wait for both to process
    if wait_for_processing(id1) and wait_for_processing(id2):
        print("\n✓ Both videos processed successfully!")
        
        # 4. Compare them
        print("\n▶ Comparing Takes...")
        payload = {
            "video_ids": [id1, id2],
            "reference_script": "Hello world this is a test" # Optional script
        }
        
        response = requests.post(f"{API_URL}/compare", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "="*60)
            print("🏆 COMPARISON RESULT")
            print("="*60)
            print(json.dumps(result, indent=2))
            
            print(f"\n✓ Best Take: {result.get('best_take_id')}")
        else:
            print(f"✗ Comparison failed: {response.text}")
    else:
        print("✗ Processing failed or timed out.")

if __name__ == "__main__":
    main()
