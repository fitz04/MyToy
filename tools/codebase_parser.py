"""Codebase parser for understanding code structure."""
import ast
import re
from pathlib import Path
from typing import List, Dict, Optional, Any


class CodebaseParser:
    """Parser for analyzing code structure and extracting information."""

    def __init__(self):
        self.python_parser = PythonParser()
        self.javascript_parser = JavaScriptParser()

    async def parse_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse a file and extract structure information."""
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension == '.py':
            return await self.python_parser.parse(content, file_path)
        elif extension in ['.js', '.jsx', '.ts', '.tsx']:
            return await self.javascript_parser.parse(content, file_path)
        else:
            return {
                "file": file_path,
                "type": "text",
                "lines": len(content.split('\n')),
            }

    async def extract_functions(self, file_path: str, content: str) -> List[Dict]:
        """Extract function definitions from a file."""
        result = await self.parse_file(file_path, content)
        return result.get("functions", [])

    async def extract_classes(self, file_path: str, content: str) -> List[Dict]:
        """Extract class definitions from a file."""
        result = await self.parse_file(file_path, content)
        return result.get("classes", [])

    async def extract_imports(self, file_path: str, content: str) -> List[str]:
        """Extract import statements from a file."""
        result = await self.parse_file(file_path, content)
        return result.get("imports", [])


class PythonParser:
    """Parser for Python files."""

    async def parse(self, content: str, file_path: str) -> Dict[str, Any]:
        """Parse Python file and extract structure."""
        try:
            tree = ast.parse(content)

            functions = []
            classes = []
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "docstring": ast.get_docstring(node),
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                    })
                elif isinstance(node, ast.ClassDef):
                    methods = [
                        m.name for m in node.body
                        if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
                    ]
                    classes.append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": methods,
                        "docstring": ast.get_docstring(node),
                        "bases": [self._get_name(base) for base in node.bases],
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    else:
                        module = node.module or ""
                        for alias in node.names:
                            imports.append(f"{module}.{alias.name}" if module else alias.name)

            return {
                "file": file_path,
                "type": "python",
                "lines": len(content.split('\n')),
                "functions": functions,
                "classes": classes,
                "imports": imports,
            }
        except SyntaxError as e:
            return {
                "file": file_path,
                "type": "python",
                "error": str(e),
                "lines": len(content.split('\n')),
            }

    def _get_name(self, node):
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(node)


class JavaScriptParser:
    """Simple parser for JavaScript/TypeScript files."""

    async def parse(self, content: str, file_path: str) -> Dict[str, Any]:
        """Parse JavaScript/TypeScript file and extract basic structure."""
        functions = []
        classes = []
        imports = []

        # Extract imports
        import_patterns = [
            r'import\s+.*?\s+from\s+[\'"](.+?)[\'"]',
            r'const\s+.*?\s*=\s*require\([\'"](.+?)[\'"]\)',
        ]
        for pattern in import_patterns:
            for match in re.finditer(pattern, content):
                imports.append(match.group(1))

        # Extract function declarations
        function_patterns = [
            r'function\s+(\w+)\s*\(',
            r'const\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>',
            r'(\w+)\s*:\s*(?:async\s+)?\([^)]*\)\s*=>',
        ]
        for pattern in function_patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                line_num = content[:match.start()].count('\n') + 1
                functions.append({
                    "name": match.group(1),
                    "line": line_num,
                })

        # Extract class declarations
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?'
        for match in re.finditer(class_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            classes.append({
                "name": match.group(1),
                "line": line_num,
                "extends": match.group(2) if match.group(2) else None,
            })

        return {
            "file": file_path,
            "type": "javascript",
            "lines": len(content.split('\n')),
            "functions": functions,
            "classes": classes,
            "imports": list(set(imports)),
        }
