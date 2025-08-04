import click
from pathlib import Path
from typing import Optional

from ..core import AIAgent
from ..utils import handle_error, format_output, validate_file_path, confirm_action


@click.group()
@click.pass_context
def file(ctx):
    """File operations: read, write, search, remove, and undo."""
    pass


@file.command()
@click.argument('path', type=click.Path())
@click.option('--format', 'output_format', default='human', 
              type=click.Choice(['human', 'json', 'yaml']),
              help='Output format')
@click.option('--metadata-only', is_flag=True, 
              help='Show only file metadata, not content')
@click.pass_context
def read(ctx, path: str, output_format: str, metadata_only: bool):
    """Read and display file contents with metadata."""
    try:
        agent: AIAgent = ctx.obj['agent']
        
        result = agent.read_file(path)
        
        if metadata_only:
            output = result['metadata']
        else:
            output = result
        
        click.echo(format_output(output, output_format))
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@file.command()
@click.argument('path', type=click.Path())
@click.option('--content', help='Content to write to file')
@click.option('--stdin', is_flag=True, help='Read content from stdin')
@click.option('--no-backup', is_flag=True, help='Disable backup creation')
@click.option('--format', 'output_format', default='human',
              type=click.Choice(['human', 'json', 'yaml']),
              help='Output format')
@click.pass_context
def write(ctx, path: str, content: Optional[str], stdin: bool, no_backup: bool, output_format: str):
    """Create or modify a file with given content."""
    try:
        agent: AIAgent = ctx.obj['agent']
        
        # Get content from various sources
        if stdin:
            content = click.get_text_stream('stdin').read()
        elif content is None:
            # If no content provided, open editor
            content = click.edit() or ""
        
        if not content and not stdin:
            raise click.ClickException("No content provided. Use --content, --stdin, or interactive editor.")
        
        create_backup = not no_backup
        result = agent.write_file(path, content, create_backup)
        
        click.echo(format_output(result, output_format))
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@file.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False))
@click.option('--pattern', help='Filename pattern (regex)')
@click.option('--extension', help='File extension filter (e.g., .py)')
@click.option('--content', help='Content search pattern (regex)')
@click.option('--format', 'output_format', default='human',
              type=click.Choice(['human', 'json', 'yaml']),
              help='Output format')
@click.option('--limit', type=int, help='Limit number of results')
@click.pass_context
def search(ctx, directory: str, pattern: str, extension: str, content: str, 
           output_format: str, limit: Optional[int]):
    """Search for files by name and/or content."""
    try:
        agent: AIAgent = ctx.obj['agent']
        
        result = agent.search_files(
            directory=directory,
            pattern=pattern or "",
            file_extension=extension or "",
            content_pattern=content or ""
        )
        
        # Apply limit if specified
        if limit and result['results']:
            result['results'] = result['results'][:limit]
            result['total_files'] = len(result['results'])
        
        click.echo(format_output(result, output_format))
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@file.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--no-backup', is_flag=True, help='Disable backup creation')
@click.option('--force', is_flag=True, help='Skip confirmation prompt')
@click.option('--format', 'output_format', default='human',
              type=click.Choice(['human', 'json', 'yaml']),
              help='Output format')
@click.pass_context
def remove(ctx, path: str, no_backup: bool, force: bool, output_format: str):
    """Remove a file with optional backup."""
    try:
        agent: AIAgent = ctx.obj['agent']
        
        # Confirmation unless --force is used
        if not force:
            if not confirm_action(f"Are you sure you want to remove '{path}'?"):
                click.echo("Operation cancelled.")
                return
        
        create_backup = not no_backup
        result = agent.remove_file(path, create_backup)
        
        click.echo(format_output(result, output_format))
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@file.command()
@click.option('--format', 'output_format', default='human',
              type=click.Choice(['human', 'json', 'yaml']),
              help='Output format')
@click.pass_context
def undo(ctx, output_format: str):
    """Undo the last file operation."""
    try:
        agent: AIAgent = ctx.obj['agent']
        
        result = agent.undo_last_operation()
        
        click.echo(format_output(result, output_format))
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))