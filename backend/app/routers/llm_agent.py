# app/routers/llm_agent.py

import os
import json
import threading
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path
from sqlalchemy.orm import Session

from app.core.rag_agent import ChatAnalysisAgent
from app.core.database import get_db
from app.models import User, UploadedFile, TodoItem, CalendarEvent
from app.tasks import process_uploaded_file, analyze_chat_async
from app.routers.auth import get_current_user

router = APIRouter()

# Initialize agent globally
agent = ChatAnalysisAgent()

# --- Pydantic Schemas ---

class ChatQueryRequest(BaseModel):
    """Schema for chat query request."""
    question: str
    file_id: Optional[int] = None


class TodoItemSchema(BaseModel):
    """Schema for a single To-Do item."""
    id: int
    task: str
    priority: str
    completed: bool
    due_date: Optional[str] = None

    class Config:
        from_attributes = True


class CalendarEventSchema(BaseModel):
    """Schema for calendar event."""
    id: int
    title: str
    event_date: str
    description: Optional[str] = None
    is_scheduled: bool

    class Config:
        from_attributes = True
    
    @staticmethod
    def from_orm(obj):
        """Override from_orm to convert datetime to string"""
        if obj is None:
            return None
        # Get the attributes as a dictionary
        data = {
            'id': obj.id,
            'title': obj.title,
            'event_date': obj.event_date.strftime('%Y-%m-%d') if hasattr(obj.event_date, 'strftime') else str(obj.event_date),
            'description': obj.description,
            'is_scheduled': obj.is_scheduled
        }
        return CalendarEventSchema(**data)


class UploadResponse(BaseModel):
    """Schema for file upload response."""
    status: str
    message: str
    file_id: int
    file_name: str
    task_id: str


class FileInfo(BaseModel):
    """Schema for uploaded file info."""
    id: int
    filename: str
    message_count: int
    uploaded_at: str

    class Config:
        from_attributes = True


class StatusResponse(BaseModel):
    """Schema for status response."""
    status: str
    message: str



# --- Endpoints ---

@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and process a chat file.
    Returns task_id for async processing status.
    """
    try:
        # Read file content
        content = await file.read()
        text_content = content.decode("utf-8", errors="ignore")
        
        # Create uploads directory if not exists
        upload_dir = Path("uploaded_data")
        upload_dir.mkdir(exist_ok=True)
        
        # Save file
        file_path = upload_dir / f"{current_user.id}_{file.filename}"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text_content)
        
        # Count messages
        message_count = text_content.count("\n")
        
        # Create file record in database
        db_file = UploadedFile(
            filename=file.filename,
            file_path=str(file_path),
            user_id=current_user.id,
            content=text_content,
            message_count=message_count
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        # Return immediately, then process in background
        task_id = f"file-{db_file.id}"
        
        # Queue background task for processing (don't wait for it)
        try:
            task = process_uploaded_file.apply_async(
                args=(db_file.id, current_user.id),
                queue='default'
            )
            task_id = task.id
        except Exception as celery_error:
            # If Celery fails, queue synchronous processing in a thread
            import logging
            import sys
            logger = logging.getLogger(__name__)
            logger.warning(f"Celery task queueing failed (expected). Processing asynchronously via thread.")
            print(f"[DEBUG] Celery failed, starting thread for file {db_file.id}", flush=True)
            
            def process_in_thread():
                try:
                    print(f"[DEBUG] Thread STARTED for file {db_file.id}", flush=True)
                    from app.tasks import process_file_sync
                    result = process_file_sync(db_file.id, current_user.id)
                    print(f"[DEBUG] Thread COMPLETED for file {db_file.id}: {result}", flush=True)
                except Exception as e:
                    print(f"[ERROR] Thread FAILED for file {db_file.id}: {e}", flush=True)
                    import traceback
                    traceback.print_exc()
            
            # Start processing in background thread (non-blocking)
            thread = threading.Thread(target=process_in_thread, daemon=True)
            thread.start()
            print(f"[DEBUG] Thread object created and started for file {db_file.id}", flush=True)
        
        return UploadResponse(
            status="success",
            message="File uploaded successfully. Processing started.",
            file_id=db_file.id,
            file_name=file.filename,
            task_id=task_id
        )
    
    except Exception as e:
        import logging
        logging.error(f"File upload error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )


@router.get("/todos", response_model=List[TodoItemSchema])
async def get_todos(
    file_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get todos for current user, optionally filtered by file"""
    query = db.query(TodoItem).filter(TodoItem.user_id == current_user.id)
    
    if file_id:
        query = query.filter(TodoItem.file_id == file_id)
    
    todos = query.order_by(TodoItem.created_at.desc()).all()
    
    return [TodoItemSchema.from_orm(todo) for todo in todos]


@router.get("/calendar", response_model=List[CalendarEventSchema])
async def get_calendar_events(
    file_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get calendar events for current user, optionally filtered by file"""
    from datetime import date as dt_date
    today = dt_date.today()
    
    query = db.query(CalendarEvent).filter(
        CalendarEvent.user_id == current_user.id,
        CalendarEvent.event_date >= today  # Today and future dates
    )
    
    if file_id:
        query = query.filter(CalendarEvent.file_id == file_id)
    
    events = query.order_by(CalendarEvent.event_date).all()
    
    return [CalendarEventSchema.from_orm(event) for event in events]


@router.post("/chat")
async def chat(
    request: ChatQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat endpoint with streaming response.
    Supports both real-time analysis and async processing.
    """
    
    # Get chat content from uploaded file or use empty
    chat_content = ""
    if request.file_id:
        file_record = db.query(UploadedFile).filter(
            UploadedFile.id == request.file_id,
            UploadedFile.user_id == current_user.id
        ).first()
        
        if file_record:
            chat_content = file_record.content or ""
    
    async def generate():
        try:
            # Stream analysis response
            for chunk in agent.analyze_chat(chat_content, request.question):
                yield f'data: {{"chunk": {json.dumps(chunk)}}}\n'
        except Exception as e:
            yield f'data: {{"error": {json.dumps(str(e))}}}\n'
    
    return StreamingResponse(generate(), media_type="application/x-ndjson")


@router.get("/files", response_model=List[FileInfo])
async def list_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all uploaded files for current user"""
    files = db.query(UploadedFile).filter(
        UploadedFile.user_id == current_user.id
    ).order_by(UploadedFile.uploaded_at.desc()).all()
    
    return [
        FileInfo(
            id=f.id,
            filename=f.filename,
            message_count=f.message_count,
            uploaded_at=f.uploaded_at.isoformat() if f.uploaded_at else None
        )
        for f in files
    ]


@router.delete("/files/{file_id}", response_model=StatusResponse)
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an uploaded file and associated data"""
    
    file_record = db.query(UploadedFile).filter(
        UploadedFile.id == file_id,
        UploadedFile.user_id == current_user.id
    ).first()
    
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    try:
        # Delete associated todos and events
        db.query(TodoItem).filter(TodoItem.file_id == file_id).delete()
        db.query(CalendarEvent).filter(CalendarEvent.file_id == file_id).delete()
        
        # Delete file from disk
        if os.path.exists(file_record.file_path):
            os.remove(file_record.file_path)
        
        # Delete file record
        db.delete(file_record)
        db.commit()
        
        return StatusResponse(
            status="success",
            message="File deleted successfully"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting file: {str(e)}"
        )


@router.get("/status", response_model=StatusResponse)
async def get_status(current_user: User = Depends(get_current_user)):
    """Get API status"""
    return StatusResponse(
        status="ok",
        message="TeamSync API is running"
    )
