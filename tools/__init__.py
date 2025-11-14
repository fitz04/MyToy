"""Tools module for file analysis, web search, and code execution."""
from .file_analyzer import FileAnalyzer
from .codebase_parser import CodebaseParser
from .executor import CodeExecutor
from .file_operations import FileOperations, file_ops
from .git_operations import GitOperations, git_ops
from .test_runner import TestRunner, TestResult, TestSummary, TestStatus, run_tests
from .code_quality import CodeQuality, CodeIssue, QualityReport, IssueLevel, check_quality
from .project_templates import ProjectTemplates, Template, create_project

# Optional: Web search (requires duckduckgo-search package)
try:
    from .web_search import WebSearchTool
    _web_search_available = True
except ImportError:
    WebSearchTool = None
    _web_search_available = False

__all__ = [
    "FileAnalyzer",
    "CodebaseParser",
    "CodeExecutor",
    "FileOperations",
    "file_ops",
    "GitOperations",
    "git_ops",
    "TestRunner",
    "TestResult",
    "TestSummary",
    "TestStatus",
    "run_tests",
    "CodeQuality",
    "CodeIssue",
    "QualityReport",
    "IssueLevel",
    "check_quality",
    "ProjectTemplates",
    "Template",
    "create_project",
]

if _web_search_available:
    __all__.append("WebSearchTool")
