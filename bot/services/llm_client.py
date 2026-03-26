"""LLM client with tool calling support."""

import json
import sys
from typing import Any

import httpx


class LLMClient:
    """Client for interacting with LLM API with tool calling support.
    
    Attributes:
        api_key: API key for authentication.
        base_url: Base URL of the LLM API.
        model: Model name to use.
    """
    
    def __init__(self, api_key: str, base_url: str, model: str):
        """Initialize the LLM client.
        
        Args:
            api_key: API key for Bearer authentication.
            base_url: Base URL of the LLM API.
            model: Model name to use for completions.
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
    
    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """Get tool definitions for all 9 backend endpoints.
        
        Returns:
            List of tool schemas for the LLM.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_items",
                    "description": "Get list of all labs and tasks. Use this to see what labs are available.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_learners",
                    "description": "Get list of enrolled students and their groups.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_scores",
                    "description": "Get score distribution (4 buckets) for a specific lab.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01'"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_pass_rates",
                    "description": "Get per-task average scores and attempt counts for a lab.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01'"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_timeline",
                    "description": "Get submission timeline (submissions per day) for a lab.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01'"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_groups",
                    "description": "Get per-group scores and student counts for a lab.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01'"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_top_learners",
                    "description": "Get top N learners by score for a lab.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01'"},
                            "limit": {"type": "integer", "description": "Number of top learners to return, e.g., 5"}
                        },
                        "required": ["lab", "limit"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_completion_rate",
                    "description": "Get completion rate percentage for a lab.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01'"}
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "trigger_sync",
                    "description": "Trigger ETL sync to refresh data from the autochecker.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
        ]
    
    def chat_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        max_iterations: int = 5,
    ) -> str:
        """Chat with the LLM using tool calling.
        
        Args:
            messages: List of conversation messages.
            tools: List of tool definitions.
            max_iterations: Maximum number of tool call iterations.
            
        Returns:
            Final response from the LLM.
        """
        for iteration in range(max_iterations):
            print(f"[llm] Iteration {iteration + 1}", file=sys.stderr)
            
            payload = {
                "model": self.model,
                "messages": messages,
                "tools": tools,
                "tool_choice": "auto",
            }
            
            url = f"{self.base_url}/chat/completions"
            
            try:
                with httpx.Client() as client:
                    response = client.post(
                        url,
                        headers=self._headers,
                        json=payload,
                        timeout=60.0,
                    )
                    response.raise_for_status()
                    result = response.json()
            except httpx.HTTPStatusError as e:
                return f"LLM error: HTTP {e.response.status_code} {e.response.reason_phrase}"
            except httpx.RequestError as e:
                return f"LLM error: {str(e)}"
            
            choice = result.get("choices", [{}])[0].get("message", {})
            
            # Check for tool calls
            tool_calls = choice.get("tool_calls", [])
            
            if not tool_calls:
                # No tool calls - return the final response
                return choice.get("content", "I didn't understand. Try asking about labs, scores, or students.")
            
            # Execute tool calls
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": tool_calls,
            })
            
            for tool_call in tool_calls:
                function = tool_call.get("function", {})
                tool_name = function.get("name", "")
                tool_args = json.loads(function.get("arguments", "{}"))
                tool_id = tool_call.get("id", "")
                
                print(f"[tool] LLM called: {tool_name}({tool_args})", file=sys.stderr)
                
                # Execute the tool
                result = self._execute_tool(tool_name, tool_args)
                print(f"[tool] Result: {result[:100] if isinstance(result, str) else str(result)[:100]}...", file=sys.stderr)
                
                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_id,
                    "content": result,
                })
        
        return "I need more iterations to answer this question."
    
    def _execute_tool(self, name: str, args: dict[str, Any]) -> str:
        """Execute a tool by calling the backend API.
        
        Args:
            name: Tool name.
            args: Tool arguments.
            
        Returns:
            Tool result as JSON string.
        """
        # Import config here to avoid circular imports
        # Use explicit path to config module
        import sys
        from pathlib import Path
        
        # Add bot directory to path
        bot_dir = Path(__file__).parent.parent
        if str(bot_dir) not in sys.path:
            sys.path.insert(0, str(bot_dir))
        
        try:
            from config import load_config
        except ImportError as e:
            print(f"[debug] ImportError: {e}", file=sys.stderr)
            print(f"[debug] sys.path: {sys.path[:5]}", file=sys.stderr)
            return f"Error: cannot load config. Check bot logs."
        
        config = load_config()
        base_url = config.get("lms_api_base_url", "")
        api_key = config.get("lms_api_key", "")
        
        print(f"[debug] base_url={base_url!r}, api_key={api_key[:10] if api_key else 'EMPTY'}", file=sys.stderr)
        
        if not base_url:
            return f"Error: LMS_API_BASE_URL is not configured"
        if not api_key:
            return f"Error: LMS_API_KEY is not configured"
        
        headers = {"Authorization": f"Bearer {api_key}"}
        
        try:
            with httpx.Client() as client:
                if name == "get_items":
                    response = client.get(f"{base_url}/items/", headers=headers)
                elif name == "get_learners":
                    response = client.get(f"{base_url}/learners/", headers=headers)
                elif name == "get_scores":
                    response = client.get(
                        f"{base_url}/analytics/scores",
                        headers=headers,
                        params={"lab": args.get("lab", "")},
                    )
                elif name == "get_pass_rates":
                    response = client.get(
                        f"{base_url}/analytics/pass-rates",
                        headers=headers,
                        params={"lab": args.get("lab", "")},
                    )
                elif name == "get_timeline":
                    response = client.get(
                        f"{base_url}/analytics/timeline",
                        headers=headers,
                        params={"lab": args.get("lab", "")},
                    )
                elif name == "get_groups":
                    response = client.get(
                        f"{base_url}/analytics/groups",
                        headers=headers,
                        params={"lab": args.get("lab", "")},
                    )
                elif name == "get_top_learners":
                    response = client.get(
                        f"{base_url}/analytics/top-learners",
                        headers=headers,
                        params={"lab": args.get("lab", ""), "limit": args.get("limit", 5)},
                    )
                elif name == "get_completion_rate":
                    response = client.get(
                        f"{base_url}/analytics/completion-rate",
                        headers=headers,
                        params={"lab": args.get("lab", "")},
                    )
                elif name == "trigger_sync":
                    response = client.post(
                        f"{base_url}/pipeline/sync",
                        headers=headers,
                        json={},
                    )
                else:
                    return f"Unknown tool: {name}"
                
                response.raise_for_status()
                return json.dumps(response.json())
                
        except httpx.RequestError as e:
            return f"Backend error: {str(e)}"
        except Exception as e:
            return f"Error executing {name}: {str(e)}"
