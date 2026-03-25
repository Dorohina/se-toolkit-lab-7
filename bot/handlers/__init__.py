"""Command handlers — plain functions separated from Telegram transport."""


def handle_start() -> str:
    """Handle /start command."""
    return "Welcome to the LMS Bot! Use /help to see available commands."


def handle_help() -> str:
    """Handle /help command."""
    return """Available commands:
/start — Welcome message
/help — Show this help
/health — Check system status
/labs — List available labs
/scores <lab> — View scores for a lab
"""


def handle_health() -> str:
    """Handle /health command."""
    return "Health check: OK (placeholder)"


def handle_labs() -> str:
    """Handle /labs command."""
    return "Labs list (placeholder)"


def handle_scores(lab: str | None = None) -> str:
    """Handle /scores command."""
    if lab:
        return f"Scores for {lab} (placeholder)"
    return "Please specify a lab, e.g., /scores lab-1"


def handle_unknown(command: str) -> str:
    """Handle unknown commands."""
    return f"Unknown command: {command}. Use /help to see available commands."
