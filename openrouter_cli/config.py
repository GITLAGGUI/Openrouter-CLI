import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class ConfigManager:
    """Manages configuration for OpenRouter CLI tool."""
    
    def __init__(self):
        self.config_dir = Path.home() / '.openrouter-cli'
        self.config_file = self.config_dir / 'config.yaml'
        self.backup_dir = self.config_dir / 'backups'
        self.history_file = self.config_dir / 'history.json'
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        self._config = None
        self._load_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'api': {
                'key': '',
                'base_url': 'https://openrouter.ai/api/v1',
                'default_model': 'qwen/qwen3-coder:free'
            },
            'preferences': {
                'backup_enabled': True,
                'backup_directory': str(self.backup_dir),
                'log_level': 'info',
                'max_history': 100,
                'verbose': False
            },
            'models': {
                'coding': 'qwen/qwen3-coder:free',
                'general': 'z-ai/glm-4.5-air:free',
                'reasoning': 'deepseek/deepseek-r1-0528:free',
                'experimental': 'openrouter/horizon-beta:free'
            }
        }
    
    def _load_config(self):
        """Load configuration from file or create default."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f)
                    
                # Merge with defaults to ensure all keys exist
                default_config = self._get_default_config()
                self._config = self._merge_configs(default_config, self._config)
            else:
                self._config = self._get_default_config()
                self._save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self._config = self._get_default_config()
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config with default config."""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def _save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'api.key')."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if not isinstance(config, dict) or config is None:
                config = {}
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        # Set the value
        if not isinstance(config, dict) or config is None:
            config = {}
        config[keys[-1]] = value
        self._save_config()
        return True
    
    def get_api_key(self) -> Optional[str]:
        """Get API key from config or environment variable."""
        # First try environment variable
        env_key = os.getenv('OPENROUTER_API_KEY')
        if env_key:
            return env_key
        
        # Then try config file
        config_key = self.get('api.key')
        if config_key:
            return config_key
        
        return None
    
    def get_model(self, model_type: str = 'default') -> str:
        """Get model for specific type or default."""
        if model_type == 'default':
            return self.get('api.default_model', 'qwen/qwen3-coder:free')
        
        return self.get(f'models.{model_type}', self.get('api.default_model', 'qwen/qwen3-coder:free'))
    
    def list_all(self) -> Dict[str, Any]:
        """Return all configuration."""
        return self._config.copy() if self._config is not None else {}
    
    def init_config(self, api_key: Optional[str] = None, force: bool = False) -> bool:
        """Initialize configuration with API key."""
        if self.config_file.exists() and not force:
            return False
        
        config = self._get_default_config()
        if api_key:
            config['api']['key'] = api_key
        
        self._config = config
        self._save_config()
        return True
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate current configuration and return status."""
        issues = []
        
        # Check API key
        api_key = self.get_api_key()
        if not api_key:
            issues.append("No API key configured. Set OPENROUTER_API_KEY environment variable or run 'openrouter-cli config set api.key <your-key>'")
        elif not api_key.startswith('sk-or-v1-'):
            issues.append("API key format appears invalid. OpenRouter keys should start with 'sk-or-v1-'")
        
        # Check backup directory
        backup_dir = Path(self.get('preferences.backup_directory'))
        if not backup_dir.exists():
            try:
                backup_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                issues.append(f"Cannot create backup directory: {e}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'config_file': str(self.config_file),
            'api_key_source': 'environment' if os.getenv('OPENROUTER_API_KEY') else 'config',
            'api_key_present': bool(api_key)
        }