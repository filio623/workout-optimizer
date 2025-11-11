"""
Session management for the LLM interface.
"""

import logging
import sqlite3
import asyncio
from datetime import datetime, timedelta
from typing import List
from agents import SQLiteSession
from backend.llm.config import DEFAULT_DB_PATH

logger = logging.getLogger(__name__)

# Basic session operations
def get_or_create_session(session_id: str, db_path: str = DEFAULT_DB_PATH) -> SQLiteSession:
    """Get or create a session for a user."""
    return SQLiteSession(session_id, db_path)

async def clear_session(session_id: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """Clear a specific session's conversation history."""
    try:
        session = get_or_create_session(session_id, db_path)
        await session.clear_session()
        session.close()
        logger.info(f"Cleared session: {session_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to clear session {session_id}: {str(e)}")
        return False

# Session cleanup operations
class SessionCleanup:
    """Manages session cleanup for SQLiteSession."""
    
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.sessions_table = "agent_sessions"
        self.messages_table = "agent_messages"
    
    async def get_old_sessions(self, days_old: int = 5) -> List[str]:
        """Get session IDs that are older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cutoff_timestamp_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')
        
        def _get_old_sessions_sync():
            conn = sqlite3.connect(self.db_path)
            try:
                # Use the actual SDK database schema with string timestamp comparison
                cursor = conn.execute(
                    """
                    SELECT session_id FROM agent_sessions 
                    WHERE created_at < ?
                    """,
                    (cutoff_timestamp_str,)
                )
                
                return [row[0] for row in cursor.fetchall()]
            finally:
                conn.close()
        
        # Run in thread to avoid blocking
        return await asyncio.to_thread(_get_old_sessions_sync)
    
    async def cleanup_old_sessions(self, days_old: int = 5) -> int:
        """Clean up sessions older than specified days. Returns number of sessions cleaned."""
        old_session_ids = await self.get_old_sessions(days_old)
        
        if not old_session_ids:
            logger.info(f"No sessions older than {days_old} days found")
            return 0
        
        logger.info(f"Found {len(old_session_ids)} sessions older than {days_old} days")
        
        cleaned_count = 0
        for session_id in old_session_ids:
            try:
                # Use the existing clear_session function
                success = await clear_session(session_id, self.db_path)
                if success:
                    cleaned_count += 1
            except Exception as e:
                logger.error(f"Failed to clean session {session_id}: {str(e)}")
        
        logger.info(f"Successfully cleaned {cleaned_count} out of {len(old_session_ids)} old sessions")
        return cleaned_count
    
    async def cleanup_sessions_by_activity(self, days_inactive: int = 5) -> int:
        """Clean up sessions that haven't had activity in specified days."""
        cutoff_date = datetime.now() - timedelta(days=days_inactive)
        cutoff_timestamp_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')
        
        def _get_inactive_sessions_sync():
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute(
                    """
                    SELECT session_id, MAX(created_at) as last_activity
                    FROM agent_messages 
                    GROUP BY session_id 
                    HAVING last_activity < ?
                    """,
                    (cutoff_timestamp_str,)
                )
                return [row[0] for row in cursor.fetchall()]
            finally:
                conn.close()
        
        inactive_session_ids = await asyncio.to_thread(_get_inactive_sessions_sync)
        
        if not inactive_session_ids:
            logger.info(f"No sessions inactive for {days_inactive} days found")
            return 0
        
        logger.info(f"Found {len(inactive_session_ids)} sessions inactive for {days_inactive} days")
        
        cleaned_count = 0
        for session_id in inactive_session_ids:
            try:
                # Use the existing clear_session function
                success = await clear_session(session_id, self.db_path)
                if success:
                    cleaned_count += 1
            except Exception as e:
                logger.error(f"Failed to clean inactive session {session_id}: {str(e)}")
        
        logger.info(f"Successfully cleaned {cleaned_count} out of {len(inactive_session_ids)} inactive sessions")
        return cleaned_count

# Convenience functions for simple cleanup
async def cleanup_old_sessions(days_old: int = 5, db_path: str = DEFAULT_DB_PATH) -> int:
    """Simple function to clean up old sessions."""
    cleanup = SessionCleanup(db_path)
    return await cleanup.cleanup_old_sessions(days_old)

async def cleanup_inactive_sessions(days_inactive: int = 5, db_path: str = DEFAULT_DB_PATH) -> int:
    """Simple function to clean up inactive sessions."""
    cleanup = SessionCleanup(db_path)
    return await cleanup.cleanup_sessions_by_activity(days_inactive)

# Background cleanup scheduling
async def schedule_cleanup():
    """Background task to schedule cleanup in your FastAPI app."""
    while True:
        try:
            # Clean up sessions older than 5 days
            cleaned_count = await cleanup_old_sessions(days_old=5)
            logger.info(f"Scheduled cleanup: cleaned {cleaned_count} old sessions")
            
            # Wait 24 hours before next cleanup
            await asyncio.sleep(24 * 60 * 60)  # 24 hours
            
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")
            await asyncio.sleep(60)  # Wait 1 minute on error 