import os
import json
import shutil
import requests
import pathlib
import re
from typing import Dict, List, Optional, Any
from openai import OpenAI
from urllib.parse import urlparse, urljoin
from datetime import datetime
from pathlib import Path

from ..config import ConfigManager
from ..utils import CLILogger, FileOperationError, APIError


class AIAgent:
    """
    Core AI Agent with comprehensive file operations and web capabilities.
    
    This is the core engine that powers all CLI commands, extracted from the original
    enhanced_ai_agent.py with improvements for CLI usage.
    """
    
    def __init__(self, config_manager: ConfigManager, logger: CLILogger):
        """Initialize the AI Agent with configuration and logging."""
        self.config = config_manager
        self.logger = logger
        
        # Get API configuration
        self.api_key = self.config.get_api_key()
        if not self.api_key:
            raise APIError("No API key configured. Set OPENROUTER_API_KEY environment variable or run 'openrouter-cli config set api.key <your-key>'")
        
        self.base_url = self.config.get('api.base_url', 'https://openrouter.ai/api/v1')
        self.default_model = self.config.get('api.default_model', 'qwen/qwen3-coder:free')
        
        # Initialize OpenAI client
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        
        # File operation history for undo functionality
        self.operation_history = []
        
        # Supported file extensions for different programming languages
        self.supported_extensions = {
            'python': ['.py', '.pyw'],
            'javascript': ['.js', '.jsx', '.mjs'],
            'typescript': ['.ts', '.tsx'],
            'html': ['.html', '.htm'],
            'css': ['.css', '.scss', '.sass'],
            'java': ['.java'],
            'cpp': ['.cpp', '.cc', '.cxx', '.c++'],
            'c': ['.c', '.h'],
            'csharp': ['.cs'],
            'php': ['.php'],
            'ruby': ['.rb'],
            'go': ['.go'],
            'rust': ['.rs'],
            'swift': ['.swift'],
            'kotlin': ['.kt'],
            'scala': ['.scala'],
            'r': ['.r', '.R'],
            'sql': ['.sql'],
            'shell': ['.sh', '.bash', '.zsh'],
            'powershell': ['.ps1'],
            'yaml': ['.yml', '.yaml'],
            'json': ['.json'],
            'xml': ['.xml'],
            'markdown': ['.md', '.markdown'],
            'text': ['.txt'],
            'config': ['.conf', '.cfg', '.ini']
        }
        
        # Get backup directory from config
        backup_dir = self.config.get('preferences.backup_directory')
        self.backup_dir = Path(backup_dir) if backup_dir else Path.home() / '.openrouter-cli' / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _backup_file(self, file_path: str) -> str:
        """Create a backup of a file before modification."""
        if not os.path.exists(file_path):
            return ''
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        backup_filename = f"{filename}.backup_{timestamp}"
        backup_path = self.backup_dir / backup_filename
        
        try:
            shutil.copy2(file_path, backup_path)
            self.logger.debug(f"Created backup: {backup_path}")
            return str(backup_path)
        except Exception as e:
            self.logger.warning(f"Could not create backup for {file_path}: {e}")
            return ""
    
    def _add_to_history(self, operation: str, file_path: str, backup_path: str = "", original_content: str = ""):
        """Add operation to history for undo functionality."""
        max_history = self.config.get('preferences.max_history', 100)
        
        self.operation_history.append({
            'operation': operation,
            'file_path': file_path,
            'backup_path': backup_path,
            'original_content': original_content,
            'timestamp': datetime.now().isoformat()
        })
        
        # Limit history size
        if len(self.operation_history) > max_history:
            self.operation_history = self.operation_history[-max_history:]
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read and analyze a file with metadata."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileOperationError(f'File not found: {file_path}')
            
            file_info = path.stat()
            file_ext = path.suffix.lower()
            
            # Determine file type
            file_type = 'unknown'
            language = 'unknown'
            for lang, extensions in self.supported_extensions.items():
                if file_ext in extensions:
                    file_type = lang
                    language = lang
                    break
            
            # Read file content
            try:
                content = path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                # Try with different encoding
                content = path.read_text(encoding='latin-1')
            
            # Basic analysis
            lines = content.split('\n')
            
            self.logger.debug(f"Read file: {file_path} ({len(content)} chars, {len(lines)} lines)")
            
            return {
                'success': True,
                'file_path': str(path),
                'content': content,
                'metadata': {
                    'size': file_info.st_size,
                    'lines': len(lines),
                    'extension': file_ext,
                    'file_type': file_type,
                    'language': language,
                    'modified_time': datetime.fromtimestamp(file_info.st_mtime).isoformat(),
                    'created_time': datetime.fromtimestamp(file_info.st_ctime).isoformat()
                }
            }
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            raise FileOperationError(f'Error reading file {file_path}: {str(e)}')
    
    def write_file(self, file_path: str, content: str, create_backup: bool = None) -> Dict[str, Any]:
        """Write content to a file with optional backup."""
        try:
            path = Path(file_path)
            
            # Use config default if not specified
            if create_backup is None:
                create_backup = self.config.get('preferences.backup_enabled', True)
            
            # Create backup if file exists
            backup_path = None
            original_content = None
            
            if path.exists() and create_backup:
                backup_path = self._backup_file(str(path))
                original_content = path.read_text(encoding='utf-8')
            
            # Create directory if it doesn't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            path.write_text(content, encoding='utf-8')
            
            # Add to history
            operation = 'modify' if path.exists() else 'create'
            self._add_to_history(operation, str(path), backup_path or "", original_content or "")
            
            self.logger.debug(f"Wrote file: {file_path} ({len(content)} chars)")
            
            return {
                'success': True,
                'file_path': str(path),
                'operation': operation,
                'backup_path': backup_path,
                'bytes_written': len(content.encode('utf-8'))
            }
        except Exception as e:
            self.logger.error(f"Error writing file {file_path}: {e}")
            raise FileOperationError(f'Error writing file {file_path}: {str(e)}')
    
    def search_files(self, directory: str, pattern: str = "", file_extension: str = "", content_pattern: str = "") -> Dict[str, Any]:
        """Search for files and content with advanced filtering."""
        try:
            results = []
            search_dir = Path(directory)
            
            if not search_dir.exists():
                raise FileOperationError(f"Directory not found: {directory}")
            
            self.logger.debug(f"Searching in: {directory}")
            
            for file_path in search_dir.rglob('*'):
                if not file_path.is_file():
                    continue
                
                file_ext = file_path.suffix.lower()
                
                # Filter by extension
                if file_extension and file_ext != file_extension:
                    continue
                
                # Filter by filename pattern
                if pattern and not re.search(pattern, file_path.name, re.IGNORECASE):
                    continue
                
                file_info = {
                    'file_path': str(file_path),
                    'filename': file_path.name,
                    'extension': file_ext,
                    'size': file_path.stat().st_size
                }
                
                # Search content if pattern provided
                if content_pattern:
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        matches = list(re.finditer(content_pattern, content, re.IGNORECASE))
                        if matches:
                            file_info['content_matches'] = len(matches)
                            file_info['match_lines'] = []
                            
                            lines = content.split('\n')
                            for match in matches[:5]:  # Limit to first 5 matches
                                line_num = content[:match.start()].count('\n') + 1
                                if line_num <= len(lines):
                                    file_info['match_lines'].append({
                                        'line_number': line_num,
                                        'line_content': lines[line_num - 1].strip(),
                                        'match_text': match.group()
                                    })
                        else:
                            continue
                    except (UnicodeDecodeError, PermissionError):
                        continue
                
                results.append(file_info)
            
            self.logger.debug(f"Found {len(results)} files")
            
            return {
                'success': True,
                'results': results,
                'total_files': len(results)
            }
        except Exception as e:
            self.logger.error(f"Error searching files: {e}")
            raise FileOperationError(f'Error searching files: {str(e)}')
    
    def remove_file(self, file_path: str, create_backup: bool = None) -> Dict[str, Any]:
        """Remove a file with optional backup."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileOperationError(f'File not found: {file_path}')
            
            # Use config default if not specified
            if create_backup is None:
                create_backup = self.config.get('preferences.backup_enabled', True)
            
            # Create backup
            backup_path = None
            original_content = None
            
            if create_backup:
                backup_path = self._backup_file(str(path))
                original_content = path.read_text(encoding='utf-8')
            
            # Remove file
            path.unlink()
            
            # Add to history
            self._add_to_history('remove', str(path), backup_path or "", original_content or "")
            
            self.logger.debug(f"Removed file: {file_path}")
            
            return {
                'success': True,
                'file_path': str(path),
                'operation': 'remove',
                'backup_path': backup_path
            }
        except Exception as e:
            self.logger.error(f"Error removing file {file_path}: {e}")
            raise FileOperationError(f'Error removing file {file_path}: {str(e)}')
    
    def undo_last_operation(self) -> Dict[str, Any]:
        """Undo the last file operation."""
        try:
            if not self.operation_history:
                raise FileOperationError('No operations to undo')
            
            last_op = self.operation_history.pop()
            operation = last_op['operation']
            file_path = last_op['file_path']
            backup_path = last_op['backup_path']
            original_content = last_op['original_content']
            
            path = Path(file_path)
            
            if operation == 'create':
                # Remove the created file
                if path.exists():
                    path.unlink()
                    
            elif operation == 'modify':
                # Restore from backup or original content
                if backup_path and Path(backup_path).exists():
                    shutil.copy2(backup_path, path)
                elif original_content:
                    path.write_text(original_content, encoding='utf-8')
                        
            elif operation == 'remove':
                # Restore from backup
                if backup_path and Path(backup_path).exists():
                    shutil.copy2(backup_path, path)
                elif original_content:
                    path.write_text(original_content, encoding='utf-8')
            
            self.logger.debug(f"Undone operation: {operation} on {file_path}")
            
            return {
                'success': True,
                'undone_operation': operation,
                'file_path': file_path,
                'timestamp': last_op['timestamp']
            }
        except Exception as e:
            self.logger.error(f"Error undoing operation: {e}")
            raise FileOperationError(f'Error undoing operation: {str(e)}')
    
    def ai_request(self, prompt: str, system_message: str = "", model: str = None) -> Dict[str, Any]:
        """Make an AI request with the configured model."""
        try:
            if not model:
                model = self.default_model
            
            messages = []
            
            if system_message:
                messages.append({"role": "system", "content": system_message})
            
            messages.append({"role": "user", "content": prompt})
            
            self.logger.debug(f"Making AI request with model: {model}")
            
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=4000
            )
            
            response = completion.choices[0].message.content
            self.logger.debug(f"AI response received ({len(response)} chars)")
            
            return {
                'success': True,
                'response': response,
                'model': model,
                'usage': dict(completion.usage) if completion.usage else None
            }
            
        except Exception as e:
            self.logger.error(f"AI request failed: {e}")
            raise APIError(f'AI request failed: {str(e)}')
    
    def get_operation_history(self) -> List[Dict[str, Any]]:
        """Get the history of file operations."""
        return self.operation_history.copy()
    
    def clear_operation_history(self) -> Dict[str, Any]:
        """Clear the operation history."""
        count = len(self.operation_history)
        self.operation_history.clear()
        self.logger.debug(f"Cleared {count} operations from history")
        return {'success': True, 'cleared_operations': count}