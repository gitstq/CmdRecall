"""
TUI package.
"""

try:
    from .app import CmdRecallApp, run_tui
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    run_tui = None
    CmdRecallApp = None

__all__ = ["CmdRecallApp", "run_tui", "TEXTUAL_AVAILABLE"]
