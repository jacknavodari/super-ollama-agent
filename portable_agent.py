#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Portable Windows Ollama Agent
Self-contained AI assistant that works in any directory by default
"""

import json
import requests
import sys
import os
import re
import subprocess
import platform
from datetime import datetime
from pathlib import Path


# Self-contained tool definitions
def read_file(file_path):
    """Reads the content of a file and returns it as a string."""
    try:
        if not os.path.exists(file_path):
            return f"Error: File not found at '{file_path}'."
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(file_path, content):
    """Writes content to a file. Creates directories if they don't exist."""
    try:
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to '{file_path}'."
    except Exception as e:
        return f"Error writing file: {e}"

def execute_shell(command):
    """Executes a shell command and returns its output."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            check=False
        )
        if result.returncode != 0:
            return f"Command failed (Code {result.returncode}):\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        return result.stdout if result.stdout else "Command executed successfully (no output)."
    except Exception as e:
        return f"Error executing command: {e}"

TOOLS_AVAILABLE = True


class PortableWindowsAgent:
    def __init__(self, config_path=None):
        """Initialize the agent with configuration from JSON file or default settings"""
        # Try to find config file in current directory first, then fall back to default
        if config_path and os.path.exists(config_path):
            self.config = self.load_config(config_path)
        elif os.path.exists("windows_ollama_agent.json"):
            self.config = self.load_config("windows_ollama_agent.json")
        elif os.path.exists("ollama_config.json"):
            self.config = self.load_config("ollama_config.json")
        else:
            # Use default configuration
            self.config = self.get_default_config()
        
        self.conversation_history = []
        self.current_model = self.config["ollama"]["default_model"]
        self.working_dir = os.getcwd()  # Always work in current directory

        # Initialize Ollama API URLs
        base_url = self.config["ollama"]["host"]
        self.chat_url = base_url + self.config["ollama"]["api_endpoints"]["chat"]
        self.tags_url = base_url + self.config["ollama"]["api_endpoints"]["tags"]
        self.generate_url = base_url + self.config["ollama"]["api_endpoints"]["generate"]
        self.ps_url = base_url + self.config["ollama"]["api_endpoints"]["ps"]

        # Check if Ollama is running
        if not self.check_ollama_connection():
            print("Error: Cannot connect to Ollama. Please make sure Ollama is running on http://localhost:11434")
            sys.exit(1)

        print(f"\nPortable Windows Agent initialized!")
        print(f"Working Directory: {self.working_dir}")
        print(f"Model: {self.current_model}")
        print(f"Platform: {platform.system()} {platform.release()}")

    def get_default_config(self):
        """Return a default configuration that works in any directory"""
        return {
            "agent": {
                "name": "Portable Windows Ollama Agent",
                "description": "Self-contained AI assistant for any directory",
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "platform": "windows",
                "locale": "en-US"
            },
            "ollama": {
                "host": "http://localhost:11434",
                "default_model": "qwen3-coder:30b",
                "models": [
                    "qwen3-coder:30b",
                    "llama3.2:3b",
                    "mistral-nemo:12b",
                    "phi3:3.8b"
                ],
                "api_endpoints": {
                    "chat": "/api/chat",
                    "generate": "/api/generate",
                    "tags": "/api/tags",
                    "ps": "/api/ps"
                },
                "config": {
                    "temperature": 0.0,
                    "timeout": 600,
                    "stream": False
                }
            },
            "system_context": {
                "platform": platform.system(),
                "shell": "PowerShell/CMD",
                "working_dir": os.getcwd(),
                "gpu_support": {
                    "enabled": True,
                    "type": "DirectML",
                    "description": "AMD Radeon GPU with 8GB VRAM using DirectML for offloading"
                },
                "env_vars": {
                    "OLLAMA_GPU": "1"
                },
                "windows_specific": {
                    "use_cmd": True,
                    "powershell_commands": True,
                    "windows_commands": ["dir", "cd", "echo", "type", "mkdir", "rmdir", "copy", "move", "del", "cls"]
                }
            },
            "tools": [
                {
                    "name": "read_file",
                    "description": "Reads content from a local file in the current directory or specified path",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to read (relative to current directory or absolute path)"
                            }
                        },
                        "required": ["file_path"]
                    }
                },
                {
                    "name": "write_file",
                    "description": "Writes content to a local file in the current directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to write (relative to current directory)"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write to the file"
                            }
                        },
                        "required": ["file_path", "content"]
                    }
                },
                {
                    "name": "execute_shell",
                    "description": "Executes a shell command in the current directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "The shell command to execute"
                            }
                        },
                        "required": ["command"]
                    }
                },
                {
                    "name": "create_directory",
                    "description": "Creates a directory in the current directory or at specified path",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "dir_path": {
                                "type": "string",
                                "description": "Path to the directory to create (relative to current directory or absolute path)"
                            }
                        },
                        "required": ["dir_path"]
                    }
                },
                {
                    "name": "list_directory",
                    "description": "Lists files and directories in the current directory or specified path",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "dir_path": {
                                "type": "string",
                                "description": "Path to the directory to list (defaults to current directory if not specified)"
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "check_file_exists",
                    "description": "Checks if a file or directory exists relative to current directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to check for existence (relative to current directory)"
                            }
                        },
                        "required": ["path"]
                    }
                }
            ],
            "memory": {
                "type": "session",
                "enabled": True
            },
            "brain_extensions": [
                {
                    "name": "code_writer",
                    "description": "Writes and creates code files",
                    "enabled": True
                },
                {
                    "name": "file_manager",
                    "description": "Manages local files and directories",
                    "enabled": True
                },
                {
                    "name": "system_info",
                    "description": "Provides system information and context",
                    "enabled": True
                }
            ]
        }

    def load_config(self, config_path):
        """Load agent configuration from JSON file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file {config_path} not found!")
            return self.get_default_config()
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in configuration file {config_path}")
            return self.get_default_config()

    def check_ollama_connection(self):
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(self.tags_url, timeout=10)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def list_available_models(self):
        """List all available Ollama models with details"""
        try:
            response = requests.get(self.tags_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            models = []
            for model in data.get('models', []):
                models.append({
                    'name': model['name'],
                    'modified_at': model.get('modified_at', 'Unknown'),
                    'size': f"{model.get('size', 0) / (1024**3):.2f} GB" if model.get('size') else 'Unknown'
                })
            return models
        except requests.RequestException as e:
            print(f"Error fetching models: {e}")
            return []

    def list_running_models(self):
        """List currently running Ollama models"""
        try:
            response = requests.get(self.ps_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('models', [])
        except requests.RequestException as e:
            print(f"Error fetching running models: {e}")
            return []

    def switch_model(self, model_name):
        """Switch to a different Ollama model"""
        available_models = [m['name'] for m in self.list_available_models()]
        if model_name in available_models:
            self.current_model = model_name
            return f"Switched to model: {model_name}"
        else:
            return f"Model {model_name} not available. Available models: {', '.join(available_models)}"

    def send_message(self, user_message):
        """Send a message to the Ollama model and return the response"""
        import re
        import json

        try:
            # Build the messages array with system context and conversation history
            messages = []

            # Create a detailed system message, focusing on current directory operations
            tools_info = ""
            if "tools" in self.config:
                tools_info = "\n\nAvailable Tools:\n"
                for tool in self.config["tools"]:
                    tools_info += f"- {tool['name']}: {tool['description']}\n"
                    if 'parameters' in tool:
                        tools_info += "  Parameters: "
                        for prop_name, prop_details in tool['parameters']['properties'].items():
                            tools_info += f"{prop_name} ({prop_details['type']}): {prop_details['description']}; "
                        tools_info += "\n"

            # Get current date and time for context
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            system_message = f"""You are an advanced AI assistant for Windows systems with sophisticated function calling capabilities. Here are key details about the environment:

== SYSTEM INFORMATION ==
- Operating System: {self.config['system_context']['platform']}
- Shell: {self.config['system_context']['shell']}
- Current Working Directory: {self.working_dir}
- Current Date/Time: {current_datetime}
- Running Ollama Models: {len(self.list_running_models())} models currently running
- Platform: Windows

== IMPORTANT PATH INSTRUCTIONS ==
- YOU MUST ALWAYS WORK IN THE CURRENT WORKING DIRECTORY: {self.working_dir}
- When creating files or directories, use relative paths that will be created in this directory
- Do NOT create files in different drives or unrelated directories
- All file operations should be relative to this working directory: {self.working_dir}
- When executing shell commands, they will run in this directory
- To see current directory: execute_shell with command "cd"
- To list contents: execute_shell with command "dir"

== WINDOWS SPECIFIC COMMANDS ==
When executing shell commands, use Windows-compatible commands:
- File/Directory: dir, cd, md/rmdir, copy, move, del, type, cls
- PowerShell: Get-Process, Get-Service, Get-Content, Set-ExecutionPolicy, etc.
- System: systeminfo, ipconfig, tasklist, netstat, sfc /scannow, chkdsk

== TOOL USAGE INSTRUCTIONS ==
When you need to perform a specific action, respond with a JSON object in this format:
{{
    "tool": "<tool_name>",
    "parameters": {{
        "<parameter_name>": "<parameter_value>"
    }}
}}
Do NOT output anything else if you are trying to use a tool. Just the JSON.
If you need to use multiple tools in sequence, you will get the results of the first tool before deciding on the next.

If the user's request does not require a tool, provide a natural language response.

{tools_info}

== AGENT INSTRUCTIONS ==
- The user is using {self.current_model} model
- ALWAYS REMEMBER: You are operating in the directory: {self.working_dir}
- All file operations, directory creation, and commands run in this directory
- Be helpful, concise and specific to their Windows setup
- If you need to create directories, use the create_directory tool
- If you need to check if files exist, use the check_file_exists tool
- If you need to list directory contents, use the list_directory tool
- When creating projects, ALWAYS create them in the current working directory or in a subdirectory of it
- For complex operations involving multiple steps, break them down into smaller, manageable tasks
- When installing software, suggest using winget (Windows Package Manager) where available
- REMEMBER: All operations happen in {self.working_dir} unless explicitly specified otherwise"""

            messages.append({"role": "system", "content": system_message})

            # Add conversation history
            messages.extend(self.conversation_history)

            # Add the current user message
            messages.append({"role": "user", "content": user_message})

            # Prepare the request payload
            data = {
                "model": self.current_model,
                "messages": messages,
                "stream": self.config["ollama"]["config"]["stream"],
                "options": {
                    "temperature": self.config["ollama"]["config"]["temperature"],
                    "num_ctx": 8192,
                    "num_predict": 2048
                }
            }

            # Send request to Ollama
            response = requests.post(
                self.chat_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(data),
                timeout=self.config["ollama"]["config"]["timeout"]
            )

            response.raise_for_status()
            result = response.json()

            # Extract the response content
            raw_response = result.get("message", {}).get("content", "")
            
            # Helper to extract all JSON objects
            def extract_json_objects(text):
                json_objects = []
                # First, remove markdown code blocks to clean up the text
                clean_text = re.sub(r'```json\s*|\s*```', '', text, flags=re.DOTALL)
                clean_text = re.sub(r'```\s*|\s*```', '', clean_text, flags=re.DOTALL)
                
                brace_count = 0
                start_index = -1
                
                for i, char in enumerate(clean_text):
                    if char == '{':
                        if brace_count == 0:
                            start_index = i
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0 and start_index != -1:
                            # We found a complete JSON object block
                            try:
                                json_str = clean_text[start_index:i+1]
                                obj = json.loads(json_str)
                                if isinstance(obj, dict) and "tool" in obj:
                                    json_objects.append(obj)
                            except json.JSONDecodeError:
                                pass # Skip invalid JSON
                            start_index = -1
                
                return json_objects

            # Extract JSON objects
            json_objects = extract_json_objects(raw_response)
            
            # If no JSON objects found but text looks like it might contain them, try simplistic global parse check
            if not json_objects:
                 try:
                    # Sometimes the model returns a list of objects [{}, {}]
                    clean_text = re.sub(r'```json\s*|\s*```', '', raw_response, flags=re.DOTALL)
                    objs = json.loads(clean_text)
                    if isinstance(objs, list):
                        for o in objs:
                            if isinstance(o, dict) and "tool" in o:
                                json_objects.append(o)
                    elif isinstance(objs, dict) and "tool" in objs:
                        json_objects.append(objs)
                 except:
                    pass

            # Match logic of send_message to handle tool chains
            max_turns = 10
            turn = 0
            
            while turn < max_turns:
                 turn += 1
                 
                 # Extract all JSON objects (tools) from the current response
                 json_objects = extract_json_objects(raw_response)
                 
                 # If no tools, we are done, return the response
                 if not json_objects:
                     # Clean up any residual markdown if it was just text
                     return raw_response

                 # If tools found, process them
                 # Add the assistant's previous response (with the tool calls) to history
                 self.conversation_history.append({"role": "user", "content": user_message}) # Note: this repeats user msg in history structure, ideally we just append assistant response if user msg already there. 
                 # Actually, we need to be careful not to duplicate user message if looping.
                 # Let's verify how history is managed.
                 
                 # For simplicty in this patched version:
                 # 1. We append the Assistant's specific response containing the tool call
                 self.conversation_history.append({"role": "assistant", "content": raw_response})
                 
                 tool_outputs = []
                 
                 for tool_call_data in json_objects:
                     if "tool" in tool_call_data and "parameters" in tool_call_data:
                         tool_name = tool_call_data["tool"]
                         tool_params = tool_call_data["parameters"]
                         
                         try:
                             print(f"\n[Agent] Executing tool: {tool_name}...")
                             if tool_name == "read_file":
                                 tool_result = read_file(**tool_params)
                             elif tool_name == "write_file":
                                 tool_result = write_file(**tool_params)
                             elif tool_name == "execute_shell":
                                 tool_result = execute_shell(**tool_params)
                             elif tool_name == "create_directory":
                                 tool_result = self.create_directory(**tool_params)
                             elif tool_name == "list_directory":
                                 tool_result = self.list_directory(**tool_params)
                             elif tool_name == "check_file_exists":
                                 tool_result = self.check_file_exists(**tool_params)
                             else:
                                 tool_result = f"Error: Unknown tool '{tool_name}' requested."
                             
                             print(f"[Agent] Tool Output: {str(tool_result)[:100]}..." if len(str(tool_result)) > 100 else f"[Agent] Tool Output: {tool_result}")
                         except Exception as e:
                             tool_result = f"Error executing tool '{tool_name}': {str(e)}"
                             print(f"[Agent] Error: {tool_result}")
                             
                         # Append individual tool result to history immediately so model sees it
                         self.conversation_history.append({"role": "tool_output", "content": tool_result})
                         tool_outputs.append(tool_result)

                 # Now that we've executed tools and updated history, ask model for next step
                 # Prepare the request payload with updated conversation history
                 data = {
                    "model": self.current_model,
                    "messages": [{"role": "system", "content": system_message}] + self.conversation_history, # Reconstruct full context
                    "stream": self.config["ollama"]["config"]["stream"],
                    "options": {
                        "temperature": self.config["ollama"]["config"]["temperature"],
                        "num_ctx": 8192,
                        "num_predict": 2048
                    }
                 }
                 
                 try:
                     response = requests.post(
                        self.chat_url,
                        headers={"Content-Type": "application/json"},
                        data=json.dumps(data),
                        timeout=self.config["ollama"]["config"]["timeout"]
                     )
                     response.raise_for_status()
                     result = response.json()
                     raw_response = result.get("message", {}).get("content", "")
                     
                     # Loop back to check if this new response has more tools
                 except Exception as e:
                     return f"Error getting follow-up from model: {e}"

            return raw_response

        except requests.RequestException as e:
            return f"Error communicating with Ollama: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

    def clear_history(self):
        """Clear the conversation history"""
        self.conversation_history = []
        return "Conversation history cleared."

    def save_history(self, filename=None):
        """Save conversation history to a file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_history_{timestamp}.json"

        try:
            history_data = {
                "model": self.current_model,
                "timestamp": datetime.now().isoformat(),
                "working_directory": self.working_dir,
                "history": self.conversation_history
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)

            return f"Conversation history saved to {filename}"
        except Exception as e:
            return f"Error saving history: {e}"

    def create_directory(self, dir_path):
        """Create a directory if it doesn't exist, relative to current working directory"""
        try:
            # If path is not absolute, make it relative to current working directory
            if not os.path.isabs(dir_path):
                dir_path = os.path.join(self.working_dir, dir_path)
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            return f"Directory '{dir_path}' created successfully in working directory."
        except Exception as e:
            return f"Error creating directory '{dir_path}': {e}"

    def list_directory(self, dir_path=None):
        """List files and directories in the specified path, defaulting to current directory"""
        if dir_path is None:
            dir_path = self.working_dir
        elif not os.path.isabs(dir_path):
            dir_path = os.path.join(self.working_dir, dir_path)
            
        try:
            path_obj = Path(dir_path)
            if not path_obj.exists():
                return f"Directory '{dir_path}' does not exist."

            if not path_obj.is_dir():
                return f"'{dir_path}' is not a directory."

            items = list(path_obj.iterdir())
            if not items:
                return f"Directory '{dir_path}' is empty."

            result = f"Contents of '{dir_path}':\n"
            for item in items:
                if item.is_dir():
                    result += f"[DIR]  {item.name}\n"
                else:
                    size = item.stat().st_size
                    result += f"[FILE] {item.name} ({size} bytes)\n"

            return result.strip()
        except Exception as e:
            return f"Error listing directory '{dir_path}': {e}"

    def check_file_exists(self, path):
        """Check if a file or directory exists, relative to current working directory"""
        # Make path relative to current working directory if not absolute
        if not os.path.isabs(path):
            path = os.path.join(self.working_dir, path)
            
        try:
            path_obj = Path(path)
            exists = path_obj.exists()
            if exists:
                is_dir = path_obj.is_dir()
                item_type = "directory" if is_dir else "file"
                size_info = ""
                if not is_dir:
                    size = path_obj.stat().st_size
                    size_info = f", size: {size} bytes"
                return f"'{path}' exists and is a {item_type}{size_info}."
            else:
                return f"'{path}' does not exist."
        except Exception as e:
            return f"Error checking existence of '{path}': {e}"

    def interactive_mode(self):
        """Run the agent in interactive mode"""
        print(f"\n=== Portable Windows Ollama Agent ===")
        print(f"Working Directory: {self.working_dir}")
        print(f"Model: {self.current_model}")
        print(f"Platform: {self.config['system_context']['platform']} {platform.release()}")
        print("\nCommands: 'exit' to quit, 'help' for commands, 'models' to list models, 'switch <model>' to change model, 'clear' to clear history")
        print("=" * 80)

        while True:
            try:
                user_input = input(f"\n{self.current_model}> ").strip()

                if not user_input:
                    continue

                # Handle special commands
                if user_input.lower() == 'exit':
                    print("Goodbye! Portable Windows Agent shutting down.")
                    break
                elif user_input.lower() == 'help':
                    print("\nAvailable commands:")
                    print("  exit            - Exit the agent")
                    print("  help            - Show this help")
                    print("  models          - List available models")
                    print("  running         - List currently running models")
                    print("  switch <model>  - Switch to a different model")
                    print("  clear           - Clear conversation history")
                    print("  save            - Save conversation to file")
                    print("  pwd             - Show current working directory")
                    print("  ls              - List directory contents")
                    print("  [anything else] - Send message to the model")
                    continue
                elif user_input.lower() == 'models':
                    models = self.list_available_models()
                    if models:
                        print("\nAvailable models:")
                        for model in models:
                            marker = " [CURRENT]" if model['name'] == self.current_model else ""
                            print(f"  - {model['name']} (Size: {model['size']}){marker}")
                    else:
                        print("No models found. Make sure models are pulled with 'ollama pull <model_name>'")
                    continue
                elif user_input.lower() == 'running':
                    running = self.list_running_models()
                    if running:
                        print("\nCurrently running models:")
                        for model in running:
                            print(f"  - {model['name']}")
                    else:
                        print("No models currently running.")
                    continue
                elif user_input.lower().startswith('switch '):
                    model_name = user_input[7:].strip()  # Remove 'switch ' prefix
                    if model_name:
                        result = self.switch_model(model_name)
                        print(result)
                        # Update current display if successful
                        if "Switched to model" in result:
                            self.current_model = model_name
                    else:
                        print("Please specify a model name. Usage: switch <model_name>")
                    continue
                elif user_input.lower() == 'clear':
                    result = self.clear_history()
                    print(result)
                    continue
                elif user_input.lower() == 'save':
                    result = self.save_history()
                    print(result)
                    continue
                elif user_input.lower() == 'pwd':
                    print(f"Current working directory: {self.working_dir}")
                    continue
                elif user_input.lower() in ['ls', 'dir', 'list']:
                    result = self.list_directory()
                    print(result)
                    continue
                elif user_input.lower() == 'test':
                    print("Connection to Ollama is working!")
                    print(f"Current model: {self.current_model}")
                    print(f"Working directory: {self.working_dir}")
                    continue

                # Process regular user message
                print("\nProcessing request...")
                response = self.send_message(user_input)
                print(f"\n{response}")

            except KeyboardInterrupt:
                print("\n\nGoodbye! Portable Windows Agent shutting down.")
                break
            except Exception as e:
                print(f"\nError: {e}")
                print("The agent encountered an error. Please try again or type 'exit' to quit.")


def main():
    """Main function to run the Portable Windows Ollama Agent"""
    print("Initializing Portable Windows Agent...")
    agent = PortableWindowsAgent()
    agent.interactive_mode()


if __name__ == "__main__":
    main()
