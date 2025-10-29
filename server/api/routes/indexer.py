from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os

router = APIRouter()

# Import services
from services.indexer.vector_store import VectorStore
from services.indexer.ast_parser import ASTParser
from services.indexer.embeddings import EmbeddingService

# Global instances
vector_store = None
ast_parser = None
embedding_service = None

async def get_vector_store():
    global vector_store
    if vector_store is None:
        vector_store = VectorStore()
        await vector_store.initialize()
    return vector_store

async def get_ast_parser():
    global ast_parser
    if ast_parser is None:
        ast_parser = ASTParser()
    return ast_parser

async def get_embedding_service():
    global embedding_service
    if embedding_service is None:
        embedding_service = EmbeddingService()
        await embedding_service.initialize()
    return embedding_service

# Request models
class IndexCodeRequest(BaseModel):
    code: str
    language: str = "python"
    metadata: Optional[Dict[str, Any]] = None

class SearchCodeRequest(BaseModel):
    query: str
    top_k: int = 5
    filters: Optional[Dict[str, Any]] = None

class ParseCodeRequest(BaseModel):
    code: str
    language: str = "python"

# Endpoints
@router.post("/index")
async def index_code(request: IndexCodeRequest):
    """Index code into the vector store."""
    try:
        # Get services
        vs = await get_vector_store()
        parser = await get_ast_parser()
        
        # Parse code to get structure
        ast_data = await parser.parse_code(request.code, request.language)
        
        # Enhance metadata with AST data
        enhanced_metadata = {
            **(request.metadata or {}),
            "language": request.language,
            "complexity": ast_data.get("complexity", 0),
            "function_count": ast_data.get("function_count", 0),
            "class_count": ast_data.get("class_count", 0),
            "line_count": ast_data.get("line_count", 0)
        }
        
        # Add to vector store
        code_id = await vs.add_code(request.code, enhanced_metadata)
        
        if not code_id:
            raise HTTPException(status_code=500, detail="Failed to index code")
        
        return {
            "status": "success",
            "code_id": code_id,
            "ast_analysis": ast_data,
            "message": "Code indexed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

@router.post("/search")
async def search_code(request: SearchCodeRequest):
    """Search for similar code."""
    try:
        vs = await get_vector_store()
        
        # Search for similar code
        results = await vs.search_similar(
            query=request.query,
            top_k=request.top_k,
            filters=request.filters
        )
        
        return {
            "status": "success",
            "query": request.query,
            "results_count": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/parse")
async def parse_code(request: ParseCodeRequest):
    """Parse code and extract structural information."""
    try:
        parser = await get_ast_parser()
        
        # Parse code
        ast_data = await parser.parse_code(request.code, request.language)
        
        return {
            "status": "success",
            "language": request.language,
            "analysis": ast_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")

@router.get("/stats")
async def get_indexer_stats():
    """Get indexer statistics."""
    try:
        vs = await get_vector_store()
        
        # Get stats
        stats = await vs.get_stats()
        
        return {
            "status": "success",
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.get("/code/{code_id}")
async def get_code(code_id: str):
    """Get code by ID."""
    try:
        vs = await get_vector_store()
        
        # Get code
        code_data = await vs.get_code_by_id(code_id)
        
        if not code_data:
            raise HTTPException(status_code=404, detail="Code not found")
        
        return {
            "status": "success",
            "code": code_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get code: {str(e)}")

@router.delete("/code/{code_id}")
async def delete_code(code_id: str):
    """Delete code from the index."""
    try:
        vs = await get_vector_store()
        
        # Delete code
        success = await vs.delete_code(code_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Code not found")
        
        return {
            "status": "success",
            "message": "Code deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete code: {str(e)}")

@router.post("/batch-index")
async def batch_index_code(requests: List[IndexCodeRequest]):
    """Index multiple code snippets."""
    try:
        vs = await get_vector_store()
        parser = await get_ast_parser()
        
        results = []
        for req in requests:
            # Parse code
            ast_data = await parser.parse_code(req.code, req.language)
            
            # Enhance metadata
            enhanced_metadata = {
                **(req.metadata or {}),
                "language": req.language,
                "complexity": ast_data.get("complexity", 0),
                "function_count": ast_data.get("function_count", 0),
                "class_count": ast_data.get("class_count", 0)
            }
            
            # Add to vector store
            code_id = await vs.add_code(req.code, enhanced_metadata)
            results.append({
                "code_id": code_id,
                "status": "success" if code_id else "failed"
            })
        
        return {
            "status": "success",
            "indexed": sum(1 for r in results if r["status"] == "success"),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch indexing failed: {str(e)}")

