#!/usr/bin/env python3
"""
Vectorization script: Extract content from markdown, chunk, embed, and upload to Qdrant
Usage: python vectorize_content.py --source docs/en --upload --language en
"""

import os
import sys
import argparse
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any
import logging

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import tiktoken
import openai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load settings
from app.config import settings

class ContentVectorizer:
    """Extract, chunk, embed, and upload educational content"""
    
    def __init__(self):
        openai.api_key = settings.openai_api_key
        self.qdrant_client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.chunk_size = 512
        self.overlap = 128
        
    def extract_markdown(self, file_path: str) -> tuple[str, str, str]:
        """Extract chapter from markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract chapter and section from frontmatter or filename
        chapter_id = Path(file_path).stem
        chapter_name = chapter_id.replace('-', ' ').title()
        
        return content, chapter_id, chapter_name
    
    def chunk_content(self, content: str, chapter_id: str) -> List[Dict[str, Any]]:
        """Split content into overlapping chunks"""
        chunks = []
        tokens = self.encoding.encode(content)
        
        chunk_idx = 0
        for i in range(0, len(tokens), self.chunk_size - self.overlap):
            chunk_tokens = tokens[i:i + self.chunk_size]
            if len(chunk_tokens) < 50:  # Skip very small chunks
                continue
            
            chunk_text = self.encoding.decode(chunk_tokens)
            
            chunks.append({
                "id": f"{chapter_id}_{chunk_idx}",
                "text": chunk_text,
                "chapter": chapter_id,
                "chunk_order": chunk_idx,
                "tokens": len(chunk_tokens),
            })
            
            chunk_idx += 1
        
        logger.info(f"Created {len(chunks)} chunks from {chapter_id}")
        return chunks
    
    def embed_chunks(self, chunks: List[Dict[str, Any]], language: str = "en") -> List[Dict[str, Any]]:
        """Embed all chunks using OpenAI API (batch)"""
        logger.info(f"Embedding {len(chunks)} chunks...")
        
        texts = [chunk["text"] for chunk in chunks]
        embeddings = []
        
        # Process in batches of 100
        for i in range(0, len(texts), 100):
            batch = texts[i:i+100]
            logger.info(f"  Batch {i//100 + 1}: {len(batch)} texts")
            
            try:
                response = openai.Embedding.create(
                    input=batch,
                    model="text-embedding-3-small",
                )
                
                batch_embeddings = sorted(response["data"], key=lambda x: x["index"])
                embeddings.extend([item["embedding"] for item in batch_embeddings])
                
            except Exception as e:
                logger.error(f"Embedding error: {str(e)}")
                raise
        
        # Attach embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding
            chunk["language"] = language
        
        logger.info(f"Embedded {len(embeddings)} vectors")
        return chunks
    
    def upload_to_qdrant(self, chunks: List[Dict[str, Any]], collection_name: str):
        """Upload chunks to Qdrant vector database"""
        logger.info(f"Uploading to Qdrant collection: {collection_name}")
        
        # Create collection if not exists
        try:
            self.qdrant_client.get_collection(collection_name)
            logger.info(f"Collection {collection_name} exists")
        except:
            logger.info(f"Creating collection {collection_name}")
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )
        
        # Create points
        points = []
        for idx, chunk in enumerate(chunks):
            point_id = hashlib.md5(chunk["text"].encode()).hexdigest()
            
            points.append(PointStruct(
                id=idx,  # Use sequential ID
                vector=chunk["embedding"],
                payload={
                    "text": chunk["text"],
                    "chapter": chunk["chapter"],
                    "chunk_order": chunk["chunk_order"],
                    "tokens": chunk["tokens"],
                    "language": chunk.get("language", "en"),
                    "content_hash": point_id,
                },
            ))
        
        # Upload in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]
            self.qdrant_client.upsert(
                collection_name=collection_name,
                points=batch,
            )
            logger.info(f"  Uploaded {len(batch)} points")
        
        logger.info(f"Uploaded {len(points)} points total")
    
    def process_directory(
        self,
        source_dir: str,
        language: str = "en",
        upload: bool = True,
    ):
        """Process all markdown files in directory"""
        source_path = Path(source_dir)
        md_files = list(source_path.glob("*.md"))
        
        logger.info(f"Found {len(md_files)} markdown files")
        
        all_chunks = []
        
        for md_file in sorted(md_files):
            logger.info(f"Processing: {md_file.name}")
            
            try:
                content, chapter_id, chapter_name = self.extract_markdown(str(md_file))
                chunks = self.chunk_content(content, chapter_id)
                all_chunks.extend(chunks)
                
            except Exception as e:
                logger.error(f"Error processing {md_file}: {str(e)}")
                continue
        
        # Embed all chunks
        embedded_chunks = self.embed_chunks(all_chunks, language)
        
        # Upload to Qdrant
        if upload:
            collection_name = f"robotics_{language}"
            self.upload_to_qdrant(embedded_chunks, collection_name)
        else:
            # Save to file
            with open(f"vectors_{language}.jsonl", "w") as f:
                for chunk in embedded_chunks:
                    f.write(json.dumps(chunk) + "\n")
            logger.info(f"Saved vectors to vectors_{language}.jsonl")

def main():
    parser = argparse.ArgumentParser(description="Vectorize textbook content")
    parser.add_argument("--source", required=True, help="Source directory with markdown files")
    parser.add_argument("--language", default="en", choices=["en", "ur"], help="Language")
    parser.add_argument("--upload", action="store_true", help="Upload to Qdrant")
    parser.add_argument("--chunk-size", type=int, default=512, help="Chunk size in tokens")
    parser.add_argument("--overlap", type=int, default=128, help="Chunk overlap in tokens")
    
    args = parser.parse_args()
    
    vectorizer = ContentVectorizer()
    vectorizer.chunk_size = args.chunk_size
    vectorizer.overlap = args.overlap
    
    vectorizer.process_directory(
        source_dir=args.source,
        language=args.language,
        upload=args.upload,
    )
    
    logger.info("Vectorization complete!")

if __name__ == "__main__":
    main()
