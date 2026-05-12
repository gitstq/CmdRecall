"""
Command classifier utility.
"""

import re
from typing import Optional, Tuple
from ..models.command import CommandCategory, RiskLevel


class CommandClassifier:
    """Classify commands by category and risk."""
    
    # Category patterns
    CATEGORY_PATTERNS = [
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
    
    # Risk patterns
    RISK_PATTERNS = {
        RiskLevel.CRITICAL: [
            r"rm\s+-rf\s+/",
            r"rm\s+-rf\s+~",
            r"mkfs",
            r"dd\s+if=.*of=/dev/",
            r">\s*/dev/sd",
            r"chmod\s+[-+]rwx\s+/",
        ],
        RiskLevel.HIGH: [
            r"rm\s+-rf",
            r"sudo\s+rm",
            r"chmod\s+777",
            r"chown\s+-R",
            r">\s*/dev/",
            r"kill\s+-9\s+1",
        ],
        RiskLevel.MEDIUM: [
            r"sudo\s",
            r"chmod\s",
            r"chown\s",
            r"kill\s+-9",
            r"pkill\s",
            r"killall\s",
        ],
        RiskLevel.LOW: [
            r"rm\s",
            r"mv\s+.*/",
            r"cp\s+-r",
        ],
    }
    
    @classmethod
    def classify(cls, command: str) -> Tuple[CommandCategory, RiskLevel]:
        """Classify a command.
        
        Args:
            command: Command string
            
        Returns:
            Tuple of (category, risk_level)
        """
        category = cls._get_category(command)
        risk = cls._get_risk(command)
        return category, risk
    
    @classmethod
    def _get_category(cls, command: str) -> CommandCategory:
        """Get command category."""
        cmd_lower = command.lower().strip()
        
        for pattern, category in cls.CATEGORY_PATTERNS:
            if re.match(pattern, cmd_lower):
                return category
        
        return CommandCategory.OTHER
    
    @classmethod
    def _get_risk(cls, command: str) -> RiskLevel:
        """Get command risk level."""
        cmd = command.lower()
        
        for risk_level, patterns in cls.RISK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, cmd):
                    return risk_level
        
        return RiskLevel.SAFE
    
    @classmethod
    def is_dangerous(cls, command: str) -> bool:
        """Check if command is dangerous.
        
        Args:
            command: Command string
            
        Returns:
            True if command is dangerous
        """
        _, risk = cls.classify(command)
        return risk in (RiskLevel.HIGH, RiskLevel.CRITICAL)
