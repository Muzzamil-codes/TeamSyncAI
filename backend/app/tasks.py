"""
Celery tasks for background processing
- File processing and LLM analysis
- Todo extraction
- Calendar event extraction
"""
from app.core.celery_config import celery_app
from app.core.database import SessionLocal
from app.core.rag_agent import ChatAnalysisAgent
from app.models import UploadedFile, TodoItem, CalendarEvent, PriorityEnum
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def process_uploaded_file(self, file_id: int, user_id: int):
    """
    Background task to process uploaded file:
    - Extract todos
    - Extract calendar events
    - Store in database
    
    Args:
        file_id: ID of uploaded file
        user_id: ID of file owner
    """
    db = SessionLocal()
    try:
        # Get the file record
        file_record = db.query(UploadedFile).filter(
            UploadedFile.id == file_id,
            UploadedFile.user_id == user_id
        ).first()
        
        if not file_record:
            logger.error(f"File {file_id} not found for user {user_id}")
            return {"error": "File not found"}
        
        # Initialize AI agent
        agent = ChatAnalysisAgent()
        
        # Extract todos and dates
        todos_list, dates_list = agent.extract_todos(file_record.content or "")
        
        # Clear existing todos and events for this file
        db.query(TodoItem).filter(TodoItem.file_id == file_id).delete()
        db.query(CalendarEvent).filter(CalendarEvent.file_id == file_id).delete()
        db.commit()
        
        # Store todos in database
        for todo in todos_list:
            todo_item = TodoItem(
                user_id=user_id,
                file_id=file_id,
                task=todo.get("task", ""),
                priority=PriorityEnum(todo.get("priority", "medium")),
                completed=False,
                due_date=None
            )
            db.add(todo_item)
        
        # Store calendar events in database
        valid_events_count = 0
        for date_event in dates_list:
            event_date = date_event.get("date")
            
            # Convert string date to datetime object if needed
            if event_date and event_date != "TBD":
                try:
                    if isinstance(event_date, str):
                        # Parse YYYY-MM-DD format
                        event_date = datetime.strptime(event_date, "%Y-%m-%d").date()
                except (ValueError, TypeError):
                    event_date = None
            else:
                # Skip events with TBD dates
                event_date = None
            
            # Only add events with valid dates
            if event_date:
                calendar_event = CalendarEvent(
                    user_id=user_id,
                    file_id=file_id,
                    title=date_event.get("title", "Event"),
                    event_date=event_date,
                    description=date_event.get("description", ""),
                    is_scheduled=date_event.get("is_scheduled", True)
                )
                db.add(calendar_event)
                valid_events_count += 1
        
        db.commit()
        
        logger.info(f"Successfully processed file {file_id}: {len(todos_list)} todos, {valid_events_count} valid dates")
        
        return {
            "status": "success",
            "todos_extracted": len(todos_list),
            "dates_extracted": valid_events_count
        }
        
    except Exception as exc:
        logger.error(f"Error processing file {file_id}: {str(exc)}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
    
    finally:
        db.close()


@celery_app.task(bind=True)
def cleanup_old_files(self, days: int = 30):
    """
    Background task to clean up old uploaded files
    
    Args:
        days: Delete files older than this many days
    """
    db = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        old_files = db.query(UploadedFile).filter(
            UploadedFile.uploaded_at < cutoff_date
        ).all()
        
        deleted_count = 0
        for file_record in old_files:
            # Delete associated todos and events
            db.query(TodoItem).filter(TodoItem.file_id == file_record.id).delete()
            db.query(CalendarEvent).filter(CalendarEvent.file_id == file_record.id).delete()
            
            # Delete file record
            db.delete(file_record)
            deleted_count += 1
        
        db.commit()
        
        logger.info(f"Cleaned up {deleted_count} old files")
        
        return {"status": "success", "deleted_count": deleted_count}
        
    except Exception as exc:
        logger.error(f"Error in cleanup task: {str(exc)}")
        db.rollback()
        return {"status": "error", "message": str(exc)}
    
    finally:
        db.close()


@celery_app.task(bind=True)
def analyze_chat_async(self, file_id: int, user_id: int, question: str):
    """
    Background task for heavy LLM analysis
    
    Args:
        file_id: ID of uploaded file
        user_id: ID of user asking
        question: User's question about the chat
    
    Returns:
        Analysis result
    """
    db = SessionLocal()
    try:
        # Get file content
        file_record = db.query(UploadedFile).filter(
            UploadedFile.id == file_id,
            UploadedFile.user_id == user_id
        ).first()
        
        if not file_record:
            return {"error": "File not found"}
        
        # Initialize AI agent
        agent = ChatAnalysisAgent()
        
        # Stream analysis (collect all chunks)
        analysis = ""
        for chunk in agent.analyze_chat(file_record.content or "", question):
            analysis += chunk
        
        logger.info(f"Completed analysis for file {file_id}")
        
        return {
            "status": "success",
            "analysis": analysis
        }
        
    except Exception as exc:
        logger.error(f"Error analyzing chat: {str(exc)}")
        return {"status": "error", "message": str(exc)}
    
    finally:
        db.close()


def process_file_sync(file_id: int, user_id: int):
    """
    Synchronous file processing (fallback when Celery is unavailable).
    Used when Redis/Celery is not running.
    
    Args:
        file_id: ID of uploaded file
        user_id: ID of file owner
    """
    print(f"[DEBUG] process_file_sync CALLED for file_id={file_id}, user_id={user_id}", flush=True)
    db = SessionLocal()
    try:
        # Get the file record
        file_record = db.query(UploadedFile).filter(
            UploadedFile.id == file_id,
            UploadedFile.user_id == user_id
        ).first()
        
        if not file_record:
            print(f"[ERROR] File {file_id} NOT FOUND in database", flush=True)
            logger.error(f"File {file_id} not found for user {user_id}")
            return {"error": "File not found"}
        
        print(f"[DEBUG] File record found, content length: {len(file_record.content or '')}", flush=True)
        
        # Initialize AI agent
        agent = ChatAnalysisAgent()
        print(f"[DEBUG] ChatAnalysisAgent initialized", flush=True)
        
        # Extract todos and dates
        print(f"[DEBUG] Starting extraction...", flush=True)
        todos_list, dates_list = agent.extract_todos(file_record.content or "")
        print(f"[DEBUG] Extraction complete: {len(todos_list)} todos, {len(dates_list)} dates", flush=True)
        
        # Clear existing todos and events for this file
        db.query(TodoItem).filter(TodoItem.file_id == file_id).delete()
        db.query(CalendarEvent).filter(CalendarEvent.file_id == file_id).delete()
        db.commit()
        
        # Store todos in database
        for todo in todos_list:
            todo_item = TodoItem(
                user_id=user_id,
                file_id=file_id,
                task=todo.get("task", ""),
                priority=PriorityEnum(todo.get("priority", "medium")),
                completed=False,
                due_date=None
            )
            db.add(todo_item)
        
        # Store calendar events in database
        valid_events_count = 0
        for date_event in dates_list:
            print(f"[DEBUG] Processing date_event: {date_event}", flush=True)
            event_date = date_event.get("date")
            
            # Convert string date to datetime object if needed
            if event_date and event_date != "TBD":
                try:
                    if isinstance(event_date, str):
                        # Parse YYYY-MM-DD format
                        event_date = datetime.strptime(event_date, "%Y-%m-%d").date()
                        print(f"[DEBUG] Parsed date: {event_date}", flush=True)
                except (ValueError, TypeError) as e:
                    print(f"[DEBUG] Date parsing failed: {e}", flush=True)
                    event_date = None
            else:
                # Skip events with TBD dates
                print(f"[DEBUG] Skipping TBD or empty date", flush=True)
                event_date = None
            
            # Only add events with valid dates
            if event_date:
                calendar_event = CalendarEvent(
                    user_id=user_id,
                    file_id=file_id,
                    title=date_event.get("title", "Event"),
                    event_date=event_date,
                    description=date_event.get("description", ""),
                    is_scheduled=date_event.get("is_scheduled", True)
                )
                db.add(calendar_event)
                valid_events_count += 1
                print(f"[DEBUG] Calendar event added: {calendar_event.title} on {calendar_event.event_date}", flush=True)
            else:
                print(f"[DEBUG] Event skipped due to invalid date", flush=True)
        
        db.commit()
        
        print(f"[DEBUG] Database commit successful", flush=True)
        logger.info(f"Successfully processed file {file_id} (sync): {len(todos_list)} todos, {valid_events_count} valid dates")
        
        return {
            "status": "success",
            "todos_extracted": len(todos_list),
            "dates_extracted": valid_events_count
        }
        
    except Exception as exc:
        print(f"[ERROR] Exception in process_file_sync: {exc}", flush=True)
        import traceback
        traceback.print_exc()
        logger.error(f"Error processing file {file_id} (sync): {str(exc)}")
        db.rollback()
        raise
    
    finally:
        db.close()
