
# OpenRouter CLI


A powerful command-line interface for AI-powered file operations, code analysis, and web interactions using OpenRouter as the AI provider.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![OpenRouter](https://img.shields.io/badge/AI-OpenRouter-orange.svg)](https://openrouter.ai)


## Features


### Interactive Tools System
- **Tool Discovery**: Use `/tools` to list 14+ available tools in interactive chat
- **Tool Execution**: Execute tools with `/tools <tool_name> [params]` syntax
- **Comprehensive Help**: Get detailed help with `/tools <tool_name>`
- **Similar to Forge/Claude/Gemini CLI**: Familiar command structure and functionality


### File Operations
- **Read Files**: Display file contents with metadata
- **Write Files**: Create or modify files with automatic backup
- **Search Files**: Advanced file and content search with regex support
- **Remove Files**: Safe file deletion with backup options
- **Undo Operations**: Revert the last file operation


### Code Analysis & Modification
- **Analyze Code**: Extract functions, classes, imports, and structure
- **AI-Powered Modification**: Natural language code changes
- **Code Review**: Get AI feedback on code quality and improvements
- **Multi-Language Support**: Python, JavaScript, Java, C++, and more


### Web Operations
- **Fetch URLs**: Download content from websites with smart headers
- **Extract Text**: Clean text extraction from HTML pages
- **API Requests**: Make HTTP requests with custom methods and data
- **Content Processing**: Handle JSON, HTML, and various content types


### AI Chat Interface
- **Interactive Chat**: Continuous conversation with AI models
- **Single Questions**: Quick Q&A with AI
- **Custom Prompts**: Execute prompts with advanced parameters
- **Model Selection**: Choose from multiple AI models


### Configuration Management
- **Secure Storage**: API keys and preferences in config files
- **Environment Variables**: Support for `OPENROUTER_API_KEY`
- **Multiple Models**: Configure different models for different tasks
- **Validation**: Built-in configuration validation and diagnostics


## Installation


### From PyPI (Recommended)
```bash
pip install openrouter-cli
```

### From Source
```bash
git clone https://github.com/openrouter-cli/openrouter-cli.git
cd openrouter-cli
pip install -e .
```


## Setup

1. **Get your OpenRouter API key:**
   - Visit [OpenRouter](https://openrouter.ai/)
   - Create an account and get your API key

2. **Initialize configuration:**
   ```bash
   openrouter-cli config init
   ```
   
3. **Or set your API key in a .env file at the project root:**
   ```env
   OPENROUTER_API_KEY="sk-or-v1-your-api-key-here"
   ```

4. **Verify setup:**
   ```bash
   openrouter-cli doctor
   ```


## Usage


### File Operations

```bash
# Read a file with metadata
openrouter-cli file read script.py

# Write content to a file
openrouter-cli file write newfile.py --content "print('Hello, World!')"

# Search for Python files containing "class"
openrouter-cli file search ./src --extension .py --content "class"

# Remove a file with backup
openrouter-cli file remove oldfile.py

# Undo the last operation
openrouter-cli file undo
```


### Code Analysis & Modification

```bash
# Analyze code structure
openrouter-cli code analyze mycode.py

# Modify code with AI
openrouter-cli code modify script.py "Add error handling to the main function"

# Get code review
openrouter-cli code review mycode.py
```


### Web Operations

```bash
# Fetch webpage content
openrouter-cli web fetch https://example.com --extract-text

# Make API request
openrouter-cli web api https://api.github.com/users/octocat

# Extract text from HTML file
openrouter-cli web extract --from-file page.html
```


### AI Chat

```bash
# Interactive chat session with tools
openrouter-cli chat interactive

# Use tools in chat
/tools                                    # List all available tools
/tools fs_read path="script.py"          # Read a file
/tools code_analyze path="main.py"       # Analyze code structure
/tools web_fetch url="https://example.com" extract_text=true

# Ask a single question
openrouter-cli chat ask "How do I optimize this Python code?"

# Custom prompt with parameters
openrouter-cli chat prompt "Explain quantum computing" --temperature 0.3
```


### Configuration

```bash
# Set API key
openrouter-cli config set api.key "sk-or-v1-your-key"

# Set default model
openrouter-cli config set api.default_model "qwen/qwen3-coder:free"

# List all configuration
openrouter-cli config list

# Validate configuration
openrouter-cli config validate
```


### History Management

```bash
# View operation history
openrouter-cli history list

# Export history to file
openrouter-cli history export history.json

# Clear old entries
openrouter-cli history cleanup --days 30
```


## Command Reference


### Global Options
- `--verbose, -v`: Enable verbose output
- `--config-file`: Use custom configuration file
- `--log-level`: Set logging level (debug, info, warning, error)


### Available Models
- `qwen/qwen3-coder:free` - Specialized for coding tasks
- `z-ai/glm-4.5-air:free` - General purpose AI model
- `openrouter/horizon-beta:free` - Experimental advanced model
- `deepseek/deepseek-r1-0528:free` - Deep reasoning model


### Output Formats
Most commands support multiple output formats:
- `--format human` (default) - Human-readable output
- `--format json` - JSON format
- `--format yaml` - YAML format


## Configuration

Configuration is stored in `~/.openrouter-cli/config.yaml`:

```yaml
api:
  key: "sk-or-v1-..."
  base_url: "https://openrouter.ai/api/v1"
  default_model: "qwen/qwen3-coder:free"

preferences:
  backup_enabled: true
  backup_directory: "~/.openrouter-cli/backups"
  log_level: "info"
  max_history: 100

models:
  coding: "qwen/qwen3-coder:free"
  general: "z-ai/glm-4.5-air:free"
  reasoning: "deepseek/deepseek-r1-0528:free"
```


## Security Features

- **Secure API Key Storage**: Keys stored in protected config files
- **Environment Variable Support**: Use `OPENROUTER_API_KEY` for CI/CD
- **Automatic Backups**: All file modifications create timestamped backups
- **Operation History**: Track all operations for undo capability
- **Input Validation**: Comprehensive validation of all inputs


## Advanced Usage


### Batch Operations
```bash
# Process multiple files
find . -name "*.py" -exec openrouter-cli code analyze {} \;

# Batch web fetching
cat urls.txt | xargs -I {} openrouter-cli web fetch {}
```


### Scripting Integration
```bash
#!/bin/bash
# Automated code review script
for file in src/*.py; do
    echo "Reviewing $file..."
    openrouter-cli code review "$file" --format json > "reviews/$(basename $file).json"
done
```


### Configuration Profiles
```bash
# Use different config for different projects
openrouter-cli --config-file ./project-config.yaml file read script.py
```


## Development


### Running from Source
```bash
git clone https://github.com/openrouter-cli/openrouter-cli.git
cd openrouter-cli
pip install -e ".[dev]"
python -m openrouter_cli.main --help
```


### Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=openrouter_cli

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest -m integration  # Run only integration tests
```


### Code Quality
```bash
# Format code
black openrouter_cli/

# Lint code
flake8 openrouter_cli/

# Type checking
mypy openrouter_cli/
```


## Troubleshooting


### Common Issues

1. **API Key Error**
   ```bash
   openrouter-cli config validate
   openrouter-cli doctor
   ```

2. **Permission Errors**
   - Check file permissions in `~/.openrouter-cli/`
   - Ensure write access to target directories

3. **Network Issues**
   - Check internet connection
   - Verify OpenRouter service status
   - Use `--verbose` for detailed error information

4. **Import Errors**
   ```bash
   pip install --upgrade openrouter-cli
   ```


### Getting Help
```bash
# General help
openrouter-cli --help

# Command-specific help
openrouter-cli file --help
openrouter-cli code analyze --help

# Diagnose issues
openrouter-cli doctor

# Check version and status
openrouter-cli version
```


## Examples


### Complete Workflow Example
```bash
# 1. Initialize and configure
openrouter-cli config init
openrouter-cli config set api.default_model "qwen/qwen3-coder:free"

# 2. Analyze existing code
openrouter-cli code analyze src/main.py --detailed

# 3. Get AI suggestions for improvement
openrouter-cli code review src/main.py

# 4. Make AI-powered modifications
openrouter-cli code modify src/main.py "Add comprehensive error handling"

# 5. Fetch documentation from web
openrouter-cli web fetch https://docs.python.org/3/library/os.html --extract-text --save-to docs.txt

# 6. Interactive planning session
openrouter-cli chat interactive --system "You are a senior software architect"

# 7. Review operation history
openrouter-cli history list --limit 10
```


## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.


### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Acknowledgments

- [OpenRouter](https://openrouter.ai/) for providing the AI API infrastructure
- [Click](https://click.palletsprojects.com/) for the excellent CLI framework
- The open-source community for inspiration and tools


## Support

- 📖 [Documentation](https://openrouter-cli.readthedocs.io/)
- 🐛 [Issue Tracker](https://github.com/openrouter-cli/openrouter-cli/issues)
- 💬 [Discussions](https://github.com/openrouter-cli/openrouter-cli/discussions)
- 📧 [Email Support](mailto:support@openrouter-cli.dev)

---


**Happy Coding with AI!**