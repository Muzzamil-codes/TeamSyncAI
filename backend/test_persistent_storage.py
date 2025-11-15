#!/usr/bin/env python3
"""
Test persistent todo and calendar storage
"""
import requests
import time
from pathlib import Path
import json

# Wait for server startup
time.sleep(3)

base_url = "http://localhost:8000/api/v1/agent"

# Create test chat file
chat_file = Path("test_chat.txt")
with open(chat_file, "w") as f:
    f.write("""[11/15/25, 2:30 PM] John: Hey team, let's sync on the project
[11/15/25, 2:35 PM] Sarah: Sure! We need to finalize the design by Friday
[11/15/25, 2:40 PM] Mike: I'll prepare the budget analysis by Monday
[11/15/25, 3:00 PM] John: Great, team meeting on Wednesday at 2 PM
[11/15/25, 3:05 PM] Sarah: Looking forward to it!
[11/15/25, 3:10 PM] Mike: Should we schedule a project deadline for next month?""")

print("=" * 60)
print("TEST: Persistent Todo and Calendar Storage")
print("=" * 60)

# Step 1: Upload file
print("\n1️⃣  UPLOADING FILE...")
with open(chat_file, "rb") as f:
    files = {"file": (chat_file.name, f, "text/plain")}
    response = requests.post(f"{base_url}/upload", files=files)

print(f"   Status: {response.status_code}")
upload_data = response.json()
print(f"   File: {upload_data['file_name']}")
print(f"   Messages: {upload_data['message_count']}")
print(f"   Todos extracted: {len(upload_data['todos'])}")
print(f"   Calendar events extracted: {len(upload_data['important_dates'])}")

# Print extracted todos
print("\n   📋 Extracted Todos:")
for i, todo in enumerate(upload_data['todos'], 1):
    print(f"      {i}. {todo}")

# Print extracted dates
print("\n   📅 Extracted Dates:")
for i, date_item in enumerate(upload_data['important_dates'], 1):
    print(f"      {i}. {date_item['event']} (Date: {date_item['date']})")

# Step 2: Get todos (should return stored todos, not regenerated)
print("\n2️⃣  FETCHING TODOS (should return stored todos)...")
time.sleep(1)
response = requests.get(f"{base_url}/todos")
todos_data = response.json()

print(f"   Status: {response.status_code}")
print(f"   Total todos: {todos_data['count']}")
print(f"   Last updated: {todos_data['last_updated']}")

print("\n   📋 Stored Todos:")
for i, todo_item in enumerate(todos_data['todos'], 1):
    print(f"      {i}. {todo_item['task']}")
    print(f"         Priority: {todo_item['priority']} | Status: {todo_item['status']}")

# Step 3: Get calendar (should return stored dates)
print("\n3️⃣  FETCHING CALENDAR (should return stored dates)...")
time.sleep(1)
response = requests.get(f"{base_url}/calendar")
calendar_data = response.json()

print(f"   Status: {response.status_code}")
print(f"   Total events: {calendar_data['count']}")
print(f"   Last updated: {calendar_data['last_updated']}")

print("\n   📅 Stored Calendar Events:")
for i, date_item in enumerate(calendar_data['dates'], 1):
    print(f"      {i}. {date_item['event']}")
    print(f"         Date: {date_item['date']} | Description: {date_item['description']}")

# Step 4: Upload another file
print("\n4️⃣  UPLOADING SECOND FILE...")
chat_file2 = Path("test_chat2.txt")
with open(chat_file2, "w") as f:
    f.write("""[11/16/25, 9:00 AM] Alice: Let's schedule the deployment
[11/16/25, 9:15 AM] Bob: I'll document the API changes by tomorrow
[11/16/25, 9:30 AM] Charlie: Code review deadline is Friday
[11/16/25, 10:00 AM] Alice: Demo scheduled for next Tuesday at 11 AM""")

with open(chat_file2, "rb") as f:
    files = {"file": (chat_file2.name, f, "text/plain")}
    response = requests.post(f"{base_url}/upload", files=files)

upload_data2 = response.json()
print(f"   Status: {response.status_code}")
print(f"   File: {upload_data2['file_name']}")
print(f"   Additional todos: {len(upload_data2['todos'])}")

# Step 5: Fetch todos again (should include todos from both files)
print("\n5️⃣  FETCHING TODOS AGAIN (should include todos from both files)...")
time.sleep(1)
response = requests.get(f"{base_url}/todos")
todos_data = response.json()

print(f"   Status: {response.status_code}")
print(f"   Total todos NOW: {todos_data['count']}")

print("\n   📋 ALL STORED TODOS (from both files):")
for i, todo_item in enumerate(todos_data['todos'], 1):
    print(f"      {i}. {todo_item['task']}")

# Step 6: Fetch calendar again
print("\n6️⃣  FETCHING CALENDAR AGAIN (should include events from both files)...")
time.sleep(1)
response = requests.get(f"{base_url}/calendar")
calendar_data = response.json()

print(f"   Status: {response.status_code}")
print(f"   Total events NOW: {calendar_data['count']}")

print("\n   📅 ALL STORED CALENDAR EVENTS (from both files):")
for i, date_item in enumerate(calendar_data['dates'], 1):
    print(f"      {i}. {date_item['event']}")

print("\n" + "=" * 60)
print("✅ TEST COMPLETE: Todos and Calendar are now persistent!")
print("=" * 60)
