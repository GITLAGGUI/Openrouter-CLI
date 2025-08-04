# Quick Start Guide - Enhanced Personal AI Agent

## Installation & Setup

1. **Install dependencies:**
```bash
pip install openai requests
```

2. **Run the agent:**
```bash
python enhanced_ai_agent.py
```

## Quick Examples

### Basic File Operations
```python
from enhanced_ai_agent import PersonalAIAgent

# Initialize
agent = PersonalAIAgent("your-api-key", "qwen/qwen3-coder:free")

# Create/modify files
agent.write_file("script.py", "print('Hello World')")

# Read files with metadata
result = agent.read_file("script.py")
print(f"Language: {result['metadata']['language']}")

# Search files
results = agent.search_files(".", file_extension=".py")
```

### AI-Powered Code Modification
```python
# Let AI modify your code
agent.intelligent_code_modification(
    "script.py", 
    "Add error handling and logging"
)
```

### Web Content Fetching
```python
# Fetch web content
result = agent.fetch_url("https://api.github.com/zen")
print(result['raw_content'])
```

### Code Analysis
```python
# Analyze code structure
analysis = agent.analyze_code("complex_script.py")
print(f"Functions: {len(analysis['analysis']['functions'])}")
```

## Available Models
- `qwen/qwen3-coder:free` (Best for coding)
- `z-ai/glm-4.5-air:free` (General purpose)
- `openrouter/horizon-beta:free` (Experimental)
- `deepseek/deepseek-r1-0528:free` (Deep reasoning)

## Safety Features
- Automatic backups before modifications
- Undo last operation: `agent.undo_last_operation()`
- Operation history: `agent.get_operation_history()`

## Supported Languages
Python, JavaScript, TypeScript, Java, C/C++, C#, PHP, Ruby, Go, Rust, Swift, Kotlin, Scala, R, SQL, Shell scripts, and more!

Run `python demo.py` to see it in action!