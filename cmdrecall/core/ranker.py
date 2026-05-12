"""
Command ranking algorithms.
"""

import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import Counter

from ..models.command import Command, CommandCategory


class CommandRanker:
    """Rank and score commands."""
    
    def __init__(self):
        """Initialize ranker."""
        self.category_weights = {
            CommandCategory.GIT: 1.2,
            CommandCategory.DOCKER: 1.1,
            CommandCategory.KUBERNETES: 1.1,
            CommandCategory.NPM: 1.0,
            CommandCategory.PIP: 1.0,
            CommandCategory.PYTHON: 1.0,
            CommandCategory.NODE: 1.0,
            CommandCategory.SYSTEM: 0.8,
            CommandCategory.NETWORK: 0.9,
            CommandCategory.DATABASE: 1.0,
            CommandCategory.FILE: 0.7,
            CommandCategory.TEXT: 0.8,
            CommandCategory.BUILD: 1.0,
            CommandCategory.TEST: 1.0,
            CommandCategory.CLOUD: 1.1,
            CommandCategory.SSH: 1.0,
            CommandCategory.GITFLOW: 1.1,
            CommandCategory.OTHER: 0.9,
        }
    
    def rank_by_relevance(self, commands: List[Command], query: str) -> List[Tuple[Command, float]]:
        """Rank commands by relevance to query.
        
        Args:
            commands: List of commands to rank
            query: Search query
            
        Returns:
            List of (command, score) tuples sorted by score
        """
        scored = []
        query_lower = query.lower()
        query_tokens = set(query_lower.split())
        
        for cmd in commands:
            score = self._calculate_relevance(cmd, query_lower, query_tokens)
            scored.append((cmd, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
    
    def _calculate_relevance(self, command: Command, query: str, query_tokens: set) -> float:
        """Calculate relevance score."""
        cmd_lower = command.command.lower()
        cmd_tokens = set(cmd_lower.split())
        
        # Token overlap
        overlap = len(query_tokens & cmd_tokens)
        overlap_score = overlap / max(len(query_tokens), 1)
        
        # Substring match
        substring_score = 1.0 if query in cmd_lower else 0.0
        
        # Prefix match
        prefix_score = 1.0 if cmd_lower.startswith(query) else 0.0
        
        # Category weight
        category_score = self.category_weights.get(command.category, 1.0)
        
        # Combine scores
        total = (
            overlap_score * 0.3 +
            substring_score * 0.3 +
            prefix_score * 0.2 +
            (category_score - 1.0) * 0.2
        )
        
        return total
    
    def rank_by_frequency(self, commands: List[Command]) -> List[Tuple[Command, int]]:
        """Rank commands by usage frequency.
        
        Args:
            commands: List of commands to rank
            
        Returns:
            List of (command, count) tuples sorted by count
        """
        scored = [(cmd, cmd.count) for cmd in commands]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
    
    def rank_by_recency(self, commands: List[Command]) -> List[Tuple[Command, float]]:
        """Rank commands by recency.
        
        Args:
            commands: List of commands to rank
            
        Returns:
            List of (command, recency_score) tuples
        """
        now = datetime.now()
        scored = []
        
        for cmd in commands:
            if cmd.timestamp:
                age = now - cmd.timestamp
                age_hours = age.total_seconds() / 3600
                # Exponential decay with 24-hour half-life
                score = math.exp(-math.log(2) * age_hours / 24)
            else:
                score = 0.0
            
            scored.append((cmd, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
    
    def rank_combined(self, commands: List[Command], 
                      freq_weight: float = 0.4,
                      recency_weight: float = 0.3,
                      relevance_weight: float = 0.3,
                      query: str = "") -> List[Tuple[Command, float]]:
        """Rank commands using combined scoring.
        
        Args:
            commands: List of commands to rank
            freq_weight: Weight for frequency score
            recency_weight: Weight for recency score
            relevance_weight: Weight for relevance score
            query: Optional search query for relevance
            
        Returns:
            List of (command, combined_score) tuples
        """
        if not commands:
            return []
        
        # Normalize weights
        total_weight = freq_weight + recency_weight + relevance_weight
        freq_weight /= total_weight
        recency_weight /= total_weight
        relevance_weight /= total_weight
        
        # Calculate max values for normalization
        max_count = max(cmd.count for cmd in commands) if commands else 1
        
        scored = []
        now = datetime.now()
        query_lower = query.lower() if query else ""
        
        for cmd in commands:
            # Frequency score (normalized)
            freq_score = math.log(cmd.count + 1) / math.log(max_count + 1) if max_count > 0 else 0
            
            # Recency score
            if cmd.timestamp:
                age_hours = (now - cmd.timestamp).total_seconds() / 3600
                recency_score = math.exp(-math.log(2) * age_hours / 168)  # 1 week half-life
            else:
                recency_score = 0
            
            # Relevance score
            if query:
                relevance_score = 1.0 if query_lower in cmd.command.lower() else 0.5
            else:
                relevance_score = 0.5
            
            # Combined score
            combined = (
                freq_score * freq_weight +
                recency_score * recency_weight +
                relevance_score * relevance_weight
            )
            
            scored.append((cmd, combined))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
    
    def get_hot_commands(self, commands: List[Command], days: int = 7) -> List[Command]:
        """Get "hot" commands - frequently used recently.
        
        Args:
            commands: List of commands
            days: Number of days to consider
            
        Returns:
            List of hot commands
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        recent = [cmd for cmd in commands if cmd.timestamp and cmd.timestamp >= cutoff]
        
        # Sort by count
        recent.sort(key=lambda x: x.count, reverse=True)
        
        return recent
    
    def get_rising_commands(self, commands: List[Command]) -> List[Command]:
        """Get rising commands - increased usage recently.
        
        Args:
            commands: List of commands
            
        Returns:
            List of rising commands
        """
        now = datetime.now()
        recent_cutoff = now - timedelta(days=7)
        older_cutoff = now - timedelta(days=14)
        
        rising = []
        
        for cmd in commands:
            # This is simplified - in real implementation, we'd track per-day usage
            if cmd.timestamp and cmd.timestamp >= recent_cutoff:
                rising.append(cmd)
        
        return rising
    
    def categorize_commands(self, commands: List[Command]) -> Dict[CommandCategory, List[Command]]:
        """Group commands by category.
        
        Args:
            commands: List of commands
            
        Returns:
            Dictionary mapping category to commands
        """
        categorized: Dict[CommandCategory, List[Command]] = {}
        
        for cmd in commands:
            if cmd.category not in categorized:
                categorized[cmd.category] = []
            categorized[cmd.category].append(cmd)
        
        return categorized
    
    def get_statistics(self, commands: List[Command]) -> Dict:
        """Get command statistics.
        
        Args:
            commands: List of commands
            
        Returns:
            Statistics dictionary
        """
        if not commands:
            return {
                "total": 0,
                "unique": 0,
                "avg_length": 0,
                "top_category": None,
                "top_command": None,
            }
        
        total_count = sum(cmd.count for cmd in commands)
        avg_length = sum(len(cmd.command) for cmd in commands) / len(commands)
        
        # Top category
        category_counts = Counter(cmd.category for cmd in commands)
        top_category = category_counts.most_common(1)[0][0] if category_counts else None
        
        # Top command
        top_command = max(commands, key=lambda x: x.count)
        
        return {
            "total": total_count,
            "unique": len(commands),
            "avg_length": avg_length,
            "top_category": top_category.value if top_category else None,
            "top_command": top_command.command,
            "by_category": {cat.value: count for cat, count in category_counts.items()},
        }
