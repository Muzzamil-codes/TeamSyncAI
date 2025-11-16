"""
Database models for TodoItem, CalendarEvent, User, and UploadedFile
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    uploaded_files = relationship("UploadedFile", back_populates="owner", cascade="all, delete-orphan")
    todos = relationship("TodoItem", back_populates="owner", cascade="all, delete-orphan")
    calendar_events = relationship("CalendarEvent", back_populates="owner", cascade="all, delete-orphan")


class UploadedFile(Base):
    """Model for uploaded chat files"""
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=True)  # Chat content
    message_count = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="uploaded_files")
    todos = relationship("TodoItem", back_populates="source_file", cascade="all, delete-orphan")
    calendar_events = relationship("CalendarEvent", back_populates="source_file", cascade="all, delete-orphan")


class PriorityEnum(str, enum.Enum):
    """Priority levels for todos"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TodoItem(Base):
    """Model for todo items"""
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_id = Column(Integer, ForeignKey("uploaded_files.id"), nullable=True)
    task = Column(String(500), nullable=False)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.MEDIUM)
    completed = Column(Boolean, default=False)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="todos")
    source_file = relationship("UploadedFile", back_populates="todos")


class CalendarEvent(Base):
    """Model for calendar events/dates"""
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_id = Column(Integer, ForeignKey("uploaded_files.id"), nullable=True)
    title = Column(String(255), nullable=False)
    event_date = Column(DateTime, nullable=False)
    description = Column(Text, nullable=True)
    is_scheduled = Column(Boolean, default=True)  # False for "TBD" dates
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="calendar_events")
    source_file = relationship("UploadedFile", back_populates="calendar_events")
