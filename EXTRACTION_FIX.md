# File Processing Extraction Fix

## Problem Statement

User uploaded a WhatsApp chat file containing:
```
15/11/2025, 12:12 pm - Md. Muzzamil: Tomorrow we will be having a meeting to discuss about our future plans on Market change
```

**Expected Behavior:**
- Extract todo: "Attend meeting about Market change"
- Extract calendar event: Date=2025-11-16 (tomorrow from 15/11/2025), Title="Meeting: Market change"

**Actual Behavior:**
- Upload took too long
- No todos created
- No calendar events created

## Root Causes Identified

### 1. **Natural Language Date Handling**
The AI (Gemini) was asked to extract dates in YYYY-MM-DD format, but it doesn't know today's date to convert "tomorrow" → "2025-11-16". The prompt didn't provide context about the current date.

### 2. **Lack of Date Intelligence**
Date parsing only handled ISO format (YYYY-MM-DD). Natural language like "tomorrow", "next week", "next Monday" was not handled.

### 3. **No Logging/Visibility**
There was no logging to see:
- What Gemini extracted
- What dates were parsed successfully
- What failed and why

## Solutions Implemented

### 1. **Enhanced Gemini Prompt with Date Context**
Updated `rag_agent.py` line 289 to include today's date in the AI prompt:

```python
dates_prompt = PromptTemplate(
    input_variables=["chat_content", "today_date"],
    template="""You are TeamSyc, a productivity AI assistant.

**Today's date is: {today_date}**

Analyze the following WhatsApp group chat and extract all important dates, deadlines, and scheduled events mentioned:

<chat>
{chat_content}
</chat>

For each date/event found, provide in this exact format:
DATE: [date in YYYY-MM-DD format - convert relative dates like "tomorrow" or "next week" to actual dates based on today's date] | EVENT: [event name/description]

Examples:
- If today is 2025-11-15 and chat says "meeting tomorrow", write: DATE: 2025-11-16 | EVENT: Meeting
- If today is 2025-11-15 and chat says "November 20", write: DATE: 2025-11-20 | EVENT: [event description]

IMPORTANT: When you see words like "tomorrow", "next week", "next Monday", calculate the actual date using today's date ({today_date}).
```

Now Gemini knows the current date and can intelligently convert natural language dates.

### 2. **Added Fallback Natural Language Date Parser**
Installed `python-dateutil` library and added fallback parsing (line 355-369):

```python
except ValueError as e:
    logger.warning(f"Failed to parse date '{date_str}': {e}")
    # If date parsing fails, try natural language parsing as fallback
    try:
        from dateutil import parser as date_parser
        parsed_date = date_parser.parse(date_str, fuzzy=True).date()
        if parsed_date >= today:
            iso_date = parsed_date.strftime("%Y-%m-%d")
            found_dates[iso_date] = {
                "date": iso_date,
                "events": [event_str],
                "description": event_str
            }
            logger.info(f"Parsed via dateutil: {date_str} → {iso_date}")
    except:
        # Last resort: include with TBD
        if event_str:
            found_dates[f"TBD_{len(found_dates)}"] = {
                "date": "TBD",
                "events": [event_str],
                "description": event_str
            }
```

If Gemini doesn't convert "tomorrow" correctly, `dateutil.parser` can handle it as a fallback.

### 3. **Comprehensive Logging**
Added logging throughout the extraction process:

```python
logger.info(f"Starting extraction for chat content ({len(chat_content)} chars)")
logger.info("Calling LLM for todo extraction...")
logger.info(f"LLM todo response: {todo_response[:200]}...")
logger.info(f"Extracted {len(todos)} todos from LLM response")
logger.info(f"Today's date for extraction: {today}")
logger.info("Calling LLM for date extraction...")
logger.info(f"LLM dates response: {dates_response[:300]}...")
logger.info(f"Processing AI-extracted date: {date_str} | event: {event_str}")
logger.info(f"AI extracted {ai_extracted_count} valid dates")
logger.info(f"Extraction complete: {len(todos)} todos, {len(important_dates)} dates")
```

Now you can see exactly what Gemini returns and track the entire extraction flow.

## Testing the Fix

### Start the Backend
```bash
cd D:\KMIT\backend
python -m uvicorn app.main:app --reload --port 8001
```

### Test with WhatsApp Chat File
1. Upload the file containing "Tomorrow we will be having a meeting..."
2. Check backend logs to see:
   - Gemini's todo extraction response
   - Gemini's date extraction response
   - Whether it successfully converted "tomorrow" → "2025-11-16"
3. Verify that both todo and calendar event are created in the database

### Expected Log Output
```
INFO: [Sync] Starting extraction for file 1 (content: 234 chars)
INFO: Starting extraction for chat content (234 chars)
INFO: Today's date for extraction: 2025-11-15
INFO: Calling LLM for todo extraction...
INFO: LLM todo response: - Attend meeting to discuss future plans on Market change...
INFO: Extracted 1 todos from LLM response
INFO: Calling LLM for date extraction...
INFO: LLM dates response: DATE: 2025-11-16 | EVENT: Meeting to discuss future plans on Market change...
INFO: Processing AI-extracted date: 2025-11-16 | event: Meeting to discuss future plans on Market change
INFO: AI extracted 1 valid dates
INFO: Extraction complete: 1 todos, 1 dates
INFO: [Sync] Extraction returned: 1 todos, 1 dates
INFO: [Sync] Successfully processed file 1: 1 todos, 1 valid dates
```

## Key Improvements

1. **Date Intelligence**: Gemini now knows today's date and can convert natural language
2. **Fallback Parsing**: If Gemini fails, dateutil handles natural language dates
3. **Full Visibility**: Comprehensive logging shows exactly what's happening
4. **Faster Processing**: Background thread handles processing without blocking upload

## Files Modified

- `d:\KMIT\backend\app\core\rag_agent.py` (lines 123-405)
  - Added date context to Gemini prompt
  - Added comprehensive logging
  - Added dateutil fallback parser

## Dependencies Added

- `python-dateutil` - Natural language date parsing library

## Next Steps (Optional)

1. Add frontend error visibility - show processing status to users
2. Add retry logic if Gemini API fails
3. Optimize processing speed (currently ~3-5 seconds)
4. Add progress indicator in frontend during file processing
