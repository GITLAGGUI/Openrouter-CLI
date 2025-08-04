import click
import json
from datetime import datetime
from typing import Optional

from ..core import AIAgent
from ..utils import handle_error, format_output


@click.group()
@click.pass_context
def history(ctx):
    """Operation history management."""
    pass


@history.command()
@click.option('--format', 'output_format', default='human',
              type=click.Choice(['human', 'json', 'yaml']),
              help='Output format')
@click.option('--limit', type=int, help='Limit number of entries to show')
@click.option('--operation', type=click.Choice(['create', 'modify', 'remove']),
              help='Filter by operation type')
@click.pass_context
def list(ctx, output_format: str, limit: Optional[int], operation: Optional[str]):
    """List operation history."""
    try:
        agent: AIAgent = ctx.obj['agent']
        
        history_data = agent.get_operation_history()
        
        # Filter by operation type if specified
        if operation:
            history_data = [entry for entry in history_data if entry['operation'] == operation]
        
        # Apply limit if specified
        if limit:
            history_data = history_data[-limit:]  # Show most recent entries
        
        if output_format == 'human' and history_data:
            click.echo("📜 Operation History:")
            click.echo("-" * 60)
            for entry in history_data:
                timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                operation_icon = {
                    'create': '📝',
                    'modify': '✏️',
                    'remove': '🗑️'
                }.get(entry['operation'], '📄')
                
                click.echo(f"{operation_icon} {timestamp} | {entry['operation'].upper()} | {entry['file_path']}")
                if entry.get('backup_path'):
                    click.echo(f"   📁 Backup: {entry['backup_path']}")
            click.echo("-" * 60)
            click.echo(f"Total entries: {len(history_data)}")
        else:
            result = {
                'success': True,
                'total_entries': len(history_data),
                'history': history_data
            }
            click.echo(format_output(result, output_format))
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@history.command()
@click.option('--force', is_flag=True, help='Skip confirmation prompt')
@click.option('--format', 'output_format', default='human',
              type=click.Choice(['human', 'json', 'yaml']),
              help='Output format')
@click.pass_context
def clear(ctx, force: bool, output_format: str):
    """Clear operation history."""
    try:
        agent: AIAgent = ctx.obj['agent']
        
        if not force:
            from ..utils import confirm_action
            if not confirm_action("This will clear all operation history. Continue?"):
                click.echo("Operation cancelled.")
                return
        
        result = agent.clear_operation_history()
        
        if output_format == 'human':
            click.echo(f"✅ Cleared {result['cleared_operations']} operations from history.")
        else:
            click.echo(format_output(result, output_format))
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@history.command()
@click.argument('output_file', type=click.Path())
@click.option('--format', 'export_format', default='json',
              type=click.Choice(['json', 'yaml', 'csv']),
              help='Export format')
@click.pass_context
def export(ctx, output_file: str, export_format: str):
    """Export operation history to a file."""
    try:
        agent: AIAgent = ctx.obj['agent']
        
        history_data = agent.get_operation_history()
        
        from pathlib import Path
        output_path = Path(output_file)
        
        if export_format == 'json':
            output_path.write_text(json.dumps(history_data, indent=2, default=str), encoding='utf-8')
        elif export_format == 'yaml':
            import yaml
            output_path.write_text(yaml.dump(history_data, default_flow_style=False, indent=2), encoding='utf-8')
        elif export_format == 'csv':
            import csv
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                if history_data:
                    fieldnames = history_data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(history_data)
        
        result = {
            'success': True,
            'exported_file': str(output_path),
            'format': export_format,
            'entries_exported': len(history_data)
        }
        
        click.echo(format_output(result, 'human'))
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@history.command()
@click.option('--days', type=int, default=30, help='Number of days to keep')
@click.option('--count', type=int, help='Maximum number of entries to keep')
@click.option('--force', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def cleanup(ctx, days: int, count: Optional[int], force: bool):
    """Clean up old history entries."""
    try:
        agent: AIAgent = ctx.obj['agent']
        
        history_data = agent.get_operation_history()
        original_count = len(history_data)
        
        if not history_data:
            click.echo("No history entries to clean up.")
            return
        
        # Filter by date
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        filtered_history = []
        
        for entry in history_data:
            entry_time = datetime.fromisoformat(entry['timestamp']).timestamp()
            if entry_time >= cutoff_date:
                filtered_history.append(entry)
        
        # Apply count limit if specified
        if count and len(filtered_history) > count:
            filtered_history = filtered_history[-count:]  # Keep most recent
        
        entries_to_remove = original_count - len(filtered_history)
        
        if entries_to_remove == 0:
            click.echo("No entries need to be cleaned up.")
            return
        
        if not force:
            from ..utils import confirm_action
            if not confirm_action(f"This will remove {entries_to_remove} old entries. Continue?"):
                click.echo("Cleanup cancelled.")
                return
        
        # Update history
        agent.operation_history = filtered_history
        
        click.echo(f"✅ Cleaned up {entries_to_remove} old entries.")
        click.echo(f"Remaining entries: {len(filtered_history)}")
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))