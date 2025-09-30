import time
from typing import List, Dict, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import KnowledgeBaseEntry


class SimpleVectorIndex:
    """A lightweight in-memory vector index using TF-IDF as a placeholder for a production vector DB.

    This is suitable for development and unit tests. For production, replace with a managed
    vector database (e.g., pgvector, Pinecone, Weaviate) and persist embeddings.
    """
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = None
        self.ids: List[int] = []

    def build(self, corpus: List[str], ids: List[int]):
        if not corpus:
            self.matrix = None
            self.ids = []
            return
        self.matrix = self.vectorizer.fit_transform(corpus)
        self.ids = ids

    def search(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        if self.matrix is None or not self.ids:
            return []
        q_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self.matrix).flatten()
        idxs = np.argsort(sims)[::-1][:top_k]
        return [(self.ids[i], float(sims[i])) for i in idxs]


class RAGService:
    """RAG pipeline: retrieve relevant KB entries and generate/compose an answer.

    ENV configuration (to be set by deployment via .env):
    - VECTOR_BACKEND (optional): to switch vector store provider in the future.
    - GENERATION_MODEL (optional): to select LLM provider in the future.
    """
    def __init__(self):
        self.index = SimpleVectorIndex()
        self._load_index()

    def _load_index(self):
        entries = KnowledgeBaseEntry.objects.filter(is_active=True)
        corpus = [f"{e.title}\n{e.question}\n{e.answer}" for e in entries]
        ids = [e.id for e in entries]
        self.index.build(corpus, ids)

    def refresh_index(self):
        self._load_index()

    def retrieve(self, question: str, k: int = 5) -> List[KnowledgeBaseEntry]:
        results = self.index.search(question, top_k=k)
        id_order = [rid for rid, _ in results]
        entries = {e.id: e for e in KnowledgeBaseEntry.objects.filter(id__in=id_order)}
        ordered = [entries[i] for i in id_order if i in entries]
        return ordered

    def generate(self, question: str, contexts: List[KnowledgeBaseEntry]) -> str:
        """Compose an answer from contexts. Placeholder for LLM call."""
        # In production, call an LLM with system prompt and context.
        # Here we return a concise composed answer using top snippets.
        snippets = []
        for e in contexts[:3]:
            snippet = e.answer.strip()
            if len(snippet) > 400:
                snippet = snippet[:400] + "..."
            snippets.append(f"- {snippet}")
        if not snippets:
            return "I don't have an exact answer in the knowledge base. Please provide more details."
        return (
            "Here is what I found related to your question:\n"
            + "\n".join(snippets)
            + "\n\nIf this doesn't fully answer your question, please rephrase or ask a follow-up."
        )

    def ask(self, question: str) -> Tuple[str, List[Dict], int]:
        """Run retrieval and generation, returning (answer, contexts_json, latency_ms)."""
        t0 = time.time()
        contexts = self.retrieve(question, k=5)
        answer = self.generate(question, contexts)
        latency_ms = int((time.time() - t0) * 1000)
        contexts_json = [{
            "id": e.id,
            "title": e.title,
            "question": e.question,
            "answer": e.answer,
            "tags": e.tags,
            "source": e.source,
        } for e in contexts]
        return answer, contexts_json, latency_ms


# Single instance for process lifetime; in ASGI with multiple workers each gets its own.
rag_service = RAGService()
