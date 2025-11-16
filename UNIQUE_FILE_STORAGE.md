# Unique File Storage Per User

## Overview

Chat files are now uniquely stored per user with automatic deduplication. This means:
- Each user can upload a file with the same name
- If they upload the same file again, it **overwrites** the previous version
- No duplicate files for the same user

## Implementation Details

### Database Design

The `uploaded_files` collection has a unique compound index:

```python
# In app/core/database.py
await database["uploaded_files"].create_index(
    [("user_id", 1), ("filename", 1)], 
    unique=True
)
```

This ensures that the combination of `(user_id, filename)` is unique.

### Upload Logic

When a file is uploaded (`POST /api/v1/agent/upload`):

```python
# Check if file already exists for this user
existing_file = await db["uploaded_files"].find_one({
    "user_id": current_user.id,
    "filename": file.filename
})

if existing_file:
    # Update existing file (overwrites previous version)
    await db["uploaded_files"].update_one(
        {"_id": existing_file["_id"]},
        {"$set": {...}}
    )
else:
    # Create new file
    await db["uploaded_files"].insert_one({...})
```

### File Storage on Disk

Files are stored with a unique naming pattern:
```
uploaded_data/
├── user_id_1_chat.txt       # User 1's chat.txt
├── user_id_1_notes.txt      # User 1's notes.txt
├── user_id_2_chat.txt       # User 2's chat.txt (different file, same name)
└── user_id_2_messages.txt   # User 2's messages.txt
```

If User 1 uploads `chat.txt` again, the file on disk is overwritten, and todos/calendar events are regenerated.

## Behavior Examples

### Example 1: First Upload
```
User uploads "chat.txt" (100 KB)
→ File saved to database
→ Todos and calendar extracted
→ File accessible in "Uploaded Files" list
```

### Example 2: Same File Uploaded Again
```
User uploads "chat.txt" again (120 KB - updated content)
→ Old file document is updated in database
→ Old todos and calendar events are cleared
→ New todos and calendar extracted from updated content
→ File metadata (uploaded_at) is preserved, updated_at is refreshed
```

### Example 3: Different Users, Same Filename
```
User A uploads "chat.txt"
User B uploads "chat.txt"  (completely different content)
→ Both files stored separately (different user_ids)
→ No conflict - each user has their own "chat.txt"
→ Each has their own todos/calendar
```

## Consequences

### Advantages ✅
- **No Duplicates**: Users can't accidentally create duplicate files
- **Easy Updates**: Upload a new version with the same name
- **Space Efficient**: Only one version of each file per user
- **Clean UI**: No clutter in the file list

### Things to Know ⚠️
- **No Version History**: Uploading overwrites the previous file
- **Data Loss**: Previous extraction results are cleared
- **No Rollback**: Can't revert to an earlier version
  - Workaround: Users can rename files (upload "chat_v1.txt", "chat_v2.txt")

## Frontend Implications

### Upload Response
The API returns the same file ID if you upload the same file twice:

```json
{
  "status": "success",
  "message": "File updated successfully. Processing started.",
  "file_id": "507f1f77bcf86cd799439011",  // Same ID as before
  "file_name": "chat.txt",
  "task_id": "file-507f1f77bcf86cd799439011"
}
```

### Polling for Changes
When uploading an existing file:
1. File is updated in database
2. Previous todos/calendar events cleared
3. Processing begins immediately
4. Frontend polls `/todos` and `/calendar` endpoints
5. New results appear as processing completes

### User Flow
```
1. User selects file "chat.txt"
2. Click upload
3. Loading animation starts
4. After 2-3 seconds, todos/calendar update
5. If uploading same file again:
   - Old todos/calendar disappear
   - New ones appear
```

## Database Queries

### Get All Files for User
```python
files = await db["uploaded_files"].find(
    {"user_id": user_id}
).sort("uploaded_at", -1).to_list(None)
```

### Check if File Exists
```python
existing = await db["uploaded_files"].find_one({
    "user_id": user_id,
    "filename": filename
})
```

### Update File Content
```python
await db["uploaded_files"].update_one(
    {"_id": file_id, "user_id": user_id},
    {"$set": {"content": new_content, "updated_at": datetime.utcnow()}}
)
```

## Testing the Feature

### Test Case 1: Upload Same File Twice
```bash
# First upload
curl -X POST http://localhost:8001/api/v1/agent/upload \
  -H "Authorization: Bearer {token}" \
  -F "file=@chat.txt"
# Returns file_id: "abc123"

# Second upload of same file
curl -X POST http://localhost:8001/api/v1/agent/upload \
  -H "Authorization: Bearer {token}" \
  -F "file=@chat.txt"
# Returns file_id: "abc123" (same ID!)
```

### Test Case 2: Different Users, Same File
```bash
# User A uploads chat.txt
# User B uploads chat.txt
# Both succeed with different file_ids
```

## Future Enhancements

Possible improvements (not implemented):
- **Version History**: Store previous versions with timestamps
- **Restore from Backup**: Allow reverting to previous versions
- **Change Detection**: Compare old vs new content before overwriting
- **Incremental Processing**: Only extract new todos/calendar if content changed
