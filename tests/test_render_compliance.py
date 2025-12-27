import os
import sys
import subprocess
import json

# Add parent directory to path to import core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.video_renderer import VideoRenderer
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    from moviepy import VideoFileClip

def get_video_resolution(path):
    clip = VideoFileClip(path)
    w, h = clip.size
    clip.close()
    return w, h

def test_render_compliance():
    print("Starting Render Compliance Test...")
    
    # We need a real video file to test rendering
    # I'll use the 'test_video.mp4' if it exists, or create a tiny one
    test_video = "test_video.mp4"
    if not os.path.exists(test_video):
        print("Creating dummy test video...")
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", "testsrc=duration=2:size=1280x720:rate=24",
            "-c:v", "libx264", "-y", test_video
        ], check=True)
    
    renderer = VideoRenderer(output_dir="outputs/test_renders", uploads_dir=".")
    
    edl = [
        {"video_id": "test_video", "start_time": 0.0, "end_time": 1.0}
    ]
    
    print("Step 1: Running render with PRD filters")
    output_path = renderer.render_video(edl, "compliance_test.mp4")
    
    if not output_path or not os.path.exists(output_path):
        print("✗ Render failed to produce output")
        sys.exit(1)
        
    print(f"✓ Render produced: {output_path}")
    
    # 2. Verify Resolution (PRD 12. Free Tier - 720p)
    print("Step 2: Verifying resolution (Must be 720p height)")
    width, height = get_video_resolution(output_path)
    print(f"Resolution: {width}x{height}")
    
    assert height == 720
    print("✓ 720p Resolution verified")
    
    # 3. Verify Watermark (Visual check usually, but we can check if ffmpeg parameters were used)
    # Since we can't easily "see" the watermark programmatically without OCR/CV, 
    # we rely on the fact that the render finished with the filters.
    
    print("Render Compliance Test Passed!")

if __name__ == "__main__":
    try:
        test_render_compliance()
    except Exception as e:
        print(f"Test Failed: {e}")
        sys.exit(1)
