"""Handler for unknown commands."""


def handle_unknown(command: str) -> str:
    """Handle unknown commands.
    
    Args:
        command: The unrecognized command string.
        
    Returns:
        Helpful error message string.
    """
    return f"Unknown command: {command}. Use /help to see available commands."
