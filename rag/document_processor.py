"""Document processor for handling various document types."""
import io
from pathlib import Path
from typing import List, Dict, Optional
import aiofiles
from pypdf import PdfReader
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import settings


class DocumentProcessor:
    """Processor for handling and chunking documents."""

    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )

    async def process_file(self, file_path: str) -> List[Dict[str, str]]:
        """Process a file and return chunked documents."""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file content based on type
        if path.suffix.lower() == '.pdf':
            content = await self._read_pdf(file_path)
        elif path.suffix.lower() in ['.docx', '.doc']:
            content = await self._read_docx(file_path)
        elif path.suffix.lower() in ['.txt', '.md']:
            content = await self._read_text(file_path)
        elif path.suffix.lower() in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.go', '.rs']:
            content = await self._read_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")

        # Split into chunks
        chunks = self.text_splitter.split_text(content)

        # Create documents with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append({
                "content": chunk,
                "metadata": {
                    "source": str(path),
                    "chunk_id": i,
                    "total_chunks": len(chunks),
                    "file_type": path.suffix,
                }
            })

        return documents

    async def _read_pdf(self, file_path: str) -> str:
        """Read PDF file and extract text."""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Error reading PDF: {e}")

    async def _read_docx(self, file_path: str) -> str:
        """Read DOCX file and extract text."""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Error reading DOCX: {e}")

    async def _read_text(self, file_path: str) -> str:
        """Read text file."""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            async with aiofiles.open(file_path, 'r', encoding='latin-1') as f:
                return await f.read()

    def chunk_text(self, text: str, metadata: Optional[Dict] = None) -> List[Dict[str, str]]:
        """Chunk text into smaller pieces."""
        chunks = self.text_splitter.split_text(text)

        documents = []
        for i, chunk in enumerate(chunks):
            doc_metadata = metadata.copy() if metadata else {}
            doc_metadata.update({
                "chunk_id": i,
                "total_chunks": len(chunks),
            })

            documents.append({
                "content": chunk,
                "metadata": doc_metadata,
            })

        return documents

    async def process_multiple_files(self, file_paths: List[str]) -> List[Dict[str, str]]:
        """Process multiple files and return all documents."""
        all_documents = []

        for file_path in file_paths:
            try:
                documents = await self.process_file(file_path)
                all_documents.extend(documents)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue

        return all_documents
