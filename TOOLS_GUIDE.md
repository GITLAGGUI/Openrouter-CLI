# OpenRouter CLI Tools System

## Overview

The OpenRouter CLI now includes a comprehensive tools system similar to Forge CLI, Claude CLI, and Gemini CLI. This system provides powerful functionality accessible through the interactive chat interface using `/tools` and `/help` commands.

## Features

### Interactive Tools System
- **Tool Discovery**: Use `/tools` to list all available tools
- **Tool Help**: Use `/tools <tool_name>` to get detailed help
- **Tool Execution**: Use `/tools <tool_name> param=value` to execute tools
- **14 Built-in Tools**: Covering file operations, code analysis, web interactions, and AI capabilities

### File Operations Tools
- `fs_read` - Read file contents with metadata and analysis
- `fs_write` - Write content to a file with automatic backup
- `fs_search` - Search for files and content with advanced filtering
- `fs_remove` - Remove a file with optional backup
- `fs_undo` - Undo the last file operation

### Code Analysis Tools
- `code_analyze` - Analyze code structure, functions, classes, and imports
- `code_modify` - Modify code using AI with natural language instructions
- `code_review` - Get AI-powered code review and suggestions

### Web Operations Tools
- `web_fetch` - Fetch content from URLs with smart text extraction
- `web_api` - Make HTTP API requests with custom methods and data

### System Tools
- `shell_exec` - Execute shell commands safely
- `env_info` - Get system and environment information

### AI Tools
- `ai_chat` - Direct AI chat with custom parameters
- `ai_summarize` - Summarize text or file content using AI

## Getting Started

### 1. Start Interactive Chat
```bash
python -m openrouter_cli.main chat interactive
```

### 2. Use Commands
The interactive chat now supports these commands:

- `/help` - Show available commands
- `/tools` - List all available tools
- `/tools <tool_name>` - Get help for a specific tool
- `/tools <tool_name> [params]` - Execute a tool
- `/model <name>` - Switch AI model
- `/clear` - Clear conversation history
- `/history` - Show conversation history
- `/exit` - End the chat session

## Tool Usage Examples

### File Operations
```bash
# Read a file
/tools fs_read path="script.py"

# Read specific lines
/tools fs_read path="script.py" lines="1-20"

# Write content to a file
/tools fs_write path="newfile.py" content="print('Hello World')"

# Search for Python files containing "class"
/tools fs_search directory="./src" extension=".py" content="class"

# Remove a file with backup
/tools fs_remove path="oldfile.py"

# Undo the last operation
/tools fs_undo
```

### Code Analysis
```bash
# Analyze code structure
/tools code_analyze path="main.py"

# Detailed analysis with AI insights
/tools code_analyze path="main.py" detailed=true

# Modify code with AI
/tools code_modify path="script.py" instruction="Add error handling to the main function"

# Get code review
/tools code_review path="mycode.py" focus="security"
```

### Web Operations
```bash
# Fetch webpage content
/tools web_fetch url="https://example.com"

# Extract clean text from HTML
/tools web_fetch url="https://example.com" extract_text=true

# Save content to file
/tools web_fetch url="https://api.github.com/users/octocat" save_to="user.json"

# Make API request
/tools web_api url="https://api.github.com/users/octocat" method="GET"

# POST request with data
/tools web_api url="https://httpbin.org/post" method="POST" data='{"key": "value"}'
```

### System Tools
```bash
# Get system information
/tools env_info

# Execute shell command
/tools shell_exec command="ls -la"

# Execute in specific directory
/tools shell_exec command="pwd" cwd="/home/user"
```

### AI Tools
```bash
# Direct AI chat
/tools ai_chat prompt="Explain quantum computing"

# AI chat with custom parameters
/tools ai_chat prompt="Write a Python function" temperature=0.3 model="qwen/qwen3-coder:free"

# Summarize text
/tools ai_summarize content="Long text to summarize..." length="short"

# Summarize file
/tools ai_summarize file_path="document.txt" length="medium"
```

## Tool Parameters

### Parameter Types
- `string` - Text values (use quotes if contains spaces)
- `boolean` - true/false values
- `integer` - Numeric values
- `float` - Decimal values

### Parameter Examples
```bash
# String parameters
/tools fs_read path="my file.py"
/tools fs_read path=script.py

# Boolean parameters
/tools code_analyze path="main.py" detailed=true
/tools fs_write path="test.py" content="print('hi')" backup=false

# Numeric parameters
/tools ai_chat prompt="Hello" temperature=0.7
/tools shell_exec command="sleep 5" timeout=10
```

## Advanced Features

### Error Handling
- All tools include comprehensive error handling
- Failed operations provide clear error messages
- File operations create automatic backups

### Safety Features
- Shell command execution includes safety checks
- Dangerous commands are blocked
- File operations support undo functionality

### AI Integration
- Code modification uses AI for natural language instructions
- Code review provides AI-powered insights
- Summarization uses AI for intelligent text processing

## Configuration

The tools system uses your existing OpenRouter CLI configuration:

```yaml
api:
  key: "sk-or-v1-..."
  base_url: "https://openrouter.ai/api/v1"
  default_model: "qwen/qwen3-coder:free"

preferences:
  backup_enabled: true
  backup_directory: "~/.openrouter-cli/backups"
  log_level: "info"
```

## Comparison with Other CLI Tools

### Similar to Forge CLI
- `/tools` command to list available tools
- Tool execution with parameters
- File operations and code analysis
- Interactive help system

### Similar to Claude CLI
- AI-powered code modification
- Natural language instructions
- Comprehensive error handling
- Chat-based interface

### Similar to Gemini CLI
- Multi-modal tool support
- Web content fetching
- System integration
- Advanced parameter handling

## Troubleshooting

### Common Issues

1. **Tool not found**
   - Use `/tools` to see available tools
   - Check tool name spelling

2. **Parameter errors**
   - Use `/tools <tool_name>` to see required parameters
   - Check parameter types and values

3. **Permission errors**
   - Check file permissions
   - Ensure write access to target directories

4. **API errors**
   - Verify OpenRouter API key is configured
   - Check internet connection

### Getting Help
```bash
# List all tools
/tools

# Get help for specific tool
/tools fs_read

# Show all commands
/help
```

## Examples Workflow

### Complete Development Workflow
```bash
# Start interactive chat
python -m openrouter_cli.main chat interactive

# Analyze existing code
/tools code_analyze path="src/main.py" detailed=true

# Get AI code review
/tools code_review path="src/main.py" focus="performance"

# Modify code based on review
/tools code_modify path="src/main.py" instruction="Optimize the main loop for better performance"

# Search for related files
/tools fs_search directory="src" extension=".py" content="main"

# Fetch documentation
/tools web_fetch url="https://docs.python.org/3/library/os.html" extract_text=true save_to="docs.txt"

# Summarize documentation
/tools ai_summarize file_path="docs.txt" length="medium"

# Check system info
/tools env_info
```

This tools system makes the OpenRouter CLI as powerful and user-friendly as other leading CLI tools while leveraging the OpenRouter AI platform for enhanced capabilities.