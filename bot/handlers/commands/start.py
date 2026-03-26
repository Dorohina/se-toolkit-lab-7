"""Handler for /start command."""


def handle_start() -> str:
    """Handle /start command.

    Returns:
        Welcome message string with inline keyboard hint.
    """
    return """Welcome to the LMS Bot! 🎓

I can help you explore lab data, scores, and student performance.

Try asking me:
• "what labs are available?"
• "show me scores for lab 4"
• "which lab has the lowest pass rate?"
• "who are the top 5 students?"

Or use slash commands: /help, /health, /labs, /scores <lab>

[buttons:labs|scores|top_students|help]
"""
