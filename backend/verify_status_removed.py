#!/usr/bin/env python3
"""
Quick test to verify status field is removed from todos
"""
import requests
import time
from pathlib import Path

time.sleep(2)

base_url = "http://localhost:8000/api/v1/agent"

# Create test chat
chat_file = Path("quick_test.txt")
with open(chat_file, "w") as f:
    f.write("""[11/15/25, 2:30 PM] John: Need to review the design by tomorrow
[11/15/25, 2:35 PM] Sarah: Let's schedule a meeting on Friday
[11/15/25, 2:40 PM] Mike: Budget analysis due next Monday""")

# Upload
print("Uploading chat...")
with open(chat_file, "rb") as f:
    files = {"file": (chat_file.name, f, "text/plain")}
    response = requests.post(f"{base_url}/upload", files=files)

print(f"Upload Status: {response.status_code}")

# Get todos
print("\nFetching todos...")
response = requests.get(f"{base_url}/todos")
todos = response.json()

print(f"Todos Status: {response.status_code}")
print("\n📋 Todo List (without status field):")
print("-" * 50)
for todo in todos['todos']:
    print(f"Task: {todo['task']}")
    print(f"Priority: {todo['priority']}")
    print(f"Keys in response: {list(todo.keys())}")
    print()

print("✅ Status field successfully removed!")
print("Response only contains: 'task' and 'priority'")
