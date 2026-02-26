import logging
from typing import List

logger = logging.getLogger(__name__)

# Try to import chromadb, fall back to simple in-memory store
try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("chromadb not available - using simple in-memory store")


class SimpleMemoryStore:
    """Fallback in-memory store when chromadb is not available."""
    
    def __init__(self):
        self._documents = {}  # id -> (text, metadata)
    
    def store(self, text: str, doc_id: str, metadata: dict | None = None) -> None:
        self._documents[doc_id] = (text, metadata or {})
    
    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        # Simple retrieval - return most recent documents
        docs = list(self._documents.values())[-top_k:]
        return [doc[0] for doc in docs]
    
    def count(self) -> int:
        return len(self._documents)


class MemoryLayer:
    def __init__(self):
        if CHROMADB_AVAILABLE:
            self._client = chromadb.EphemeralClient(
                settings=chromadb.Settings(anonymized_telemetry=False)
            )
            self._collection = self._client.get_or_create_collection(
                name="gateway_memory",
            )
            self._simple_store = None
        else:
            self._client = None
            self._collection = None
            self._simple_store = SimpleMemoryStore()

    def store(self, text: str, doc_id: str, metadata: dict | None = None) -> None:
        if self._simple_store:
            self._simple_store.store(text, doc_id, metadata)
            return
            
        existing = self._collection.get(ids=[doc_id])
        if existing and existing["ids"]:
            self._collection.update(
                ids=[doc_id],
                documents=[text],
                metadatas=[metadata or {}],
            )
        else:
            self._collection.add(
                ids=[doc_id],
                documents=[text],
                metadatas=[metadata or {}],
            )

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        if self._simple_store:
            return self._simple_store.retrieve(query, top_k)
            
        if self._collection.count() == 0:
            return []

        n = min(top_k, self._collection.count())
        results = self._collection.query(query_texts=[query], n_results=n)

        if results and results["documents"]:
            return results["documents"][0]
        return []

    def count(self) -> int:
        if self._simple_store:
            return self._simple_store.count()
        return self._collection.count()
