"""
Evaluate OpenAI AgentKit using Vertex AI Evaluation SDK
"""

from openai import OpenAI
from vertexai.evaluation import EvalTask, PointwiseMetric
import vertexai
import os

# Initialize
vertexai.init(project=os.getenv("GCP_PROJECT_ID"), location="us-central1")
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define tools
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_flights",
            "description": "Search for flights",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string"},
                    "date": {"type": "string"}
                },
                "required": ["destination"]
            }
        }
    }
]

# Agent wrapper
def openai_agent(query: str) -> dict:
    """OpenAI agent that returns response and tool calls"""
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": query}],
        tools=TOOLS
    )
    
    msg = response.choices[0].message
    result = {"response": msg.content or ""}
    
    if msg.tool_calls:
        result["tool_calls"] = [
            {
                "name": tc.function.name,
                "arguments": tc.function.arguments
            } for tc in msg.tool_calls
        ]
    
    return result

# Evaluation dataset
dataset = [
    {
        "query": "What's the weather in San Francisco?",
        "reference": "get_weather"
    },
    {
        "query": "Find flights to Tokyo next week",
        "reference": "search_flights"
    },
    {
        "query": "Tell me about the weather in NYC",
        "reference": "get_weather"
    }
]

# Custom metric
quality_metric = PointwiseMetric(
    metric="agent_quality",
    metric_prompt_template="""
    Rate the agent's response quality (1-5):
    Query: {query}
    Response: {response}
    """
)

# Run evaluation
print("Starting evaluation...")
eval_task = EvalTask(
    dataset=dataset,
    metrics=[
        "tool_call_valid",
        "tool_name_match",
        quality_metric
    ]
)

results = eval_task.evaluate(model=openai_agent)

# Print results
print("\n=== Evaluation Results ===")
print(f"Tool Call Valid: {results.summary_metrics.get('tool_call_valid', 'N/A')}")
print(f"Tool Name Match: {results.summary_metrics.get('tool_name_match', 'N/A')}")
print(f"Agent Quality: {results.summary_metrics.get('agent_quality', 'N/A')}")
