"""
Template data model.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
import re


@dataclass
class Template:
    """Command template model."""
    
    name: str
    command: str
    description: Optional[str] = None
    variables: Dict[str, str] = field(default_factory=dict)  # var_name -> default_value
    tags: List[str] = field(default_factory=list)
    category: str = "other"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    usage_count: int = 0
    id: Optional[int] = None
    
    def __post_init__(self):
        """Post-initialization."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if not self.variables:
            self._extract_variables()
    
    def _extract_variables(self) -> None:
        """Extract variables from command template."""
        # Find {{var}} patterns
        matches = re.findall(r"\{\{(\w+)\}\}", self.command)
        for var in matches:
            if var not in self.variables:
                self.variables[var] = ""
    
    def render(self, values: Optional[Dict[str, str]] = None) -> str:
        """Render template with provided values.
        
        Args:
            values: Variable values to substitute
            
        Returns:
            Rendered command string
        """
        values = values or {}
        result = self.command
        
        # Merge with defaults
        final_values = {**self.variables, **values}
        
        for var_name, var_value in final_values.items():
            result = result.replace(f"{{{{{var_name}}}}}", var_value)
        
        return result
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "command": self.command,
            "description": self.description,
            "variables": self.variables,
            "tags": self.tags,
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "usage_count": self.usage_count,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Template":
        """Create from dictionary."""
        return cls(
            id=data.get("id"),
            name=data["name"],
            command=data["command"],
            description=data.get("description"),
            variables=data.get("variables", {}),
            tags=data.get("tags", []),
            category=data.get("category", "other"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            usage_count=data.get("usage_count", 0),
        )
    
    def __str__(self) -> str:
        return f"{self.name}: {self.command}"
