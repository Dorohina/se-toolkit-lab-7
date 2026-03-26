"""Intent router — uses LLM to route natural language to backend tools."""

import sys
from pathlib import Path

# Add bot directory to path for imports
bot_dir = Path(__file__).parent.parent
sys.path.insert(0, str(bot_dir))

from config import load_config
from services.llm_client import LLMClient

# System prompt for the LLM
SYSTEM_PROMPT = """You are a helpful assistant for an LMS (Learning Management System). 
You have access to tools that fetch data about labs, students, scores, and analytics.

When the user asks a question:
1. Use the available tools to fetch the data they need
2. Analyze the results
3. Provide a clear, helpful answer with specific numbers and names

Available tools:
- get_items: List all labs and tasks
- get_learners: List enrolled students and groups
- get_scores: Score distribution for a lab
- get_pass_rates: Per-task pass rates for a lab
- get_timeline: Submission timeline for a lab
- get_groups: Per-group performance for a lab
- get_top_learners: Top N students for a lab
- get_completion_rate: Completion percentage for a lab
- trigger_sync: Refresh data from autochecker

Always call tools to get real data before answering. If you don't have data, don't make up numbers.

For greetings like "hello" or "hi", respond warmly and mention what you can help with (labs, scores, students, etc.).

For unclear messages, ask what specific information they want about labs or students.
"""


def route_intent(message: str) -> str:
    """Route a natural language message to the LLM and backend tools.
    
    Args:
        message: User's natural language message.
        
    Returns:
        Response from the LLM after executing tool calls.
    """
    config = load_config()
    
    llm_api_key = config.get("llm_api_key", "")
    llm_base_url = config.get("llm_api_base_url", "")
    llm_model = config.get("llm_api_model", "")
    
    # Check if LLM is configured
    if not llm_api_key or not llm_base_url or not llm_model:
        return "LLM is not configured. Please set LLM_API_KEY, LLM_API_BASE_URL, and LLM_API_MODEL in .env.bot.secret"
    
    # Initialize LLM client
    llm = LLMClient(
        api_key=llm_api_key,
        base_url=llm_base_url,
        model=llm_model,
    )
    
    # Get tool definitions
    tools = llm.get_tool_definitions()
    
    # Build conversation messages
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message},
    ]
    
    print(f"[intent] Processing: {message}", file=sys.stderr)
    
    # Chat with tools
    response = llm.chat_with_tools(messages, tools)
    
    print(f"[intent] Response: {response[:100]}...", file=sys.stderr)
    
    return response
