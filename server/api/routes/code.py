from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Any
import asyncio
import logging

from services.llm.openai_client import OpenAIClient
from services.indexer.ast_parser import ASTParser
from services.indexer.embeddings import EmbeddingService
from api.middleware.auth import get_current_user
from api.middleware.exceptions import (
    ServiceUnavailableException,
    ValidationException,
    TimeoutException
)

logger = logging.getLogger(__name__)

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
    explanation: Any
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
        # Validate input
        if not request.code or not request.code.strip():
            raise ValidationException(
                message="Code content cannot be empty",
                details={"field": "code"}
            )

        if len(request.code) > 100000:  # 100KB limit
            raise ValidationException(
                message="Code content exceeds maximum size limit",
                details={"max_size": "100KB", "actual_size": f"{len(request.code)} chars"}
            )

        # Initialize services
        try:
            openai_client = OpenAIClient()
            ast_parser = ASTParser()
            embedding_service = EmbeddingService()
        except Exception as e:
            logger.error(f"Failed to initialize services: {str(e)}")
            raise ServiceUnavailableException(
                message="Required services are currently unavailable",
                details={"service": "code_analysis_services"}
            )

        # Parse AST with timeout protection
        try:
            ast_result = await asyncio.wait_for(
                ast_parser.parse_code(request.code, request.language),
                timeout=10.0  # 10 second timeout for AST parsing
            )
        except asyncio.TimeoutError:
            logger.warning("AST parsing timed out")
            raise TimeoutException(
                message="Code parsing timed out",
                details={"operation": "ast_parsing", "timeout_seconds": 10.0}
            )
        except Exception as e:
            logger.error(f"AST parsing failed: {str(e)}")
            # Continue with empty AST result for basic analysis

        # Generate embeddings with error handling
        try:
            embeddings = await asyncio.wait_for(
                embedding_service.generate_embeddings(request.code),
                timeout=15.0  # 15 second timeout for embeddings
            )
        except asyncio.TimeoutError:
            logger.warning("Embedding generation timed out")
            # Continue without embeddings
        except Exception as e:
            logger.warning(f"Embedding generation failed: {str(e)}")
            # Continue without embeddings

        # Analyze with OpenAI with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
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

                analysis_result = await asyncio.wait_for(
                    openai_client.analyze_code(analysis_prompt),
                    timeout=30.0  # 30 second timeout for AI analysis
                )
                break  # Success, exit retry loop

            except asyncio.TimeoutError:
                if attempt == max_retries - 1:
                    logger.error("AI analysis timed out after all retries")
                    raise TimeoutException(
                        message="Code analysis timed out",
                        details={"operation": "ai_analysis", "attempts": max_retries}
                    )
                logger.warning(f"AI analysis attempt {attempt + 1} timed out, retrying...")
                await asyncio.sleep(1)  # Brief delay before retry

            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"AI analysis failed after all retries: {str(e)}")
                    raise ServiceUnavailableException(
                        message="AI analysis service is currently unavailable",
                        details={"attempts": max_retries, "last_error": str(e)}
                    )
                logger.warning(f"AI analysis attempt {attempt + 1} failed: {str(e)}, retrying...")
                await asyncio.sleep(1)

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

    except ValidationException:
        raise  # Re-raise validation errors
    except TimeoutException:
        raise  # Re-raise timeout errors
    except ServiceUnavailableException:
        raise  # Re-raise service unavailable errors
    except Exception as e:
        logger.critical(f"Unexpected error in code analysis: {str(e)}", exc_info=True)
        raise ServiceUnavailableException(
            message="An unexpected error occurred during code analysis",
            details={"error_type": type(e).__name__}
        )

@router.post("/explain", response_model=CodeExplanationResponse)
async def explain_code(
    request: CodeExplanationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Explain code functionality and structure."""
    try:
        # Validate input
        if not request.code or not request.code.strip():
            raise ValidationException(
                message="Code content cannot be empty",
                details={"field": "code"}
            )

        if len(request.code) > 50000:  # 50KB limit for explanations
            raise ValidationException(
                message="Code content exceeds maximum size limit for explanation",
                details={"max_size": "50KB", "actual_size": f"{len(request.code)} chars"}
            )

        # Validate detail level
        valid_detail_levels = ["low", "medium", "high"]
        if request.detail_level not in valid_detail_levels:
            raise ValidationException(
                message=f"Invalid detail level. Must be one of: {', '.join(valid_detail_levels)}",
                details={"valid_levels": valid_detail_levels, "provided": request.detail_level}
            )

        # Initialize OpenAI client
        try:
            openai_client = OpenAIClient()
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise ServiceUnavailableException(
                message="AI explanation service is currently unavailable",
                details={"service": "openai_client"}
            )

        # Generate explanation with timeout and retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
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

                explanation_result = await asyncio.wait_for(
                    openai_client.explain_code(explanation_prompt),
                    timeout=25.0  # 25 second timeout for explanation
                )
                break  # Success, exit retry loop

            except asyncio.TimeoutError:
                if attempt == max_retries - 1:
                    logger.error("Code explanation timed out after all retries")
                    raise TimeoutException(
                        message="Code explanation timed out",
                        details={"operation": "code_explanation", "attempts": max_retries}
                    )
                logger.warning(f"Explanation attempt {attempt + 1} timed out, retrying...")
                await asyncio.sleep(1)

            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Code explanation failed after all retries: {str(e)}")
                    raise ServiceUnavailableException(
                        message="AI explanation service failed",
                        details={"attempts": max_retries, "last_error": str(e)}
                    )
                logger.warning(f"Explanation attempt {attempt + 1} failed: {str(e)}, retrying...")
                await asyncio.sleep(1)

        # Extract components with error handling
        try:
            components = extract_components(request.code, request.language)
        except Exception as e:
            logger.warning(f"Component extraction failed: {str(e)}")
            components = []

        # Analyze data flow with error handling
        try:
            data_flow = analyze_data_flow(request.code, request.language)
        except Exception as e:
            logger.warning(f"Data flow analysis failed: {str(e)}")
            data_flow = "Data flow analysis unavailable due to processing error."

        # Extract dependencies with error handling
        try:
            dependencies = extract_dependencies(request.code, request.language)
        except Exception as e:
            logger.warning(f"Dependency extraction failed: {str(e)}")
            dependencies = []

        return CodeExplanationResponse(
            explanation=explanation_result,
            components=components,
            data_flow=data_flow,
            dependencies=dependencies
        )

    except ValidationException:
        raise  # Re-raise validation errors
    except TimeoutException:
        raise  # Re-raise timeout errors
    except ServiceUnavailableException:
        raise  # Re-raise service unavailable errors
    except Exception as e:
        logger.critical(f"Unexpected error in code explanation: {str(e)}", exc_info=True)
        raise ServiceUnavailableException(
            message="An unexpected error occurred during code explanation",
            details={"error_type": type(e).__name__}
        )

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
