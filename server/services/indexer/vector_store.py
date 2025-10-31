import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

class VectorStore:
    def __init__(self):
        self.store_file = "data/vector_store.json"
        self.embeddings = []
        self.metadata = []
        self.embedding_service = None

    async def initialize(self):
        """Initialize the vector store."""
        try:
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(self.store_file), exist_ok=True)
            
            # Load existing data
            await self.load_store()
            
            # Initialize embedding service
            from .embeddings import EmbeddingService
            self.embedding_service = EmbeddingService()
            await self.embedding_service.initialize()
            
            print("Vector store initialized successfully")
        except Exception as e:
            print(f"Vector store initialization failed: {e}")

    async def add_code(self, code: str, metadata: Dict[str, Any] = None) -> str:
        """Add code to the vector store."""
        try:
            # Generate embedding
            embedding_data = await self.embedding_service.generate_code_embeddings(code, metadata)
            embedding = embedding_data["embedding"]
            
            # Create unique ID
            code_id = self.generate_code_id(code, metadata)
            
            # Store embedding and metadata
            self.embeddings.append(embedding)
            self.metadata.append({
                "id": code_id,
                "code": code,
                "metadata": metadata or {},
                "created_at": datetime.now().isoformat(),
                "text_hash": embedding_data["text_hash"]
            })
            
            # Save to file
            await self.save_store()
            
            return code_id
            
        except Exception as e:
            print(f"Failed to add code to vector store: {e}")
            return None

    async def search_similar(self, query: str, top_k: int = 5, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search for similar code."""
        try:
            # Generate query embedding
            query_embedding = await self.embedding_service.generate_embeddings(query)
            
            # Calculate similarities
            similarities = []
            for i, embedding in enumerate(self.embeddings):
                similarity = self.embedding_service.calculate_cosine_similarity(query_embedding, embedding)
                
                # Apply filters if provided
                if filters:
                    metadata = self.metadata[i]
                    if not self.matches_filters(metadata, filters):
                        continue
                
                similarities.append({
                    "similarity": similarity,
                    "code": self.metadata[i]["code"],
                    "metadata": self.metadata[i]["metadata"],
                    "id": self.metadata[i]["id"]
                })
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            print(f"Similarity search failed: {e}")
            return []

    async def get_code_by_id(self, code_id: str) -> Optional[Dict[str, Any]]:
        """Get code by ID."""
        for metadata in self.metadata:
            if metadata["id"] == code_id:
                return metadata
        return None

    async def update_code(self, code_id: str, code: str, metadata: Dict[str, Any] = None) -> bool:
        """Update existing code."""
        try:
            for i, meta in enumerate(self.metadata):
                if meta["id"] == code_id:
                    # Generate new embedding
                    embedding_data = await self.embedding_service.generate_code_embeddings(code, metadata)
                    embedding = embedding_data["embedding"]
                    
                    # Update data
                    self.embeddings[i] = embedding
                    self.metadata[i].update({
                        "code": code,
                        "metadata": metadata or meta["metadata"],
                        "updated_at": datetime.now().isoformat(),
                        "text_hash": embedding_data["text_hash"]
                    })
                    
                    # Save to file
                    await self.save_store()
                    return True
            
            return False
            
        except Exception as e:
            print(f"Failed to update code: {e}")
            return False

    async def delete_code(self, code_id: str) -> bool:
        """Delete code from the store."""
        try:
            for i, metadata in enumerate(self.metadata):
                if metadata["id"] == code_id:
                    # Remove from both lists
                    del self.embeddings[i]
                    del self.metadata[i]
                    
                    # Save to file
                    await self.save_store()
                    return True
            
            return False
            
        except Exception as e:
            print(f"Failed to delete code: {e}")
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        return {
            "total_codes": len(self.metadata),
            "embedding_dimensions": self.embedding_service.get_embedding_dimensions() if self.embedding_service else 0,
            "store_size_mb": os.path.getsize(self.store_file) / (1024 * 1024) if os.path.exists(self.store_file) else 0
        }

    async def load_store(self):
        """Load vector store from file."""
        try:
            if os.path.exists(self.store_file):
                with open(self.store_file, 'r') as f:
                    data = json.load(f)
                    self.embeddings = data.get("embeddings", [])
                    self.metadata = data.get("metadata", [])
            else:
                self.embeddings = []
                self.metadata = []
        except Exception as e:
            print(f"Failed to load vector store: {e}")
            self.embeddings = []
            self.metadata = []

    async def save_store(self):
        """Save vector store to file."""
        try:
            data = {
                "embeddings": self.embeddings,
                "metadata": self.metadata,
                "updated_at": datetime.now().isoformat()
            }
            
            with open(self.store_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save vector store: {e}")

    def generate_code_id(self, code: str, metadata: Dict[str, Any] = None) -> str:
        """Generate a unique ID for code."""
        import hashlib
        
        # Create a hash based on code and metadata
        content = code
        if metadata:
            content += json.dumps(metadata, sort_keys=True)
        
        return hashlib.md5(content.encode()).hexdigest()

    def matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if metadata matches the provided filters."""
        for key, value in filters.items():
            if key not in metadata.get("metadata", {}):
                return False
            if metadata["metadata"][key] != value:
                return False
        return True