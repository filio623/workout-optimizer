"""
SQLAlchemy models for the Workout Optimizer database.
These define the structure of our database tables.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, UUID, Numeric, func, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
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

class NutritionDaily(Base):
    """Daily Nutrition Data from MyNetDiary"""
    __tablename__ = 'nutrition_daily'

    __table_args__ = (UniqueConstraint('user_id', 'log_date', name='uix_user_logdate'),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    #Date (just the date)
    log_date = Column(Date, nullable=False)

    #Macros and calories
    calories = Column(Numeric)
    protein_g = Column(Numeric)
    carbs_g = Column(Numeric)
    fats_g = Column(Numeric)
    fiber_g = Column(Numeric)

    # Raw data dump from MyNetDiary (all columns as JSON)
    raw_data = Column(JSONB)
 
    #Source tracking
    source = Column(String(100), default='mynetdiary')  # e.g., 'MyNetDiary'

    #timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User")

class HealthMetricsRaw(Base):
    """Raw Health Metrics from Apple Health (and other sources)"""
    __tablename__ = 'health_metrics_raw'

    __table_args__ = (UniqueConstraint('user_id', 'source', 'metric_date', 'metric_type', name='uix_user_metric_datetime_type'),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    metric_date = Column(DateTime, nullable=False)
    metric_type = Column(String(100), nullable=False)  # e.g., 'weight', 'body_fat_percentage'
    value = Column(Numeric, nullable=False)
    unit = Column(String(50))  # e.g., 'kg', '%'
    source = Column(String(50))  # e.g., 'apple_health'

    source_metadata = Column(JSONB, default={})  # Additional metadata if needed

    user = relationship("User")

class HealthMetricsDaily(Base):
    """Aggregated Daily Health Metrics"""
    __tablename__ = 'health_metrics_daily'

    __table_args__ = (UniqueConstraint('user_id', 'metric_date', name='uix_user_metric_date'),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    metric_date = Column(Date, nullable=False)

    # Common health metrics (pre-aggregated)
    steps = Column(Integer)
    weight_lbs = Column(Numeric)  # Changed from weight_kg to match Apple Health export
    active_calories = Column(Integer)
    resting_heart_rate = Column(Numeric)
    distance_miles = Column(Numeric)  # Changed from distance_meters to match Apple Health

    # Activity time metrics
    workout_minutes = Column(Integer)  # Total workout time (all workouts including walks, bike rides)
    exercise_minutes = Column(Integer)  # Apple Exercise Time (moderate+ intensity)
    stand_minutes = Column(Integer)  # Apple Stand Time

    #flexible storage for additional metrics we may add later
    additional_metrics = Column(JSONB, default={})

    #timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User")

class WorkoutCache(Base):
    """Cached Workout Data from Hevy"""
    __tablename__ = 'workout_cache'

    __table_args__ = (UniqueConstraint('user_id', 'source', 'source_workout_id', name='uix_user_source_workout'),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    # External Source Info
    source = Column(String(100), nullable=False)  # e.g., 'hevy'
    source_workout_id = Column(String(100), nullable=False)  # ID from Hevy

    # Workout Basic info
    workout_date = Column(DateTime, nullable=False)
    title = Column(String(200))
    duration_minutes = Column(Integer)
    total_sets = Column(Integer)
    total_volume_kg = Column(Numeric)  # Volume for weighted exercises only
    bodyweight_reps = Column(Integer)  # Total reps for bodyweight exercises
    exercise_count = Column(Integer)
    calories_burned = Column(Integer)
    muscle_groups = Column(JSONB)  # List of muscle groups worked

    #Full workout data as JSONB
    workout_data = Column(JSONB, nullable=False)
    last_synced = Column(DateTime, server_default=func.now())

    #timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User")


   