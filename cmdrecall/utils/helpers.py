"""
Utility functions.
"""

import re
from datetime import datetime
from typing import Optional, List


def format_timestamp(dt: datetime, relative: bool = True) -> str:
    """Format timestamp for display.
    
    Args:
        dt: Datetime object
        relative: Whether to use relative time format
        
    Returns:
        Formatted string
    """
    if not dt:
        return ""
    
    if relative:
        now = datetime.now()
        diff = now - dt
        
        if diff.days == 0:
            seconds = diff.seconds
            if seconds < 60:
                return "just now"
            elif seconds < 3600:
                return f"{seconds // 60}m ago"
            else:
                return f"{seconds // 3600}h ago"
        elif diff.days == 1:
            return "yesterday"
        elif diff.days < 7:
            return f"{diff.days}d ago"
        elif diff.days < 30:
            return f"{diff.days // 7}w ago"
        else:
            return dt.strftime("%Y-%m-%d")
    else:
        return dt.strftime("%Y-%m-%d %H:%M")


def truncate_command(command: str, max_length: int = 80) -> str:
    """Truncate command for display.
    
    Args:
        command: Command string
        max_length: Maximum length
        
    Returns:
        Truncated string
    """
    if len(command) <= max_length:
        return command
    
    return command[:max_length - 3] + "..."


def highlight_match(text: str, query: str) -> str:
    """Highlight matching parts of text.
    
    Args:
        text: Text to highlight
        query: Query to match
        
    Returns:
        Text with highlighted matches
    """
    if not query:
        return text
    
    # Case-insensitive highlight
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(f"[bold yellow]{query}[/bold yellow]", text)


def get_risk_color(risk_level: str) -> str:
    """Get color for risk level.
    
    Args:
        risk_level: Risk level string
        
    Returns:
        Color name
    """
    colors = {
        "safe": "green",
        "low": "blue",
        "medium": "yellow",
        "high": "orange",
        "critical": "red",
    }
    return colors.get(risk_level, "white")


def get_category_icon(category: str) -> str:
    """Get icon for command category.
    
    Args:
        category: Category string
        
    Returns:
        Icon string
    """
    icons = {
        "git": "🔀",
        "docker": "🐳",
        "kubectl": "☸️",
        "npm": "📦",
        "pip": "🐍",
        "python": "🐍",
        "node": "💚",
        "system": "⚙️",
        "network": "🌐",
        "database": "🗄️",
        "file": "📁",
        "text": "📝",
        "build": "🔨",
        "test": "🧪",
        "cloud": "☁️",
        "ssh": "🔐",
        "gitflow": "🌿",
        "other": "❓",
    }
    return icons.get(category, "❓")


def parse_variables(text: str) -> List[str]:
    """Parse variable placeholders from text.
    
    Args:
        text: Text containing variables
        
    Returns:
        List of variable names
    """
    patterns = [
        r"\{\{(\w+)\}\}",
        r"\$\{(\w+)\}",
        r"\$(\w+)(?!\w)",
    ]
    
    variables = []
    for pattern in patterns:
        variables.extend(re.findall(pattern, text))
    
    return list(set(variables))


def shell_quote(s: str) -> str:
    """Quote string for shell.
    
    Args:
        s: String to quote
        
    Returns:
        Quoted string
    """
    if not s:
        return "''"
    
    # Check if quoting is needed
    if re.match(r'^[\w\-\.\/]+$', s):
        return s
    
    # Use single quotes
    return "'" + s.replace("'", "'\"'\"'") + "'"


def is_valid_command(command: str) -> bool:
    """Check if command is valid.
    
    Args:
        command: Command string
        
    Returns:
        True if valid
    """
    if not command or not command.strip():
        return False
    
    # Check for obvious invalid patterns
    invalid_patterns = [
        r'^\s*#',  # Comment
        r'^\s*$',  # Empty
    ]
    
    for pattern in invalid_patterns:
        if re.match(pattern, command):
            return False
    
    return True
