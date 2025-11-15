# app/routers/llm_agent.py

import os
import json
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path

from app.core import ChatAnalysisAgent, get_agent, parse_whatsapp_chat, chat_to_string

router = APIRouter()

# --- Pydantic Schemas for Request/Response ---

class ChatMessage(BaseModel):
    """Schema for a single chat message."""
    message: str


class UploadResponse(BaseModel):
    """Schema for file upload response."""
    status: str
    message: str
    file_name: str
    message_count: int
    todos: List[str]
    important_dates: List[Dict[str, str]]


class ChatQueryRequest(BaseModel):
    """Schema for chat query request."""
    question: str


class ChatQueryResponse(BaseModel):
    """Schema for chat query response."""
    answer: str


class TodoItem(BaseModel):
    """Schema for a single To-Do item."""
    task: str
    priority: Optional[str] = "medium"


class TodosResponse(BaseModel):
    """Schema for todos response."""
    todos: List[TodoItem]
    count: int
    last_updated: str


class ImportantDate(BaseModel):
    """Schema for an important date/event."""
    date: str
    event: str
    description: Optional[str] = None


class CalendarResponse(BaseModel):
    """Schema for calendar response."""
    dates: List[ImportantDate]
    count: int
    last_updated: str


class DataStoreItem(BaseModel):
    """Schema for data store."""
    file_name: str
    content: str
    uploaded_at: str
    todos: List[str]
    important_dates: List[Dict[str, str]]


# Module-level state - Common storage for all uploaded chats
_data_store: Dict[str, DataStoreItem] = {}
_current_file_name: Optional[str] = None


def _get_upload_dir() -> Path:
    """Get or create the uploaded data directory."""
    upload_dir = Path("uploaded_data")
    upload_dir.mkdir(exist_ok=True)
    return upload_dir


def _get_combined_chat_content() -> str:
    """Get all chat content from the data store combined."""
    if not _data_store:
        return ""
    
    combined = []
    for store_item in _data_store.values():
        combined.append(f"--- File: {store_item.file_name} ---")
        combined.append(store_item.content)
    
    return "\n\n".join(combined)


# --- MAIN ENDPOINTS FOR FRONTEND ---

@router.post("/upload", response_model=UploadResponse)
async def upload_chat(file: UploadFile = File(...)):
    """
    Upload a WhatsApp chat export file.
    
    This endpoint:
    1. Stores the chat content in common storage
    2. Automatically extracts todos
    3. Automatically identifies important dates
    4. Makes data available to all other endpoints
    
    Returns: Upload confirmation with extracted todos and dates
    """
    global _current_file_name
    
    try:
        # Read file content
        content = await file.read()
        chat_content = content.decode("utf-8")
        
        # Save file
        upload_dir = _get_upload_dir()
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Extract todos and dates using AI
        agent = get_agent()
        todos, important_dates = agent.extract_todos(chat_content)
        
        # Store in common storage
        _data_store[file.filename] = DataStoreItem(
            file_name=file.filename,
            content=chat_content,
            uploaded_at=datetime.now().isoformat(),
            todos=todos,
            important_dates=important_dates
        )
        
        _current_file_name = file.filename
        
        # Count messages
        lines = chat_content.strip().split("\n")
        message_count = len([l for l in lines if " - " in l])
        
        return {
            "status": "success",
            "message": f"Successfully uploaded {file.filename} with {message_count} messages",
            "file_name": file.filename,
            "message_count": message_count,
            "todos": todos,
            "important_dates": important_dates,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.get("/todos", response_model=TodosResponse)
async def get_todos():
    """
    Get all extracted todos from uploaded chats.
    
    Returns todos that were extracted and stored during file upload.
    """
    try:
        # Collect all todos from stored files
        all_todos = []
        latest_updated = datetime.now().isoformat()
        
        for store_item in _data_store.values():
            for todo_text in store_item.todos:
                all_todos.append({
                    "task": todo_text.strip('- '),
                    "priority": "medium"
                })
            # Update latest timestamp from most recent file
            if store_item.uploaded_at > latest_updated:
                latest_updated = store_item.uploaded_at
        
        # Convert to TodoItem objects
        todo_items = [
            TodoItem(
                task=todo["task"],
                priority=todo["priority"]
            )
            for todo in all_todos
        ]
        
        return {
            "todos": todo_items,
            "count": len(todo_items),
            "last_updated": latest_updated,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching todos: {str(e)}")


@router.get("/calendar", response_model=CalendarResponse)
async def get_calendar_events():
    """
    Get important dates and events from uploaded chats.
    
    Returns dates and events that were extracted and stored during file upload.
    """
    try:
        # Collect all dates from stored files
        all_dates = []
        latest_updated = datetime.now().isoformat()
        
        for store_item in _data_store.values():
            all_dates.extend(store_item.important_dates)
            # Update latest timestamp from most recent file
            if store_item.uploaded_at > latest_updated:
                latest_updated = store_item.uploaded_at
        
        # Convert to ImportantDate objects
        important_dates = [
            ImportantDate(
                date=date_item.get("date", "TBD"),
                event=date_item.get("event", ""),
                description=date_item.get("description")
            )
            for date_item in all_dates
        ]
        
        return {
            "dates": important_dates,
            "count": len(important_dates),
            "last_updated": latest_updated,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching calendar: {str(e)}")


@router.post("/chat", response_model=ChatQueryResponse)
async def chat_with_agent(request: ChatQueryRequest):
    """
    Chat with the AI agent about the uploaded chats.
    
    This endpoint uses the common storage populated by the upload endpoint.
    The agent has access to all uploaded chat content.
    
    Returns: AI response to the user's question
    """
    try:
        combined_content = _get_combined_chat_content()
        
        if not combined_content:
            raise HTTPException(
                status_code=400,
                detail="No chat files uploaded. Please upload a chat file first using the /upload endpoint."
            )
        
        agent = get_agent()
        answer = agent.analyze_chat(combined_content, request.question)
        
        return {
            "answer": answer,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@router.get("/files")
async def list_uploaded_files():
    """
    Get list of all uploaded chat files.
    
    Returns: List of file names and their metadata
    """
    try:
        files_list = []
        for file_name, store_item in _data_store.items():
            files_list.append({
                "file_name": file_name,
                "uploaded_at": store_item.uploaded_at,
                "message_count": len(store_item.content.split("\n")),
                "todo_count": len(store_item.todos),
                "date_count": len(store_item.important_dates),
            })
        
        return {
            "files": files_list,
            "total_files": len(files_list),
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching files: {str(e)}")


@router.delete("/files/{file_name}")
async def delete_file(file_name: str):
    """
    Delete an uploaded chat file from storage.
    
    This will remove the file from common storage and the uploaded_data directory.
    """
    try:
        # Remove from memory store
        if file_name in _data_store:
            del _data_store[file_name]
        
        # Remove from disk
        upload_dir = _get_upload_dir()
        file_path = upload_dir / file_name
        if file_path.exists():
            file_path.unlink()
        
        return {
            "status": "success",
            "message": f"File {file_name} deleted successfully",
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")


@router.get("/status")
async def get_status():
    """
    Get current status of the system.
    
    Returns: Information about uploaded files and storage
    """
    try:
        combined_content = _get_combined_chat_content()
        total_todos = sum(len(item.todos) for item in _data_store.values())
        total_dates = sum(len(item.important_dates) for item in _data_store.values())
        
        return {
            "files_uploaded": len(_data_store),
            "total_messages": len(combined_content.split("\n")),
            "total_todos": total_todos,
            "total_calendar_events": total_dates,
            "is_ready": len(_data_store) > 0,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")