import click
import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from ..core import AIAgent
from ..utils import handle_error, format_output, ai_thinking_animation


@click.group()
@click.pass_context
def html(ctx):
    """HTML generation and management commands."""
    pass


@html.command()
@click.argument('prompt', type=str)
@click.option('--model', help='AI model to use for generation')
@click.option('--output-dir', default='.', help='Directory to save the HTML file')
@click.option('--filename', help='Custom filename (without extension)')
@click.option('--template', type=click.Choice(['basic', 'ecommerce', 'portfolio', 'blog', 'landing']), 
              default='basic', help='HTML template type')
@click.option('--include-css', is_flag=True, help='Include embedded CSS styling')
@click.option('--include-js', is_flag=True, help='Include embedded JavaScript')
@click.option('--responsive', is_flag=True, default=True, help='Make the design responsive')
@click.option('--framework', type=click.Choice(['none', 'bootstrap', 'tailwind']), 
              default='none', help='CSS framework to use')
@click.pass_context
def generate(ctx, prompt: str, model: Optional[str], output_dir: str, filename: Optional[str],
             template: str, include_css: bool, include_js: bool, responsive: bool, framework: str):
    """Generate an HTML file based on a prompt with automatic naming."""
    try:
        agent: AIAgent = ctx.obj['agent']
        logger = ctx.obj['logger']
        
        if not model:
            model = agent.config.get_model('general')
        
        # Generate filename if not provided
        if not filename:
            filename = _generate_filename_from_prompt(prompt)
        
        # Ensure .html extension
        if not filename.endswith('.html'):
            filename += '.html'
        
        # Create full path
        output_path = Path(output_dir) / filename
        
        # Create enhanced prompt for HTML generation
        enhanced_prompt = _create_html_prompt(prompt, template, include_css, include_js, responsive, framework)
        
        click.echo(f"Generating HTML file: {filename}")
        click.echo(f"Template: {template}")
        click.echo(f"Framework: {framework}")
        
        # Show loading animation
        loader = ai_thinking_animation("AI is generating HTML")
        
        try:
            # Make AI request
            ai_response = agent.ai_request(enhanced_prompt, _get_system_message(template), model)
            loader.stop()
            
            if not ai_response['success']:
                raise click.ClickException(ai_response['error'])
            
            # Extract HTML content
            html_content = _extract_html_from_response(ai_response['response'])
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write HTML file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Create metadata file
            metadata = {
                'filename': filename,
                'generated_at': datetime.now().isoformat(),
                'prompt': prompt,
                'template': template,
                'framework': framework,
                'model_used': model,
                'file_size': len(html_content),
                'features': {
                    'responsive': responsive,
                    'embedded_css': include_css,
                    'embedded_js': include_js
                }
            }
            
            metadata_path = output_path.with_suffix('.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            click.echo(f"HTML file generated successfully: {output_path}")
            click.echo(f"Metadata saved: {metadata_path}")
            click.echo(f"File size: {len(html_content)} characters")
            
            # Show preview option
            if click.confirm("Would you like to open the file in your default browser?"):
                import webbrowser
                webbrowser.open(f"file://{output_path.absolute()}")
            
        except Exception as e:
            loader.stop()
            raise click.ClickException(f"HTML generation failed: {e}")
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@html.command()
@click.argument('html_file', type=click.Path(exists=True))
@click.option('--model', help='AI model to use for enhancement')
@click.option('--instruction', required=True, help='Enhancement instruction')
@click.option('--backup', is_flag=True, default=True, help='Create backup of original file')
@click.pass_context
def enhance(ctx, html_file: str, model: Optional[str], instruction: str, backup: bool):
    """Enhance an existing HTML file with AI assistance."""
    try:
        agent: AIAgent = ctx.obj['agent']
        
        if not model:
            model = agent.config.get_model('general')
        
        html_path = Path(html_file)
        
        # Read existing HTML
        with open(html_path, 'r', encoding='utf-8') as f:
            current_html = f.read()
        
        # Create backup if requested
        if backup:
            backup_path = html_path.with_suffix(f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(current_html)
            click.echo(f"📋 Backup created: {backup_path}")
        
        # Create enhancement prompt
        enhancement_prompt = f"""
Enhance this HTML file according to the instruction: {instruction}

Current HTML:
{current_html}

Please provide the complete enhanced HTML file, maintaining the existing structure while implementing the requested changes.
"""
        
        click.echo(f"Enhancing HTML file with instruction: {instruction}")
        
        # Show loading animation
        loader = ai_thinking_animation("AI is enhancing HTML")
        
        try:
            ai_response = agent.ai_request(enhancement_prompt, "You are an expert web developer specializing in HTML, CSS, and JavaScript.", model)
            loader.stop()
            
            if not ai_response['success']:
                raise click.ClickException(ai_response['error'])
            
            # Extract enhanced HTML
            enhanced_html = _extract_html_from_response(ai_response['response'])
            
            # Write enhanced HTML
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_html)
            
            click.echo(f"HTML file enhanced successfully: {html_path}")
            
        except Exception as e:
            loader.stop()
            raise click.ClickException(f"HTML enhancement failed: {e}")
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@html.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--recursive', is_flag=True, help='Search recursively in subdirectories')
@click.pass_context
def list(ctx, directory: str, recursive: bool):
    """List all HTML files in a directory with metadata."""
    try:
        dir_path = Path(directory)
        pattern = "**/*.html" if recursive else "*.html"
        
        html_files = list(dir_path.glob(pattern))
        
        if not html_files:
            click.echo("No HTML files found.")
            return
        
        click.echo(f"Found {len(html_files)} HTML file(s):")
        click.echo("=" * 60)
        
        for html_file in sorted(html_files):
            # Get file stats
            stats = html_file.stat()
            size = stats.st_size
            modified = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            # Try to load metadata
            metadata_file = html_file.with_suffix('.json')
            metadata = {}
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                except:
                    pass
            
            click.echo(f"📄 {html_file.name}")
            click.echo(f"   Path: {html_file}")
            click.echo(f"   Size: {size} bytes")
            click.echo(f"   Modified: {modified}")
            
            if metadata:
                click.echo(f"   Template: {metadata.get('template', 'Unknown')}")
                click.echo(f"   Generated: {metadata.get('generated_at', 'Unknown')}")
                if 'prompt' in metadata:
                    prompt_preview = metadata['prompt'][:50] + "..." if len(metadata['prompt']) > 50 else metadata['prompt']
                    click.echo(f"   Prompt: {prompt_preview}")
            
            click.echo()
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


def _generate_filename_from_prompt(prompt: str) -> str:
    """Generate a meaningful filename from the prompt."""
    # Extract key words from prompt
    words = re.findall(r'\b[a-zA-Z]+\b', prompt.lower())
    
    # Filter out common words
    stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'create', 'make', 'build', 'generate', 'website', 'page', 'html'}
    
    meaningful_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Take first 3-4 meaningful words
    filename_words = meaningful_words[:4] if len(meaningful_words) >= 4 else meaningful_words
    
    if not filename_words:
        # Fallback to timestamp-based name
        return f"generated_html_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Join with underscores and add timestamp
    base_name = "_".join(filename_words)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    
    return f"{base_name}_{timestamp}"


def _create_html_prompt(prompt: str, template: str, include_css: bool, include_js: bool, responsive: bool, framework: str) -> str:
    """Create an enhanced prompt for HTML generation."""
    
    template_instructions = {
        'basic': "Create a clean, simple HTML page",
        'ecommerce': "Create a modern e-commerce website with product listings, shopping cart functionality, and payment sections",
        'portfolio': "Create a professional portfolio website with sections for projects, skills, and contact information",
        'blog': "Create a blog-style website with article listings, sidebar, and navigation",
        'landing': "Create a compelling landing page with hero section, features, testimonials, and call-to-action"
    }
    
    framework_instructions = {
        'bootstrap': "Use Bootstrap 5 CSS framework with CDN links",
        'tailwind': "Use Tailwind CSS framework with CDN links",
        'none': "Use custom CSS styling"
    }
    
    enhanced_prompt = f"""
{template_instructions.get(template, template_instructions['basic'])} based on this request: {prompt}

Requirements:
- Template type: {template}
- CSS Framework: {framework_instructions.get(framework, framework_instructions['none'])}
- Responsive design: {'Yes' if responsive else 'No'}
- Embedded CSS: {'Yes' if include_css else 'No'}
- Embedded JavaScript: {'Yes' if include_js else 'No'}

Please create a complete, functional HTML file that includes:
1. Proper HTML5 structure with semantic elements
2. Modern, visually appealing design
3. {'Responsive layout that works on all devices' if responsive else 'Fixed layout design'}
4. {'Embedded CSS styles in <style> tags' if include_css else 'Minimal inline styles only'}
5. {'Interactive JavaScript functionality in <script> tags' if include_js else 'No JavaScript required'}
6. Accessibility features (alt tags, proper headings, etc.)
7. SEO-friendly meta tags
8. Clean, well-commented code

{f'Use {framework} framework with proper CDN links.' if framework != 'none' else 'Use custom CSS for styling.'}

Provide only the complete HTML file content, no additional explanations.
"""
    
    return enhanced_prompt


def _get_system_message(template: str) -> str:
    """Get appropriate system message based on template."""
    messages = {
        'basic': "You are an expert web developer specializing in clean, semantic HTML and CSS.",
        'ecommerce': "You are an expert e-commerce web developer with experience in creating modern online stores.",
        'portfolio': "You are an expert web developer specializing in professional portfolio websites.",
        'blog': "You are an expert web developer specializing in blog and content websites.",
        'landing': "You are an expert web developer specializing in high-converting landing pages."
    }
    
    return messages.get(template, messages['basic'])


def _extract_html_from_response(response: str) -> str:
    """Extract HTML content from AI response."""
    # Try to find HTML content between code blocks
    html_pattern = r'```html\n(.*?)\n```'
    match = re.search(html_pattern, response, re.DOTALL | re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    # Try to find HTML content between generic code blocks
    code_pattern = r'```\n(.*?)\n```'
    match = re.search(code_pattern, response, re.DOTALL)
    
    if match and '<!DOCTYPE html>' in match.group(1):
        return match.group(1).strip()
    
    # If no code blocks, check if the response itself is HTML
    if '<!DOCTYPE html>' in response or '<html' in response:
        return response.strip()
    
    # Fallback: wrap content in basic HTML structure
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Page</title>
</head>
<body>
    {response}
</body>
</html>"""