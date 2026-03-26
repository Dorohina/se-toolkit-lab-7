"""Telegram bot entry point with --test mode."""

import argparse
import sys

from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_unknown,
)
from handlers.intent_router import route_intent


def parse_command(command: str) -> tuple[str, list[str]]:
    """Parse command string into command name and arguments.

    Args:
        command: Full command string, e.g., '/scores lab-1'

    Returns:
        Tuple of (command_name, arguments_list)
    """
    parts = command.strip().split()
    return parts[0], parts[1:] if len(parts) > 1 else []


def execute_command(command: str, args: list[str]) -> str:
    """Execute a command and return the response.

    Args:
        command: Command name, e.g., '/start'
        args: List of command arguments

    Returns:
        Response string from the handler
    """
    if command == "/start":
        return handle_start()
    elif command == "/help":
        return handle_help()
    elif command == "/health":
        return handle_health()
    elif command == "/labs":
        return handle_labs()
    elif command == "/scores":
        lab = args[0] if args else None
        return handle_scores(lab)
    else:
        return handle_unknown(command)


def is_natural_language(input_text: str) -> bool:
    """Check if input is natural language (not a slash command).
    
    Args:
        input_text: User input text.
        
    Returns:
        True if natural language, False if slash command.
    """
    return not input_text.strip().startswith("/")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="MESSAGE",
        help="Test a message without Telegram, e.g., '/start' or 'what labs are available'",
    )
    args = parser.parse_args()

    if args.test:
        input_text = args.test.strip()
        
        # Check if natural language or slash command
        if is_natural_language(input_text):
            # Route to LLM for intent-based processing
            response = route_intent(input_text)
        else:
            # Parse and execute slash command
            command, cmd_args = parse_command(input_text)
            response = execute_command(command, cmd_args)
        
        print(response)
        sys.exit(0)

    # Normal bot mode (not implemented yet)
    print("Bot starting in normal mode (not implemented yet)...")
    print("Inline keyboard buttons will be available in Telegram.")


if __name__ == "__main__":
    main()
