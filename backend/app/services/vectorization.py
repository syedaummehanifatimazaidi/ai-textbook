import logging
import tiktoken
from typing import List, Tuple, Optional, Dict, Any
import openai
from app.config import settings

logger = logging.getLogger(__name__)

class VectorizationService:
    """Service for embedding text and interacting with vector database"""
    
    def __init__(self):
        openai.api_key = settings.openai_api_key
        self.embedding_model = settings.openai_embedding_model
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        
    async def embed_text(self, text: str, model: str = "text-embedding-3-small") -> Tuple[List[float], int]:
        """
        Embed text using OpenAI API
        Returns: (embedding_vector, token_count)
        """
        try:
            # Count tokens
            tokens = len(self.encoding.encode(text))
            
            # Call OpenAI embedding API
            response = openai.Embedding.create(
                input=text,
                model=model,
            )
            
            embedding = response["data"][0]["embedding"]
            logger.debug(f"Embedded text: {tokens} tokens")
            
            return embedding, tokens
            
        except Exception as e:
            logger.error(f"Error embedding text: {str(e)}")
            raise
    
    async def embed_batch(self, texts: List[str], model: str = "text-embedding-3-small") -> List[List[float]]:
        """
        Embed multiple texts efficiently (batch up to 100 at a time)
        """
        try:
            embeddings = []
            
            # Process in batches of 100
            for i in range(0, len(texts), 100):
                batch = texts[i:i+100]
                logger.info(f"Embedding batch {i//100 + 1}: {len(batch)} texts")
                
                response = openai.Embedding.create(
                    input=batch,
                    model=model,
                )
                
                # Sort by index to maintain order
                sorted_data = sorted(response["data"], key=lambda x: x["index"])
                embeddings.extend([item["embedding"] for item in sorted_data])
            
            logger.info(f"Completed batch embedding: {len(embeddings)} vectors")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error in batch embedding: {str(e)}")
            raise
    
    async def search_qdrant(
        self,
        embedding: List[float],
        collection_name: str,
        top_k: int = 5,
        threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search Qdrant for similar vectors
        Returns: List of similar chunks with metadata
        """
        try:
            from qdrant_client import QdrantClient
            
            client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
            )
            
            # Search collection
            search_result = client.search(
                collection_name=collection_name,
                query_vector=embedding,
                limit=top_k,
                score_threshold=threshold,
            )
            
            results = []
            for point in search_result:
                result = {
                    "id": str(point.id),
                    "score": point.score,
                    "chunk": point.payload.get("text", ""),
                    "chapter": point.payload.get("chapter", ""),
                    "section": point.payload.get("section"),
                    "language": point.payload.get("language", "en"),
                    "metadata": {k: v for k, v in point.payload.items() 
                                if k not in ["text", "chapter", "section", "language"]},
                }
                results.append(result)
            
            logger.debug(f"Qdrant search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching Qdrant: {str(e)}")
            raise
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    def truncate_text(self, text: str, max_tokens: int) -> str:
        """Truncate text to max tokens"""
        tokens = self.encoding.encode(text)
        if len(tokens) > max_tokens:
            truncated = self.encoding.decode(tokens[:max_tokens])
            return truncated
        return text
