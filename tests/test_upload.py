import requests
import time
import sys
import os

BASE_URL = "http://localhost:8000"

def test_upload_flow():
    # 1. Create a dummy video file if not exists
    video_path = "test_video.mp4"
    if not os.path.exists(video_path):
        print("Creating dummy video...")
        # This requires ffmpeg installed on the system
        os.system("ffmpeg -f lavfi -i testsrc=duration=3:size=640x480:rate=30 -f lavfi -i sine=frequency=1000:duration=3 -y test_video.mp4")
    
    if not os.path.exists(video_path):
        print("Failed to create test video. Skipping upload test.")
        return False

    # 2. Upload Video
    print(f"Uploading {video_path}...")
    with open(video_path, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    if response.status_code != 200:
        print(f"Upload failed: {response.text}")
        return False
    
    data = response.json()
    video_id = data["id"]
    print(f"Upload successful. Video ID: {video_id}")
    
    # 3. Poll Status
    print("Polling status...")
    for _ in range(30): # Wait up to 30 seconds
        response = requests.get(f"{BASE_URL}/status/{video_id}")
        if response.status_code != 200:
            print(f"Status check failed: {response.text}")
            return False
            
        status_data = response.json()
        status = status_data["status"]
        print(f"Current status: {status}")
        
        if status == "completed":
            print("Processing completed!")
            
            # 4. Get Result
            response = requests.get(f"{BASE_URL}/result/{video_id}")
            if response.status_code == 200:
                print("Result retrieved successfully:")
                # print(response.json())
                return True
            else:
                print(f"Failed to get result: {response.text}")
                return False
        
        elif status == "failed":
            print(f"Processing failed: {status_data.get('error')}")
            return False
            
        time.sleep(1)
        
    print("Timeout waiting for processing.")
    return False

if __name__ == "__main__":
    if test_upload_flow():
        sys.exit(0)
    else:
        sys.exit(1)
