import click
import re
import json
from pathlib import Path
from typing import Optional

from ..core import AIAgent
from ..utils import handle_error, format_output, validate_file_path


@click.group()
@click.pass_context
def code(ctx):
    """Code analysis and modification operations."""
    pass


@code.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--format', 'output_format', default='human',
              type=click.Choice(['human', 'json', 'yaml']),
              help='Output format')
@click.option('--detailed', is_flag=True, help='Show detailed analysis')
@click.pass_context
def analyze(ctx, path: str, output_format: str, detailed: bool):
    """Analyze code structure, functions, classes, and imports."""
    try:
        agent: AIAgent = ctx.obj['agent']
        
        # Read and analyze the file
        file_data = agent.read_file(path)
        content = file_data['content']
        language = file_data['metadata']['language']
        
        analysis = {
            'file_path': path,
            'language': language,
            'total_lines': len(content.split('\n')),
            'non_empty_lines': len([line for line in content.split('\n') if line.strip()]),
        }
        
        # Language-specific analysis
        if language == 'python':
            analysis.update(_analyze_python_code(content))
        elif language in ['javascript', 'typescript']:
            analysis.update(_analyze_js_code(content))
        elif language == 'java':
            analysis.update(_analyze_java_code(content))
        else:
            analysis['note'] = f"Detailed analysis not yet supported for {language}"
        
        result = {'success': True, 'analysis': analysis}
        
        if not detailed:
            # Simplified output for human format
            if output_format == 'human':
                summary = {
                    'file': path,
                    'language': language,
                    'lines': analysis['total_lines'],
                    'functions': len(analysis.get('functions', [])),
                    'classes': len(analysis.get('classes', [])),
                    'imports': len(analysis.get('imports', []))
                }
                click.echo(format_output(summary, output_format))
                return
        
        click.echo(format_output(result, output_format))
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@code.command()
@click.argument('path', type=click.Path(exists=True))
@click.argument('request', type=str)
@click.option('--model', help='AI model to use for modification')
@click.option('--backup/--no-backup', default=True, help='Create backup before modification')
@click.option('--format', 'output_format', default='human',
              type=click.Choice(['human', 'json', 'yaml']),
              help='Output format')
@click.pass_context
def modify(ctx, path: str, request: str, model: Optional[str], backup: bool, output_format: str):
    """Use AI to modify code based on natural language request."""
    try:
        agent: AIAgent = ctx.obj['agent']
        
        # Read and analyze the file
        file_data = agent.read_file(path)
        if 'error' in file_data:
            raise click.ClickException(file_data['error'])
        
        # Prepare AI prompt
        system_message = f"""
        You are an expert programmer assistant. You will be given a code file and a modification request.
        Your task is to understand the code structure and make the requested modifications while:
        1. Maintaining code quality and best practices
        2. Preserving existing functionality unless explicitly asked to change it
        3. Adding appropriate comments and documentation
        4. Following the existing code style and conventions
        
        File Language: {file_data['metadata']['language']}
        File Type: {file_data['metadata']['file_type']}
        """
        
        prompt = f"""
        Here is the current code file '{path}':
        
        ```{file_data['metadata']['language']}
        {file_data['content']}
        ```
        
        Modification Request: {request}
        
        Please provide the complete modified code. Return ONLY the code without any explanations or markdown formatting.
        """
        
        # Make AI request
        ai_response = agent.ai_request(prompt, system_message, model)
        
        if 'error' in ai_response:
            raise click.ClickException(ai_response['error'])
        
        # Write the modified code
        modified_code = ai_response['response'].strip()
        
        # Remove code block markers if present
        if modified_code.startswith('```'):
            lines = modified_code.split('\n')
            modified_code = '\n'.join(lines[1:-1])
        
        write_result = agent.write_file(path, modified_code, backup)
        
        result = {
            'success': True,
            'file_path': path,
            'modification_request': request,
            'model_used': ai_response['model'],
            'write_result': write_result
        }
        
        click.echo(format_output(result, output_format))
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@code.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--model', help='AI model to use for review')
@click.option('--format', 'output_format', default='human',
              type=click.Choice(['human', 'json', 'yaml']),
              help='Output format')
@click.pass_context
def review(ctx, path: str, model: Optional[str], output_format: str):
    """Get AI-powered code review and suggestions."""
    try:
        agent: AIAgent = ctx.obj['agent']
        
        # Read the file
        file_data = agent.read_file(path)
        if 'error' in file_data:
            raise click.ClickException(file_data['error'])
        
        # Prepare AI prompt for code review
        system_message = """
        You are an expert code reviewer. Analyze the provided code and give constructive feedback on:
        1. Code quality and best practices
        2. Potential bugs or issues
        3. Performance improvements
        4. Security considerations
        5. Maintainability and readability
        6. Suggestions for improvement
        
        Provide specific, actionable feedback.
        """
        
        prompt = f"""
        Please review this {file_data['metadata']['language']} code:
        
        ```{file_data['metadata']['language']}
        {file_data['content']}
        ```
        
        Provide a comprehensive code review with specific suggestions for improvement.
        """
        
        # Make AI request
        ai_response = agent.ai_request(prompt, system_message, model)
        
        if 'error' in ai_response:
            raise click.ClickException(ai_response['error'])
        
        result = {
            'success': True,
            'file_path': path,
            'language': file_data['metadata']['language'],
            'review': ai_response['response'],
            'model_used': ai_response['model']
        }
        
        click.echo(format_output(result, output_format))
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


def _analyze_python_code(content: str) -> dict:
    """Analyze Python code structure."""
    analysis = {
        'functions': [],
        'classes': [],
        'imports': [],
        'comments': 0,
        'docstrings': 0
    }
    
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Count comments
        if stripped.startswith('#'):
            analysis['comments'] += 1
        
        # Find functions
        if stripped.startswith('def '):
            func_match = re.match(r'def\s+(\w+)\s*\(([^)]*)\)', stripped)
            if func_match:
                analysis['functions'].append({
                    'name': func_match.group(1),
                    'parameters': func_match.group(2),
                    'line_number': i + 1
                })
        
        # Find classes
        if stripped.startswith('class '):
            class_match = re.match(r'class\s+(\w+)(?:\([^)]*\))?:', stripped)
            if class_match:
                analysis['classes'].append({
                    'name': class_match.group(1),
                    'line_number': i + 1
                })
        
        # Find imports
        if stripped.startswith(('import ', 'from ')):
            analysis['imports'].append({
                'statement': stripped,
                'line_number': i + 1
            })
        
        # Count docstrings
        if '"""' in stripped or "'''" in stripped:
            analysis['docstrings'] += 1
    
    return analysis


def _analyze_js_code(content: str) -> dict:
    """Analyze JavaScript/TypeScript code structure."""
    analysis = {
        'functions': [],
        'classes': [],
        'imports': [],
        'exports': [],
        'comments': 0
    }
    
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Count comments
        if stripped.startswith('//') or stripped.startswith('/*'):
            analysis['comments'] += 1
        
        # Find functions
        func_patterns = [
            r'function\s+(\w+)\s*\(',
            r'const\s+(\w+)\s*=\s*\(',
            r'let\s+(\w+)\s*=\s*\(',
            r'var\s+(\w+)\s*=\s*\(',
            r'(\w+)\s*:\s*function\s*\(',
            r'(\w+)\s*\([^)]*\)\s*=>\s*{?'
        ]
        
        for pattern in func_patterns:
            match = re.search(pattern, stripped)
            if match:
                analysis['functions'].append({
                    'name': match.group(1),
                    'line_number': i + 1
                })
                break
        
        # Find classes
        if stripped.startswith('class '):
            class_match = re.match(r'class\s+(\w+)', stripped)
            if class_match:
                analysis['classes'].append({
                    'name': class_match.group(1),
                    'line_number': i + 1
                })
        
        # Find imports/exports
        if 'import' in stripped:
            analysis['imports'].append({
                'statement': stripped,
                'line_number': i + 1
            })
        elif 'export' in stripped:
            analysis['exports'].append({
                'statement': stripped,
                'line_number': i + 1
            })
    
    return analysis


def _analyze_java_code(content: str) -> dict:
    """Analyze Java code structure."""
    analysis = {
        'classes': [],
        'methods': [],
        'imports': [],
        'packages': [],
        'comments': 0
    }
    
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Count comments
        if stripped.startswith('//') or stripped.startswith('/*'):
            analysis['comments'] += 1
        
        # Find packages
        if stripped.startswith('package '):
            analysis['packages'].append({
                'statement': stripped,
                'line_number': i + 1
            })
        
        # Find imports
        if stripped.startswith('import '):
            analysis['imports'].append({
                'statement': stripped,
                'line_number': i + 1
            })
        
        # Find classes
        if re.search(r'\bclass\s+\w+', stripped):
            class_match = re.search(r'class\s+(\w+)', stripped)
            if class_match:
                analysis['classes'].append({
                    'name': class_match.group(1),
                    'line_number': i + 1
                })
        
        # Find methods
        method_match = re.search(r'(public|private|protected)?\s*(static)?\s*\w+\s+(\w+)\s*\(', stripped)
        if method_match:
            analysis['methods'].append({
                'name': method_match.group(3),
                'line_number': i + 1
            })
    
    return analysis