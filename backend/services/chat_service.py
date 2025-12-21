from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, desc
from backend.db.models import ChatSession, ChatMessage
from typing import List, Optional
import uuid

async def get_or_create_session(db: AsyncSession, user_id: str, session_id: Optional[str] = None) -> ChatSession:
    """
    Get an existing chat session or create a new one.
    If session_id is provided but not found, creates a new one.
    """
    if session_id:
        try:
            # Validate UUID format
            uuid_obj = uuid.UUID(session_id)
            query = select(ChatSession).where(
                ChatSession.id == uuid_obj,
                ChatSession.user_id == uuid.UUID(user_id)
            )
            result = await db.execute(query)
            session = result.scalar_one_or_none()
            if session:
                return session
        except ValueError:
            # Invalid UUID format, treat as new session
            pass
    
    # Create new session
    new_session = ChatSession(
        user_id=uuid.UUID(user_id),
        session_name="New Conversation"
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return new_session

async def save_message(db: AsyncSession, session_id: uuid.UUID, role: str, content: str) -> ChatMessage:
    """
    Save a new message to the database.
    """
    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message

async def get_user_sessions(db: AsyncSession, user_id: str) -> List[ChatSession]:
    """
    Get all chat sessions for a user, ordered by last activity.
    """
    query = select(ChatSession).where(
        ChatSession.user_id == uuid.UUID(user_id)
    ).order_by(desc(ChatSession.last_activity))
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_session_messages(db: AsyncSession, session_id: str, user_id: str) -> List[ChatMessage]:
    """
    Get all messages for a specific session.
    """
    try:
        session_uuid = uuid.UUID(session_id)
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return []

    # Verify session belongs to user
    session_query = select(ChatSession).where(
        ChatSession.id == session_uuid,
        ChatSession.user_id == user_uuid
    )
    session_result = await db.execute(session_query)
    if not session_result.scalar_one_or_none():
        return []

    # Get messages
    query = select(ChatMessage).where(
        ChatMessage.session_id == session_uuid
    ).order_by(ChatMessage.timestamp)
    
    result = await db.execute(query)
    return result.scalars().all()

async def update_session_title(db: AsyncSession, session_id: uuid.UUID, title: str):
    """
    Update the title of a chat session.
    """
    query = select(ChatSession).where(ChatSession.id == session_id)
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if session:
        session.session_name = title
        await db.commit()

async def delete_session(db: AsyncSession, session_id: str, user_id: str) -> bool:
    """
    Delete a chat session and all its messages.
    """
    try:
        session_uuid = uuid.UUID(session_id)
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return False

    # Check ownership
    query = select(ChatSession).where(
        ChatSession.id == session_uuid,
        ChatSession.user_id == user_uuid
    )
    result = await db.execute(query)
    if not result.scalar_one_or_none():
        return False

    # Delete (cascade should handle messages, but explicit is safe)
    stmt = delete(ChatSession).where(ChatSession.id == session_uuid)
    await db.execute(stmt)
    await db.commit()
    return True
