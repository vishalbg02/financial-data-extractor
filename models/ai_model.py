import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


class AIExtractor:
    """AI-powered extraction using semantic similarity"""

    def __init__(self):
        try:
            # Use sentence transformers for semantic matching
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.use_transformer = True
            logger.info("Loaded transformer model successfully")
        except Exception as e:
            logger.warning(f"Could not load transformer model: {e}. Using TF-IDF fallback.")
            self.vectorizer = TfidfVectorizer()
            self.use_transformer = False

    def find_best_match(self,
                       query: str,
                       candidates: List[str],
                       threshold: float = 0.75) -> Optional[Tuple[str, float]]:
        """Find the best matching candidate for a query"""

        if not candidates:
            return None

        if self.use_transformer:
            return self._match_with_transformer(query, candidates, threshold)
        else:
            return self._match_with_tfidf(query, candidates, threshold)

    def _match_with_transformer(self,
                               query: str,
                               candidates: List[str],
                               threshold: float) -> Optional[Tuple[str, float]]:
        """Match using sentence transformers (semantic)"""
        try:
            # Encode query and candidates
            query_embedding = self.model.encode([query])
            candidate_embeddings = self.model.encode(candidates)

            # Calculate cosine similarities
            similarities = cosine_similarity(query_embedding, candidate_embeddings)[0]

            # Find best match
            best_idx = np.argmax(similarities)
            best_score = similarities[best_idx]

            if best_score >= threshold:
                return candidates[best_idx], float(best_score)

            return None

        except Exception as e:
            logger.error(f"Transformer matching failed: {e}")
            return None

    def _match_with_tfidf(self,
                         query: str,
                         candidates: List[str],
                         threshold: float) -> Optional[Tuple[str, float]]:
        """Match using TF-IDF (keyword-based)"""
        try:
            # Fit vectorizer on candidates + query
            all_texts = [query] + candidates
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)

            # Calculate similarities
            query_vec = tfidf_matrix[0:1]
            candidate_vecs = tfidf_matrix[1:]

            similarities = cosine_similarity(query_vec, candidate_vecs)[0]

            # Find best match
            best_idx = np.argmax(similarities)
            best_score = similarities[best_idx]

            if best_score >= threshold:
                return candidates[best_idx], float(best_score)

            return None

        except Exception as e:
            logger.error(f"TF-IDF matching failed: {e}")
            return None

    def extract_numbers_with_context(self, text: str) -> List[Tuple[float, str]]:
        """Extract numbers along with their context"""
        import re

        results = []

        # Pattern to find numbers with context
        pattern = r'([\w\s]{0,30})([\d,]+\.?\d*)\s*([KMB]?)([\w\s]{0,30})'

        matches = re.finditer(pattern, text)

        for match in matches:
            try:
                before_context = match.group(1).strip()
                number_str = match.group(2).replace(',', '')
                multiplier = match.group(3)
                after_context = match.group(4).strip()

                number = float(number_str)

                # Apply multiplier
                if multiplier:
                    multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
                    number *= multipliers.get(multiplier, 1)

                context = f"{before_context} {after_context}".strip()
                results.append((number, context))

            except (ValueError, AttributeError):
                continue

        return results
