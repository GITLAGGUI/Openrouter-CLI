"""
OpenRouter CLI Tools System

This module implements a comprehensive tools system similar to Forge CLI,
providing file operations, code analysis, web interactions, and more.
"""

import os
import json
import re
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import tempfile
import shutil

from ..utils import CLILogger, FileOperationError, APIError


class ToolsManager:
    """
    Manages all available tools for the OpenRouter CLI.
    
    Provides functionality similar to Forge CLI tools with /tools and /help commands.
    """
    
    def __init__(self, agent, logger: CLILogger):
        """Initialize the tools manager."""
        self.agent = agent
        self.logger = logger
        self.tools = {}
        self._register_tools()
    
    def _register_tools(self):
        """Register all available tools."""
        
        # File Operations Tools
        self.tools['fs_read'] = {
            'name': 'fs_read',
            'description': 'Read file contents with metadata and analysis',
            'category': 'File Operations',
            'parameters': {
                'path': {'type': 'string', 'required': True, 'description': 'Path to the file to read'},
                'lines': {'type': 'string', 'required': False, 'description': 'Line range (e.g., "1-50")'}
            },
            'function': self._fs_read
        }
        
        self.tools['fs_create'] = {
            'name': 'fs_create',
            'description': 'Create a new file with content using AI assistance',
            'category': 'File Operations',
            'parameters': {
                'path': {'type': 'string', 'required': True, 'description': 'Path where the file should be created'},
                'content': {'type': 'string', 'required': False, 'description': 'Initial content for the file'},
                'prompt': {'type': 'string', 'required': False, 'description': 'AI prompt to generate file content'},
                'file_type': {'type': 'string', 'required': False, 'description': 'Type of file to create (html, python, javascript, etc.)'},
                'backup': {'type': 'boolean', 'required': False, 'description': 'Create backup if file exists (default: true)'}
            },
            'function': self._fs_create
        }
        
        self.tools['fs_write'] = {
            'name': 'fs_write',
            'description': 'Write content to a file with automatic backup',
            'category': 'File Operations',
            'parameters': {
                'path': {'type': 'string', 'required': True, 'description': 'Path to the file to write'},
                'content': {'type': 'string', 'required': True, 'description': 'Content to write to the file'},
                'backup': {'type': 'boolean', 'required': False, 'description': 'Create backup (default: true)'}
            },
            'function': self._fs_write
        }
        
        self.tools['fs_search'] = {
            'name': 'fs_search',
            'description': 'Search for files and content with advanced filtering',
            'category': 'File Operations',
            'parameters': {
                'directory': {'type': 'string', 'required': True, 'description': 'Directory to search in'},
                'pattern': {'type': 'string', 'required': False, 'description': 'Filename pattern (regex)'},
                'extension': {'type': 'string', 'required': False, 'description': 'File extension filter'},
                'content': {'type': 'string', 'required': False, 'description': 'Content pattern to search for'}
            },
            'function': self._fs_search
        }
        
        self.tools['fs_remove'] = {
            'name': 'fs_remove',
            'description': 'Remove a file with optional backup',
            'category': 'File Operations',
            'parameters': {
                'path': {'type': 'string', 'required': True, 'description': 'Path to the file to remove'},
                'backup': {'type': 'boolean', 'required': False, 'description': 'Create backup (default: true)'}
            },
            'function': self._fs_remove
        }
        
        self.tools['fs_undo'] = {
            'name': 'fs_undo',
            'description': 'Undo the last file operation',
            'category': 'File Operations',
            'parameters': {},
            'function': self._fs_undo
        }
        
        # Code Analysis Tools
        self.tools['code_analyze'] = {
            'name': 'code_analyze',
            'description': 'Analyze code structure, functions, classes, and imports',
            'category': 'Code Analysis',
            'parameters': {
                'path': {'type': 'string', 'required': True, 'description': 'Path to the code file'},
                'detailed': {'type': 'boolean', 'required': False, 'description': 'Include detailed analysis'}
            },
            'function': self._code_analyze
        }
        
        self.tools['code_modify'] = {
            'name': 'code_modify',
            'description': 'Modify code using AI with natural language instructions',
            'category': 'Code Analysis',
            'parameters': {
                'path': {'type': 'string', 'required': True, 'description': 'Path to the code file'},
                'instruction': {'type': 'string', 'required': True, 'description': 'Natural language modification instruction'},
                'backup': {'type': 'boolean', 'required': False, 'description': 'Create backup (default: true)'}
            },
            'function': self._code_modify
        }
        
        self.tools['code_review'] = {
            'name': 'code_review',
            'description': 'Get AI-powered code review and suggestions',
            'category': 'Code Analysis',
            'parameters': {
                'path': {'type': 'string', 'required': True, 'description': 'Path to the code file'},
                'focus': {'type': 'string', 'required': False, 'description': 'Review focus (security, performance, style, etc.)'}
            },
            'function': self._code_review
        }
        
        # Web Operations Tools
        self.tools['web_fetch'] = {
            'name': 'web_fetch',
            'description': 'Fetch content from URLs with smart text extraction',
            'category': 'Web Operations',
            'parameters': {
                'url': {'type': 'string', 'required': True, 'description': 'URL to fetch'},
                'extract_text': {'type': 'boolean', 'required': False, 'description': 'Extract clean text from HTML'},
                'save_to': {'type': 'string', 'required': False, 'description': 'Save content to file'}
            },
            'function': self._web_fetch
        }
        
        self.tools['web_api'] = {
            'name': 'web_api',
            'description': 'Make HTTP API requests with custom methods and data',
            'category': 'Web Operations',
            'parameters': {
                'url': {'type': 'string', 'required': True, 'description': 'API endpoint URL'},
                'method': {'type': 'string', 'required': False, 'description': 'HTTP method (GET, POST, etc.)'},
                'data': {'type': 'string', 'required': False, 'description': 'JSON data for request body'},
                'headers': {'type': 'string', 'required': False, 'description': 'Custom headers (JSON format)'}
            },
            'function': self._web_api
        }
        
        # System Tools
        self.tools['shell_exec'] = {
            'name': 'shell_exec',
            'description': 'Execute shell commands safely',
            'category': 'System Tools',
            'parameters': {
                'command': {'type': 'string', 'required': True, 'description': 'Shell command to execute'},
                'cwd': {'type': 'string', 'required': False, 'description': 'Working directory'},
                'timeout': {'type': 'integer', 'required': False, 'description': 'Timeout in seconds (default: 30)'}
            },
            'function': self._shell_exec
        }
        
        self.tools['env_info'] = {
            'name': 'env_info',
            'description': 'Get system and environment information',
            'category': 'System Tools',
            'parameters': {},
            'function': self._env_info
        }
        
        # AI Tools
        self.tools['ai_chat'] = {
            'name': 'ai_chat',
            'description': 'Direct AI chat with custom parameters',
            'category': 'AI Tools',
            'parameters': {
                'prompt': {'type': 'string', 'required': True, 'description': 'Prompt for the AI'},
                'system': {'type': 'string', 'required': False, 'description': 'System message'},
                'model': {'type': 'string', 'required': False, 'description': 'AI model to use'},
                'temperature': {'type': 'float', 'required': False, 'description': 'Response creativity (0.0-2.0)'}
            },
            'function': self._ai_chat
        }
        
        self.tools['ai_summarize'] = {
            'name': 'ai_summarize',
            'description': 'Summarize text or file content using AI',
            'category': 'AI Tools',
            'parameters': {
                'content': {'type': 'string', 'required': False, 'description': 'Text content to summarize'},
                'file_path': {'type': 'string', 'required': False, 'description': 'Path to file to summarize'},
                'length': {'type': 'string', 'required': False, 'description': 'Summary length (short, medium, long)'}
            },
            'function': self._ai_summarize
        }
    
    def list_tools(self, category: str = None) -> Dict[str, Any]:
        """List all available tools or tools in a specific category."""
        if category:
            filtered_tools = {name: tool for name, tool in self.tools.items() 
                            if tool['category'].lower() == category.lower()}
            return {
                'category': category,
                'tools': filtered_tools,
                'count': len(filtered_tools)
            }
        
        # Group tools by category
        categories = {}
        for name, tool in self.tools.items():
            cat = tool['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append({
                'name': name,
                'description': tool['description']
            })
        
        return {
            'categories': categories,
            'total_tools': len(self.tools)
        }
    
    def get_tool_help(self, tool_name: str) -> Dict[str, Any]:
        """Get detailed help for a specific tool."""
        if tool_name not in self.tools:
            return {'error': f'Tool "{tool_name}" not found'}
        
        tool = self.tools[tool_name]
        return {
            'name': tool['name'],
            'description': tool['description'],
            'category': tool['category'],
            'parameters': tool['parameters'],
            'usage_example': self._get_usage_example(tool_name)
        }
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool with given parameters."""
        if tool_name not in self.tools:
            return {'error': f'Tool "{tool_name}" not found'}
        
        tool = self.tools[tool_name]
        
        # Validate required parameters
        for param_name, param_info in tool['parameters'].items():
            if param_info.get('required', False) and param_name not in kwargs:
                return {'error': f'Required parameter "{param_name}" missing'}
        
        try:
            result = tool['function'](**kwargs)
            return result
        except Exception as e:
            self.logger.error(f"Tool execution failed: {e}")
            return {'error': f'Tool execution failed: {str(e)}'}
    
    def _get_usage_example(self, tool_name: str) -> str:
        """Get usage example for a tool."""
        examples = {
            'fs_read': '/tools fs_read path="script.py"',
            'fs_create': '/tools fs_create path="website.html" prompt="Create a modern e-commerce website"',
            'fs_write': '/tools fs_write path="newfile.py" content="print(\'Hello World\')"',
            'fs_search': '/tools fs_search directory="./src" extension=".py" content="class"',
            'code_analyze': '/tools code_analyze path="main.py" detailed=true',
            'code_modify': '/tools code_modify path="script.py" instruction="Add error handling"',
            'web_fetch': '/tools web_fetch url="https://example.com" extract_text=true',
            'ai_chat': '/tools ai_chat prompt="Explain quantum computing" temperature=0.3',
            'shell_exec': '/tools shell_exec command="ls -la" cwd="/home/user"'
        }
        return examples.get(tool_name, f'/tools {tool_name} [parameters]')
    
    # Tool Implementation Methods
    
    def _fs_read(self, path: str, lines: str = None) -> Dict[str, Any]:
        """Read file with optional line range."""
        try:
            result = self.agent.read_file(path)
            
            if lines and result['success']:
                content_lines = result['content'].split('\n')
                if '-' in lines:
                    start, end = map(int, lines.split('-'))
                    result['content'] = '\n'.join(content_lines[start-1:end])
                    result['metadata']['displayed_lines'] = f"{start}-{end}"
                else:
                    line_num = int(lines)
                    result['content'] = content_lines[line_num-1] if line_num <= len(content_lines) else ""
                    result['metadata']['displayed_lines'] = str(line_num)
            
            return result
        except Exception as e:
            return {'error': str(e)}
    
    def _fs_create(self, path: str, content: str = None, prompt: str = None, file_type: str = None, backup: bool = True) -> Dict[str, Any]:
        """Create a new file with content, optionally using AI to generate content."""
        try:
            # If prompt is provided, use AI to generate content
            if prompt and not content:
                # Determine file type from extension if not provided
                if not file_type:
                    ext = Path(path).suffix.lower()
                    type_mapping = {
                        '.html': 'HTML',
                        '.py': 'Python',
                        '.js': 'JavaScript',
                        '.ts': 'TypeScript',
                        '.css': 'CSS',
                        '.java': 'Java',
                        '.cpp': 'C++',
                        '.c': 'C',
                        '.cs': 'C#',
                        '.php': 'PHP',
                        '.rb': 'Ruby',
                        '.go': 'Go',
                        '.rs': 'Rust',
                        '.sql': 'SQL',
                        '.md': 'Markdown',
                        '.txt': 'text'
                    }
                    file_type = type_mapping.get(ext, 'text')
                
                # Create AI prompt for file generation
                ai_prompt = f"""
Create a {file_type} file based on this request: {prompt}

Please provide complete, well-structured code/content that is:
1. Functional and ready to use
2. Well-commented and documented
3. Following best practices for {file_type}
4. Modern and up-to-date

Only provide the file content, no additional explanations.
"""
                
                ai_result = self.agent.ai_request(ai_prompt, f"You are an expert {file_type} developer.")
                if not ai_result['success']:
                    return ai_result
                
                # Extract content from AI response
                content = self._extract_code_from_response(ai_result['response'], file_type.lower())
            
            # Use empty content if none provided
            if not content:
                content = ""
            
            # Create the file using the existing write_file method
            result = self.agent.write_file(path, content, backup)
            if result['success']:
                result['created'] = True
                result['ai_generated'] = prompt is not None
                if prompt:
                    result['generation_prompt'] = prompt
            
            return result
        except Exception as e:
            return {'error': str(e)}
    
    def _fs_write(self, path: str, content: str, backup: bool = True) -> Dict[str, Any]:
        """Write content to file."""
        try:
            return self.agent.write_file(path, content, backup)
        except Exception as e:
            return {'error': str(e)}
    
    def _fs_search(self, directory: str, pattern: str = "", extension: str = "", content: str = "") -> Dict[str, Any]:
        """Search for files and content."""
        try:
            return self.agent.search_files(directory, pattern, extension, content)
        except Exception as e:
            return {'error': str(e)}
    
    def _fs_remove(self, path: str, backup: bool = True) -> Dict[str, Any]:
        """Remove a file."""
        try:
            return self.agent.remove_file(path, backup)
        except Exception as e:
            return {'error': str(e)}
    
    def _fs_undo(self) -> Dict[str, Any]:
        """Undo last file operation."""
        try:
            return self.agent.undo_last_operation()
        except Exception as e:
            return {'error': str(e)}
    
    def _code_analyze(self, path: str, detailed: bool = False) -> Dict[str, Any]:
        """Analyze code structure."""
        try:
            file_result = self.agent.read_file(path)
            if not file_result['success']:
                return file_result
            
            content = file_result['content']
            language = file_result['metadata']['language']
            
            # Basic analysis
            analysis = {
                'file_path': path,
                'language': language,
                'lines_of_code': len([line for line in content.split('\n') if line.strip()]),
                'total_lines': len(content.split('\n')),
                'file_size': len(content)
            }
            
            if language == 'python':
                analysis.update(self._analyze_python_code(content))
            elif language in ['javascript', 'typescript']:
                analysis.update(self._analyze_js_code(content))
            
            if detailed:
                # Use AI for detailed analysis
                ai_prompt = f"Analyze this {language} code and provide insights about structure, complexity, and potential improvements:\n\n{content}"
                ai_result = self.agent.ai_request(ai_prompt, "You are a senior code reviewer.")
                if ai_result['success']:
                    analysis['ai_insights'] = ai_result['response']
            
            return {'success': True, 'analysis': analysis}
        except Exception as e:
            return {'error': str(e)}
    
    def _code_modify(self, path: str, instruction: str, backup: bool = True) -> Dict[str, Any]:
        """Modify code using AI."""
        try:
            file_result = self.agent.read_file(path)
            if not file_result['success']:
                return file_result
            
            content = file_result['content']
            language = file_result['metadata']['language']
            
            ai_prompt = f"""
Modify this {language} code according to the instruction: {instruction}

Current code:
{content}

Please provide the complete modified code, maintaining the original structure and style.
"""
            
            ai_result = self.agent.ai_request(ai_prompt, f"You are an expert {language} developer.")
            if not ai_result['success']:
                return ai_result
            
            # Extract code from AI response
            modified_code = self._extract_code_from_response(ai_result['response'], language)
            
            # Write modified code
            write_result = self.agent.write_file(path, modified_code, backup)
            if write_result['success']:
                write_result['modification_instruction'] = instruction
                write_result['ai_response'] = ai_result['response']
            
            return write_result
        except Exception as e:
            return {'error': str(e)}
    
    def _code_review(self, path: str, focus: str = "general") -> Dict[str, Any]:
        """Get AI code review."""
        try:
            file_result = self.agent.read_file(path)
            if not file_result['success']:
                return file_result
            
            content = file_result['content']
            language = file_result['metadata']['language']
            
            focus_prompts = {
                'security': 'Focus on security vulnerabilities and best practices',
                'performance': 'Focus on performance optimization opportunities',
                'style': 'Focus on code style and readability improvements',
                'general': 'Provide a comprehensive code review'
            }
            
            focus_instruction = focus_prompts.get(focus, focus_prompts['general'])
            
            ai_prompt = f"""
Review this {language} code. {focus_instruction}.

Code to review:
{content}

Please provide:
1. Overall assessment
2. Specific issues found
3. Suggestions for improvement
4. Best practices recommendations
"""
            
            ai_result = self.agent.ai_request(ai_prompt, f"You are a senior {language} code reviewer.")
            if ai_result['success']:
                return {
                    'success': True,
                    'file_path': path,
                    'review_focus': focus,
                    'review': ai_result['response'],
                    'language': language
                }
            return ai_result
        except Exception as e:
            return {'error': str(e)}
    
    def _web_fetch(self, url: str, extract_text: bool = False, save_to: str = None) -> Dict[str, Any]:
        """Fetch content from URL."""
        try:
            headers = {
                'User-Agent': 'OpenRouter-CLI/1.0.0 (https://github.com/openrouter-cli/openrouter-cli)'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            content = response.text
            content_type = response.headers.get('content-type', '')
            
            result = {
                'success': True,
                'url': url,
                'status_code': response.status_code,
                'content_type': content_type,
                'content_length': len(content),
                'content': content
            }
            
            if extract_text and 'html' in content_type.lower():
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(content, 'html.parser')
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    text = soup.get_text()
                    # Clean up whitespace
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)
                    result['extracted_text'] = text
                except ImportError:
                    result['error'] = 'BeautifulSoup not available for text extraction'
            
            if save_to:
                with open(save_to, 'w', encoding='utf-8') as f:
                    f.write(result.get('extracted_text', content))
                result['saved_to'] = save_to
            
            return result
        except Exception as e:
            return {'error': str(e)}
    
    def _web_api(self, url: str, method: str = 'GET', data: str = None, headers: str = None) -> Dict[str, Any]:
        """Make HTTP API request."""
        try:
            request_headers = {'User-Agent': 'OpenRouter-CLI/1.0.0'}
            
            if headers:
                try:
                    custom_headers = json.loads(headers)
                    request_headers.update(custom_headers)
                except json.JSONDecodeError:
                    return {'error': 'Invalid JSON format for headers'}
            
            request_data = None
            if data:
                try:
                    request_data = json.loads(data)
                    request_headers['Content-Type'] = 'application/json'
                except json.JSONDecodeError:
                    request_data = data
            
            response = requests.request(
                method.upper(),
                url,
                headers=request_headers,
                json=request_data if isinstance(request_data, dict) else None,
                data=request_data if isinstance(request_data, str) else None,
                timeout=30
            )
            
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = response.text
            
            return {
                'success': True,
                'url': url,
                'method': method.upper(),
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'data': response_data
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _shell_exec(self, command: str, cwd: str = None, timeout: int = 30) -> Dict[str, Any]:
        """Execute shell command safely."""
        try:
            # Basic security check
            dangerous_commands = ['rm -rf', 'del /f', 'format', 'fdisk', 'mkfs']
            if any(dangerous in command.lower() for dangerous in dangerous_commands):
                return {'error': 'Dangerous command detected and blocked'}
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                'success': True,
                'command': command,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'cwd': cwd or os.getcwd()
            }
        except subprocess.TimeoutExpired:
            return {'error': f'Command timed out after {timeout} seconds'}
        except Exception as e:
            return {'error': str(e)}
    
    def _env_info(self) -> Dict[str, Any]:
        """Get system and environment information."""
        try:
            import platform
            import sys
            
            return {
                'success': True,
                'system': {
                    'platform': platform.platform(),
                    'system': platform.system(),
                    'release': platform.release(),
                    'version': platform.version(),
                    'machine': platform.machine(),
                    'processor': platform.processor()
                },
                'python': {
                    'version': sys.version,
                    'executable': sys.executable,
                    'path': sys.path[:5]  # First 5 paths only
                },
                'environment': {
                    'cwd': os.getcwd(),
                    'home': str(Path.home()),
                    'user': os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _ai_chat(self, prompt: str, system: str = None, model: str = None, temperature: float = 0.7) -> Dict[str, Any]:
        """Direct AI chat."""
        try:
            return self.agent.ai_request(prompt, system or "", model)
        except Exception as e:
            return {'error': str(e)}
    
    def _ai_summarize(self, content: str = None, file_path: str = None, length: str = "medium") -> Dict[str, Any]:
        """Summarize text or file content."""
        try:
            if file_path:
                file_result = self.agent.read_file(file_path)
                if not file_result['success']:
                    return file_result
                content = file_result['content']
            
            if not content:
                return {'error': 'No content provided for summarization'}
            
            length_instructions = {
                'short': 'Provide a brief 2-3 sentence summary',
                'medium': 'Provide a comprehensive paragraph summary',
                'long': 'Provide a detailed multi-paragraph summary'
            }
            
            instruction = length_instructions.get(length, length_instructions['medium'])
            
            ai_prompt = f"""
{instruction} of the following content:

{content}
"""
            
            ai_result = self.agent.ai_request(ai_prompt, "You are an expert at creating clear, concise summaries.")
            if ai_result['success']:
                return {
                    'success': True,
                    'summary': ai_result['response'],
                    'original_length': len(content),
                    'summary_length': len(ai_result['response']),
                    'compression_ratio': len(ai_result['response']) / len(content)
                }
            return ai_result
        except Exception as e:
            return {'error': str(e)}
    
    # Helper methods for code analysis
    
    def _analyze_python_code(self, content: str) -> Dict[str, Any]:
        """Analyze Python code structure."""
        import ast
        try:
            tree = ast.parse(content)
            
            functions = []
            classes = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args]
                    })
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        imports.extend([alias.name for alias in node.names])
                    else:
                        imports.append(f"{node.module}.{alias.name}" for alias in node.names)
            
            return {
                'functions': functions,
                'classes': classes,
                'imports': list(set(imports)),
                'function_count': len(functions),
                'class_count': len(classes)
            }
        except SyntaxError:
            return {'error': 'Python syntax error in code'}
    
    def _analyze_js_code(self, content: str) -> Dict[str, Any]:
        """Basic JavaScript code analysis using regex."""
        functions = re.findall(r'function\s+(\w+)\s*\(([^)]*)\)', content)
        classes = re.findall(r'class\s+(\w+)', content)
        imports = re.findall(r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]', content)
        
        return {
            'functions': [{'name': f[0], 'params': f[1]} for f in functions],
            'classes': [{'name': c} for c in classes],
            'imports': imports,
            'function_count': len(functions),
            'class_count': len(classes)
        }
    
    def _extract_code_from_response(self, response: str, language: str) -> str:
        """Extract code from AI response."""
        # Look for code blocks
        code_block_pattern = rf'```{language}?\s*\n(.*?)\n```'
        matches = re.findall(code_block_pattern, response, re.DOTALL | re.IGNORECASE)
        
        if matches:
            return matches[0].strip()
        
        # If no code blocks, try to extract the largest code-like section
        lines = response.split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            if any(keyword in line for keyword in ['def ', 'class ', 'import ', 'function ', 'var ', 'let ', 'const ']):
                in_code = True
            
            if in_code:
                code_lines.append(line)
                
                # Stop if we hit explanatory text
                if line.strip() and not line.startswith((' ', '\t')) and any(word in line.lower() for word in ['this', 'the', 'here', 'now']):
                    break
        
        return '\n'.join(code_lines).strip() if code_lines else response