from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="User query")
    selected_text: Optional[str] = Field(None, description="Highlighted text from content")
    chapter: Optional[str] = Field(None, description="Chapter ID for context filtering")
    language: str = Field("en", pattern="^(en|ur)$", description="Language: en or ur")
    conversation_id: Optional[str] = None

class Source(BaseModel):
    chapter: str
    section: Optional[str] = None
    content_preview: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source] = []
    tokens_used: int = 0
    confidence: float = Field(0.5, ge=0.0, le=1.0)
    conversation_id: str

class VectorSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    language: str = Field("en", pattern="^(en|ur)$")
    top_k: int = Field(5, ge=1, le=100)
    threshold: Optional[float] = Field(None, ge=0.0, le=1.0)

class SearchResult(BaseModel):
    id: str
    score: float
    chunk: str
    chapter: str
    section: Optional[str] = None
    metadata: Dict[str, Any] = {}

class VectorSearchResponse(BaseModel):
    results: List[SearchResult]
    query_embedding_tokens: int

class PersonalizationData(BaseModel):
    user_id: str
    chapter_id: str
    progress_percent: int = Field(0, ge=0, le=100)
    bookmarks: List[str] = []
    quiz_scores: Dict[str, float] = {}
    language_preference: str = "en"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PersonalizationUpdate(BaseModel):
    progress_percent: Optional[int] = None
    bookmarks: Optional[List[str]] = None
    quiz_scores: Optional[Dict[str, float]] = None
    language_preference: Optional[str] = None

class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    language: str = "en"
    created_at: datetime

class SessionData(BaseModel):
    user_id: Optional[str] = None
    session_token: Optional[str] = None
    language: str = "en"
    authenticated: bool = False

class QuizSubmission(BaseModel):
    chapter_id: str
    answers: Dict[str, str]

class QuizResult(BaseModel):
    score: float
    total_questions: int
    feedback: Optional[str] = None
    correct_answers: Dict[str, bool] = {}

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
