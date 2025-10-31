from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import logging

from services.llm.openai_client import OpenAIClient
from services.generator.test_gen import TestGenerator
from api.middleware.auth import get_current_user
from api.middleware.exceptions import (
    ServiceUnavailableException,
    ValidationException,
    TimeoutException
)

logger = logging.getLogger(__name__)

router = APIRouter()

class TestGenerationRequest(BaseModel):
    code: str
    file_path: str
    framework: Optional[str] = "auto"
    test_type: Optional[str] = "unit"  # unit, integration, e2e
    coverage_target: Optional[float] = 0.8

class TestGenerationResponse(BaseModel):
    tests: List[dict]
    coverage_estimate: float
    framework_used: str
    test_count: int

class TestCase(BaseModel):
    name: str
    description: str
    test_code: str
    test_type: str
    expected_behavior: str
    setup_required: Optional[bool] = False

@router.post("/test", response_model=TestGenerationResponse)
async def generate_test(
    request: TestGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate tests for the provided code."""
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

        if not request.file_path or not request.file_path.strip():
            raise ValidationException(
                message="File path cannot be empty",
                details={"field": "file_path"}
            )

        # Validate test type
        valid_test_types = ["unit", "integration", "e2e"]
        if request.test_type not in valid_test_types:
            raise ValidationException(
                message=f"Invalid test type. Must be one of: {', '.join(valid_test_types)}",
                details={"valid_types": valid_test_types, "provided": request.test_type}
            )

        # Validate coverage target
        if not (0.0 <= request.coverage_target <= 1.0):
            raise ValidationException(
                message="Coverage target must be between 0.0 and 1.0",
                details={"provided": request.coverage_target, "valid_range": "0.0-1.0"}
            )

        # Initialize services
        try:
            test_generator = TestGenerator()
            openai_client = OpenAIClient()
        except Exception as e:
            logger.error(f"Failed to initialize test generation services: {str(e)}")
            raise ServiceUnavailableException(
                message="Test generation services are currently unavailable",
                details={"service": "test_generation_services"}
            )

        # Detect framework if auto
        framework = request.framework
        if framework == "auto":
            try:
                framework = detect_test_framework(request.file_path, request.code)
            except Exception as e:
                logger.warning(f"Framework detection failed: {str(e)}, using default")
                framework = "jest"  # Default fallback

        # Generate test cases with timeout and retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                test_prompt = f"""
                Generate comprehensive tests for the following code:

                Code:
                ```python
                {request.code}
                ```

                File: {request.file_path}
                Framework: {framework}
                Test type: {request.test_type}
                Coverage target: {request.coverage_target}

                Provide:
                1. Unit tests for individual functions
                2. Integration tests for component interactions
                3. Edge cases and error conditions
                4. Mock objects where needed
                5. Setup and teardown code
                6. Test data and fixtures

                Focus on:
                - Functionality testing
                - Edge cases
                - Error handling
                - Performance considerations
                - Security aspects
                """

                test_result = await asyncio.wait_for(
                    openai_client.generate_tests(test_prompt),
                    timeout=45.0  # 45 second timeout for test generation
                )
                break  # Success, exit retry loop

            except asyncio.TimeoutError:
                if attempt == max_retries - 1:
                    logger.error("Test generation timed out after all retries")
                    raise TimeoutException(
                        message="Test generation timed out",
                        details={"operation": "test_generation", "attempts": max_retries}
                    )
                logger.warning(f"Test generation attempt {attempt + 1} timed out, retrying...")
                await asyncio.sleep(1)

            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Test generation failed after all retries: {str(e)}")
                    raise ServiceUnavailableException(
                        message="AI test generation service failed",
                        details={"attempts": max_retries, "last_error": str(e)}
                    )
                logger.warning(f"Test generation attempt {attempt + 1} failed: {str(e)}, retrying...")
                await asyncio.sleep(1)

        # Parse and structure test cases with error handling
        try:
            test_cases = parse_test_cases(test_result, framework)
        except Exception as e:
            logger.warning(f"Failed to parse test cases: {str(e)}")
            test_cases = []

        # Calculate coverage estimate with error handling
        try:
            coverage_estimate = calculate_coverage_estimate(request.code, test_cases)
        except Exception as e:
            logger.warning(f"Failed to calculate coverage estimate: {str(e)}")
            coverage_estimate = 0.0

        return TestGenerationResponse(
            tests=test_cases,
            coverage_estimate=coverage_estimate,
            framework_used=framework,
            test_count=len(test_cases)
        )

    except ValidationException:
        raise  # Re-raise validation errors
    except TimeoutException:
        raise  # Re-raise timeout errors
    except ServiceUnavailableException:
        raise  # Re-raise service unavailable errors
    except Exception as e:
        logger.critical(f"Unexpected error in test generation: {str(e)}", exc_info=True)
        raise ServiceUnavailableException(
            message="An unexpected error occurred during test generation",
            details={"error_type": type(e).__name__}
        )

@router.post("/coverage", response_model=dict)
async def analyze_coverage(
    code: str,
    tests: List[str],
    current_user: dict = Depends(get_current_user)
):
    """Analyze test coverage for code and tests."""
    try:
        # Validate input
        if not code or not code.strip():
            raise ValidationException(
                message="Code content cannot be empty",
                details={"field": "code"}
            )

        if not tests:
            raise ValidationException(
                message="Tests list cannot be empty",
                details={"field": "tests"}
            )

        # Perform coverage analysis with error handling
        try:
            line_coverage = calculate_line_coverage(code, tests)
        except Exception as e:
            logger.warning(f"Line coverage calculation failed: {str(e)}")
            line_coverage = 0.0

        try:
            function_coverage = calculate_function_coverage(code, tests)
        except Exception as e:
            logger.warning(f"Function coverage calculation failed: {str(e)}")
            function_coverage = 0.0

        try:
            branch_coverage = calculate_branch_coverage(code, tests)
        except Exception as e:
            logger.warning(f"Branch coverage calculation failed: {str(e)}")
            branch_coverage = 0.0

        try:
            uncovered_lines = find_uncovered_lines(code, tests)
        except Exception as e:
            logger.warning(f"Uncovered lines detection failed: {str(e)}")
            uncovered_lines = []

        try:
            recommendations = generate_coverage_recommendations(code, tests)
        except Exception as e:
            logger.warning(f"Coverage recommendations generation failed: {str(e)}")
            recommendations = ["Unable to generate recommendations due to analysis error"]

        coverage_analysis = {
            "line_coverage": line_coverage,
            "function_coverage": function_coverage,
            "branch_coverage": branch_coverage,
            "uncovered_lines": uncovered_lines,
            "recommendations": recommendations
        }

        return coverage_analysis

    except ValidationException:
        raise  # Re-raise validation errors
    except Exception as e:
        logger.critical(f"Unexpected error in coverage analysis: {str(e)}", exc_info=True)
        raise ServiceUnavailableException(
            message="An unexpected error occurred during coverage analysis",
            details={"error_type": type(e).__name__}
        )

def detect_test_framework(file_path: str, code: str) -> str:
    """Detect the appropriate test framework based on file and code."""
    file_ext = file_path.split('.')[-1].lower()
    
    if file_ext == 'py':
        return 'pytest'
    elif file_ext in ['js', 'ts', 'jsx', 'tsx']:
        # Check for existing test framework indicators
        if 'jest' in code.lower() or 'describe(' in code:
            return 'jest'
        elif 'mocha' in code.lower() or 'it(' in code:
            return 'mocha'
        else:
            return 'jest'  # Default for JS/TS
    elif file_ext == 'java':
        return 'junit'
    elif file_ext == 'go':
        return 'testing'
    elif file_ext == 'rs':
        return 'cargo-test'
    else:
        return 'jest'  # Default fallback

def parse_test_cases(test_result: dict, framework: str) -> List[dict]:
    """Parse AI-generated test cases into structured format."""
    test_cases = []
    
    # This would parse the AI response and extract test cases
    # For now, we'll create some example test cases based on common patterns
    
    if framework == 'pytest':
        test_cases = generate_pytest_tests()
    elif framework == 'jest':
        test_cases = generate_jest_tests()
    elif framework == 'junit':
        test_cases = generate_junit_tests()
    else:
        test_cases = generate_generic_tests()
    
    return test_cases

def generate_pytest_tests() -> List[dict]:
    """Generate pytest test cases."""
    return [
        {
            "name": "test_basic_functionality",
            "description": "Test basic function behavior",
            "test_code": """
def test_basic_functionality():
    # Test basic functionality
    assert True  # Replace with actual test
    """,
            "test_type": "unit",
            "expected_behavior": "Function should work as expected",
            "setup_required": False
        },
        {
            "name": "test_edge_cases",
            "description": "Test edge cases and error conditions",
            "test_code": """
def test_edge_cases():
    # Test edge cases
    with pytest.raises(ValueError):
        # Test error conditions
        pass
    """,
            "test_type": "unit",
            "expected_behavior": "Should handle edge cases properly",
            "setup_required": False
        }
    ]

def generate_jest_tests() -> List[dict]:
    """Generate Jest test cases."""
    return [
        {
            "name": "should work correctly",
            "description": "Test basic functionality",
            "test_code": """
describe('Basic functionality', () => {
    test('should work correctly', () => {
        expect(true).toBe(true);
    });
});
            """,
            "test_type": "unit",
            "expected_behavior": "Function should work as expected",
            "setup_required": False
        }
    ]

def generate_junit_tests() -> List[dict]:
    """Generate JUnit test cases."""
    return [
        {
            "name": "testBasicFunctionality",
            "description": "Test basic functionality",
            "test_code": """
@Test
public void testBasicFunctionality() {
    assertTrue(true);
}
            """,
            "test_type": "unit",
            "expected_behavior": "Function should work as expected",
            "setup_required": False
        }
    ]

def generate_generic_tests() -> List[dict]:
    """Generate generic test cases."""
    return [
        {
            "name": "basic_test",
            "description": "Basic functionality test",
            "test_code": "// Basic test implementation",
            "test_type": "unit",
            "expected_behavior": "Function should work as expected",
            "setup_required": False
        }
    ]

def calculate_coverage_estimate(code: str, test_cases: List[dict]) -> float:
    """Calculate estimated test coverage."""
    if not test_cases:
        return 0.0
    
    # Simple coverage estimation based on test count and code complexity
    lines_of_code = len(code.split('\n'))
    test_count = len(test_cases)
    
    # Basic coverage calculation
    base_coverage = min(0.9, test_count * 0.1)  # Each test adds ~10% coverage
    
    return min(1.0, base_coverage)

def calculate_line_coverage(code: str, tests: List[str]) -> float:
    """Calculate line coverage percentage."""
    # This would implement actual line coverage analysis
    return 0.8  # Placeholder

def calculate_function_coverage(code: str, tests: List[str]) -> float:
    """Calculate function coverage percentage."""
    # This would implement actual function coverage analysis
    return 0.75  # Placeholder

def calculate_branch_coverage(code: str, tests: List[str]) -> float:
    """Calculate branch coverage percentage."""
    # This would implement actual branch coverage analysis
    return 0.7  # Placeholder

def find_uncovered_lines(code: str, tests: List[str]) -> List[int]:
    """Find lines not covered by tests."""
    # This would implement actual uncovered line detection
    return []  # Placeholder

def generate_coverage_recommendations(code: str, tests: List[str]) -> List[str]:
    """Generate recommendations to improve test coverage."""
    return [
        "Add tests for error conditions",
        "Test edge cases and boundary values",
        "Add integration tests for component interactions",
        "Consider adding performance tests"
    ]
