from fastapi import APIRouter, HTTPException, Query
import logging
import uuid
from typing import Optional

from app.models import ChatRequest, ChatResponse, Source
from app.services.rag import RAGPipeline

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize RAG pipeline once
rag_pipeline = RAGPipeline()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint: process user query with RAG pipeline
    
    - **query**: User's question
    - **selected_text**: Optional highlighted text
    - **chapter**: Optional chapter ID for filtering
    - **language**: "en" for English or "ur" for Urdu
    """
    try:
        logger.info(f"Chat request: {request.query[:50]}... (lang: {request.language})")
        
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Call RAG pipeline
        answer, sources, tokens_used = await rag_pipeline.process_query(
            query=request.query,
            selected_text=request.selected_text,
            chapter=request.chapter,
            language=request.language,
        )
        
        # Format sources
        formatted_sources = [
            Source(
                chapter=source.get("chapter", ""),
                section=source.get("section"),
                content_preview=source.get("content_preview"),
            )
            for source in sources
        ]
        
        logger.info(f"Response generated: {tokens_used} tokens used")
        
        return ChatResponse(
            answer=answer,
            sources=formatted_sources,
            tokens_used=tokens_used,
            conversation_id=conversation_id,
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat: {str(e)}"
        )

@router.get("/chat/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = Query(20, ge=1, le=100)):
    """Get chat history for a user"""
    try:
        # TODO: Implement chat history retrieval from database
        return {"messages": []}
    except Exception as e:
        logger.error(f"Error fetching chat history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error fetching chat history"
        )

@router.post("/chat/rate")
async def rate_response(
    conversation_id: str,
    rating: int = Query(..., ge=1, le=5),
    feedback: Optional[str] = None
):
    """Rate an AI response for quality feedback"""
    try:
        logger.info(f"Rating: {rating}/5 for conversation {conversation_id}")
        # TODO: Store rating in database for quality improvement
        return {"status": "rated", "conversation_id": conversation_id}
    except Exception as e:
        logger.error(f"Error rating response: {str(e)}")
        raise HTTPException(status_code=500, detail="Error saving rating")
