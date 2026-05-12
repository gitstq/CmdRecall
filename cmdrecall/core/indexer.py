"""
Indexer for building search indices.
"""

from typing import List, Dict
from collections import Counter
import math

from ..models.command import Command
from ..storage.database import Database


class Indexer:
    """Build and maintain search indices."""
    
    def __init__(self, db: Database):
        """Initialize indexer.
        
        Args:
            db: Database instance
        """
        self.db = db
    
    def build_index(self, commands: List[Command]) -> None:
        """Build search index for commands.
        
        Args:
            commands: List of commands to index
        """
        # Clear existing index
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM search_index")
        
        # Build new index
        for cmd in commands:
            if cmd.id:
                self._index_command(cmd)
    
    def _index_command(self, command: Command) -> None:
        """Index a single command."""
        tokens = command.tokenize()
        if not tokens:
            return
        
        # Calculate term frequency
        tf = Counter(tokens)
        total = len(tokens)
        
        # Normalize TF
        for token in tf:
            tf[token] = tf[token] / total
        
        # Store in database
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            for token, weight in tf.items():
                cursor.execute("""
                    INSERT INTO search_index (command_id, token, tf)
                    VALUES (?, ?, ?)
                """, (command.id, token, weight))
    
    def update_index(self, command: Command) -> None:
        """Update index for a single command.
        
        Args:
            command: Command to update
        """
        if not command.id:
            return
        
        # Remove old index entries
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM search_index WHERE command_id = ?", (command.id,))
        
        # Add new entries
        self._index_command(command)
    
    def get_document_frequency(self) -> Dict[str, int]:
        """Get document frequency for all tokens.
        
        Returns:
            Dictionary mapping token to document frequency
        """
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT token, COUNT(DISTINCT command_id) as df
                FROM search_index
                GROUP BY token
            """)
            return {row["token"]: row["df"] for row in cursor.fetchall()}
    
    def calculate_idf(self, total_docs: int) -> Dict[str, float]:
        """Calculate IDF for all tokens.
        
        Args:
            total_docs: Total number of documents
            
        Returns:
            Dictionary mapping token to IDF value
        """
        df = self.get_document_frequency()
        
        idf = {}
        for token, doc_freq in df.items():
            # Smooth IDF
            idf[token] = math.log((total_docs + 1) / (doc_freq + 1)) + 1
        
        return idf
