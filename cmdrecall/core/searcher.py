"""
Command search engine with TF-IDF and BM25 algorithms.
"""

import math
import re
from typing import List, Dict, Tuple, Optional
from collections import Counter
from datetime import datetime, timedelta

from ..models.command import Command
from ..storage.database import Database


class CommandSearcher:
    """Intelligent command search engine."""
    
    def __init__(self, db: Database):
        """Initialize searcher.
        
        Args:
            db: Database instance
        """
        self.db = db
        self._idf_cache: Dict[str, float] = {}
        self._doc_count = 0
        self._avg_doc_length = 0.0
        self._update_stats()
    
    def _update_stats(self) -> None:
        """Update search statistics."""
        commands = self.db.get_all_commands(limit=10000)
        self._doc_count = len(commands)
        
        if self._doc_count > 0:
            total_length = sum(len(cmd.tokenize()) for cmd in commands)
            self._avg_doc_length = total_length / self._doc_count
        
        # Build IDF cache
        self._build_idf_cache(commands)
    
    def _build_idf_cache(self, commands: List[Command]) -> None:
        """Build IDF cache for all tokens."""
        doc_freq: Dict[str, int] = Counter()
        
        for cmd in commands:
            tokens = set(cmd.tokenize())
            for token in tokens:
                doc_freq[token] += 1
        
        # Calculate IDF
        for token, df in doc_freq.items():
            self._idf_cache[token] = math.log((self._doc_count - df + 0.5) / (df + 0.5) + 1)
    
    def search(self, query: str, limit: int = 20) -> List[Tuple[Command, float]]:
        """Search commands with intelligent ranking.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of (command, score) tuples
        """
        # Get candidate commands
        candidates = self.db.search_commands(query, limit=limit * 3)
        
        if not candidates:
            return []
        
        # Score candidates
        scored = []
        query_tokens = self._tokenize(query)
        
        for cmd in candidates:
            score = self._calculate_score(cmd, query_tokens, query)
            scored.append((cmd, score))
        
        # Sort by score
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return scored[:limit]
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text."""
        return re.findall(r"[\w\-\.\/]+", text.lower())
    
    def _calculate_score(self, command: Command, query_tokens: List[str], original_query: str) -> float:
        """Calculate combined score for a command.
        
        Combines:
        - BM25 score
        - TF-IDF score
        - Time decay
        - Usage frequency
        - Exact match bonus
        """
        # BM25 score
        bm25_score = self._bm25_score(command, query_tokens)
        
        # TF-IDF score
        tfidf_score = self._tfidf_score(command, query_tokens)
        
        # Time decay (prefer recent commands)
        time_score = self._time_decay_score(command)
        
        # Frequency score (prefer frequently used)
        freq_score = self._frequency_score(command)
        
        # Exact match bonus
        exact_bonus = self._exact_match_bonus(command, original_query)
        
        # Combine scores with weights
        total_score = (
            bm25_score * 0.3 +
            tfidf_score * 0.2 +
            time_score * 0.2 +
            freq_score * 0.2 +
            exact_bonus * 0.1
        )
        
        return total_score
    
    def _bm25_score(self, command: Command, query_tokens: List[str], k1: float = 1.5, b: float = 0.75) -> float:
        """Calculate BM25 score.
        
        BM25 formula:
        score(D, Q) = Σ IDF(qi) * (f(qi, D) * (k1 + 1)) / (f(qi, D) + k1 * (1 - b + b * |D| / avgdl))
        """
        cmd_tokens = command.tokenize()
        doc_length = len(cmd_tokens)
        
        if doc_length == 0 or self._avg_doc_length == 0:
            return 0.0
        
        score = 0.0
        token_freq = Counter(cmd_tokens)
        
        for token in query_tokens:
            if token not in token_freq:
                continue
            
            tf = token_freq[token]
            idf = self._idf_cache.get(token, 0.0)
            
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * doc_length / self._avg_doc_length)
            
            score += idf * numerator / denominator
        
        return score
    
    def _tfidf_score(self, command: Command, query_tokens: List[str]) -> float:
        """Calculate TF-IDF score."""
        cmd_tokens = command.tokenize()
        
        if not cmd_tokens:
            return 0.0
        
        token_freq = Counter(cmd_tokens)
        total = len(cmd_tokens)
        
        score = 0.0
        for token in query_tokens:
            if token in token_freq:
                tf = token_freq[token] / total
                idf = self._idf_cache.get(token, 1.0)
                score += tf * idf
        
        return score
    
    def _time_decay_score(self, command: Command, half_life_days: int = 30) -> float:
        """Calculate time decay score.
        
        Uses exponential decay: score = exp(-λ * age)
        where λ = ln(2) / half_life
        """
        if not command.timestamp:
            return 0.5
        
        age = datetime.now() - command.timestamp
        age_days = age.total_seconds() / 86400
        
        # Exponential decay
        decay_rate = math.log(2) / half_life_days
        score = math.exp(-decay_rate * age_days)
        
        return max(0.0, min(1.0, score))
    
    def _frequency_score(self, command: Command) -> float:
        """Calculate frequency score.
        
        Normalizes count using log scale.
        """
        if command.count <= 0:
            return 0.0
        
        # Log scale normalization
        score = math.log(command.count + 1) / math.log(100)  # Normalize to ~1 for count=100
        
        return min(1.0, score)
    
    def _exact_match_bonus(self, command: Command, query: str) -> float:
        """Calculate exact match bonus."""
        cmd_lower = command.command.lower()
        query_lower = query.lower()
        
        if cmd_lower == query_lower:
            return 1.0
        elif cmd_lower.startswith(query_lower):
            return 0.8
        elif query_lower in cmd_lower:
            return 0.5
        else:
            return 0.0
    
    def fuzzy_search(self, query: str, limit: int = 20) -> List[Tuple[Command, float]]:
        """Fuzzy search with character-level matching.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of (command, score) tuples
        """
        commands = self.db.get_all_commands(limit=1000)
        
        scored = []
        for cmd in commands:
            score = self._fuzzy_match_score(cmd.command, query)
            if score > 0:
                # Combine with other factors
                time_score = self._time_decay_score(cmd)
                freq_score = self._frequency_score(cmd)
                combined = score * 0.6 + time_score * 0.2 + freq_score * 0.2
                scored.append((cmd, combined))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:limit]
    
    def _fuzzy_match_score(self, text: str, query: str) -> float:
        """Calculate fuzzy match score.
        
        Uses a simple algorithm that rewards:
        - Consecutive character matches
        - Matches at word boundaries
        - Matches at string start
        """
        text_lower = text.lower()
        query_lower = query.lower()
        
        if not query_lower:
            return 0.0
        
        # Exact substring match
        if query_lower in text_lower:
            return 1.0
        
        # Character-by-character matching
        score = 0.0
        text_idx = 0
        consecutive = 0
        
        for q_char in query_lower:
            found = False
            while text_idx < len(text_lower):
                if text_lower[text_idx] == q_char:
                    found = True
                    consecutive += 1
                    score += 1.0 + (consecutive * 0.1)  # Bonus for consecutive matches
                    
                    # Bonus for word boundary
                    if text_idx == 0 or text_lower[text_idx - 1] in " \t/-_":
                        score += 0.5
                    
                    text_idx += 1
                    break
                else:
                    consecutive = 0
                    text_idx += 1
            
            if not found:
                return 0.0
        
        # Normalize score
        max_score = len(query_lower) * 1.5
        return min(1.0, score / max_score)
    
    def suggest(self, partial: str, limit: int = 10) -> List[Command]:
        """Suggest commands based on partial input.
        
        Args:
            partial: Partial command input
            limit: Maximum suggestions
            
        Returns:
            List of suggested commands
        """
        commands = self.db.get_all_commands(limit=500)
        
        suggestions = []
        for cmd in commands:
            if cmd.command.startswith(partial):
                suggestions.append(cmd)
        
        # Sort by frequency
        suggestions.sort(key=lambda x: x.count, reverse=True)
        
        return suggestions[:limit]
