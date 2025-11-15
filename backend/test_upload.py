#!/usr/bin/env python3
"""
Test the upload endpoint
"""
import requests
import time
from pathlib import Path

# Wait for server
time.sleep(3)

# Create test chat file if it doesn't exist
chat_file = Path("chat.txt")
if not chat_file.exists():
    with open(chat_file, "w") as f:
        f.write("""[11/15/25, 2:30 PM] John: Hey team, let's sync on the project
[11/15/25, 2:35 PM] Sarah: Sure! We need to finalize the design
[11/15/25, 2:40 PM] Mike: I'll prepare the budget by Friday
[11/15/25, 3:00 PM] John: Great, meeting on Monday at 10 AM
[11/15/25, 3:05 PM] Sarah: Looking forward to it!""")

# Test upload
url = "http://localhost:8000/api/v1/agent/upload"
with open(chat_file, "rb") as f:
    files = {"file": (chat_file.name, f, "text/plain")}
    
    print("Testing upload endpoint...")
    print(f"URL: {url}")
    print(f"File: {chat_file.name}")
    print()
    
    try:
        response = requests.post(url, files=files)
        print(f"Status Code: {response.status_code}")
        print()
        print("Response:")
        print(response.json())
    except Exception as e:
        print(f"Error: {e}")
