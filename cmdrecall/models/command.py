"""
Command data model.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum
import re
import hashlib


class CommandCategory(Enum):
    """Command category enumeration."""
    GIT = "git"
    DOCKER = "docker"
    KUBERNETES = "kubectl"
    NPM = "npm"
    PIP = "pip"
    PYTHON = "python"
    NODE = "node"
    SYSTEM = "system"
    NETWORK = "network"
    DATABASE = "database"
    FILE = "file"
    TEXT = "text"
    BUILD = "build"
    TEST = "test"
    CLOUD = "cloud"
    SSH = "ssh"
    GITFLOW = "gitflow"
    OTHER = "other"


class RiskLevel(Enum):
    """Command risk level."""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Command:
    """Command data model."""
    
    command: str
    timestamp: Optional[datetime] = None
    count: int = 1
    category: CommandCategory = CommandCategory.OTHER
    risk_level: RiskLevel = RiskLevel.SAFE
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    is_template: bool = False
    template_vars: List[str] = field(default_factory=list)
    id: Optional[int] = None
    
    # Search-related fields
    tokens: List[str] = field(default_factory=list)
    tfidf_vector: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
        self._classify()
        self._assess_risk()
        self._extract_template_vars()
    
    def _classify(self) -> None:
        """Auto-classify command category."""
        cmd_lower = self.command.lower().strip()
        
        # Classification rules
        classification_rules = [
            (r"^(git|gh)\s", CommandCategory.GIT),
            (r"^docker\s", CommandCategory.DOCKER),
            (r"^kubectl\s", CommandCategory.KUBERNETES),
            (r"^npm\s|yarn\s|pnpm\s", CommandCategory.NPM),
            (r"^pip\s|pip3\s|poetry\s|conda\s", CommandCategory.PIP),
            (r"^python\s|python3\s", CommandCategory.PYTHON),
            (r"^node\s", CommandCategory.NODE),
            (r"^(ls|cd|pwd|mkdir|rmdir|cp|mv|rm|touch|cat|less|more|head|tail)\s", CommandCategory.FILE),
            (r"^(curl|wget|ping|nc|netstat|ss|ifconfig|ip\s|dig|nslookup)\s", CommandCategory.NETWORK),
            (r"^(mysql|psql|sqlite|mongo|redis-cli)\s", CommandCategory.DATABASE),
            (r"^(grep|sed|awk|cut|sort|uniq|wc|tr)\s", CommandCategory.TEXT),
            (r"^(make|cmake|cargo|gradle|maven|npm\srun|yarn\sbuild)\s", CommandCategory.BUILD),
            (r"^(pytest|jest|mocha|unittest|go\stest|cargo\stest)\s", CommandCategory.TEST),
            (r"^(aws|gcloud|az)\s", CommandCategory.CLOUD),
            (r"^ssh\s|scp\s|rsync\s", CommandCategory.SSH),
            (r"^gitflow\s", CommandCategory.GITFLOW),
            (r"^(sudo|apt|yum|dnf|brew|pacman)\s", CommandCategory.SYSTEM),
        ]
        
        for pattern, category in classification_rules:
            if re.match(pattern, cmd_lower):
                self.category = category
                return
    
    def _assess_risk(self) -> None:
        """Assess command risk level."""
        cmd = self.command.lower()
        
        critical_patterns = [
            r"rm\s+-rf\s+/",
            r"rm\s+-rf\s+~",
            r"mkfs",
            r"dd\s+if=.*of=/dev/",
            r">\s*/dev/sd",
            r"chmod\s+[-+]rwx\s+/",
        ]
        
        high_patterns = [
            r"rm\s+-rf",
            r"sudo\s+rm",
            r"chmod\s+777",
            r"chown\s+-R",
            r">\s*/dev/",
            r"kill\s+-9\s+1",
        ]
        
        medium_patterns = [
            r"sudo\s",
            r"chmod\s",
            r"chown\s",
            r"kill\s+-9",
            r"pkill\s",
            r"killall\s",
        ]
        
        low_patterns = [
            r"rm\s",
            r"mv\s+.*/",
            r"cp\s+-r",
        ]
        
        for pattern in critical_patterns:
            if re.search(pattern, cmd):
                self.risk_level = RiskLevel.CRITICAL
                return
        
        for pattern in high_patterns:
            if re.search(pattern, cmd):
                self.risk_level = RiskLevel.HIGH
                return
        
        for pattern in medium_patterns:
            if re.search(pattern, cmd):
                self.risk_level = RiskLevel.MEDIUM
                return
        
        for pattern in low_patterns:
            if re.search(pattern, cmd):
                self.risk_level = RiskLevel.LOW
                return
    
    def _extract_template_vars(self) -> None:
        """Extract template variables from command."""
        # Find variables like {{var}}, ${var}, $var
        patterns = [
            r"\{\{(\w+)\}\}",
            r"\$\{(\w+)\}",
            r"\$(\w+)(?!\w)",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, self.command)
            self.template_vars.extend(matches)
        
        self.template_vars = list(set(self.template_vars))
        self.is_template = len(self.template_vars) > 0
    
    def tokenize(self) -> List[str]:
        """Tokenize command for search."""
        # Remove special characters and split
        tokens = re.findall(r"[\w\-\.\/]+", self.command.lower())
        self.tokens = tokens
        return tokens
    
    def get_hash(self) -> str:
        """Get unique hash for command."""
        return hashlib.md5(self.command.encode()).hexdigest()[:8]
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "command": self.command,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "count": self.count,
            "category": self.category.value,
            "risk_level": self.risk_level.value,
            "tags": self.tags,
            "notes": self.notes,
            "is_template": self.is_template,
            "template_vars": self.template_vars,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Command":
        """Create from dictionary."""
        return cls(
            id=data.get("id"),
            command=data["command"],
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None,
            count=data.get("count", 1),
            category=CommandCategory(data.get("category", "other")),
            risk_level=RiskLevel(data.get("risk_level", "safe")),
            tags=data.get("tags", []),
            notes=data.get("notes"),
            is_template=data.get("is_template", False),
            template_vars=data.get("template_vars", []),
        )
    
    def __str__(self) -> str:
        """String representation."""
        return self.command
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"Command({self.command[:50]}..., category={self.category.value}, risk={self.risk_level.value})"
