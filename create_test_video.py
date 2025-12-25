#!/usr/bin/env python3
"""
Quick test script to verify the updated brain with PRD-compliant output
"""

import cv2
import numpy as np
import os

def create_test_video(output_path="test_video.mp4", duration=5, fps=30):
    """Create a simple test video with changing colors and text"""
    print(f"Creating test video: {output_path}")
    
    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    total_frames = fps * duration
    
    for i in range(total_frames):
        # Create frame with gradient
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Color changes over time
        color_value = int((i / total_frames) * 255)
        frame[:, :] = [color_value, 100, 255 - color_value]
        
        # Add text
        text = f"Frame {i+1}/{total_frames}"
        cv2.putText(frame, text, (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 
                   1.5, (255, 255, 255), 2)
        
        # Add scene marker every 1 second
        if i % fps == 0:
            scene_text = f"Scene {i//fps + 1}"
            cv2.putText(frame, scene_text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 
                       2, (0, 255, 0), 3)
        
        out.write(frame)
    
    out.release()
    print(f"✓ Test video created: {output_path}")
    print(f"  Duration: {duration}s, FPS: {fps}, Frames: {total_frames}")
    return output_path

if __name__ == "__main__":
    video_path = create_test_video()
    print(f"\nNow run: python3 test_pipeline.py {video_path}")
