"""Handler for /health command."""

import httpx
import sys
from pathlib import Path

# Add bot directory to path for imports
bot_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(bot_dir))
from config import load_config


def handle_health() -> str:
    """Handle /health command.
    
    Returns:
        Health status string with backend info or error message.
    """
    config = load_config()
    base_url = config.get("lms_api_base_url", "")
    api_key = config.get("lms_api_key", "")
    
    if not base_url or not api_key:
        return "Backend error: configuration missing (LMS_API_BASE_URL or LMS_API_KEY)."
    
    try:
        url = f"{base_url.rstrip('/')}/items/"
        headers = {"Authorization": f"Bearer {api_key}"}
        with httpx.Client() as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            items = response.json()
            return f"Backend is healthy. {len(items)} items available."
    except httpx.ConnectError as e:
        return f"Backend error: connection refused ({base_url}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except httpx.RequestError as e:
        return f"Backend error: {str(e)}"
    except Exception as e:
        return f"Backend error: {str(e)}"
