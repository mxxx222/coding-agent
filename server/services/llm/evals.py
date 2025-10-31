"""Evaluation metrics for LLM outputs."""

from typing import Dict, Any, List
import re

class LLMEvaluator:
    """Evaluate LLM outputs for quality and correctness."""
    
    def evaluate_code_quality(self, code: str) -> Dict[str, Any]:
        """Evaluate code quality metrics."""
        lines = code.split('\n')
        
        return {
            "line_count": len(lines),
            "average_line_length": sum(len(line) for line in lines) / len(lines) if lines else 0,
            "max_line_length": max(len(line) for line in lines) if lines else 0,
            "complexity_score": self._calculate_complexity(code),
            "readability_score": self._calculate_readability(code)
        }
    
    def _calculate_complexity(self, code: str) -> float:
        """Calculate code complexity score."""
        # Simple complexity based on control structures
        if_count = len(re.findall(r'\bif\b', code))
        for_count = len(re.findall(r'\bfor\b', code))
        while_count = len(re.findall(r'\bwhile\b', code))
        
        return (if_count + for_count + while_count) / 10.0
    
    def _calculate_readability(self, code: str) -> float:
        """Calculate readability score."""
        # Simple readability based on line length
        lines = code.split('\n')
        long_lines = sum(1 for line in lines if len(line) > 80)
        
        if not lines:
            return 0.0
        
        readability = 1.0 - (long_lines / len(lines))
        return max(0.0, min(1.0, readability))
    
    def evaluate_test_coverage(self, code: str, tests: List[str]) -> Dict[str, Any]:
        """Evaluate test coverage."""
        # Simple coverage estimation
        code_lines = len(code.split('\n'))
        test_lines = sum(len(test.split('\n')) for test in tests)
        
        return {
            "estimated_coverage": min(1.0, test_lines / (code_lines * 2)) if code_lines > 0 else 0.0,
            "test_count": len(tests),
            "total_test_lines": test_lines
        }

