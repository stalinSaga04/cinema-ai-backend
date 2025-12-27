#!/usr/bin/env python3
"""
Test script for Cinema AI Backend video upload pipeline
Tests: Upload → Status Polling → Results Retrieval
"""

import requests
import time
import sys
import json
from pathlib import Path

# Configuration
API_URL = "https://cinema-ai-backend.onrender.com"
TIMEOUT = 300  # 5 minutes max wait time

class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

def print_step(msg):
    print(f"{Colors.BLUE}▶ {msg}{Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.YELLOW}ℹ {msg}{Colors.END}")

def test_health():
    """Test 1: Health check"""
    print_step("Testing health endpoint...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=30)
        if response.status_code == 200:
            print_success(f"Health check passed: {response.json()}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False

def create_test_video():
    """Create a simple test video using OpenCV"""
    print_step("Creating test video...")
    try:
        import cv2
        import numpy as np
        
        # Create a 5-second video at 30fps
        width, height = 640, 480
        fps = 30
        duration = 5
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_path = 'test_video.mp4'
        out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
        
        for i in range(fps * duration):
            # Create a frame with changing colors
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            color_value = int((i / (fps * duration)) * 255)
            frame[:, :] = [color_value, 100, 255 - color_value]
            
            # Add text
            text = f"Frame {i+1}"
            cv2.putText(frame, text, (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 
                       2, (255, 255, 255), 3)
            out.write(frame)
        
        out.release()
        print_success(f"Test video created: {video_path}")
        return video_path
    except ImportError:
        print_error("OpenCV not installed. Please provide a test video manually.")
        return None
    except Exception as e:
        print_error(f"Error creating test video: {e}")
        return None

def upload_video(video_path):
    """Test 2: Upload video"""
    print_step(f"Uploading video: {video_path}...")
    
    if not Path(video_path).exists():
        print_error(f"Video file not found: {video_path}")
        return None
    
    try:
        with open(video_path, 'rb') as f:
            files = {'file': (Path(video_path).name, f, 'video/mp4')}
            response = requests.post(f"{API_URL}/upload", files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            video_id = data.get('id')
            print_success(f"Upload successful! Video ID: {video_id}")
            print_info(f"Response: {data}")
            return video_id
        else:
            print_error(f"Upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print_error(f"Upload error: {e}")
        return None

def poll_status(video_id, max_wait=TIMEOUT):
    """Test 3: Poll processing status"""
    print_step(f"Polling status for video ID: {video_id}...")
    
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{API_URL}/status/{video_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                
                if status != last_status:
                    print_info(f"Status: {status}")
                    last_status = status
                
                if status == 'completed':
                    elapsed = time.time() - start_time
                    print_success(f"Processing completed in {elapsed:.1f} seconds!")
                    return True
                elif status == 'failed':
                    print_error(f"Processing failed: {data}")
                    return False
                
                time.sleep(2)  # Poll every 2 seconds
            else:
                print_error(f"Status check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"Status polling error: {e}")
            time.sleep(2)
    
    print_error(f"Timeout after {max_wait} seconds")
    return False

def get_results(video_id):
    """Test 4: Retrieve results"""
    print_step(f"Retrieving results for video ID: {video_id}...")
    
    try:
        response = requests.get(f"{API_URL}/result/{video_id}", timeout=10)
        
        if response.status_code == 200:
            results = response.json()
            print_success("Results retrieved successfully!")
            
            # Pretty print results
            print("\n" + "="*60)
            print("ANALYSIS RESULTS")
            print("="*60)
            print(json.dumps(results, indent=2))
            print("="*60 + "\n")
            
            # Save to file
            results_file = f"results_{video_id}.json"
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            print_success(f"Results saved to: {results_file}")
            
            return results
        else:
            print_error(f"Failed to retrieve results: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Error retrieving results: {e}")
        return None

def main():
    print("\n" + "="*60)
    print("🎬 Cinema AI Backend - Full Pipeline Test")
    print("="*60 + "\n")
    
    # Test 1: Health Check
    if not test_health():
        print_error("Health check failed. Aborting tests.")
        sys.exit(1)
    
    print()
    
    # Get video path
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        print_info(f"Using provided video: {video_path}")
    else:
        print_info("No video provided. Creating test video...")
        video_path = create_test_video()
        if not video_path:
            print_error("Please provide a video file: python test_pipeline.py <video_path>")
            sys.exit(1)
    
    print()
    
    # Test 2: Upload
    video_id = upload_video(video_path)
    if not video_id:
        print_error("Upload failed. Aborting tests.")
        sys.exit(1)
    
    print()
    
    # Test 3: Poll Status
    if not poll_status(video_id):
        print_error("Processing failed or timed out.")
        sys.exit(1)
    
    print()
    
    # Test 4: Get Results
    results = get_results(video_id)
    if not results:
        print_error("Failed to retrieve results.")
        sys.exit(1)
    
    print()
    print_success("🎉 All tests passed successfully!")
    print()

if __name__ == "__main__":
    main()
