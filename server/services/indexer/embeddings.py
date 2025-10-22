import numpy as np
from typing import List, Dict, Any, Optional
import asyncio
from sentence_transformers import SentenceTransformer
import hashlib

class EmbeddingService:
    def __init__(self):
        self.model_name = "all-MiniLM-L6-v2"  # Lightweight model
        self.model = None
        self.embedding_cache = {}

    async def initialize(self):
        """Initialize the embedding model."""
        try:
            self.model = SentenceTransformer(self.model_name)
            print(f"Embedding model {self.model_name} loaded successfully")
        except Exception as e:
            print(f"Failed to load embedding model: {e}")
            # Fallback to a simple hash-based embedding
            self.model = None

    async def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for text."""
        try:
            if self.model:
                # Use sentence transformers
                embeddings = self.model.encode(text)
                return embeddings.tolist()
            else:
                # Fallback to hash-based embedding
                return self.generate_hash_embedding(text)
        except Exception as e:
            print(f"Embedding generation failed: {e}")
            return self.generate_hash_embedding(text)

    def generate_hash_embedding(self, text: str, dimensions: int = 384) -> List[float]:
        """Generate a simple hash-based embedding as fallback."""
        # Create a hash of the text
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to numbers
        hash_int = int(text_hash, 16)
        
        # Generate embedding vector
        embedding = []
        for i in range(dimensions):
            # Use different parts of the hash for each dimension
            val = (hash_int >> (i % 32)) & 0xFFFF
            # Normalize to [-1, 1]
            normalized = (val / 0xFFFF) * 2 - 1
            embedding.append(normalized)
        
        return embedding

    async def generate_code_embeddings(self, code: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate embeddings for code with metadata."""
        try:
            # Combine code and metadata for embedding
            combined_text = code
            if metadata:
                combined_text += f" {metadata.get('language', '')} {metadata.get('function_name', '')}"
            
            embedding = await self.generate_embeddings(combined_text)
            
            return {
                "embedding": embedding,
                "metadata": metadata or {},
                "text_hash": hashlib.md5(code.encode()).hexdigest()
            }
        except Exception as e:
            print(f"Code embedding generation failed: {e}")
            return {
                "embedding": self.generate_hash_embedding(code),
                "metadata": metadata or {},
                "text_hash": hashlib.md5(code.encode()).hexdigest()
            }

    async def find_similar_code(self, query_embedding: List[float], code_embeddings: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """Find similar code based on embeddings."""
        try:
            similarities = []
            
            for code_data in code_embeddings:
                similarity = self.calculate_cosine_similarity(query_embedding, code_data["embedding"])
                similarities.append({
                    "similarity": similarity,
                    "code": code_data.get("code", ""),
                    "metadata": code_data.get("metadata", {})
                })
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            print(f"Similarity search failed: {e}")
            return []

    def calculate_cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            print(f"Similarity calculation failed: {e}")
            return 0.0

    async def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts efficiently."""
        try:
            if self.model:
                # Use batch processing
                embeddings = self.model.encode(texts)
                return embeddings.tolist()
            else:
                # Fallback to individual processing
                return [self.generate_hash_embedding(text) for text in texts]
        except Exception as e:
            print(f"Batch embedding generation failed: {e}")
            return [self.generate_hash_embedding(text) for text in texts]

    def get_embedding_dimensions(self) -> int:
        """Get the dimension size of embeddings."""
        if self.model:
            return self.model.get_sentence_embedding_dimension()
        else:
            return 384  # Default for hash-based embeddings