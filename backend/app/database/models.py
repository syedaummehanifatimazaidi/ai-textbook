from sqlalchemy import create_engine, Column, String, Integer, DateTime, JSON, ForeignKey, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password_hash = Column(String, nullable=True)
    oauth_provider = Column(String, nullable=True)  # github, google, etc.
    oauth_id = Column(String, nullable=True)
    language_preference = Column(String, default="en")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    personalization_data = relationship("PersonalizationData", back_populates="user", cascade="all, delete-orphan")
    quiz_submissions = relationship("QuizSubmission", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"

class Session(Base):
    __tablename__ = "session"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), index=True)
    token = Column(String, unique=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="sessions")
    
    def is_valid(self):
        return datetime.utcnow() < self.expires_at

class PersonalizationData(Base):
    __tablename__ = "personalization_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), index=True)
    chapter_id = Column(String, index=True)
    progress_percent = Column(Integer, default=0)
    bookmarks = Column(JSON, default=list)
    quiz_scores = Column(JSON, default=dict)
    notes = Column(Text, nullable=True)
    language_preference = Column(String, default="en")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="personalization_data")
    
    def __repr__(self):
        return f"<PersonalizationData user={self.user_id} chapter={self.chapter_id}>"

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), index=True)
    conversation_id = Column(String, index=True)
    query = Column(Text)
    answer = Column(Text)
    sources = Column(JSON, default=list)
    tokens_used = Column(Integer)
    rating = Column(Integer, nullable=True)  # 1-5 star rating
    feedback = Column(Text, nullable=True)
    language = Column(String, default="en")
    created_at = Column(DateTime, default=datetime.utcnow)

class QuizSubmission(Base):
    __tablename__ = "quiz_submission"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), index=True)
    chapter_id = Column(String, index=True)
    answers = Column(JSON)  # {question_id: answer}
    score = Column(Float)  # 0.0 - 1.0
    total_questions = Column(Integer)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="quiz_submissions")

class EmbeddingMetadata(Base):
    __tablename__ = "embedding_metadata"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = Column(String, index=True)
    section_id = Column(String, nullable=True)
    chunk_order = Column(Integer)
    content_hash = Column(String, unique=True)
    language = Column(String, default="en")
    tokens = Column(Integer)
    embedding_model = Column(String)
    embedded_at = Column(DateTime, default=datetime.utcnow)
    qdrant_id = Column(String, unique=True, nullable=True)  # Reference to Qdrant point ID
