import click
from typing import Optional

from ..config import ConfigManager
from ..utils import handle_error, format_output, confirm_action


@click.group()
@click.pass_context
def config(ctx):
    """Configuration management for OpenRouter CLI."""
    pass


@config.command()
@click.option('--api-key', help='OpenRouter API key')
@click.option('--force', is_flag=True, help='Overwrite existing configuration')
@click.pass_context
def init(ctx, api_key: Optional[str], force: bool):
    """Initialize configuration file."""
    try:
        config_manager: ConfigManager = ctx.obj['config']
        
        if config_manager.config_file.exists() and not force:
            if not confirm_action("Configuration file already exists. Overwrite?"):
                click.echo("Configuration initialization cancelled.")
                return
        
        # Get API key if not provided
        if not api_key:
            api_key = click.prompt("Enter your OpenRouter API key", hide_input=True, default="")
        
        # Initialize config
        success = config_manager.init_config(api_key, force=True)
        
        if success:
            click.echo(f"Configuration initialized at: {config_manager.config_file}")
            click.echo("You can now use the OpenRouter CLI!")
        else:
            click.echo("Failed to initialize configuration.")
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@config.command()
@click.argument('key', type=str)
@click.argument('value', type=str)
@click.pass_context
def set(ctx, key: str, value: str):
    """Set a configuration value using dot notation (e.g., api.key)."""
    try:
        config_manager: ConfigManager = ctx.obj['config']
        
        # Special handling for certain keys
        if key == 'api.key' and not value.startswith('sk-or-v1-'):
            if not confirm_action("API key format appears invalid. Continue anyway?"):
                return
        
        success = config_manager.set(key, value)
        
        if success:
            # Mask API key in output
            display_value = value
            if 'key' in key.lower() and len(value) > 10:
                display_value = value[:10] + '...'
            
            click.echo(f"Set {key} = {display_value}")
        else:
            click.echo(f"Failed to set {key}")
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@config.command()
@click.argument('key', type=str)
@click.option('--format', 'output_format', default='human',
              type=click.Choice(['human', 'json', 'yaml']),
              help='Output format')
@click.pass_context
def get(ctx, key: str, output_format: str):
    """Get a configuration value using dot notation."""
    try:
        config_manager: ConfigManager = ctx.obj['config']
        
        value = config_manager.get(key)
        
        if value is None:
            click.echo(f"Configuration key '{key}' not found.")
            return
        
        # Mask sensitive values
        if 'key' in key.lower() and isinstance(value, str) and len(value) > 10:
            display_value = value[:10] + '...'
        else:
            display_value = value
        
        result = {key: display_value}
        click.echo(format_output(result, output_format))
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@config.command()
@click.option('--format', 'output_format', default='human',
              type=click.Choice(['human', 'json', 'yaml']),
              help='Output format')
@click.option('--show-sensitive', is_flag=True, help='Show sensitive values like API keys')
@click.pass_context
def list(ctx, output_format: str, show_sensitive: bool):
    """List all configuration values."""
    try:
        config_manager: ConfigManager = ctx.obj['config']
        
        config_data = config_manager.list_all()
        
        # Mask sensitive values unless explicitly requested
        if not show_sensitive:
            config_data = _mask_sensitive_values(config_data)
        
        click.echo(format_output(config_data, output_format))
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@config.command()
@click.option('--format', 'output_format', default='human',
              type=click.Choice(['human', 'json', 'yaml']),
              help='Output format')
@click.pass_context
def validate(ctx, output_format: str):
    """Validate current configuration."""
    try:
        config_manager: ConfigManager = ctx.obj['config']
        
        validation_result = config_manager.validate_config()
        
        if output_format == 'human':
            if validation_result['valid']:
                click.echo("Configuration is valid!")
            else:
                click.echo("Configuration has issues:")
                for issue in validation_result['issues']:
                    click.echo(f"  - {issue}")
            
            click.echo(f"\nConfiguration file: {validation_result['config_file']}")
            click.echo(f"API key source: {validation_result['api_key_source']}")
            click.echo(f"API key present: {validation_result['api_key_present']}")
        else:
            click.echo(format_output(validation_result, output_format))
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@config.command()
@click.pass_context
def path(ctx):
    """Show configuration file path."""
    try:
        config_manager: ConfigManager = ctx.obj['config']
        click.echo(str(config_manager.config_file))
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@config.command()
@click.option('--backup', is_flag=True, help='Create backup before reset')
@click.option('--force', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def reset(ctx, backup: bool, force: bool):
    """Reset configuration to defaults."""
    try:
        config_manager: ConfigManager = ctx.obj['config']
        
        if not force:
            if not confirm_action("This will reset all configuration to defaults. Continue?"):
                click.echo("Configuration reset cancelled.")
                return
        
        # Create backup if requested
        if backup and config_manager.config_file.exists():
            import shutil
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = config_manager.config_file.with_suffix(f'.backup_{timestamp}')
            shutil.copy2(config_manager.config_file, backup_path)
            click.echo(f"📁 Backup created: {backup_path}")
        
        # Reset configuration
        config_manager.init_config(force=True)
        
        click.echo("Configuration reset to defaults.")
        click.echo("Run 'openrouter-cli config init' to set up your API key.")
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


def _mask_sensitive_values(config_data, mask_keys=None):
    """Recursively mask sensitive values in configuration."""
    if mask_keys is None:
        mask_keys = ['key', 'password', 'secret', 'token']
    
    if isinstance(config_data, dict):
        result = {}
        for key, value in config_data.items():
            if any(sensitive in key.lower() for sensitive in mask_keys):
                if isinstance(value, str) and len(value) > 10:
                    result[key] = value[:10] + '...'
                else:
                    result[key] = '***'
            elif isinstance(value, dict):
                result[key] = _mask_sensitive_values(value, mask_keys)
            else:
                result[key] = value
        return result
    else:
        return config_data