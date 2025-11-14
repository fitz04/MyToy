"""Retriever for finding relevant documents."""
from typing import List, Dict, Optional
from .vectorstore import VectorStore
from .document_processor import DocumentProcessor


class Retriever:
    """Retriever for finding and ranking relevant documents."""

    def __init__(self, collection_name: str = "documents"):
        self.vectorstore = VectorStore(collection_name)
        self.doc_processor = DocumentProcessor()

    async def add_document(self, file_path: str) -> int:
        """Add a document to the vector store."""
        documents = await self.doc_processor.process_file(file_path)
        return self.vectorstore.add_documents(documents)

    async def add_documents(self, file_paths: List[str]) -> int:
        """Add multiple documents to the vector store."""
        documents = await self.doc_processor.process_multiple_files(file_paths)
        return self.vectorstore.add_documents(documents)

    async def add_text(self, text: str, metadata: Optional[Dict] = None) -> int:
        """Add raw text to the vector store."""
        documents = self.doc_processor.chunk_text(text, metadata)
        return self.vectorstore.add_documents(documents)

    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        filter_by_source: Optional[str] = None,
        filter_by_type: Optional[str] = None
    ) -> List[Dict]:
        """Retrieve relevant documents for a query."""
        # Build filter
        filter_metadata = {}
        if filter_by_source:
            filter_metadata["source"] = filter_by_source
        if filter_by_type:
            filter_metadata["file_type"] = filter_by_type

        # Search
        results = self.vectorstore.search(
            query,
            n_results=n_results,
            filter_metadata=filter_metadata if filter_metadata else None
        )

        return results

    def get_context(
        self,
        query: str,
        n_results: int = 5,
        max_tokens: int = 4000
    ) -> str:
        """Get context string from retrieved documents."""
        results = self.retrieve(query, n_results)

        context_parts = []
        total_length = 0

        for i, result in enumerate(results):
            source = result["metadata"].get("source", "unknown")
            content = result["content"]

            part = f"[Source {i+1}: {source}]\n{content}\n"
            part_length = len(part)

            if total_length + part_length > max_tokens * 4:  # Rough token estimate
                break

            context_parts.append(part)
            total_length += part_length

        return "\n---\n".join(context_parts)

    def delete_source(self, source: str) -> int:
        """Delete all documents from a source."""
        return self.vectorstore.delete_by_source(source)

    def clear_all(self):
        """Clear all documents."""
        self.vectorstore.clear()

    def get_stats(self) -> Dict:
        """Get retriever statistics."""
        return self.vectorstore.get_stats()

    def list_sources(self) -> List[str]:
        """List all sources."""
        return self.vectorstore.list_sources()
