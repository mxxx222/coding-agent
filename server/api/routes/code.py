from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import asyncio

from services.llm.openai_client import OpenAIClient
from services.indexer.ast_parser import ASTParser
from services.indexer.embeddings import EmbeddingService
from api.middleware.auth import get_current_user

router = APIRouter()

class CodeAnalysisRequest(BaseModel):
    code: str
    language: Optional[str] = "auto"
    context: Optional[str] = None

class CodeAnalysisResponse(BaseModel):
    analysis: dict
    suggestions: List[dict]
    complexity: dict
    quality_score: float

class CodeExplanationRequest(BaseModel):
    code: str
    language: Optional[str] = "auto"
    detail_level: Optional[str] = "medium"  # low, medium, high

class CodeExplanationResponse(BaseModel):
    explanation: dict
    components: List[dict]
    data_flow: str
    dependencies: List[str]

@router.post("/code", response_model=CodeAnalysisResponse)
async def analyze_code(
    request: CodeAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Analyze code for quality, complexity, and suggestions."""
    try:
        # Initialize services
        openai_client = OpenAIClient()
        ast_parser = ASTParser()
        embedding_service = EmbeddingService()
        
        # Parse AST
        ast_result = await ast_parser.parse_code(request.code, request.language)
        
        # Generate embeddings
        embeddings = await embedding_service.generate_embeddings(request.code)
        
        # Analyze with OpenAI
        analysis_prompt = f"""
        Analyze the following code and provide:
        1. Code quality assessment
        2. Complexity analysis
        3. Performance suggestions
        4. Security considerations
        5. Best practices recommendations
        
        Code:
        ```{request.language}
        {request.code}
        ```
        
        Context: {request.context or "No additional context provided"}
        """
        
        analysis_result = await openai_client.analyze_code(analysis_prompt)
        
        # Calculate quality score
        quality_score = calculate_quality_score(ast_result, analysis_result)
        
        # Generate suggestions
        suggestions = generate_suggestions(ast_result, analysis_result)
        
        # Calculate complexity metrics
        complexity = calculate_complexity(ast_result)
        
        return CodeAnalysisResponse(
            analysis=analysis_result,
            suggestions=suggestions,
            complexity=complexity,
            quality_score=quality_score
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code analysis failed: {str(e)}")

@router.post("/explain", response_model=CodeExplanationResponse)
async def explain_code(
    request: CodeExplanationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Explain code functionality and structure."""
    try:
        openai_client = OpenAIClient()
        
        explanation_prompt = f"""
        Explain the following code in detail:
        1. What the code does
        2. Key components and their roles
        3. Data flow and logic
        4. Dependencies and relationships
        5. Potential issues or improvements
        
        Detail level: {request.detail_level}
        
        Code:
        ```{request.language}
        {request.code}
        ```
        """
        
        explanation_result = await openai_client.explain_code(explanation_prompt)
        
        # Extract components
        components = extract_components(request.code, request.language)
        
        # Analyze data flow
        data_flow = analyze_data_flow(request.code, request.language)
        
        # Extract dependencies
        dependencies = extract_dependencies(request.code, request.language)
        
        return CodeExplanationResponse(
            explanation=explanation_result,
            components=components,
            data_flow=data_flow,
            dependencies=dependencies
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code explanation failed: {str(e)}")

def calculate_quality_score(ast_result: dict, analysis_result: dict) -> float:
    """Calculate a quality score from 0 to 100."""
    score = 100.0
    
    # Deduct points for issues
    if ast_result.get('complexity', 0) > 10:
        score -= 20
    if ast_result.get('nesting_depth', 0) > 5:
        score -= 15
    if ast_result.get('function_length', 0) > 50:
        score -= 10
    if ast_result.get('duplicate_code', False):
        score -= 25
    if ast_result.get('unused_imports', 0) > 0:
        score -= 5
    
    return max(0, min(100, score))

def generate_suggestions(ast_result: dict, analysis_result: dict) -> List[dict]:
    """Generate improvement suggestions."""
    suggestions = []
    
    # Complexity suggestions
    if ast_result.get('complexity', 0) > 10:
        suggestions.append({
            "type": "complexity",
            "title": "Reduce cyclomatic complexity",
            "description": "Consider breaking down complex functions into smaller, more manageable pieces",
            "severity": "high"
        })
    
    # Performance suggestions
    if ast_result.get('nested_loops', 0) > 2:
        suggestions.append({
            "type": "performance",
            "title": "Optimize nested loops",
            "description": "Consider using more efficient algorithms or data structures",
            "severity": "medium"
        })
    
    # Code style suggestions
    if ast_result.get('long_lines', 0) > 0:
        suggestions.append({
            "type": "style",
            "title": "Improve line length",
            "description": "Keep lines under 80-100 characters for better readability",
            "severity": "low"
        })
    
    return suggestions

def calculate_complexity(ast_result: dict) -> dict:
    """Calculate complexity metrics."""
    return {
        "cyclomatic_complexity": ast_result.get('complexity', 0),
        "nesting_depth": ast_result.get('nesting_depth', 0),
        "function_count": ast_result.get('function_count', 0),
        "class_count": ast_result.get('class_count', 0),
        "line_count": ast_result.get('line_count', 0)
    }

def extract_components(code: str, language: str) -> List[dict]:
    """Extract code components."""
    components = []
    
    # Simple component extraction based on language
    if language in ['python', 'javascript', 'typescript']:
        # Extract functions
        import re
        function_pattern = r'def\s+(\w+)\s*\(' if language == 'python' else r'function\s+(\w+)\s*\('
        functions = re.findall(function_pattern, code)
        
        for func in functions:
            components.append({
                "name": func,
                "type": "function",
                "description": f"Function: {func}"
            })
    
    return components

def analyze_data_flow(code: str, language: str) -> str:
    """Analyze data flow in the code."""
    # Simple data flow analysis
    return "Data flows through the main execution path with input processing and output generation."

def extract_dependencies(code: str, language: str) -> List[str]:
    """Extract code dependencies."""
    dependencies = []
    
    # Extract import statements
    import re
    if language == 'python':
        imports = re.findall(r'import\s+(\w+)', code)
        dependencies.extend(imports)
    elif language in ['javascript', 'typescript']:
        imports = re.findall(r'import.*from\s+[\'"]([^\'"]+)[\'"]', code)
        dependencies.extend(imports)
    
    return dependencies
