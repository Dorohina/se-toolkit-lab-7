"""Handler for /scores command."""

import httpx
import sys
from pathlib import Path

# Add bot directory to path for imports
bot_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(bot_dir))
from config import load_config


def handle_scores(lab: str | None = None) -> str:
    """Handle /scores command.
    
    Args:
        lab: Optional lab identifier, e.g., 'lab-01'.
        
    Returns:
        Scores information string with pass rates or error message.
    """
    if not lab:
        return "Please specify a lab, e.g., /scores lab-01"
    
    config = load_config()
    base_url = config.get("lms_api_base_url", "")
    api_key = config.get("lms_api_key", "")
    
    if not base_url or not api_key:
        return "Backend error: configuration missing (LMS_API_BASE_URL or LMS_API_KEY)."
    
    try:
        url = f"{base_url.rstrip('/')}/analytics/pass-rates"
        params = {"lab": lab}
        headers = {"Authorization": f"Bearer {api_key}"}
        with httpx.Client() as client:
            response = client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
        
        # Format pass rates
        lines = [f"Pass rates for {lab}:"]
        
        # Handle different response formats
        if isinstance(data, list):
            for item in data:
                task_name = item.get("task_name", item.get("task", "Unknown"))
                pass_rate = item.get("pass_rate", item.get("passRate", 0))
                attempts = item.get("attempts", 0)
                lines.append(f"- {task_name}: {pass_rate:.1f}% ({attempts} attempts)")
        elif isinstance(data, dict):
            tasks = data.get("tasks", data.get("pass_rates", []))
            for task in tasks:
                task_name = task.get("task_name", task.get("task", "Unknown"))
                pass_rate = task.get("pass_rate", task.get("passRate", 0))
                attempts = task.get("attempts", 0)
                lines.append(f"- {task_name}: {pass_rate:.1f}% ({attempts} attempts)")
        
        return "\n".join(lines)
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Lab '{lab}' not found. Use /labs to see available labs."
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}."
    except httpx.ConnectError:
        return f"Backend error: connection refused ({base_url}). Check that the services are running."
    except httpx.RequestError as e:
        return f"Backend error: {str(e)}"
    except Exception as e:
        return f"Backend error: {str(e)}"
