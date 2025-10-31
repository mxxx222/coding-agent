"""Prompt templates for LLM interactions."""

class PromptTemplates:
    """Collection of prompt templates for different tasks."""
    
    CODE_ANALYSIS = """
    Analyze the following code and provide:
    1. Code quality assessment
    2. Complexity analysis
    3. Performance suggestions
    4. Security considerations
    5. Best practices recommendations
    
    Code:
    ```{language}
    {code}
    ```
    
    Context: {context}
    """
    
    CODE_EXPLANATION = """
    Explain the following code in detail:
    1. What the code does
    2. Key components and their roles
    3. Data flow and logic
    4. Dependencies and relationships
    5. Potential issues or improvements
    
    Detail level: {detail_level}
    
    Code:
    ```{language}
    {code}
    ```
    """
    
    TEST_GENERATION = """
    Generate comprehensive tests for the following code:
    
    Code:
    ```{language}
    {code}
    ```
    
    Framework: {framework}
    Test type: {test_type}
    
    Provide:
    1. Unit tests for individual functions
    2. Integration tests for component interactions
    3. Edge cases and error conditions
    4. Mock objects where needed
    """
    
    REFACTORING = """
    Analyze the following code for refactoring opportunities:
    
    Code:
    ```{language}
    {code}
    ```
    
    Focus areas: {focus_areas}
    
    Provide specific refactoring suggestions with:
    1. Type of refactoring
    2. Severity level
    3. Clear title and description
    4. Current code snippet
    5. Suggested improved code
    6. Reasoning for the change
    """

