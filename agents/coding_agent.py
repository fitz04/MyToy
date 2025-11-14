"""Main coding agent implementation."""
import os
from typing import List, Dict, Optional, AsyncGenerator
from pathlib import Path

from llm import LLMManager, Message
from tools import FileAnalyzer, CodebaseParser, CodeExecutor
from .prompts import (
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
    CONTEXT_TEMPLATE,
    ANALYSIS_PROMPT,
)

# Optional: Web search
try:
    from tools import WebSearchTool
except ImportError:
    WebSearchTool = None

# Optional: RAG
try:
    from rag import Retriever
except ImportError:
    Retriever = None


class CodingAgent:
    """Main coding agent with access to multiple tools and capabilities."""

    def __init__(self, project_path: Optional[str] = None):
        self.llm_manager = LLMManager()
        self.file_analyzer = FileAnalyzer(project_path)
        self.codebase_parser = CodebaseParser()
        self.web_search = WebSearchTool() if WebSearchTool is not None else None
        self.code_executor = CodeExecutor()
        self.retriever = Retriever() if Retriever is not None else None

        self.conversation_history: List[Message] = []
        self.project_path = Path(project_path) if project_path else Path.cwd()

    async def process_message(
        self,
        user_message: str,
        stream: bool = True,
        use_rag: bool = True,
        use_web: bool = False,
        analyze_project: bool = False,
    ) -> AsyncGenerator[str, None]:
        """Process a user message and generate a response."""

        # Build context
        context_parts = {}

        # Project info if requested
        if analyze_project:
            project_info = await self._get_project_info()
            context_parts["project_info"] = project_info
        else:
            context_parts["project_info"] = ""

        # Get relevant files based on message
        relevant_files = await self._get_relevant_files(user_message)
        context_parts["relevant_files"] = relevant_files

        # RAG context
        if use_rag and self.retriever is not None:
            rag_context = self.retriever.get_context(user_message, n_results=3)
            context_parts["rag_context"] = rag_context if rag_context else "No relevant documentation found."
        else:
            context_parts["rag_context"] = ""

        # Web search if requested
        if use_web and self.web_search is not None:
            web_results = await self._web_search(user_message)
            context_parts["web_results"] = web_results
        else:
            context_parts["web_results"] = ""

        # Build full context
        context = CONTEXT_TEMPLATE.format(**context_parts)

        # Create messages
        system_message = Message(role="system", content=SYSTEM_PROMPT)
        user_prompt = USER_PROMPT_TEMPLATE.format(
            user_message=user_message,
            context=context
        )

        messages = [system_message] + self.conversation_history + [
            Message(role="user", content=user_prompt)
        ]

        # Generate response
        if stream:
            async for chunk in self.llm_manager.stream_generate(messages):
                yield chunk

            # Store in history (we need to accumulate the streamed response)
            # For simplicity, we'll just store the user message
            self.conversation_history.append(Message(role="user", content=user_message))
        else:
            response = await self.llm_manager.generate(messages)
            self.conversation_history.append(Message(role="user", content=user_message))
            self.conversation_history.append(Message(role="assistant", content=response.content))
            yield response.content

    async def _get_project_info(self) -> str:
        """Get project information and structure."""
        try:
            stats = await self.file_analyzer.analyze_codebase()
            structure = await self.file_analyzer.get_file_structure(max_depth=2)

            info = f"""Project Statistics:
- Total files: {stats['total_files']}
- Total size: {stats['total_size'] / 1024:.2f} KB

File breakdown by extension:
"""
            for ext, data in stats['by_extension'].items():
                info += f"  {ext}: {data['count']} files ({data['size'] / 1024:.2f} KB)\n"

            return info
        except Exception as e:
            return f"Error analyzing project: {e}"

    async def _get_relevant_files(self, query: str, max_files: int = 5) -> str:
        """Get relevant files based on query."""
        try:
            # Search for files mentioning keywords from query
            results = await self.file_analyzer.search_in_files(query, case_sensitive=False)

            if not results:
                return "No directly relevant files found."

            relevant = "Relevant files:\n"
            for result in results[:max_files]:
                relevant += f"\n{result['file']}:\n"
                for match in result['matches'][:3]:
                    relevant += f"  Line {match['line']}: {match['content']}\n"

            return relevant
        except Exception as e:
            return f"Error searching files: {e}"

    async def _web_search(self, query: str) -> str:
        """Perform web search and return formatted results."""
        try:
            results = await self.web_search.search_documentation(query)

            if not results:
                return "No web search results found."

            formatted = "Web search results:\n"
            for i, result in enumerate(results[:3], 1):
                formatted += f"\n{i}. {result['title']}\n"
                formatted += f"   URL: {result['url']}\n"
                formatted += f"   {result['snippet']}\n"

                if result.get('content'):
                    # Include first 500 chars of content
                    content_preview = result['content'][:500]
                    formatted += f"   Preview: {content_preview}...\n"

            return formatted
        except Exception as e:
            return f"Error searching web: {e}"

    async def analyze_project(self) -> str:
        """Analyze the entire project."""
        messages = [
            Message(role="system", content=SYSTEM_PROMPT),
            Message(role="user", content=ANALYSIS_PROMPT)
        ]

        # Get project context
        project_info = await self._get_project_info()
        messages.append(Message(role="user", content=f"Project Info:\n{project_info}"))

        response = await self.llm_manager.generate(messages)
        return response.content

    async def execute_code(self, code: str, language: str) -> Dict:
        """Execute code and return results."""
        return await self.code_executor.execute(code, language)

    async def add_document_to_rag(self, file_path: str) -> int:
        """Add a document to RAG knowledge base."""
        return await self.retriever.add_document(file_path)

    async def search_rag(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search RAG knowledge base."""
        return self.retriever.retrieve(query, n_results)

    def switch_llm(self, provider: str) -> str:
        """Switch LLM provider."""
        return self.llm_manager.switch_provider(provider)

    def get_current_llm(self) -> str:
        """Get current LLM provider."""
        return self.llm_manager.get_current_provider()

    def get_llm_info(self) -> dict:
        """Get LLM provider information."""
        return self.llm_manager.get_provider_info()

    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []

    def get_rag_stats(self) -> Dict:
        """Get RAG statistics."""
        return self.retriever.get_stats()

    def clear_rag(self):
        """Clear RAG knowledge base."""
        self.retriever.clear_all()
