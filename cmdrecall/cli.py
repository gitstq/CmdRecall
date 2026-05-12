#!/usr/bin/env python3
"""
CmdRecall - Lightweight Terminal Command History Intelligent Recall Engine
轻量级终端命令历史智能召回引擎

CLI entry point.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

from .config import Config, get_config
from .core.history import HistoryParser
from .core.searcher import CommandSearcher
from .core.ranker import CommandRanker
from .storage.database import Database
from .models.command import Command, CommandCategory, RiskLevel
from .models.template import Template
from .utils.helpers import (
    format_timestamp, 
    truncate_command, 
    get_category_icon,
    get_risk_color,
    is_valid_command,
)
from . import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="cmdrecall",
        description="🧠 Lightweight Terminal Command History Intelligent Recall Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cmdrecall search "git commit"      Search for git commit commands
  cmdrecall sync                     Sync shell history
  cmdrecall top                      Show most used commands
  cmdrecall tui                      Launch interactive TUI
  cmdrecall template add             Add a command template
  cmdrecall stats                    Show statistics
        """
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "-c", "--config",
        type=Path,
        help="Path to config file"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Search command
    search_parser = subparsers.add_parser("search", aliases=["s"], help="Search commands")
    search_parser.add_argument("query", nargs="?", default="", help="Search query")
    search_parser.add_argument("-l", "--limit", type=int, default=20, help="Number of results")
    search_parser.add_argument("-c", "--category", help="Filter by category")
    search_parser.add_argument("--fuzzy", action="store_true", help="Enable fuzzy search")
    
    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Sync shell history")
    sync_parser.add_argument("-f", "--force", action="store_true", help="Force full sync")
    
    # Top command
    top_parser = subparsers.add_parser("top", help="Show most used commands")
    top_parser.add_argument("-l", "--limit", type=int, default=20, help="Number of results")
    
    # Recent command
    recent_parser = subparsers.add_parser("recent", aliases=["r"], help="Show recent commands")
    recent_parser.add_argument("-l", "--limit", type=int, default=20, help="Number of results")
    
    # TUI command
    subparsers.add_parser("tui", help="Launch interactive TUI")
    
    # Stats command
    subparsers.add_parser("stats", help="Show statistics")
    
    # Template commands
    template_parser = subparsers.add_parser("template", aliases=["t"], help="Manage templates")
    template_subparsers = template_parser.add_subparsers(dest="template_cmd")
    
    template_add = template_subparsers.add_parser("add", help="Add template")
    template_add.add_argument("name", help="Template name")
    template_add.add_argument("command", help="Command template (use {{var}} for variables)")
    template_add.add_argument("-d", "--description", help="Template description")
    
    template_list = template_subparsers.add_parser("list", aliases=["ls"], help="List templates")
    template_list.add_argument("-l", "--limit", type=int, default=20, help="Number of results")
    
    template_show = template_subparsers.add_parser("show", help="Show template")
    template_show.add_argument("name", help="Template name")
    
    template_use = template_subparsers.add_parser("use", help="Use template")
    template_use.add_argument("name", help="Template name")
    template_use.add_argument("vars", nargs="*", help="Variable values (key=value)")
    
    template_delete = template_subparsers.add_parser("delete", aliases=["rm"], help="Delete template")
    template_delete.add_argument("name", help="Template name")
    
    # Category command
    cat_parser = subparsers.add_parser("category", aliases=["cat"], help="Browse by category")
    cat_parser.add_argument("category", nargs="?", help="Category name")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize shell integration")
    init_parser.add_argument("--shell", choices=["bash", "zsh", "fish"], help="Shell type")
    
    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear database")
    clear_parser.add_argument("-f", "--force", action="store_true", help="Force clear without confirmation")
    
    return parser


def print_commands(commands, show_score=False):
    """Print commands in a formatted way."""
    if not commands:
        print("No commands found.")
        return
    
    for item in commands:
        if show_score and isinstance(item, tuple):
            cmd, score = item
        else:
            cmd = item
            score = None
        
        icon = get_category_icon(cmd.category.value)
        time_str = format_timestamp(cmd.timestamp) if cmd.timestamp else ""
        cmd_display = truncate_command(cmd.command, 60)
        
        line = f"{icon} {cmd_display}"
        if score is not None:
            line += f" [score: {score:.2f}]"
        line += f" [{cmd.count}] {time_str}"
        
        print(line)


def cmd_search(args, db: Database):
    """Handle search command."""
    searcher = CommandSearcher(db)
    
    if args.fuzzy:
        results = searcher.fuzzy_search(args.query, limit=args.limit)
        print_commands(results, show_score=True)
    else:
        results = searcher.search(args.query, limit=args.limit)
        print_commands(results, show_score=True)


def cmd_sync(args, db: Database):
    """Handle sync command."""
    parser = HistoryParser()
    commands = parser.parse()
    
    count = 0
    for cmd in commands:
        if is_valid_command(cmd.command):
            db.add_command(cmd)
            count += 1
    
    print(f"✅ Synced {count} commands from history")


def cmd_top(args, db: Database):
    """Handle top command."""
    commands = db.get_top_commands(limit=args.limit)
    print_commands(commands)


def cmd_recent(args, db: Database):
    """Handle recent command."""
    commands = db.get_all_commands(limit=args.limit)
    print_commands(commands)


def cmd_tui(args, db: Database):
    """Handle TUI command."""
    try:
        from .tui import run_tui
        selected = run_tui(db)
        if selected:
            print(selected.command)
    except ImportError:
        print("Error: textual is required for TUI mode")
        print("Install with: pip install textual")
        sys.exit(1)


def cmd_stats(args, db: Database):
    """Handle stats command."""
    stats = db.get_stats()
    
    print("📊 CmdRecall Statistics")
    print(f"  Total commands: {stats['total_commands']}")
    print(f"  Total templates: {stats['total_templates']}")
    print(f"  Unique tokens: {stats['unique_tokens']}")
    
    if stats['by_category']:
        print("\n📁 By Category:")
        for cat, count in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True):
            icon = get_category_icon(cat)
            print(f"  {icon} {cat}: {count}")
    
    if stats['by_risk']:
        print("\n⚠️ By Risk Level:")
        for risk, count in stats['by_risk'].items():
            print(f"  {risk}: {count}")


def cmd_template(args, db: Database):
    """Handle template commands."""
    if args.template_cmd == "add":
        template = Template(
            name=args.name,
            command=args.command,
            description=args.description
        )
        db.add_template(template)
        print(f"✅ Template '{args.name}' added")
    
    elif args.template_cmd in ["list", "ls"]:
        templates = db.get_all_templates()
        for t in templates[:args.limit]:
            vars_str = ", ".join(t.variables.keys()) if t.variables else ""
            print(f"📝 {t.name}: {truncate_command(t.command, 40)} [{vars_str}]")
    
    elif args.template_cmd == "show":
        template = db.get_template_by_name(args.name)
        if template:
            print(f"📝 {template.name}")
            print(f"   Command: {template.command}")
            if template.description:
                print(f"   Description: {template.description}")
            if template.variables:
                print(f"   Variables: {', '.join(template.variables.keys())}")
        else:
            print(f"Template '{args.name}' not found")
    
    elif args.template_cmd == "use":
        template = db.get_template_by_name(args.name)
        if template:
            # Parse variables
            values = {}
            for var in args.vars:
                if "=" in var:
                    key, val = var.split("=", 1)
                    values[key] = val
            
            result = template.render(values)
            print(result)
            db.increment_template_usage(template.id)
        else:
            print(f"Template '{args.name}' not found")
    
    elif args.template_cmd in ["delete", "rm"]:
        template = db.get_template_by_name(args.name)
        if template:
            db.delete_template(template.id)
            print(f"✅ Template '{args.name}' deleted")
        else:
            print(f"Template '{args.name}' not found")


def cmd_category(args, db: Database):
    """Handle category command."""
    if args.category:
        try:
            category = CommandCategory(args.category.lower())
            commands = db.get_commands_by_category(category)
            print_commands(commands)
        except ValueError:
            print(f"Invalid category. Valid categories: {[c.value for c in CommandCategory]}")
    else:
        stats = db.get_stats()
        print("📁 Available Categories:")
        for cat, count in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True):
            icon = get_category_icon(cat)
            print(f"  {icon} {cat}: {count}")


def cmd_init(args, db: Database):
    """Handle init command."""
    config = get_config()
    shell = args.shell or config.shell
    
    if shell == "bash":
        hook = '''
# CmdRecall shell integration
if command -v cmdrecall &> /dev/null; then
    export PROMPT_COMMAND='cmdrecall hook --last "$?" 2>/dev/null; '"$PROMPT_COMMAND"
fi
'''
        print("Add the following to your ~/.bashrc:")
        print(hook)
    
    elif shell == "zsh":
        hook = '''
# CmdRecall shell integration
if command -v cmdrecall &> /dev/null; then
    precmd_cmdrecall() { cmdrecall hook --last "$?" 2>/dev/null; }
    precmd_functions+=(precmd_cmdrecall)
fi
'''
        print("Add the following to your ~/.zshrc:")
        print(hook)
    
    elif shell == "fish":
        hook = '''
# CmdRecall shell integration
if type -q cmdrecall
    function cmdrecall_hook --on-event fish_postexec
        cmdrecall hook --last $status 2>/dev/null
    end
end
'''
        print("Add the following to your ~/.config/fish/config.fish:")
        print(hook)


def cmd_clear(args, db: Database):
    """Handle clear command."""
    if not args.force:
        confirm = input("Are you sure you want to clear all commands? [y/N] ")
        if confirm.lower() != 'y':
            print("Cancelled")
            return
    
    count = db.clear_commands()
    print(f"✅ Cleared {count} commands")


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Initialize config
    if args.config:
        config = Config(args.config)
    else:
        config = get_config()
    
    # Initialize database
    db = Database(config.database_path)
    
    # Handle commands
    if args.command == "search" or args.command == "s":
        cmd_search(args, db)
    elif args.command == "sync":
        cmd_sync(args, db)
    elif args.command == "top":
        cmd_top(args, db)
    elif args.command == "recent" or args.command == "r":
        cmd_recent(args, db)
    elif args.command == "tui":
        cmd_tui(args, db)
    elif args.command == "stats":
        cmd_stats(args, db)
    elif args.command == "template" or args.command == "t":
        cmd_template(args, db)
    elif args.command == "category" or args.command == "cat":
        cmd_category(args, db)
    elif args.command == "init":
        cmd_init(args, db)
    elif args.command == "clear":
        cmd_clear(args, db)
    else:
        # Default: show help
        parser.print_help()


if __name__ == "__main__":
    main()
