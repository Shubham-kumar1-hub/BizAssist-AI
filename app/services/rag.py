import hashlib
import math
import uuid
from pathlib import Path

import chromadb
from chromadb.api.types import EmbeddingFunction
from pypdf import PdfReader

from app.core.config import settings


class HashEmbeddingFunction(EmbeddingFunction):
    """Small local embedding function so the project works without paid embedding APIs."""

    def __call__(self, input):
        return [self._embed(text) for text in input]

    @staticmethod
    def _embed(text: str, dimensions: int = 384) -> list[float]:
        vector = [0.0] * dimensions
        for token in text.lower().split():
            digest = hashlib.md5(token.encode("utf-8")).hexdigest()
            index = int(digest, 16) % dimensions
            vector[index] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class RAGService:
    def __init__(self):
        Path(settings.chroma_path).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=settings.chroma_path)
        self.collection = self.client.get_or_create_collection(
            name="business_documents",
            embedding_function=HashEmbeddingFunction(),
        )

    def add_document(self, filename: str, content: bytes) -> int:
        text = self._extract_text(filename, content)
        chunks = self._chunk_text(text)
        if not chunks:
            return 0

        upload_id = uuid.uuid4().hex[:8]
        ids = [f"{filename}-{upload_id}-{index}" for index, _ in enumerate(chunks)]
        self.collection.add(
            ids=ids,
            documents=chunks,
            metadatas=[{"filename": filename, "chunk": index} for index, _ in enumerate(chunks)],
        )
        return len(chunks)

    def search(self, query: str, limit: int = 4) -> tuple[list[str], list[str]]:
        result = self.collection.query(query_texts=[query], n_results=limit)
        docs = result.get("documents", [[]])[0]
        metadata = result.get("metadatas", [[]])[0]
        sources = [item.get("filename", "uploaded document") for item in metadata]
        return docs, sources

    @staticmethod
    def _extract_text(filename: str, content: bytes) -> str:
        if filename.lower().endswith(".pdf"):
            temp_path = Path("data") / f"tmp_{filename}"
            temp_path.write_bytes(content)
            try:
                reader = PdfReader(str(temp_path))
                return "\n".join(page.extract_text() or "" for page in reader.pages)
            finally:
                temp_path.unlink(missing_ok=True)
        return content.decode("utf-8", errors="ignore")

    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
        cleaned = " ".join(text.split())
        chunks = []
        start = 0
        while start < len(cleaned):
            chunk = cleaned[start : start + chunk_size]
            if chunk.strip():
                chunks.append(chunk)
            start += chunk_size - overlap
        return chunks


rag_service = RAGService()
