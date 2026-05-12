"""
Terminal User Interface for CmdRecall.
"""

from typing import Optional, List
from datetime import datetime

try:
    from textual.app import App, ComposeResult
    from textual.widgets import Header, Footer, Static, Input, ListView, ListItem, Label
    from textual.containers import Container, Horizontal, Vertical
    from textual.binding import Binding
    from textual.reactive import reactive
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False

from ..models.command import Command, CommandCategory, RiskLevel
from ..core.searcher import CommandSearcher
from ..core.ranker import CommandRanker
from ..storage.database import Database
from ..utils.helpers import format_timestamp, truncate_command, get_category_icon, get_risk_color


if TEXTUAL_AVAILABLE:
    class CommandItem(ListItem):
        """Widget for displaying a command."""
        
        def __init__(self, command: Command):
            super().__init__()
            self.command = command
        
        def compose(self) -> ComposeResult:
            icon = get_category_icon(self.command.category.value)
            time_str = format_timestamp(self.command.timestamp) if self.command.timestamp else ""
            cmd_display = truncate_command(self.command.command, 60)
            
            yield Label(
                f"{icon} {cmd_display} [{self.command.count}] {time_str}",
                classes=f"command-item risk-{self.command.risk_level.value}"
            )
    
    
    class SearchInput(Input):
        """Search input widget."""
        
        def __init__(self):
            super().__init__(
                placeholder="Search commands... (ESC to exit)",
                id="search-input"
            )
    
    
    class CommandList(ListView):
        """List of commands."""
        
        def __init__(self, commands: List[Command]):
            items = [CommandItem(cmd) for cmd in commands]
            super().__init__(*items, id="command-list")
    
    
    class StatsPanel(Static):
        """Statistics panel."""
        
        def __init__(self, stats: dict):
            super().__init__()
            self.stats = stats
        
        def render(self) -> str:
            lines = [
                "📊 Statistics",
                f"  Total: {self.stats.get('total', 0)}",
                f"  Unique: {self.stats.get('unique', 0)}",
            ]
            return "\n".join(lines)
    
    
    class CmdRecallApp(App):
        """CmdRecall TUI Application."""
        
        CSS = """
        Screen {
            background: $surface;
        }
        
        #search-input {
            dock: top;
            margin: 1;
            padding: 1;
            background: $panel;
            border: solid $primary;
        }
        
        #command-list {
            margin: 1;
        }
        
        .command-item {
            padding: 1;
            margin: 0 1;
        }
        
        .risk-safe { color: green; }
        .risk-low { color: blue; }
        .risk-medium { color: yellow; }
        .risk-high { color: orange; }
        .risk-critical { color: red; }
        
        #stats-panel {
            dock: right;
            width: 20;
            padding: 1;
            background: $panel;
        }
        
        #help-bar {
            dock: bottom;
            height: 3;
            background: $panel;
            padding: 1;
        }
        """
        
        BINDINGS = [
            Binding("escape", "quit", "Quit"),
            Binding("enter", "select_command", "Select"),
            Binding("ctrl+s", "sync", "Sync"),
            Binding("ctrl+t", "templates", "Templates"),
            Binding("ctrl+h", "history", "History"),
            Binding("?", "help", "Help"),
        ]
        
        commands: reactive[List[Command]] = reactive([])
        selected_command: reactive[Optional[Command]] = reactive(None)
        
        def __init__(self, db: Database):
            super().__init__()
            self.db = db
            self.searcher = CommandSearcher(db)
            self.ranker = CommandRanker()
        
        def compose(self) -> ComposeResult:
            yield Header()
            yield SearchInput()
            with Horizontal():
                yield CommandList(self._get_initial_commands())
                with Vertical(id="stats-panel"):
                    yield StatsPanel(self.db.get_stats())
            yield Footer()
        
        def _get_initial_commands(self) -> List[Command]:
            """Get initial commands to display."""
            return self.db.get_top_commands(limit=50)
        
        def on_input_changed(self, event: Input.Changed) -> None:
            """Handle search input changes."""
            query = event.value.strip()
            
            if not query:
                self.commands = self._get_initial_commands()
            else:
                results = self.searcher.search(query, limit=50)
                self.commands = [cmd for cmd, _ in results]
            
            self._update_list()
        
        def _update_list(self) -> None:
            """Update command list."""
            try:
                list_view = self.query_one("#command-list", ListView)
                list_view.clear()
                for cmd in self.commands:
                    list_view.append(CommandItem(cmd))
            except Exception:
                pass
        
        def action_select_command(self) -> None:
            """Select current command."""
            try:
                list_view = self.query_one("#command-list", ListView)
                if list_view.index is not None and list_view.index < len(self.commands):
                    self.selected_command = self.commands[list_view.index]
                    self.exit()
            except Exception:
                pass
        
        def action_sync(self) -> None:
            """Sync history."""
            from ..core.history import HistoryParser
            parser = HistoryParser()
            commands = parser.parse()
            for cmd in commands:
                self.db.add_command(cmd)
            self.commands = self._get_initial_commands()
            self._update_list()
        
        def action_templates(self) -> None:
            """Show templates."""
            # TODO: Implement template view
            pass
        
        def action_history(self) -> None:
            """Show full history."""
            self.commands = self.db.get_all_commands(limit=100)
            self._update_list()
        
        def action_help(self) -> None:
            """Show help."""
            self.push_screen("help")
        
        def get_selected_command(self) -> Optional[Command]:
            """Get selected command after app exits."""
            return self.selected_command


def run_tui(db: Database) -> Optional[Command]:
    """Run TUI application.
    
    Args:
        db: Database instance
        
    Returns:
        Selected command or None
    """
    if not TEXTUAL_AVAILABLE:
        print("Error: textual is required for TUI mode. Install with: pip install textual")
        return None
    
    app = CmdRecallApp(db)
    app.run()
    return app.get_selected_command()
