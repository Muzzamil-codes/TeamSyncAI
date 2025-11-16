# Testing Guide - File Upload and Extraction

## Quick Test Instructions

### 1. Start Backend (if not already running)
```powershell
cd D:\KMIT\backend
python -m uvicorn app.main:app --reload --port 8001
```

### 2. Start Frontend (if not already running)
```powershell
cd D:\KMIT\frontend
npm run dev
```

### 3. Test File Upload

1. **Login/Register** at http://localhost:5173
2. **Upload the WhatsApp chat file** containing:
   ```
   15/11/2025, 12:12 pm - Md. Muzzamil: Tomorrow we will be having a meeting to discuss about our future plans on Market change
   ```
3. **Wait for processing** (should be quick, ~3-5 seconds)
4. **Check the dashboard** for:
   - ✅ A todo item: "Attend meeting to discuss future plans on Market change"
   - ✅ A calendar event for 2025-11-16: "Meeting: Market change"

### 4. Check Backend Logs

Look for these log messages in the terminal running the backend:

```
INFO: [Sync] Starting extraction for file X (content: XXX chars)
INFO: Starting extraction for chat content (XXX chars)
INFO: Today's date for extraction: 2025-11-15
INFO: Calling LLM for todo extraction...
INFO: LLM todo response: - Attend meeting...
INFO: Extracted 1 todos from LLM response
INFO: Calling LLM for date extraction...
INFO: LLM dates response: DATE: 2025-11-16 | EVENT: Meeting...
INFO: Processing AI-extracted date: 2025-11-16 | event: Meeting...
INFO: AI extracted 1 valid dates
INFO: Extraction complete: 1 todos, 1 dates
INFO: [Sync] Extraction returned: 1 todos, 1 dates
INFO: [Sync] Successfully processed file X: 1 todos, 1 valid dates
```

## What Was Fixed

### Before ❌
- Gemini didn't know today's date
- "Tomorrow" wasn't converted to "2025-11-16"
- No logging to debug issues
- No fallback date parsing

### After ✅
- Gemini receives today's date in the prompt
- "Tomorrow" automatically converted to ISO date
- Full logging shows extraction process
- Dateutil fallback for natural language dates

## Common Issues & Solutions

### Issue: No todos/calendar events created
**Solution:** Check backend logs for extraction errors. Gemini API key might be invalid or rate-limited.

### Issue: Upload takes too long
**Solution:** 
- Check if backend is running on port 8001
- Verify background threading is working
- Check if Gemini API is responding (network issues)

### Issue: Dates shown as "TBD"
**Solution:**
- Check if date was in the past (past dates are filtered out)
- Verify Gemini prompt includes today's date
- Check logs to see if dateutil fallback tried to parse

### Issue: Backend not starting
**Solution:**
```powershell
# Make sure you're using system Python with packages installed
cd D:\KMIT\backend
python -m uvicorn app.main:app --reload --port 8001
```

## Testing Different Date Formats

Try uploading files with these date mentions:

| Input | Expected Output |
|-------|----------------|
| "meeting tomorrow" | Next day's date (YYYY-MM-DD) |
| "November 20" | 2025-11-20 |
| "next week" | ~7 days from today |
| "next Monday" | Date of next Monday |
| "15/11/25" | 2025-11-15 |
| "2025-12-25" | 2025-12-25 |

All should be converted to YYYY-MM-DD format and stored in the database.

## Verifying Database

To manually check the database:

```powershell
cd D:\KMIT\backend
python
```

```python
from app.core.database import SessionLocal, engine
from app.models import TodoItem, CalendarEvent, UploadedFile

db = SessionLocal()

# Check uploaded files
files = db.query(UploadedFile).all()
print(f"Files: {len(files)}")

# Check todos
todos = db.query(TodoItem).all()
for todo in todos:
    print(f"Todo: {todo.task} - Priority: {todo.priority} - Due: {todo.due_date}")

# Check calendar events
events = db.query(CalendarEvent).all()
for event in events:
    print(f"Event: {event.title} - Date: {event.event_date}")

db.close()
```

## Success Criteria

✅ Backend starts without errors  
✅ Frontend connects to backend  
✅ File upload completes in <5 seconds  
✅ Todos are extracted from chat  
✅ Calendar events are created with correct dates  
✅ "Tomorrow" is converted to actual ISO date  
✅ Logs show extraction process clearly  
✅ No errors in backend or frontend console  

## Need Help?

Check:
1. Backend logs (terminal running uvicorn)
2. Frontend console (browser DevTools)
3. Network tab (check API calls to /upload-file)
4. Database content (using Python script above)
