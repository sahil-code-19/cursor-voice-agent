import pathlib
import subprocess
import json
import os

from typing import Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver

from dotenv import load_dotenv

from speech_to_text import main as speech_to_text
from text_to_speech import main as text_to_speech

load_dotenv()

config = {"configurable":{"thread_id":42}}

system_prompt = SystemMessage(content="""
    You are expert in development. 
    You assist and help the developer
    
    Following Task that you assist and help:
    1) Write the full fledge code wihtout any bugs and errors
    2) Find Bugs in existing codebase and solved it.
    3) Commit & Push the code to the github.
    
    Your flow of work:
    1) Plan
    2) Analysis
    3) Recheck
    4) Excute
                              
    RULES:
    - ALWAYS USE THE `excute` TOOL FOR ANY FILE OR COMMAND OPERATION
    - NEVER GUESS FILE CONTENT, ALWAYS WRITE EXPLICITLY
    - ONLY OPERATE INSIDE THE PROJECT DIRECTORY.
                              
    YOU WILL WORK AS AGENT NOT A AI CHATBOT.
                              
    Response Format after make complete your task:
    {
        "summary": "I found 3 Python files in your project",
        "action": "list_files",
        "result": "main.py, utils/tool.py, graph.py"
    }         
                     
""")

BASE_DIR = pathlib.Path(".").resolve().parent

def _safe_path(requested: str) -> pathlib.Path:
    resolved = (BASE_DIR / requested).resolve()
    if not resolved.is_relative_to(BASE_DIR):
        raise PermissionError(f"Path outside project directory: {requested}")
    return resolved


def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]

    if last_message.tool_calls:
        return "tools"
    
    return END

ALLOWED_COMMANDS = {
    "python", "python3",
    "pip", "pip3",
    "git",
    "pytest", "black", "flake8",
    "ls", "cat", "pwd", "touch", "mkdir",
    "echo", "which", "node", "npm", "npx"
}

@tool
def run_command(command: str="", path: str="", content: str="") -> str:
    """
    A tool for running commands and writing files.
    - To run a command → provide `command` e.g. "python main.py"
    - To write a file  → provide `path` and `content`
    """
    #______ WRITE FILES _________________________
    if path and content:
        try:
            target = _safe_path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return f"File is created at {path}. Total characters in file {len(content)}"
        except PermissionError as p:
            return f"Permission denied: {p}"
        except Exception as e:
            return f"write the error {e}"
    elif command:
        try:
            part = command.strip().split()

            if not part:
                return f"Empty CMD!"
            
            if part[0] not in ALLOWED_COMMANDS:
                return f"Error: '{part[0]} is not allowed. Allowed: {sorted(ALLOWED_COMMANDS)}"
            
            result = subprocess.run(
                part,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(BASE_DIR),
                shell=False
            )

            output = (result.stdout + result.stderr).strip()

            return output or f"Command run successfully with no output."
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 30 seconds."
        except Exception as e:
            return f"Execution error: {e}"
    else:
        return "Error: provide either `command` to run or `path` + `content` to write a file."      

tools = [run_command]
tool_node = ToolNode(tools)

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0).bind_tools(tools)


def call_llm(state : MessagesState):
    message = state['messages']
    response = model.invoke(message)
    return { "messages" : [response] }

def run_voice_agent():
    """This function for running our cursor voice agent"""
    choices = """
        1. Voice
        2. Text
    """
    user_input = int(input("How do you want to interact the AI. \n " + choices))

    if user_input == 1:
        query = speech_to_text()
    elif user_input == 2:
        query = input("Write what you want")
        
    if query in ["exit", "quit", "Bye"]:
        return False
    
    result = graph.invoke({"messages": [system_prompt, HumanMessage(content=query)]}, config)

    if isinstance(result["messages"][-1].content, list):
        final_message = " ".join(
            block.get("text","") if isinstance(block, dict) else str(block)
            for block in result["messages"][-1].content
        )
    else:
        final_message = result["messages"][-1].content

    final_message = final_message.strip()

    if final_message.startswith("```"):
        final_message = final_message.split("```")[1]  # get content between fences
        if final_message.startswith("json"):
            final_message = final_message[4:]  

    try:
        response = json.loads(final_message.strip())
        summary = response["summary"]
        print(f"Action : {response.get('action','')}")
        print(f"Result : {response.get('result','')}")
    except json.JSONDecodeError:
        summary = final_message

    print(f"AI is speaking : {summary}")
    data = text_to_speech(summary)
    print(data)
    return True
    
graph = StateGraph(MessagesState)

graph.add_node("agent", call_llm)
graph.add_node("tools", tool_node)

graph.add_edge(START, "agent")
graph.add_conditional_edges(
    "agent",
    should_continue,
    ["tools", END]
)
graph.add_edge("tools","agent")
graph = graph.compile(checkpointer=MemorySaver())

while True:
    if not run_voice_agent():
        break