#!/usr/bin/env python3
"""
Test enhanced date extraction
"""
import requests
import time
from pathlib import Path
import json

time.sleep(3)

base_url = "http://localhost:8000/api/v1/agent"

# Create test chat with various date formats
chat_file = Path("test_dates.txt")
with open(chat_file, "w") as f:
    f.write("""[11/15/25, 2:30 PM] John: The hackathon is on November 16th, 2025
[11/15/25, 2:35 PM] Sarah: We need to submit by 2025-11-20
[11/15/25, 2:40 PM] Mike: Team meeting scheduled for 11/18/25 at 3 PM
[11/15/25, 3:00 PM] John: Deadline is November 25th for final submission
[11/15/25, 3:05 PM] Alice: Can we schedule a demo on 11-22-2025?
[11/15/25, 3:10 PM] Bob: Project review on December 5, 2025""")

print("=" * 70)
print("TESTING ENHANCED DATE EXTRACTION")
print("=" * 70)

# Upload file
print("\n1️⃣  UPLOADING CHAT FILE WITH MULTIPLE DATE FORMATS...")
with open(chat_file, "rb") as f:
    files = {"file": (chat_file.name, f, "text/plain")}
    response = requests.post(f"{base_url}/upload", files=files)

upload_data = response.json()
print(f"   Status: {response.status_code}")
print(f"   File: {upload_data['file_name']}")

print("\n   📋 Extracted Todos:")
for i, todo in enumerate(upload_data['todos'], 1):
    print(f"      {i}. {todo}")

print("\n   📅 Extracted Dates (from upload response):")
for i, date_item in enumerate(upload_data['important_dates'], 1):
    print(f"      {i}. Date: {date_item['date']}")
    print(f"         Event: {date_item['event']}")
    if date_item.get('description'):
        print(f"         Description: {date_item['description']}")

# Get calendar
print("\n2️⃣  FETCHING CALENDAR ENDPOINT...")
time.sleep(1)
response = requests.get(f"{base_url}/calendar")
calendar_data = response.json()

print(f"   Status: {response.status_code}")
print(f"   Total events: {calendar_data['count']}")

print("\n   📅 CALENDAR EVENTS WITH DATES:")
print("   " + "=" * 66)
for i, date_item in enumerate(calendar_data['dates'], 1):
    print(f"\n   {i}. Date: {date_item['date']}")
    print(f"      Event: {date_item['event']}")
    if date_item.get('description'):
        print(f"      Description: {date_item['description']}")

print("\n" + "=" * 70)
print("✅ Enhanced Date Extraction Complete!")
print("=" * 70)

# Print raw JSON for verification
print("\nRaw JSON Response:")
print(json.dumps(calendar_data, indent=2))
