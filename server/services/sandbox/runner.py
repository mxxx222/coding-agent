"""Code execution runner."""

from typing import Dict, Any, Optional
import subprocess
import tempfile
import os

class CodeRunner:
    """Execute code safely in isolated environment."""
    
    def __init__(self):
        self.supported_languages = ["python", "javascript", "bash"]
    
    async def run_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Run code and return result."""
        if language not in self.supported_languages:
            return {
                "success": False,
                "error": f"Unsupported language: {language}"
            }
        
        try:
            if language == "python":
                return await self._run_python(code)
            elif language == "javascript":
                return await self._run_javascript(code)
            elif language == "bash":
                return await self._run_bash(code)
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _run_python(self, code: str) -> Dict[str, Any]:
        """Run Python code."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            result = subprocess.run(
                ["python", temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": True,
                "output": result.stdout,
                "error": result.stderr,
                "exit_code": result.returncode
            }
        finally:
            os.unlink(temp_file)
    
    async def _run_javascript(self, code: str) -> Dict[str, Any]:
        """Run JavaScript code."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            result = subprocess.run(
                ["node", temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": True,
                "output": result.stdout,
                "error": result.stderr,
                "exit_code": result.returncode
            }
        finally:
            os.unlink(temp_file)
    
    async def _run_bash(self, code: str) -> Dict[str, Any]:
        """Run Bash code."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            result = subprocess.run(
                ["bash", temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": True,
                "output": result.stdout,
                "error": result.stderr,
                "exit_code": result.returncode
            }
        finally:
            os.unlink(temp_file)

