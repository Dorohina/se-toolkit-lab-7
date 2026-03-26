"""Handler for /help command."""


def handle_help() -> str:
    """Handle /help command.
    
    Returns:
        String listing all available commands.
    """
    return """Available commands:
/start — Welcome message
/help — Show this help
/health — Check system status
/labs — List available labs
/scores <lab> — View scores for a lab
"""
