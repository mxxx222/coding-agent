from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import asyncio

from services.llm.openai_client import OpenAIClient
from services.generator.refactor import RefactorService
from api.middleware.auth import get_current_user

router = APIRouter()

class RefactorRequest(BaseModel):
    code: str
    file_path: str
    language: Optional[str] = "auto"
    focus_areas: Optional[List[str]] = ["performance", "readability", "maintainability"]

class RefactorResponse(BaseModel):
    suggestions: List[dict]
    refactored_code: Optional[str] = None
    confidence_score: float

class RefactorSuggestion(BaseModel):
    type: str
    severity: str
    title: str
    description: str
    current_code: str
    suggested_code: str
    reasoning: str
    line_number: Optional[int] = None

@router.post("/refactor", response_model=RefactorResponse)
async def suggest_refactor(
    request: RefactorRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get AI-powered refactoring suggestions for code."""
    try:
        refactor_service = RefactorService()
        openai_client = OpenAIClient()
        
        # Analyze code for refactoring opportunities
        analysis_prompt = f"""
        Analyze the following code for refactoring opportunities:
        
        Code:
        ```{request.language}
        {request.code}
        ```
        
        File: {request.file_path}
        Focus areas: {', '.join(request.focus_areas)}
        
        Provide specific refactoring suggestions with:
        1. Type of refactoring (performance, readability, maintainability, security, best-practice)
        2. Severity level (low, medium, high)
        3. Clear title and description
        4. Current code snippet
        5. Suggested improved code
        6. Reasoning for the change
        7. Line number if applicable
        """
        
        analysis_result = await openai_client.analyze_code(analysis_prompt)
        
        # Parse suggestions from AI response
        suggestions = parse_refactor_suggestions(analysis_result, request.code)
        
        # Calculate confidence score
        confidence_score = calculate_confidence_score(suggestions)
        
        # Generate refactored code if requested
        refactored_code = None
        if len(suggestions) > 0:
            refactored_code = await generate_refactored_code(
                request.code, 
                suggestions, 
                openai_client
            )
        
        return RefactorResponse(
            suggestions=suggestions,
            refactored_code=refactored_code,
            confidence_score=confidence_score
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refactoring analysis failed: {str(e)}")

@router.post("/apply", response_model=dict)
async def apply_refactor(
    request: RefactorRequest,
    suggestion_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Apply a specific refactoring suggestion."""
    try:
        refactor_service = RefactorService()
        
        # Get the specific suggestion
        suggestions = await refactor_service.get_suggestions(request.code, request.language)
        suggestion = next((s for s in suggestions if s.get('id') == suggestion_id), None)
        
        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        
        # Apply the refactoring
        refactored_code = await refactor_service.apply_suggestion(
            request.code, 
            suggestion
        )
        
        return {
            "success": True,
            "refactored_code": refactored_code,
            "applied_suggestion": suggestion
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply refactoring: {str(e)}")

def parse_refactor_suggestions(analysis_result: dict, original_code: str) -> List[dict]:
    """Parse AI response into structured suggestions."""
    suggestions = []
    
    # This would parse the AI response and extract structured suggestions
    # For now, we'll create some example suggestions based on common patterns
    
    lines = original_code.split('\n')
    
    # Check for common refactoring opportunities
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Long lines
        if len(line) > 120:
            suggestions.append({
                "id": f"long_line_{line_num}",
                "type": "readability",
                "severity": "medium",
                "title": "Long line detected",
                "description": "Consider breaking this long line into multiple lines",
                "current_code": line,
                "suggested_code": break_long_line(line),
                "reasoning": "Long lines reduce readability and make code harder to maintain",
                "line_number": line_num
            })
        
        # Console.log statements
        if 'console.log' in line and not line.strip().startswith('//'):
            suggestions.append({
                "id": f"console_log_{line_num}",
                "type": "best-practice",
                "severity": "low",
                "title": "Console.log statement found",
                "description": "Consider removing or replacing with proper logging",
                "current_code": line,
                "suggested_code": line.replace('console.log', '// console.log'),
                "reasoning": "Console.log statements should be removed from production code",
                "line_number": line_num
            })
        
        # TODO comments
        if 'TODO' in line or 'FIXME' in line:
            suggestions.append({
                "id": f"todo_{line_num}",
                "type": "maintainability",
                "severity": "medium",
                "title": "TODO/FIXME comment found",
                "description": "Address this TODO or FIXME comment",
                "current_code": line,
                "suggested_code": line,
                "reasoning": "TODO and FIXME comments indicate incomplete work that should be addressed",
                "line_number": line_num
            })
    
    return suggestions

def break_long_line(line: str) -> str:
    """Break a long line into multiple lines."""
    if len(line) <= 80:
        return line
    
    # Simple line breaking at 80 characters
    parts = []
    current = line
    while len(current) > 80:
        break_point = current.rfind(' ', 0, 80)
        if break_point == -1:
            break_point = 80
        parts.append(current[:break_point])
        current = '  ' + current[break_point:].lstrip()
    parts.append(current)
    
    return '\n'.join(parts)

def calculate_confidence_score(suggestions: List[dict]) -> float:
    """Calculate confidence score for suggestions."""
    if not suggestions:
        return 0.0
    
    # Base confidence on suggestion quality and severity
    total_score = 0.0
    for suggestion in suggestions:
        severity_score = {"low": 0.3, "medium": 0.6, "high": 0.9}.get(
            suggestion.get("severity", "low"), 0.3
        )
        total_score += severity_score
    
    return min(1.0, total_score / len(suggestions))

async def generate_refactored_code(
    original_code: str, 
    suggestions: List[dict], 
    openai_client: OpenAIClient
) -> str:
    """Generate refactored code based on suggestions."""
    refactor_prompt = f"""
    Refactor the following code based on these suggestions:
    
    Original code:
    ```python
    {original_code}
    ```
    
    Suggestions to apply:
    {format_suggestions_for_prompt(suggestions)}
    
    Provide the refactored code that addresses the suggestions while maintaining functionality.
    """
    
    try:
        result = await openai_client.generate_code(refactor_prompt)
        return result.get('code', original_code)
    except Exception:
        # Fallback to original code if refactoring fails
        return original_code

def format_suggestions_for_prompt(suggestions: List[dict]) -> str:
    """Format suggestions for the AI prompt."""
    formatted = []
    for i, suggestion in enumerate(suggestions, 1):
        formatted.append(f"""
        {i}. {suggestion.get('title', 'Suggestion')}
           - Type: {suggestion.get('type', 'unknown')}
           - Severity: {suggestion.get('severity', 'low')}
           - Description: {suggestion.get('description', '')}
           - Reasoning: {suggestion.get('reasoning', '')}
        """)
    
    return '\n'.join(formatted)
