import logging
from typing import List

import chromadb

logger = logging.getLogger(__name__)


class MemoryLayer:
    def __init__(self):
        self._client = chromadb.EphemeralClient(
            settings=chromadb.Settings(anonymized_telemetry=False)
        )
        self._collection = self._client.get_or_create_collection(
            name="gateway_memory",
        )

    def store(self, text: str, doc_id: str, metadata: dict | None = None) -> None:
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
        if self._collection.count() == 0:
            return []

        n = min(top_k, self._collection.count())
        results = self._collection.query(query_texts=[query], n_results=n)

        if results and results["documents"]:
            return results["documents"][0]
        return []

    def count(self) -> int:
        return self._collection.count()
