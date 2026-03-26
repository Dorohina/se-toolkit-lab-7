"""Handler for /scores command."""


def handle_scores(lab: str | None = None) -> str:
    """Handle /scores command.
    
    Args:
        lab: Optional lab identifier, e.g., 'lab-1'.
        
    Returns:
        Scores information string (placeholder for now).
    """
    if lab:
        return f"Scores for {lab} (placeholder)"
    return "Please specify a lab, e.g., /scores lab-1"
