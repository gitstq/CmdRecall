"""
Shell history parser.
"""

import re
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Tuple
import os

from ..models.command import Command
from ..config import get_config


class HistoryParser:
    """Parse shell history files."""
    
    def __init__(self, history_file: Optional[Path] = None):
        """Initialize history parser.
        
        Args:
            history_file: Optional custom history file path
        """
        config = get_config()
        self.history_file = history_file or config.history_file
        self.exclude_patterns = config.get("exclude_patterns", [])
    
    def parse(self) -> List[Command]:
        """Parse history file and return commands.
        
        Returns:
            List of Command objects
        """
        if not self.history_file.exists():
            return []
        
        shell = get_config().shell
        
        if shell == "zsh":
            return self._parse_zsh_history()
        elif shell == "fish":
            return self._parse_fish_history()
        else:
            return self._parse_bash_history()
    
    def _parse_bash_history(self) -> List[Command]:
        """Parse bash history file."""
        commands = []
        
        try:
            with open(self.history_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    
                    if self._should_exclude(line):
                        continue
                    
                    cmd = Command(command=line)
                    commands.append(cmd)
        except IOError:
            pass
        
        return commands
    
    def _parse_zsh_history(self) -> List[Command]:
        """Parse zsh history file.
        
        Zsh history format:
        `: 1234567890:0;command`
        """
        commands = []
        
        try:
            with open(self.history_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Pattern for extended history
            pattern = r": (\d+):\d+;(.+?)(?=:\s*\d+:\d+;|$)"
            matches = re.findall(pattern, content, re.DOTALL)
            
            for timestamp_str, cmd_text in matches:
                cmd_text = cmd_text.strip()
                if not cmd_text or self._should_exclude(cmd_text):
                    continue
                
                try:
                    timestamp = datetime.fromtimestamp(int(timestamp_str))
                except (ValueError, OSError):
                    timestamp = None
                
                cmd = Command(command=cmd_text, timestamp=timestamp)
                commands.append(cmd)
            
            # Fallback for simple history format
            if not matches:
                for line in content.split("\n"):
                    line = line.strip()
                    if line and not line.startswith(":") and not self._should_exclude(line):
                        commands.append(Command(command=line))
        
        except IOError:
            pass
        
        return commands
    
    def _parse_fish_history(self) -> List[Command]:
        """Parse fish shell history.
        
        Fish history format:
        - cmd: command text
          when: timestamp
        """
        commands = []
        
        try:
            with open(self.history_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Parse YAML-like format
            cmd_pattern = r"- cmd: (.+)\n\s+when: (\d+)"
            matches = re.findall(cmd_pattern, content)
            
            for cmd_text, timestamp_str in matches:
                cmd_text = cmd_text.strip()
                if not cmd_text or self._should_exclude(cmd_text):
                    continue
                
                try:
                    timestamp = datetime.fromtimestamp(int(timestamp_str))
                except (ValueError, OSError):
                    timestamp = None
                
                cmd = Command(command=cmd_text, timestamp=timestamp)
                commands.append(cmd)
        
        except IOError:
            pass
        
        return commands
    
    def _should_exclude(self, command: str) -> bool:
        """Check if command should be excluded."""
        for pattern in self.exclude_patterns:
            if re.search(pattern, command):
                return True
        return False
    
    def get_new_commands(self, last_count: int = 0) -> List[Command]:
        """Get new commands since last sync.
        
        Args:
            last_count: Number of commands from last sync
            
        Returns:
            List of new commands
        """
        all_commands = self.parse()
        if len(all_commands) <= last_count:
            return []
        return all_commands[last_count:]
    
    def watch(self, callback, interval: int = 5) -> None:
        """Watch history file for changes.
        
        Args:
            callback: Function to call with new commands
            interval: Check interval in seconds
        """
        import time
        
        last_mtime = 0
        last_size = 0
        
        while True:
            try:
                current_mtime = self.history_file.stat().st_mtime
                current_size = self.history_file.stat().st_size
                
                if current_mtime > last_mtime or current_size != last_size:
                    # File changed, parse new commands
                    new_commands = self.parse()
                    if new_commands:
                        callback(new_commands)
                    
                    last_mtime = current_mtime
                    last_size = current_size
            
            except (IOError, OSError):
                pass
            
            time.sleep(interval)
