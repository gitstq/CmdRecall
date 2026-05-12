"""
CmdRecall - Lightweight Terminal Command History Intelligent Recall Engine
轻量级终端命令历史智能召回引擎

A zero-dependency, intelligent command history search and recall tool.
"""

__version__ = "1.0.0"
__author__ = "gitstq"
__description__ = "Lightweight Terminal Command History Intelligent Recall Engine"

from .core.history import HistoryParser
from .core.searcher import CommandSearcher
from .core.ranker import CommandRanker
from .storage.database import Database
from .models.command import Command

__all__ = [
    "HistoryParser",
    "CommandSearcher", 
    "CommandRanker",
    "Database",
    "Command",
]
