# Quick Deploy to Render.com

## 🚀 Quick Steps

1. **Go to**: https://render.com
2. **Sign in** with GitHub
3. **New +** → **Web Service**
4. **Select repo**: `stalinSaga04/cinema-ai-backend`
5. **Configure**:
   - Environment: **Docker**
   - Instance: **Free** (or Starter for production)
6. **Create Web Service**

## ⏱️ Wait Time
- First build: **10-15 minutes**
- Downloading PyTorch, Whisper, DeepFace models

## ✅ Test After Deploy
```bash
# Health check
curl https://cinema-ai-backend.onrender.com/health

# Full test
python3 test_pipeline.py test_video.mp4
```

## 📋 What's Already Configured
✅ Dockerfile optimized for ML dependencies  
✅ render.yaml with Docker environment  
✅ All dependencies in requirements.txt  
✅ Model download script included  
✅ Code tested and working locally  

## 🎯 Your URL
`https://cinema-ai-backend.onrender.com`

---

**Note**: Free tier sleeps after 15 min inactivity. First request takes 30-60s to wake up.
