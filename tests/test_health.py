import requests
import time
import sys

def test_health():
    url = "http://localhost:8000/health"
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("Health check passed!")
                return True
        except requests.exceptions.ConnectionError:
            print(f"Connection failed, retrying ({i+1}/{max_retries})...")
            time.sleep(2)
    
    print("Health check failed after retries.")
    return False

if __name__ == "__main__":
    if test_health():
        sys.exit(0)
    else:
        sys.exit(1)
