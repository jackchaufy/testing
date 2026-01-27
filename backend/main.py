from __future__ import annotations

import json
import os
from pathlib import Path
import urllib.request
from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

def load_env() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return
    with env_path.open("r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


load_env()

app = FastAPI()
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@tool
def get_time() -> str:
    """Get the current UTC time."""
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


@tool
def calculator(expression: str) -> str:
    """Evaluate a simple arithmetic expression."""
    allowed_chars = set("0123456789+-*/(). ")
    if not set(expression).issubset(allowed_chars):
        raise ValueError("Expression contains unsupported characters.")
    try:
        result = eval(expression, {"__builtins__": {}}, {})
    except Exception as exc:  # noqa: BLE001
        raise ValueError("Invalid expression.") from exc
    return str(result)


@tool
def quick_fact(topic: str) -> str:
    """Return a short placeholder fact about a topic."""
    return (
        f"Here's a quick placeholder fact about {topic}: "
        "AI agents can chain tools together to solve tasks." 
        "Update this tool to call a real knowledge source if needed."
    )


@tool
def send_booking_request(chat_input: str) -> str:
    """Send a booking request payload to the local webhook endpoint."""
    payload = {
        "chatInput": chat_input,
        "sessionId": "3fc257c8d0e04083a4a2e21e57ba8703",
        "action": "sendMessage",
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        "http://localhost:5678/webhook-test/99215717-d8d9-4486-9ac4-1cdc932fbf28",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        raw_response = response.read().decode("utf-8")
    try:
        data = json.loads(raw_response)
    except json.JSONDecodeError:
        return raw_response
    summary = data.get("summary")
    if summary:
        return summary
    return json.dumps(data, ensure_ascii=False)


TOOLS = [get_time, calculator, quick_fact, send_booking_request]
TOOL_STATE = {tool_.name: True for tool_ in TOOLS}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(os.path.join(frontend_path, "index.html"))


@app.get("/api/tools")
def list_tools() -> Dict[str, List[Dict[str, Any]]]:
    return {
        "tools": [
            {
                "name": tool_.name,
                "description": tool_.description,
                "enabled": TOOL_STATE.get(tool_.name, False),
            }
            for tool_ in TOOLS
        ]
    }


@app.post("/api/tools/{tool_name}/toggle")
def toggle_tool(tool_name: str) -> Dict[str, Any]:
    if tool_name not in TOOL_STATE:
        raise HTTPException(status_code=404, detail="Tool not found")
    TOOL_STATE[tool_name] = not TOOL_STATE[tool_name]
    return {"name": tool_name, "enabled": TOOL_STATE[tool_name]}


@app.post("/api/chat")
def chat(payload: Dict[str, Any]) -> Dict[str, Any]:
    message = payload.get("message")
    history = payload.get("history", [])
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    if not os.getenv("OPENAI_API_KEY"):
        return {
            "reply": "Missing OPENAI_API_KEY. Set it to enable the LangChain agent.",
            "tool_usage": [],
        }

    enabled_tools = [tool_ for tool_ in TOOLS if TOOL_STATE.get(tool_.name, False)]
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    chat_history = []
    for entry in history:
        if entry.get("role") == "user":
            chat_history.append(HumanMessage(content=entry.get("content", "")))
        elif entry.get("role") == "assistant":
            chat_history.append(AIMessage(content=entry.get("content", "")))

    system_message = SystemMessage(
        content="You are a helpful agent that can use tools to answer questions."
    )

    agent = create_react_agent(llm, enabled_tools)
    result = agent.invoke(
        {"messages": [system_message, *chat_history, HumanMessage(content=message)]}
    )

    messages = result.get("messages", [])
    reply = messages[-1].content if messages else ""

    tool_usage = []
    for message_item in messages:
        if isinstance(message_item, AIMessage):
            for tool_call in message_item.tool_calls or []:
                if isinstance(tool_call, dict):
                    name = tool_call.get("name")
                else:
                    name = getattr(tool_call, "name", None)
                if name:
                    tool_usage.append(name)

    return {"reply": reply, "tool_usage": tool_usage}
