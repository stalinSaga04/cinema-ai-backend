#!/usr/bin/env python3
"""
Simple monitoring script for Cinema AI Backend
Monitors health, active processing, and logs errors
"""

import requests
import time
import json
from datetime import datetime

API_URL = "https://cinema-ai-backend.onrender.com"
CHECK_INTERVAL = 30  # seconds

def check_health():
    """Check if service is healthy"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def log_event(event_type, message):
    """Log events with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{event_type}] {message}"
    print(log_entry)
    
    # Append to log file
    with open("monitor.log", "a") as f:
        f.write(log_entry + "\n")

def main():
    print("🔍 Starting Cinema AI Backend Monitor...")
    print(f"Checking every {CHECK_INTERVAL} seconds")
    print("Press Ctrl+C to stop\n")
    
    consecutive_failures = 0
    
    try:
        while True:
            is_healthy = check_health()
            
            if is_healthy:
                if consecutive_failures > 0:
                    log_event("RECOVERY", "Service is back online")
                    consecutive_failures = 0
                else:
                    log_event("OK", "Service is healthy")
            else:
                consecutive_failures += 1
                log_event("ERROR", f"Service is down (failure #{consecutive_failures})")
                
                if consecutive_failures >= 3:
                    log_event("ALERT", "Service has been down for 3+ checks!")
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n✓ Monitoring stopped")

if __name__ == "__main__":
    main()
