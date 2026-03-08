from fastapi import APIRouter, HTTPException
import logging

from app.models import VectorSearchRequest, VectorSearchResponse, SearchResult
from app.services.vectorization import VectorizationService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize vectorization service
vector_service = VectorizationService()

@router.post("/vector-search", response_model=VectorSearchResponse)
async def vector_search(request: VectorSearchRequest):
    """
    Vector search endpoint: find similar chunks in knowledge base
    
    - **query**: Search query
    - **language**: "en" or "ur"
    - **top_k**: Number of results to return (1-100)
    - **threshold**: Minimum similarity score (0.0-1.0)
    """
    try:
        logger.info(f"Vector search: {request.query[:50]}... (lang: {request.language})")
        
        # Embed the query
        query_embedding, embedding_tokens = await vector_service.embed_text(
            request.query,
            model="text-embedding-3-small"
        )
        
        # Search Qdrant
        results = await vector_service.search_qdrant(
            embedding=query_embedding,
            collection_name=f"robotics_{request.language}",
            top_k=request.top_k,
            threshold=request.threshold,
        )
        
        # Format results
        formatted_results = [
            SearchResult(
                id=result.get("id", ""),
                score=result.get("score", 0.0),
                chunk=result.get("chunk", ""),
                chapter=result.get("chapter", ""),
                section=result.get("section"),
                metadata=result.get("metadata", {}),
            )
            for result in results
        ]
        
        return VectorSearchResponse(
            results=formatted_results,
            query_embedding_tokens=embedding_tokens,
        )
        
    except Exception as e:
        logger.error(f"Error in vector search: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error performing vector search: {str(e)}"
        )

@router.post("/vector-search/semantic")
async def semantic_search(query: str, language: str = "en", top_k: int = 5):
    """
    Semantic search with more intelligent filtering
    """
    try:
        logger.info(f"Semantic search: {query[:50]}...")
        
        # This could include advanced filtering, reranking, etc.
        # For now, delegates to standard vector search
        request = VectorSearchRequest(
            query=query,
            language=language,
            top_k=top_k,
            threshold=0.5,
        )
        return await vector_search(request)
        
    except Exception as e:
        logger.error(f"Error in semantic search: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error performing semantic search"
        )
