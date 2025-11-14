"""Vector store for storing and retrieving document embeddings."""
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from config import settings


class VectorStore:
    """Vector store using ChromaDB for document storage and retrieval."""

    def __init__(self, collection_name: str = "documents"):
        self.collection_name = collection_name
        self.embedding_model = SentenceTransformer(settings.embedding_model)

        # Initialize ChromaDB
        persist_directory = str(settings.vector_store_path)
        Path(persist_directory).mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
            )
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, documents: List[Dict[str, str]]) -> int:
        """Add documents to the vector store."""
        if not documents:
            return 0

        # Extract contents and metadata
        contents = [doc["content"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]

        # Generate embeddings
        embeddings = self.embedding_model.encode(contents, convert_to_numpy=True)

        # Generate IDs
        existing_count = self.collection.count()
        ids = [f"doc_{existing_count + i}" for i in range(len(documents))]

        # Add to collection
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=contents,
            metadatas=metadatas,
            ids=ids
        )

        return len(documents)

    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for similar documents."""
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)

        # Search
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results,
            where=filter_metadata if filter_metadata else None,
        )

        # Format results
        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0,
                })

        return formatted_results

    def delete_by_source(self, source: str) -> int:
        """Delete all documents from a specific source."""
        try:
            # Get all documents with this source
            results = self.collection.get(
                where={"source": source}
            )

            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                return len(results["ids"])
            return 0
        except Exception as e:
            print(f"Error deleting documents: {e}")
            return 0

    def clear(self):
        """Clear all documents from the collection."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def get_stats(self) -> Dict:
        """Get statistics about the vector store."""
        count = self.collection.count()

        # Get all metadata to analyze sources
        if count > 0:
            all_docs = self.collection.get()
            sources = set()
            file_types = set()

            for metadata in all_docs.get("metadatas", []):
                if "source" in metadata:
                    sources.add(metadata["source"])
                if "file_type" in metadata:
                    file_types.add(metadata["file_type"])

            return {
                "total_documents": count,
                "unique_sources": len(sources),
                "file_types": list(file_types),
                "sources": list(sources),
            }
        else:
            return {
                "total_documents": 0,
                "unique_sources": 0,
                "file_types": [],
                "sources": [],
            }

    def list_sources(self) -> List[str]:
        """List all unique sources in the vector store."""
        try:
            all_docs = self.collection.get()
            sources = set()

            for metadata in all_docs.get("metadatas", []):
                if "source" in metadata:
                    sources.add(metadata["source"])

            return sorted(list(sources))
        except Exception:
            return []
