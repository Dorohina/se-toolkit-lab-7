"""Handler for /labs command."""

import httpx
from ...config import load_config


def handle_labs() -> str:
    """Handle /labs command.
    
    Returns:
        Formatted list of available labs or error message.
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
        
        # Group items by lab
        labs = {}
        for item in items:
            lab_id = item.get("lab_id", "unknown")
            lab_name = item.get("lab_name", "Unknown Lab")
            task_name = item.get("task_name", "")
            
            if lab_id not in labs:
                labs[lab_id] = {"name": lab_name, "tasks": []}
            if task_name:
                labs[lab_id]["tasks"].append(task_name)
        
        # Format output
        lines = ["Available labs:"]
        for lab_id, lab_info in sorted(labs.items()):
            lines.append(f"- {lab_id} — {lab_info['name']}")
        
        return "\n".join(lines)
        
    except httpx.ConnectError:
        return f"Backend error: connection refused ({base_url}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except httpx.RequestError as e:
        return f"Backend error: {str(e)}"
    except Exception as e:
        return f"Backend error: {str(e)}"
