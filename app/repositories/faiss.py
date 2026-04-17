from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass

import faiss
import numpy as np

from app.core.config import settings


@dataclass(frozen=True)
class FaissHit:
    chunk_id: uuid.UUID
    score: float


class FaissRepository:
    """
    V1 design: store a per-document FAISS index on disk.
    We also store an ordered list of chunk_ids aligned with FAISS vector ids.
    """

    def _doc_dir(self, document_id: uuid.UUID) -> str:
        return os.path.join(settings.data_dir, "faiss", str(document_id))

    def _index_path(self, document_id: uuid.UUID) -> str:
        return os.path.join(self._doc_dir(document_id), "index.faiss")

    def _meta_path(self, document_id: uuid.UUID) -> str:
        return os.path.join(self._doc_dir(document_id), "meta.json")

    def save_index(self, *, document_id: uuid.UUID, vectors: list[list[float]], chunk_ids: list[uuid.UUID]) -> None:
        if len(vectors) != len(chunk_ids):
            raise ValueError("vectors and chunk_ids length mismatch")
        if not vectors:
            raise ValueError("No vectors to index")

        dim = len(vectors[0])
        mat = np.asarray(vectors, dtype="float32")
        if mat.ndim != 2 or mat.shape[1] != dim:
            raise ValueError("Invalid vector matrix shape")

        # Cosine similarity via normalized inner product.
        faiss.normalize_L2(mat)
        index = faiss.IndexFlatIP(dim)
        index.add(mat)

        os.makedirs(self._doc_dir(document_id), exist_ok=True)
        faiss.write_index(index, self._index_path(document_id))
        with open(self._meta_path(document_id), "w", encoding="utf-8") as f:
            json.dump({"chunk_ids": [str(cid) for cid in chunk_ids], "dim": dim}, f)

    def search(self, *, document_id: uuid.UUID, query_vector: list[float], top_n: int = 20) -> list[FaissHit]:
        index_path = self._index_path(document_id)
        meta_path = self._meta_path(document_id)
        if not os.path.exists(index_path) or not os.path.exists(meta_path):
            return []

        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        chunk_ids = [uuid.UUID(x) for x in meta["chunk_ids"]]

        index = faiss.read_index(index_path)

        q = np.asarray([query_vector], dtype="float32")
        faiss.normalize_L2(q)
        scores, ids = index.search(q, top_n)

        hits: list[FaissHit] = []
        for score, idx in zip(scores[0].tolist(), ids[0].tolist(), strict=False):
            if idx < 0:
                continue
            if idx >= len(chunk_ids):
                continue
            hits.append(FaissHit(chunk_id=chunk_ids[idx], score=float(score)))
        return hits

