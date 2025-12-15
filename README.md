# Portable Windows Ollama Agent

The Portable Windows Ollama Agent is a self-contained AI assistant specifically designed to work in any directory without path confusion issues.

## Purpose

This agent addresses the common problem where AI agents create files in unexpected directories. The Portable Agent always operates in the current working directory where it's placed, eliminating path confusion issues.

## Features

- **Self-Contained**: The single `portable_agent.py` file contains *everything*—no external dependencies like `tools.py` or config files needed.
- **Robust Tool Execution**: Automatically handles complex model outputs, including multiple tool calls in one go and markdown-wrapped JSON.
- **Recursive Action Loop**: Can perform chains of actions (e.g., create folder -> write multiple files -> run build command) in a single turn.
- **Visible Feedback**: Prints clear logs of what tools are being executed and their output.
- **Location-Aware**: Always works in the current directory where the script is placed.
- **Windows-Optimized**: Tailored specifically for Windows environments.

## Usage

### Method 1: Manual Copy
1. Copy `portable_agent.py` to ANY directory you want to work in.
2. Open a terminal there.
3. Run: `python portable_agent.py`

That's it. The agent will now create files and folders *only* inside that directory.

## What It Can Do
- **Create Apps**: "Create a React app called my-app"
- **Write Code**: "Make a Python script that scrapes a website"
- **Build Projects**: "Turn this HTML into an Electron app and build the EXE"
- **Manage Files**: "Organize this folder by file type"

## Key Commands

- `models` - List all available Ollama models with sizes
- `running` - Show currently running Ollama models  
- `switch <model>` - Change to a different model (e.g. `switch qwen2.5-coder:7b`)
- `pwd` - Show current working directory
- `ls` - List directory contents
- `save` - Save conversation history to file
- `clear` - Clear conversation history
- `help` - Show available commands
- `exit` - Exit the agent

## Requirements

- Python 3.7+
- Ollama running on http://localhost:11434
- Windows 10 or 11

## Troubleshooting
- **If tools fail**: The agent now auto-corrects most JSON errors. If it fails, try rephrasing your command simply.
- **If it hangs**: Check if Ollama is running and responsive.
- **Debug Logs**: The agent prints `[Agent] Executing tool...` so you can verify it's working.
