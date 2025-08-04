import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from .loading import LoadingAnimation, with_loading, show_loading, ai_thinking_animation, file_processing_animation, web_fetching_animation


class CLILogger:
    """Enhanced logging for CLI operations."""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.logger = logging.getLogger('openrouter_cli')
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Get log level from config
        log_level = 'info'
        if self.config_manager:
            log_level = self.config_manager.get('preferences.log_level', 'info')
        
        level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(level)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
        
        # File handler (optional)
        if self.config_manager:
            log_dir = Path(self.config_manager.config_dir) / 'logs'
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / 'openrouter-cli.log'
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message."""
        self.logger.critical(message)


class CLIError(Exception):
    """Base exception for CLI errors."""
    
    def __init__(self, message: str, exit_code: int = 1):
        super().__init__(message)
        self.exit_code = exit_code


class ConfigError(CLIError):
    """Configuration-related errors."""
    pass


class APIError(CLIError):
    """API-related errors."""
    pass


class FileOperationError(CLIError):
    """File operation errors."""
    pass


class ValidationError(CLIError):
    """Input validation errors."""
    pass


def handle_error(error: Exception, logger: Optional[CLILogger] = None, verbose: bool = False):
    """Handle and display errors appropriately."""
    if isinstance(error, CLIError):
        if logger:
            logger.error(str(error))
        else:
            print(f"Error: {error}", file=sys.stderr)
        
        if verbose and hasattr(error, '__traceback__'):
            import traceback
            traceback.print_exc()
        
        sys.exit(error.exit_code)
    else:
        if logger:
            logger.critical(f"Unexpected error: {error}")
        else:
            print(f"Unexpected error: {error}", file=sys.stderr)
        
        if verbose:
            import traceback
            traceback.print_exc()
        
        sys.exit(1)


def format_output(data, format_type: str = 'human'):
    """Format output for different display types."""
    if format_type == 'json':
        import json
        return json.dumps(data, indent=2, default=str)
    elif format_type == 'yaml':
        import yaml
        return yaml.dump(data, default_flow_style=False, indent=2)
    else:
        # Human-readable format
        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                if isinstance(value, dict):
                    lines.append(f"{key}:")
                    for sub_key, sub_value in value.items():
                        lines.append(f"  {sub_key}: {sub_value}")
                else:
                    lines.append(f"{key}: {value}")
            return '\n'.join(lines)
        elif isinstance(data, list):
            return '\n'.join(str(item) for item in data)
        else:
            return str(data)


def confirm_action(message: str, default: bool = False) -> bool:
    """Ask user for confirmation."""
    suffix = " [Y/n]" if default else " [y/N]"
    response = input(f"{message}{suffix}: ").strip().lower()
    
    if not response:
        return default
    
    return response in ('y', 'yes', 'true', '1')


def validate_file_path(path: str, must_exist: bool = True) -> Path:
    """Validate and return Path object."""
    file_path = Path(path)
    
    if must_exist and not file_path.exists():
        raise ValidationError(f"File does not exist: {path}")
    
    return file_path


def validate_url(url: str) -> str:
    """Validate URL format."""
    from urllib.parse import urlparse
    
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValidationError(f"Invalid URL format: {url}")
    
    return url