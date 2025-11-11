"""
SQLAlchemy models for the Workout Optimizer database.
These define the structure of our database tables.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UUID, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid


Base = declarative_base()


class User(Base):
    """User Accounts"""
    __tablename__ = 'users'

    #UUID primary key (instead of integer)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User info
    name = Column(String(100), nullable=False)
    email = Column(String(250), unique=True)

    #timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")

class ChatSession(Base):
    """Chat Conversation Sessions"""
    __tablename__ = 'chat_sessions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    #session info
    session_name = Column(String(200))
    created_at = Column(DateTime, server_default=func.now())
    last_activity = Column(DateTime, server_default=func.now(), onupdate=func.now())

    #relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    """Individual Chat Messages"""
    __tablename__ = 'chat_messages'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('chat_sessions.id'), nullable=False)

    #message content
    role = Column(String(50), nullable=False)  # e.g., 'user', 'assistant'
    content = Column(Text, nullable=False)

    #metadata
    timestamp = Column(DateTime, server_default=func.now())
    token_count = Column(Integer)# Optional track tokens used

    session = relationship("ChatSession", back_populates="messages")