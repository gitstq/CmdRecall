"""
SQLite database storage layer.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from ..models.command import Command, CommandCategory, RiskLevel
from ..models.template import Template


class Database:
    """SQLite database manager for CmdRecall."""
    
    SCHEMA_VERSION = 1
    
    def __init__(self, db_path: Path):
        """Initialize database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_tables()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _ensure_tables(self) -> None:
        """Create tables if not exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Commands table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL UNIQUE,
                    command_hash TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    count INTEGER DEFAULT 1,
                    category TEXT DEFAULT 'other',
                    risk_level TEXT DEFAULT 'safe',
                    tags TEXT DEFAULT '[]',
                    notes TEXT,
                    is_template INTEGER DEFAULT 0,
                    template_vars TEXT DEFAULT '[]',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_commands_hash 
                ON commands(command_hash)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_commands_category 
                ON commands(category)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_commands_timestamp 
                ON commands(timestamp)
            """)
            
            # Templates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    command TEXT NOT NULL,
                    description TEXT,
                    variables TEXT DEFAULT '{}',
                    tags TEXT DEFAULT '[]',
                    category TEXT DEFAULT 'other',
                    usage_count INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Search index table (for TF-IDF)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_id INTEGER NOT NULL,
                    token TEXT NOT NULL,
                    tf REAL DEFAULT 0,
                    FOREIGN KEY (command_id) REFERENCES commands(id) ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_search_token 
                ON search_index(token)
            """)
            
            # Metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            
            # Set schema version
            cursor.execute("""
                INSERT OR REPLACE INTO metadata (key, value) 
                VALUES ('schema_version', ?)
            """, (str(self.SCHEMA_VERSION),))
    
    # ==================== Command Operations ====================
    
    def add_command(self, command: Command) -> int:
        """Add or update a command.
        
        Args:
            command: Command object to add
            
        Returns:
            Command ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if command exists
            cursor.execute(
                "SELECT id, count FROM commands WHERE command_hash = ?",
                (command.get_hash(),)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update count and timestamp
                cursor.execute("""
                    UPDATE commands 
                    SET count = ?, timestamp = ?, updated_at = ?
                    WHERE id = ?
                """, (existing["count"] + 1, command.timestamp.isoformat(), 
                      datetime.now().isoformat(), existing["id"]))
                return existing["id"]
            
            # Insert new command
            cursor.execute("""
                INSERT INTO commands 
                (command, command_hash, timestamp, count, category, risk_level, 
                 tags, notes, is_template, template_vars)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                command.command,
                command.get_hash(),
                command.timestamp.isoformat(),
                command.count,
                command.category.value,
                command.risk_level.value,
                json.dumps(command.tags),
                command.notes,
                1 if command.is_template else 0,
                json.dumps(command.template_vars),
            ))
            
            command_id = cursor.lastrowid
            
            # Build search index
            self._index_command(cursor, command_id, command)
            
            return command_id
    
    def _index_command(self, cursor, command_id: int, command: Command) -> None:
        """Build search index for a command."""
        tokens = command.tokenize()
        if not tokens:
            return
        
        # Calculate term frequency
        tf = {}
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1
        
        # Normalize TF
        total = len(tokens)
        for token, count in tf.items():
            tf[token] = count / total
        
        # Insert into search index
        for token, weight in tf.items():
            cursor.execute("""
                INSERT INTO search_index (command_id, token, tf)
                VALUES (?, ?, ?)
            """, (command_id, token, weight))
    
    def get_command(self, command_id: int) -> Optional[Command]:
        """Get command by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM commands WHERE id = ?", (command_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_command(row)
        return None
    
    def get_all_commands(self, limit: int = 1000) -> List[Command]:
        """Get all commands."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM commands ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            return [self._row_to_command(row) for row in cursor.fetchall()]
    
    def search_commands(self, query: str, limit: int = 50) -> List[Command]:
        """Search commands by query."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Simple LIKE search
            cursor.execute("""
                SELECT * FROM commands 
                WHERE command LIKE ?
                ORDER BY count DESC, timestamp DESC
                LIMIT ?
            """, (f"%{query}%", limit))
            
            return [self._row_to_command(row) for row in cursor.fetchall()]
    
    def get_commands_by_category(self, category: CommandCategory) -> List[Command]:
        """Get commands by category."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM commands WHERE category = ? ORDER BY count DESC",
                (category.value,)
            )
            return [self._row_to_command(row) for row in cursor.fetchall()]
    
    def get_top_commands(self, limit: int = 20) -> List[Command]:
        """Get most used commands."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM commands ORDER BY count DESC LIMIT ?",
                (limit,)
            )
            return [self._row_to_command(row) for row in cursor.fetchall()]
    
    def delete_command(self, command_id: int) -> bool:
        """Delete a command."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM commands WHERE id = ?", (command_id,))
            return cursor.rowcount > 0
    
    def clear_commands(self) -> int:
        """Clear all commands."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM search_index")
            cursor.execute("DELETE FROM commands")
            return cursor.rowcount
    
    def _row_to_command(self, row: sqlite3.Row) -> Command:
        """Convert database row to Command object."""
        return Command(
            id=row["id"],
            command=row["command"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            count=row["count"],
            category=CommandCategory(row["category"]),
            risk_level=RiskLevel(row["risk_level"]),
            tags=json.loads(row["tags"]) if row["tags"] else [],
            notes=row["notes"],
            is_template=bool(row["is_template"]),
            template_vars=json.loads(row["template_vars"]) if row["template_vars"] else [],
        )
    
    # ==================== Template Operations ====================
    
    def add_template(self, template: Template) -> int:
        """Add or update a template."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO templates 
                (name, command, description, variables, tags, category)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    command = excluded.command,
                    description = excluded.description,
                    variables = excluded.variables,
                    tags = excluded.tags,
                    category = excluded.category,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                template.name,
                template.command,
                template.description,
                json.dumps(template.variables),
                json.dumps(template.tags),
                template.category,
            ))
            
            return cursor.lastrowid
    
    def get_template(self, template_id: int) -> Optional[Template]:
        """Get template by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM templates WHERE id = ?", (template_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_template(row)
        return None
    
    def get_template_by_name(self, name: str) -> Optional[Template]:
        """Get template by name."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM templates WHERE name = ?", (name,))
            row = cursor.fetchone()
            if row:
                return self._row_to_template(row)
        return None
    
    def get_all_templates(self) -> List[Template]:
        """Get all templates."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM templates ORDER BY usage_count DESC")
            return [self._row_to_template(row) for row in cursor.fetchall()]
    
    def increment_template_usage(self, template_id: int) -> None:
        """Increment template usage count."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE templates SET usage_count = usage_count + 1 WHERE id = ?",
                (template_id,)
            )
    
    def delete_template(self, template_id: int) -> bool:
        """Delete a template."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM templates WHERE id = ?", (template_id,))
            return cursor.rowcount > 0
    
    def _row_to_template(self, row: sqlite3.Row) -> Template:
        """Convert database row to Template object."""
        return Template(
            id=row["id"],
            name=row["name"],
            command=row["command"],
            description=row["description"],
            variables=json.loads(row["variables"]) if row["variables"] else {},
            tags=json.loads(row["tags"]) if row["tags"] else [],
            category=row["category"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
            usage_count=row["usage_count"],
        )
    
    # ==================== Statistics ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total commands
            cursor.execute("SELECT COUNT(*) FROM commands")
            total_commands = cursor.fetchone()[0]
            
            # Total templates
            cursor.execute("SELECT COUNT(*) FROM templates")
            total_templates = cursor.fetchone()[0]
            
            # Commands by category
            cursor.execute("""
                SELECT category, COUNT(*) as count 
                FROM commands 
                GROUP BY category 
                ORDER BY count DESC
            """)
            by_category = {row["category"]: row["count"] for row in cursor.fetchall()}
            
            # Commands by risk level
            cursor.execute("""
                SELECT risk_level, COUNT(*) as count 
                FROM commands 
                GROUP BY risk_level 
                ORDER BY count DESC
            """)
            by_risk = {row["risk_level"]: row["count"] for row in cursor.fetchall()}
            
            # Unique tokens
            cursor.execute("SELECT COUNT(DISTINCT token) FROM search_index")
            unique_tokens = cursor.fetchone()[0]
            
            return {
                "total_commands": total_commands,
                "total_templates": total_templates,
                "by_category": by_category,
                "by_risk": by_risk,
                "unique_tokens": unique_tokens,
            }
