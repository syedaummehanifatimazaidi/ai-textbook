import logging
from typing import Tuple, List, Dict, Any, Optional
import openai
from app.config import settings
from app.services.vectorization import VectorizationService

logger = logging.getLogger(__name__)

class RAGPipeline:
    """RAG (Retrieval-Augmented Generation) pipeline for answering questions"""
    
    def __init__(self):
        openai.api_key = settings.openai_api_key
        self.vector_service = VectorizationService()
        self.llm_model = settings.openai_chat_model
        self.max_context_tokens = 3000
        
    async def process_query(
        self,
        query: str,
        selected_text: Optional[str] = None,
        chapter: Optional[str] = None,
        language: str = "en",
    ) -> Tuple[str, List[Dict[str, Any]], int]:
        """
        Process a query through the RAG pipeline
        
        Returns: (answer, sources, tokens_used)
        """
        try:
            logger.info(f"Processing query: {query[:50]}...")
            
            # Step 1: Embed the query
            query_embedding, _ = await self.vector_service.embed_text(query)
            
            # Step 2: Search for relevant chunks
            collection_name = f"robotics_{language}"
            search_results = await self.vector_service.search_qdrant(
                embedding=query_embedding,
                collection_name=collection_name,
                top_k=10,
                threshold=0.5,
            )
            
            # Step 3: Filter by chapter if selected text provided
            if selected_text and chapter:
                search_results = [r for r in search_results if r.get("chapter") == chapter]
                logger.info(f"Filtered to chapter: {len(search_results)} results")
            
            # Step 4: Build context window
            context_chunks = await self._build_context(search_results)
            context_tokens = self.vector_service.count_tokens(context_chunks)
            
            logger.info(f"Context window: {context_tokens} tokens, {len(search_results)} chunks")
            
            # Step 5: Call LLM
            answer, llm_tokens = await self._call_llm(query, context_chunks, language)
            
            # Step 6: Format sources
            sources = [
                {
                    "chapter": r.get("chapter", ""),
                    "section": r.get("section"),
                    "content_preview": r.get("chunk", "")[:100],
                }
                for r in search_results[:3]  # Top 3 sources
            ]
            
            total_tokens = context_tokens + llm_tokens
            logger.info(f"Query complete: {total_tokens} total tokens used")
            
            return answer, sources, total_tokens
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {str(e)}", exc_info=True)
            raise
    
    async def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Build context window from retrieved chunks
        - Respects max token limit
        - Formats with metadata
        """
        if not chunks:
            return "No relevant information found."
        
        context_parts = []
        current_tokens = 0
        
        for chunk in chunks:
            chunk_text = chunk.get("chunk", "")
            chunk_tokens = self.vector_service.count_tokens(chunk_text)
            
            # Check if adding this chunk would exceed limit
            if current_tokens + chunk_tokens > self.max_context_tokens:
                logger.debug(f"Context limit reached: {current_tokens} tokens")
                break
            
            # Format chunk with metadata
            chapter = chunk.get("chapter", "Unknown")
            section = chunk.get("section", "")
            score = chunk.get("score", 0.0)
            
            formatted = f"[{chapter}{f'/' + section if section else ''}]\n{chunk_text}"
            context_parts.append(formatted)
            current_tokens += chunk_tokens
        
        context = "\n\n---\n\n".join(context_parts)
        logger.debug(f"Built context: {len(context_parts)} chunks, {current_tokens} tokens")
        
        return context
    
    async def _call_llm(
        self,
        query: str,
        context: str,
        language: str = "en",
    ) -> Tuple[str, int]:
        """
        Call OpenAI LLM with context
        Returns: (answer, tokens_used)
        """
        try:
            # System prompt in user's language
            if language == "ur":
                system_prompt = """آپ ایک روبوٹکس اور AI متخصص ہو۔ دیے گئے سیاق میں سے صرف معلومات استعمال کرتے ہوئے سوالات کے جوابات دیں۔
اگر جواب سیاق میں موجود نہیں ہے تو یہ کہیں کہ آپ نہیں جانتے۔ اردو میں جواب دیں۔"""
            else:
                system_prompt = """You are an expert in robotics and AI. Answer questions using ONLY the provided context.
If the answer is not in the context, say you don't know. Be concise and clear."""
            
            # Build messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
            ]
            
            # Call OpenAI
            response = openai.ChatCompletion.create(
                model=self.llm_model,
                messages=messages,
                temperature=0.3,  # Lower temperature for factual answers
                max_tokens=500,
            )
            
            answer = response.choices[0].message.content
            tokens_used = response.usage.completion_tokens
            
            logger.debug(f"LLM response: {tokens_used} tokens")
            return answer, tokens_used
            
        except Exception as e:
            logger.error(f"Error calling LLM: {str(e)}")
            # Fallback response
            fallback = "I encountered an error processing your question. Please try again."
            return fallback, 50
    
    async def answer_from_selected_only(
        self,
        query: str,
        selected_text: str,
        chapter: str,
    ) -> str:
        """
        Answer question using ONLY the selected text
        (strict context filtering)
        """
        try:
            # Use selected text directly as context
            answer, _ = await self._call_llm(
                query=query,
                context=f"Selected text:\n{selected_text}",
            )
            return answer
            
        except Exception as e:
            logger.error(f"Error in selected-text answer: {str(e)}")
            raise
