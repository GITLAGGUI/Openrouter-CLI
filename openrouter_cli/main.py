#!/usr/bin/env python3
"""
OpenRouter CLI - Main entry point

A powerful command-line interface for AI-powered file operations and web interactions
using OpenRouter as the AI provider.
"""

import click
import sys
import os
from pathlib import Path

# Add the package to Python path if running from source
if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).parent.parent))

from .config import ConfigManager
from .utils import CLILogger, handle_error, CLIError
from .core import AIAgent
from .commands import file, code, web, chat, config, history
from .commands.html_generator import html
from .commands.debug_agent import debug


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--config-file', type=click.Path(), help='Custom configuration file path')
@click.option('--log-level', type=click.Choice(['debug', 'info', 'warning', 'error']),
              default='info', help='Set logging level')
@click.version_option(version='1.0.0', prog_name='openrouter-cli')
@click.pass_context
def cli(ctx, verbose: bool, config_file: str, log_level: str):
    """
    OpenRouter CLI - AI-powered file operations and web interactions.
    
    A comprehensive command-line tool for interacting with AI models through OpenRouter,
    offering file operations, code analysis, web content fetching, and direct chat capabilities.
    
    Examples:
      openrouter-cli file read script.py
      openrouter-cli code analyze mycode.py
      openrouter-cli chat ask "How do I optimize this code?"
      openrouter-cli web fetch https://example.com --extract-text
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    try:
        # Initialize configuration manager
        config_manager = ConfigManager()
        if config_file:
            config_manager.config_file = Path(config_file)
            config_manager._load_config()
        
        # Override log level if specified
        if log_level != 'info':
            config_manager.set('preferences.log_level', log_level)
        
        # Initialize logger
        logger = CLILogger(config_manager)
        
        # Store in context
        ctx.obj['config'] = config_manager
        ctx.obj['logger'] = logger
        ctx.obj['verbose'] = verbose
        
        # Initialize AI agent (only if not running config commands)
        if ctx.invoked_subcommand != 'config':
            try:
                agent = AIAgent(config_manager, logger)
                ctx.obj['agent'] = agent
            except Exception as e:
                if 'api key' in str(e).lower():
                    click.echo("No API key configured. Run 'openrouter-cli config init' to set up your API key.")
                    sys.exit(1)
                else:
                    raise
        
    except Exception as e:
        handle_error(e, None, verbose)


# Add command groups
cli.add_command(file)
cli.add_command(code)
cli.add_command(web)
cli.add_command(chat)
cli.add_command(config)
cli.add_command(history)
cli.add_command(html)
cli.add_command(debug)


@cli.command()
@click.pass_context
def version(ctx):
    """Show version information and configuration status."""
    try:
        config_manager: ConfigManager = ctx.obj['config']
        
        click.echo("OpenRouter CLI v1.0.0")
        click.echo("=" * 40)
        
        # Configuration status
        validation = config_manager.validate_config()
        
        if validation['valid']:
            click.echo("Configuration: Valid")
        else:
            click.echo("Configuration: Issues detected")
            for issue in validation['issues']:
                click.echo(f"   - {issue}")
        
        click.echo(f"Config file: {validation['config_file']}")
        click.echo(f"API key source: {validation['api_key_source']}")
        click.echo(f"Base URL: {config_manager.get('api.base_url')}")
        click.echo(f"Default model: {config_manager.get('api.default_model')}")
        
        # Available models
        models = config_manager.get('models', {})
        if models:
            click.echo("\nConfigured models:")
            for model_type, model_name in models.items():
                click.echo(f"   {model_type}: {model_name}")
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@cli.command()
@click.pass_context
def doctor(ctx):
    """Diagnose common configuration and setup issues."""
    try:
        config_manager: ConfigManager = ctx.obj['config']
        logger: CLILogger = ctx.obj['logger']
        
        click.echo("OpenRouter CLI Doctor")
        click.echo("=" * 40)
        
        issues_found = 0
        
        # Check configuration
        validation = config_manager.validate_config()
        if not validation['valid']:
            click.echo("Configuration Issues:")
            for issue in validation['issues']:
                click.echo(f"   - {issue}")
            issues_found += len(validation['issues'])
        else:
            click.echo("Configuration is valid")
        
        # Check API connectivity
        if validation['api_key_present']:
            try:
                agent = AIAgent(config_manager, logger)
                test_response = agent.ai_request("Hello", "", "qwen/qwen3-coder:free")
                if test_response.get('success'):
                    click.echo("API connectivity test passed")
                else:
                    click.echo("API connectivity test failed")
                    issues_found += 1
            except Exception as e:
                click.echo(f"API connectivity test failed: {e}")
                issues_found += 1
        else:
            click.echo("Cannot test API connectivity (no API key)")
        
        # Check file permissions
        try:
            test_file = config_manager.config_dir / 'test_permissions'
            test_file.write_text("test")
            test_file.unlink()
            click.echo("File permissions are working")
        except Exception as e:
            click.echo(f"File permission issue: {e}")
            issues_found += 1
        
        # Check dependencies
        try:
            import openai
            import requests
            import yaml
            click.echo("All required dependencies are installed")
        except ImportError as e:
            click.echo(f"Missing dependency: {e}")
            issues_found += 1
        
        # Summary
        click.echo("=" * 40)
        if issues_found == 0:
            click.echo("Everything looks good! OpenRouter CLI is ready to use.")
        else:
            click.echo(f"Found {issues_found} issue(s). Please address them for optimal functionality.")
            click.echo("\nFor help, run: openrouter-cli config init")
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()