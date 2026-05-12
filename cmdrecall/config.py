"""
Configuration management for CmdRecall.
"""

import os
from pathlib import Path
from typing import Optional
import json


class Config:
    """Configuration manager for CmdRecall."""
    
    DEFAULT_CONFIG = {
        "database_path": None,  # Will be set to ~/.cmdrecall/cmdrecall.db
        "history_limit": 10000,
        "search_limit": 50,
        "time_decay_factor": 0.95,
        "frequency_weight": 0.3,
        "recency_weight": 0.3,
        "relevance_weight": 0.4,
        "auto_sync": True,
        "sync_interval": 300,  # seconds
        "shell": None,  # Auto-detect
        "exclude_patterns": [
            "^ls$",
            "^cd$",
            "^pwd$",
            "^clear$",
            "^exit$",
            "^history",
        ],
        "risk_commands": [
            "rm -rf",
            "sudo rm",
            "mkfs",
            "dd if=",
            "> /dev/",
            "chmod 777",
            "chown -R",
        ],
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration.
        
        Args:
            config_path: Optional custom config path
        """
        self.config_dir = config_path or Path.home() / ".cmdrecall"
        self.config_file = self.config_dir / "config.json"
        self._config = self.DEFAULT_CONFIG.copy()
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self._config.update(loaded)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Set default database path
        if self._config["database_path"] is None:
            self._config["database_path"] = str(self.config_dir / "cmdrecall.db")
    
    def save(self) -> None:
        """Save configuration to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default=None):
        """Get configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value) -> None:
        """Set configuration value."""
        self._config[key] = value
    
    @property
    def database_path(self) -> Path:
        """Get database path."""
        return Path(self._config["database_path"])
    
    @property
    def shell(self) -> Optional[str]:
        """Get configured shell or auto-detect."""
        if self._config["shell"]:
            return self._config["shell"]
        
        # Auto-detect shell
        shell = os.environ.get("SHELL", "")
        if "zsh" in shell:
            return "zsh"
        elif "bash" in shell:
            return "bash"
        elif "fish" in shell:
            return "fish"
        return "bash"  # Default fallback
    
    @property
    def history_file(self) -> Path:
        """Get shell history file path."""
        home = Path.home()
        shell = self.shell
        
        if shell == "zsh":
            # Check for custom history file
            histfile = os.environ.get("HISTFILE", "")
            if histfile:
                return Path(histfile)
            return home / ".zsh_history"
        elif shell == "fish":
            return home / ".local" / "share" / "fish" / "fish_history"
        else:  # bash
            histfile = os.environ.get("HISTFILE", "")
            if histfile:
                return Path(histfile)
            return home / ".bash_history"


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config
