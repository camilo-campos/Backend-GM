"""
Mini RAG Engine usando TF-IDF para buscar chunks relevantes.
Rapido (~1ms), sin dependencias externas, suficiente para ~70 chunks.
"""

import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .knowledge_base import CHUNKS

logger = logging.getLogger(__name__)


class RAGEngine:
    """Motor de busqueda por similitud TF-IDF sobre chunks de conocimiento."""

    def __init__(self):
        self._vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents='unicode',
            ngram_range=(1, 2),  # unigramas y bigramas
            max_features=5000,
        )
        self._matrix = self._vectorizer.fit_transform(CHUNKS)
        logger.info(f"[RAG] Indexados {len(CHUNKS)} chunks ({self._matrix.shape[1]} features)")

    def buscar(self, query: str, top_k: int = 5, threshold: float = 0.05) -> list[str]:
        """
        Busca los chunks mas relevantes para una query.

        Args:
            query: Pregunta del usuario
            top_k: Cantidad maxima de chunks a retornar
            threshold: Similitud minima para incluir un chunk

        Returns:
            Lista de chunks relevantes ordenados por similitud
        """
        query_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._matrix).flatten()

        # Obtener indices ordenados por score descendente
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

        resultados = []
        for idx, score in ranked[:top_k]:
            if score >= threshold:
                resultados.append(CHUNKS[idx])
                logger.debug(f"[RAG] Score {score:.3f}: {CHUNKS[idx][:80]}...")

        logger.info(f"[RAG] Query: '{query[:50]}...' -> {len(resultados)} chunks (top score: {ranked[0][1]:.3f})")
        return resultados


# Instancia global (se crea una sola vez al importar)
rag = RAGEngine()
