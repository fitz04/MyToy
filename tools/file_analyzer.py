"""File analyzer for reading and analyzing local files."""
import os
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
import aiofiles
from config import settings


class FileAnalyzer:
    """Analyzer for local files and codebase."""

    def __init__(self, project_path: Optional[str] = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.max_file_size = settings.max_file_size
        self.supported_extensions = settings.supported_extensions

    async def read_file(self, file_path: str) -> Dict[str, str]:
        """Read a single file and return its contents."""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if path.stat().st_size > self.max_file_size:
            raise ValueError(f"File too large: {file_path} (max {self.max_file_size} bytes)")

        try:
            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                content = await f.read()

            return {
                "path": str(path),
                "name": path.name,
                "extension": path.suffix,
                "size": path.stat().st_size,
                "content": content,
            }
        except UnicodeDecodeError:
            return {
                "path": str(path),
                "name": path.name,
                "extension": path.suffix,
                "size": path.stat().st_size,
                "content": "[Binary file - cannot display content]",
                "is_binary": True,
            }

    async def scan_directory(
        self,
        directory: Optional[str] = None,
        recursive: bool = True,
        max_depth: int = 5
    ) -> List[Dict[str, str]]:
        """Scan directory and return list of supported files."""
        dir_path = Path(directory) if directory else self.project_path

        if not dir_path.exists() or not dir_path.is_dir():
            raise ValueError(f"Invalid directory: {directory}")

        files = []
        ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env', 'dist', 'build'}

        def should_ignore(path: Path) -> bool:
            """Check if path should be ignored."""
            return any(ignored in path.parts for ignored in ignore_dirs)

        def scan_dir(current_path: Path, depth: int = 0):
            """Recursively scan directory."""
            if depth > max_depth or should_ignore(current_path):
                return

            try:
                for item in current_path.iterdir():
                    if item.is_file():
                        if item.suffix in self.supported_extensions:
                            files.append({
                                "path": str(item),
                                "name": item.name,
                                "extension": item.suffix,
                                "size": item.stat().st_size,
                                "relative_path": str(item.relative_to(dir_path)),
                            })
                    elif item.is_dir() and recursive:
                        scan_dir(item, depth + 1)
            except PermissionError:
                pass  # Skip directories without permission

        scan_dir(dir_path)
        return sorted(files, key=lambda x: x["path"])

    async def get_file_structure(
        self,
        directory: Optional[str] = None,
        max_depth: int = 3
    ) -> Dict:
        """Get tree structure of the directory."""
        dir_path = Path(directory) if directory else self.project_path

        if not dir_path.exists() or not dir_path.is_dir():
            raise ValueError(f"Invalid directory: {directory}")

        ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env', 'dist', 'build'}

        def build_tree(current_path: Path, depth: int = 0) -> Dict:
            """Build directory tree structure."""
            if depth > max_depth:
                return {"type": "truncated", "name": "..."}

            if current_path.name in ignore_dirs:
                return None

            if current_path.is_file():
                return {
                    "type": "file",
                    "name": current_path.name,
                    "extension": current_path.suffix,
                    "size": current_path.stat().st_size,
                }

            # Directory
            children = []
            try:
                for item in sorted(current_path.iterdir()):
                    if item.name.startswith('.') and item.name not in {'.env.example', '.gitignore'}:
                        continue
                    child = build_tree(item, depth + 1)
                    if child:
                        children.append(child)
            except PermissionError:
                pass

            return {
                "type": "directory",
                "name": current_path.name,
                "children": children,
            }

        return build_tree(dir_path)

    async def search_in_files(
        self,
        pattern: str,
        directory: Optional[str] = None,
        case_sensitive: bool = False
    ) -> List[Dict]:
        """Search for pattern in files."""
        files = await self.scan_directory(directory)
        results = []

        for file_info in files[:settings.max_context_files]:
            try:
                file_data = await self.read_file(file_info["path"])
                content = file_data.get("content", "")

                if file_data.get("is_binary"):
                    continue

                search_pattern = pattern if case_sensitive else pattern.lower()
                search_content = content if case_sensitive else content.lower()

                if search_pattern in search_content:
                    # Find line numbers
                    lines = content.split('\n')
                    matches = []
                    for i, line in enumerate(lines, 1):
                        line_search = line if case_sensitive else line.lower()
                        if search_pattern in line_search:
                            matches.append({
                                "line": i,
                                "content": line.strip(),
                            })

                    results.append({
                        "file": file_info["relative_path"],
                        "matches": matches[:10],  # Limit to 10 matches per file
                    })
            except Exception as e:
                continue  # Skip files with errors

        return results

    async def analyze_codebase(self, directory: Optional[str] = None) -> Dict:
        """Analyze codebase and return summary statistics."""
        files = await self.scan_directory(directory)

        stats = {
            "total_files": len(files),
            "total_size": sum(f["size"] for f in files),
            "by_extension": {},
            "largest_files": [],
        }

        # Count by extension
        for file_info in files:
            ext = file_info["extension"]
            if ext not in stats["by_extension"]:
                stats["by_extension"][ext] = {"count": 0, "size": 0}
            stats["by_extension"][ext]["count"] += 1
            stats["by_extension"][ext]["size"] += file_info["size"]

        # Get largest files
        stats["largest_files"] = sorted(
            files,
            key=lambda x: x["size"],
            reverse=True
        )[:10]

        return stats
