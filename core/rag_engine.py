import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Tuple
import streamlit as st
from config import Config

class OptimizedRAGEngine:
    def __init__(self):
        self.config = Config()
        self.embedding_model = SentenceTransformer(self.config.EMBEDDING_MODEL)
        self.vector_index = None
        self.chunks = []
        self.chunk_metadata = []
        
    def create_embeddings(self, chunks: List[Dict]) -> None:
        """Create embeddings for document chunks with progress tracking"""
        if not chunks:
            return
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Extract text from chunks
        texts = [chunk["text"] for chunk in chunks]
        self.chunks = chunks
        
        # Create embeddings in batches
        all_embeddings = []
        batch_size = self.config.BATCH_SIZE
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            status_text.text(f"Creating embeddings: {i//batch_size + 1}/{(len(texts)//batch_size) + 1}")
            
            batch_embeddings = self.embedding_model.encode(batch, show_progress_bar=False)
            all_embeddings.append(batch_embeddings)
            
            progress_bar.progress(min(1.0, (i + batch_size) / len(texts)))
        
        # Combine all embeddings
        embeddings = np.vstack(all_embeddings)
        
        # Create optimized FAISS index
        self.create_vector_index(embeddings)
        
        status_text.text("Embeddings created successfully!")
    
    def create_vector_index(self, embeddings: np.ndarray) -> None:
        """Create optimized FAISS index based on data size"""
        dimension = embeddings.shape[1]
        
        if len(embeddings) > 1000:
            # Use IVF for large datasets
            nlist = min(100, len(embeddings) // 10)
            quantizer = faiss.IndexFlatL2(dimension)
            self.vector_index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
            
            # Train the index
            self.vector_index.train(embeddings.astype('float32'))
            self.vector_index.nprobe = 10  # Search more clusters
        else:
            # Use flat index for smaller datasets
            self.vector_index = faiss.IndexFlatL2(dimension)
        
        # Add vectors to index
        self.vector_index.add(embeddings.astype('float32'))
    
    def search_similar_chunks(self, query: str, top_k: int = 8) -> List[Dict]:
        """Advanced similarity search with reranking"""
        if not self.vector_index or not self.chunks:
            return []
        
        try:
            # Get query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Search with higher k for reranking
            search_k = min(top_k * 2, len(self.chunks))
            distances, indices = self.vector_index.search(
                query_embedding.astype('float32'), 
                search_k
            )
            
            # Prepare results with metadata
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.chunks):
                    chunk = self.chunks[idx]
                    results.append({
                        "chunk": chunk,
                        "similarity_score": 1 / (1 + distance),  # Convert distance to similarity
                        "rank": i + 1
                    })
            
            # Rerank results
            reranked_results = self.rerank_results(results, query)
            
            return reranked_results[:top_k]
            
        except Exception as e:
            st.error(f"Search error: {str(e)}")
            return []
    
    def rerank_results(self, results: List[Dict], query: str) -> List[Dict]:
        """Rerank results based on multiple factors"""
        query_lower = query.lower()
        
        for result in results:
            chunk_text = result["chunk"]["text"].lower()
            
            # Calculate additional scoring factors
            keyword_score = self.calculate_keyword_score(chunk_text, query_lower)
            section_score = self.calculate_section_score(result["chunk"], query_lower)
            
            # Combine scores
            final_score = (
                result["similarity_score"] * 0.6 +
                keyword_score * 0.3 +
                section_score * 0.1
            )
            
            result["final_score"] = final_score
        
        return sorted(results, key=lambda x: x["final_score"], reverse=True)
    
    def calculate_keyword_score(self, chunk_text: str, query: str) -> float:
        """Calculate keyword overlap score"""
        query_words = set(query.split())
        chunk_words = set(chunk_text.split())
        
        if not query_words:
            return 0.0
        
        overlap = len(query_words.intersection(chunk_words))
        return overlap / len(query_words)
    
    def calculate_section_score(self, chunk: Dict, query: str) -> float:
        """Calculate section relevance score"""
        section_title = chunk.get("section", "").lower()
        
        # Boost score if query matches section title
        if any(word in section_title for word in query.split()):
            return 1.0
        
        return 0.0
