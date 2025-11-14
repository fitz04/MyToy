"""Code executor for running code snippets safely."""
import asyncio
import tempfile
import os
from pathlib import Path
from typing import Dict, Optional, List


class CodeExecutor:
    """Executor for running code in a controlled environment."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.supported_languages = ["python", "javascript", "bash"]

    async def execute_python(self, code: str, args: List[str] = None) -> Dict[str, str]:
        """Execute Python code."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            cmd = ["python3", temp_file]
            if args:
                cmd.extend(args)

            result = await self._run_command(cmd)
            return result
        finally:
            os.unlink(temp_file)

    async def execute_javascript(self, code: str, args: List[str] = None) -> Dict[str, str]:
        """Execute JavaScript code using Node.js."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            cmd = ["node", temp_file]
            if args:
                cmd.extend(args)

            result = await self._run_command(cmd)
            return result
        finally:
            os.unlink(temp_file)

    async def execute_bash(self, code: str) -> Dict[str, str]:
        """Execute bash script."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            os.chmod(temp_file, 0o755)
            result = await self._run_command(["bash", temp_file])
            return result
        finally:
            os.unlink(temp_file)

    async def _run_command(self, cmd: List[str]) -> Dict[str, str]:
        """Run a command and capture output."""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout
                )

                return {
                    "status": "success",
                    "exit_code": process.returncode,
                    "stdout": stdout.decode('utf-8', errors='replace'),
                    "stderr": stderr.decode('utf-8', errors='replace'),
                }
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    "status": "timeout",
                    "error": f"Execution timed out after {self.timeout} seconds",
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    async def execute(
        self,
        code: str,
        language: str,
        args: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """Execute code in the specified language."""
        language = language.lower()

        if language not in self.supported_languages:
            return {
                "status": "error",
                "error": f"Unsupported language: {language}. Supported: {', '.join(self.supported_languages)}"
            }

        if language == "python":
            return await self.execute_python(code, args)
        elif language == "javascript":
            return await self.execute_javascript(code, args)
        elif language == "bash":
            return await self.execute_bash(code)

    def validate_code(self, code: str, language: str) -> Dict[str, any]:
        """Validate code syntax without executing."""
        if language.lower() == "python":
            try:
                compile(code, '<string>', 'exec')
                return {"valid": True}
            except SyntaxError as e:
                return {
                    "valid": False,
                    "error": str(e),
                    "line": e.lineno,
                }

        # For other languages, just return true for now
        return {"valid": True, "note": "Syntax validation not implemented for this language"}
