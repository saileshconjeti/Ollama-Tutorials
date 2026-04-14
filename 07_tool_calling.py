# File name: 07_tool_calling.py
# Purpose: Demonstrate tool-calling where the model requests a function and the app executes it.
# Concepts covered: Tool schemas, tool-call detection, application-executed tools, agentic control loop.
# Prerequisites: `ollama serve` running, model `qwen3:4b` pulled, `pip install ollama`.
# How to run: `python 07_tool_calling.py`
# What students should observe: The model may return tool-call objects first; Python executes the tool and sends result back.
# Usage example:
#   python 07_tool_calling.py
# Author: Dr. Sailesh Conjeti
# Course: Generative and Agentic AI

import json
from ollama import chat

# Tool schema advertised to the model.
# Important: this defines what can be requested, but the model does not execute tools itself.
tools = [
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "Add two numbers together.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        }
    }
]

messages = [
    {"role": "user", "content": "What is 37 + 58?"}
]

# First model call: ask the question while exposing available tools.
response = chat(
    model="qwen3:4b",
    messages=messages,
    tools=tools,
)

message = response["message"]

# Print raw model output so students can inspect whether a tool call was requested.
print("Model response:")
print(json.dumps(message.model_dump(), indent=2))

# Agentic pattern:
# if tool_calls are present, the application executes tools and returns tool results to the model.
tool_calls = message.tool_calls or []

if not tool_calls:
    # Some runs may produce a direct text answer without a tool call.
    print("\nNo tool call was requested by the model.")
    print(message.content)
else:
    for call in tool_calls:
        fn_name = call.function.name
        args = call.function.arguments

        if fn_name == "add_numbers":
            # The Python application performs the actual computation.
            result = args["a"] + args["b"]

            # Send back both the assistant tool-call message and tool output.
            messages.append(message.model_dump())
            messages.append({
                "role": "tool",
                "content": json.dumps({"result": result})
            })

            # Second model call: model reads tool result and produces final user-facing answer.
            final_response = chat(
                model="qwen3:4b",
                messages=messages,
                tools=tools,
            )

            print("\nFinal answer:")
            print(final_response["message"].content)
