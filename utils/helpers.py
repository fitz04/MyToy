"""Helper utilities."""
from typing import List, Dict, Any
import re


def format_code_block(code: str, language: str = "") -> str:
    """Format code as markdown code block."""
    return f"```{language}\n{code}\n```"


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """Extract code blocks from markdown text."""
    pattern = r"```(\w+)?\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)

    code_blocks = []
    for lang, code in matches:
        code_blocks.append({
            "language": lang or "text",
            "code": code.strip()
        })

    return code_blocks


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def count_tokens_estimate(text: str) -> int:
    """Rough estimate of token count (4 chars ≈ 1 token)."""
    return len(text) // 4


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing special characters."""
    # Remove or replace special characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    return filename


def parse_language_from_filename(filename: str) -> str:
    """Get programming language from file extension."""
    extension_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.sh': 'bash',
        '.md': 'markdown',
    }

    ext = filename[filename.rfind('.'):].lower() if '.' in filename else ''
    return extension_map.get(ext, 'text')
