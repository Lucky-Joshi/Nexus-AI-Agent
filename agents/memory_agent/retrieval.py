"""
Retrieval pipeline for NEXUS Memory Agent.
Multi-stage retrieval: keyword matching → importance scoring → recency boost → ranking.
"""

import re
import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from core.logger import Logger


class RetrievalPipeline:
    """
    Multi-stage retrieval pipeline for memory entries.
    Stages:
    1. Candidate generation (keyword/semantic search)
    2. Relevance scoring (TF-IDF-like keyword matching)
    3. Importance weighting (stored importance + access frequency)
    4. Recency boost (temporal decay)
    5. Final ranking and deduplication
    """

    def __init__(self):
        self.logger = Logger().get_logger("RetrievalPipeline")
        self._stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "shall", "can", "need", "must", "of", "in",
            "to", "for", "with", "on", "at", "from", "by", "about", "as", "into",
            "through", "during", "before", "after", "above", "below", "between",
            "and", "but", "or", "nor", "not", "so", "yet", "both", "either",
            "neither", "each", "every", "all", "any", "few", "more", "most",
            "other", "some", "such", "no", "only", "own", "same", "than", "too",
            "very", "just", "because", "if", "when", "where", "which", "while",
            "who", "whom", "what", "how", "this", "that", "these", "those", "it",
            "its", "i", "me", "my", "myself", "we", "our", "ours", "you", "your",
            "he", "him", "his", "she", "her", "they", "them", "their", "there",
        }

    def retrieve(self, query: str, candidates: List[Dict], top_k: int = 10,
                 type_filter: str = None, category_filter: str = None) -> List[Dict]:
        """
        Full retrieval pipeline.
        candidates: list of memory dicts from storage
        Returns: ranked list with scores
        """
        if not candidates:
            return []

        filtered = candidates
        if type_filter:
            filtered = [c for c in filtered if c.get("memory_type") == type_filter]
        if category_filter:
            filtered = [c for c in filtered if c.get("category") == category_filter]

        if not filtered:
            return []

        scored = []
        for candidate in filtered:
            relevance = self._compute_relevance(query, candidate)
            importance = self._compute_importance(candidate)
            recency = self._compute_recency(candidate)
            access_boost = self._compute_access_boost(candidate)

            final_score = (
                0.45 * relevance +
                0.25 * importance +
                0.20 * recency +
                0.10 * access_boost
            )

            scored.append({
                **candidate,
                "retrieval_score": round(final_score, 4),
                "relevance": round(relevance, 4),
                "importance_weight": round(importance, 4),
                "recency_weight": round(recency, 4),
            })

        scored.sort(key=lambda x: x["retrieval_score"], reverse=True)
        return scored[:top_k]

    def _compute_relevance(self, query: str, candidate: Dict) -> float:
        """Compute relevance score using keyword overlap and field matching."""
        query_words = self._tokenize(query)
        if not query_words:
            return 0.0

        content = candidate.get("content", "")
        tags = candidate.get("tags", [])
        metadata = candidate.get("metadata", {})

        content_words = self._tokenize(content)
        all_words = set(content_words)
        if tags:
            all_words.update(self._tokenize(" ".join(tags)))
        if metadata:
            meta_text = " ".join(str(v) for v in metadata.values())
            all_words.update(self._tokenize(meta_text))

        if not all_words:
            return 0.0

        matches = query_words & all_words
        base_score = len(matches) / len(query_words)

        exact_bonus = 0.0
        if query.lower() in content.lower():
            exact_bonus = 0.3
        elif any(q.lower() in content.lower() for q in query_words if len(q) > 3):
            exact_bonus = 0.15

        tag_bonus = 0.0
        if tags:
            tag_matches = sum(1 for q in query_words if q in [t.lower() for t in tags])
            tag_bonus = 0.2 * (tag_matches / len(query_words)) if query_words else 0

        return min(1.0, base_score + exact_bonus + tag_bonus)

    def _compute_importance(self, candidate: Dict) -> float:
        """Get stored importance score, normalized to [0, 1]."""
        importance = candidate.get("importance", 0.5)
        return max(0.0, min(1.0, importance))

    def _compute_recency(self, candidate: Dict) -> float:
        """Compute recency score using exponential decay."""
        updated_at = candidate.get("updated_at", candidate.get("created_at", ""))
        if not updated_at:
            return 0.5

        try:
            dt = datetime.fromisoformat(updated_at)
            age_hours = (datetime.now() - dt).total_seconds() / 3600
            half_life = 168
            return math.exp(-0.693 * age_hours / half_life)
        except (ValueError, TypeError):
            return 0.5

    def _compute_access_boost(self, candidate: Dict) -> float:
        """Boost score based on access frequency."""
        access_count = candidate.get("access_count", 0)
        if access_count == 0:
            return 0.0
        return min(1.0, math.log1p(access_count) / math.log1p(50))

    def _tokenize(self, text: str) -> set:
        """Tokenize text into meaningful words."""
        words = re.findall(r"\b[a-z]{2,}\b", text.lower())
        return set(w for w in words if w not in self._stop_words)

    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract top keywords from text."""
        words = self._tokenize(text)
        word_freq = {}
        for word in re.findall(r"\b[a-z]{2,}\b", text.lower()):
            if word not in self._stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1

        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in sorted_words[:max_keywords]]

    def compute_importance_score(self, content: str, is_user_stated: bool = False,
                                  has_action: bool = False, entity_count: int = 0) -> float:
        """
        Compute importance score for new memory.
        Factors: user explicit statement, actionability, entity richness, length.
        """
        score = 0.3

        if is_user_stated:
            score += 0.2

        if has_action:
            score += 0.15

        words = self._tokenize(content)
        if len(words) > 10:
            score += 0.1
        if entity_count > 2:
            score += 0.15
        if entity_count > 5:
            score += 0.1

        return min(1.0, score)
