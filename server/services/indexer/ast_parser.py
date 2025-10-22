import ast
import re
from typing import Dict, Any, List, Optional
import asyncio

class ASTParser:
    def __init__(self):
        self.supported_languages = ["python", "javascript", "typescript"]

    async def parse_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Parse code and extract structural information."""
        try:
            if language == "python":
                return await self.parse_python_code(code)
            elif language in ["javascript", "typescript"]:
                return await self.parse_javascript_code(code)
            else:
                return await self.parse_generic_code(code)
        except Exception as e:
            return {
                "error": str(e),
                "complexity": 0,
                "functions": [],
                "classes": [],
                "imports": [],
                "line_count": len(code.split('\n'))
            }

    async def parse_python_code(self, code: str) -> Dict[str, Any]:
        """Parse Python code using AST."""
        try:
            tree = ast.parse(code)
            
            # Extract information
            functions = []
            classes = []
            imports = []
            complexity = 0
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_complexity = self.calculate_cyclomatic_complexity(node)
                    complexity += func_complexity
                    
                    functions.append({
                        "name": node.name,
                        "line_number": node.lineno,
                        "complexity": func_complexity,
                        "parameters": [arg.arg for arg in node.args.args],
                        "docstring": ast.get_docstring(node)
                    })
                
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        "name": node.name,
                        "line_number": node.lineno,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        "docstring": ast.get_docstring(node)
                    })
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        imports.extend([alias.name for alias in node.names])
                    else:
                        imports.append(node.module or "")
            
            return {
                "complexity": complexity,
                "functions": functions,
                "classes": classes,
                "imports": imports,
                "line_count": len(code.split('\n')),
                "function_count": len(functions),
                "class_count": len(classes),
                "nesting_depth": self.calculate_max_nesting_depth(tree),
                "duplicate_code": self.detect_duplicate_code(code),
                "unused_imports": self.detect_unused_imports(code, imports)
            }
            
        except SyntaxError as e:
            return {
                "error": f"Syntax error: {e}",
                "complexity": 0,
                "functions": [],
                "classes": [],
                "imports": [],
                "line_count": len(code.split('\n'))
            }

    async def parse_javascript_code(self, code: str) -> Dict[str, Any]:
        """Parse JavaScript/TypeScript code using regex patterns."""
        functions = []
        classes = []
        imports = []
        complexity = 0
        
        # Extract functions
        function_pattern = r'function\s+(\w+)\s*\([^)]*\)\s*\{'
        for match in re.finditer(function_pattern, code):
            functions.append({
                "name": match.group(1),
                "line_number": code[:match.start()].count('\n') + 1,
                "complexity": 1,  # Simplified
                "parameters": [],
                "docstring": None
            })
        
        # Extract arrow functions
        arrow_pattern = r'(\w+)\s*=\s*\([^)]*\)\s*=>'
        for match in re.finditer(arrow_pattern, code):
            functions.append({
                "name": match.group(1),
                "line_number": code[:match.start()].count('\n') + 1,
                "complexity": 1,
                "parameters": [],
                "docstring": None
            })
        
        # Extract classes
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, code):
            classes.append({
                "name": match.group(1),
                "line_number": code[:match.start()].count('\n') + 1,
                "methods": [],
                "docstring": None
            })
        
        # Extract imports
        import_pattern = r'import\s+.*from\s+[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(import_pattern, code):
            imports.append(match.group(1))
        
        # Calculate complexity (simplified)
        complexity = len(functions) + len(classes)
        
        return {
            "complexity": complexity,
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "line_count": len(code.split('\n')),
            "function_count": len(functions),
            "class_count": len(classes),
            "nesting_depth": self.calculate_js_nesting_depth(code),
            "duplicate_code": self.detect_duplicate_code(code),
            "unused_imports": []
        }

    async def parse_generic_code(self, code: str) -> Dict[str, Any]:
        """Parse generic code using basic analysis."""
        lines = code.split('\n')
        
        return {
            "complexity": 1,
            "functions": [],
            "classes": [],
            "imports": [],
            "line_count": len(lines),
            "function_count": 0,
            "class_count": 0,
            "nesting_depth": 1,
            "duplicate_code": False,
            "unused_imports": []
        }

    def calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity for a function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity

    def calculate_max_nesting_depth(self, tree: ast.AST) -> int:
        """Calculate maximum nesting depth."""
        max_depth = 0
        
        def visit_node(node: ast.AST, depth: int):
            nonlocal max_depth
            max_depth = max(max_depth, depth)
            
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With, ast.AsyncWith)):
                    visit_node(child, depth + 1)
                else:
                    visit_node(child, depth)
        
        visit_node(tree, 0)
        return max_depth

    def calculate_js_nesting_depth(self, code: str) -> int:
        """Calculate nesting depth for JavaScript code."""
        max_depth = 0
        current_depth = 0
        
        for char in code:
            if char in '{([[':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char in '})]]':
                current_depth = max(0, current_depth - 1)
        
        return max_depth

    def detect_duplicate_code(self, code: str) -> bool:
        """Detect duplicate code patterns."""
        lines = code.split('\n')
        
        # Simple duplicate detection
        line_counts = {}
        for line in lines:
            line = line.strip()
            if len(line) > 10:  # Only check substantial lines
                line_counts[line] = line_counts.get(line, 0) + 1
        
        # Check for duplicates
        for line, count in line_counts.items():
            if count > 1:
                return True
        
        return False

    def detect_unused_imports(self, code: str, imports: List[str]) -> List[str]:
        """Detect unused imports."""
        unused = []
        
        for import_name in imports:
            if import_name not in code:
                unused.append(import_name)
        
        return unused