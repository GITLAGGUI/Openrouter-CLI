import click
import requests
import re
from urllib.parse import urlparse
from typing import Optional

from ..core import AIAgent
from ..utils import handle_error, format_output, validate_url


@click.group()
@click.pass_context
def web(ctx):
    """Web operations: fetch content, extract text, and make API requests."""
    pass


@web.command()
@click.argument('url', type=str)
@click.option('--extract-text', is_flag=True, help='Extract clean text from HTML')
@click.option('--save-to', type=click.Path(), help='Save content to file')
@click.option('--format', 'output_format', default='human',
              type=click.Choice(['human', 'json', 'yaml']),
              help='Output format')
@click.option('--timeout', type=int, default=30, help='Request timeout in seconds')
@click.pass_context
def fetch(ctx, url: str, extract_text: bool, save_to: Optional[str], 
          output_format: str, timeout: int):
    """Fetch content from a URL with optional text extraction."""
    try:
        # Validate URL
        validate_url(url)
        
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Make request
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '').lower()
        
        result = {
            'success': True,
            'url': url,
            'status_code': response.status_code,
            'content_type': content_type,
            'content_length': len(response.content),
            'headers': dict(response.headers)
        }
        
        # Handle different content types
        if 'application/json' in content_type:
            try:
                result['json_data'] = response.json()
            except:
                result['raw_content'] = response.text
        elif 'text/' in content_type or 'html' in content_type:
            result['raw_content'] = response.text
            
            if extract_text and 'html' in content_type:
                # Basic HTML text extraction
                text = _extract_text_from_html(response.text)
                result['extracted_text'] = text
        else:
            result['raw_content'] = response.content.decode('utf-8', errors='ignore')
        
        # Save to file if requested
        if save_to:
            from pathlib import Path
            save_path = Path(save_to)
            
            if 'extracted_text' in result:
                save_path.write_text(result['extracted_text'], encoding='utf-8')
            elif 'raw_content' in result:
                save_path.write_text(result['raw_content'], encoding='utf-8')
            else:
                save_path.write_bytes(response.content)
            
            result['saved_to'] = str(save_path)
        
        click.echo(format_output(result, output_format))
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@web.command()
@click.argument('url', type=str)
@click.option('--method', default='GET', type=click.Choice(['GET', 'POST', 'PUT', 'DELETE', 'PATCH']),
              help='HTTP method')
@click.option('--data', help='JSON data to send with request')
@click.option('--headers', help='Additional headers as JSON')
@click.option('--timeout', type=int, default=30, help='Request timeout in seconds')
@click.option('--format', 'output_format', default='human',
              type=click.Choice(['human', 'json', 'yaml']),
              help='Output format')
@click.pass_context
def api(ctx, url: str, method: str, data: Optional[str], headers: Optional[str], 
        timeout: int, output_format: str):
    """Make API requests with custom methods, data, and headers."""
    try:
        import json
        
        # Validate URL
        validate_url(url)
        
        # Prepare headers
        request_headers = {
            'User-Agent': 'OpenRouter-CLI/1.0',
            'Accept': 'application/json',
        }
        
        if headers:
            try:
                custom_headers = json.loads(headers)
                request_headers.update(custom_headers)
            except json.JSONDecodeError:
                raise click.ClickException("Invalid JSON format for headers")
        
        # Prepare data
        request_data = None
        if data:
            try:
                request_data = json.loads(data)
                request_headers['Content-Type'] = 'application/json'
            except json.JSONDecodeError:
                # Treat as raw data
                request_data = data
        
        # Make request
        response = requests.request(
            method=method,
            url=url,
            headers=request_headers,
            json=request_data if isinstance(request_data, dict) else None,
            data=request_data if not isinstance(request_data, dict) else None,
            timeout=timeout
        )
        
        # Prepare result
        result = {
            'success': True,
            'url': url,
            'method': method,
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'content_type': response.headers.get('content-type', ''),
        }
        
        # Handle response content
        try:
            if response.headers.get('content-type', '').startswith('application/json'):
                result['data'] = response.json()
            else:
                result['data'] = response.text
        except:
            result['data'] = response.text
        
        # Add error info if not successful
        if not response.ok:
            result['success'] = False
            result['error'] = f"HTTP {response.status_code}: {response.reason}"
        
        click.echo(format_output(result, output_format))
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@web.command()
@click.argument('html_content', type=str)
@click.option('--from-file', type=click.Path(exists=True), help='Read HTML from file')
@click.option('--save-to', type=click.Path(), help='Save extracted text to file')
@click.option('--format', 'output_format', default='human',
              type=click.Choice(['human', 'json', 'yaml']),
              help='Output format')
@click.pass_context
def extract(ctx, html_content: str, from_file: Optional[str], save_to: Optional[str], 
            output_format: str):
    """Extract clean text from HTML content."""
    try:
        # Get HTML content
        if from_file:
            from pathlib import Path
            html_content = Path(from_file).read_text(encoding='utf-8')
        
        # Extract text
        extracted_text = _extract_text_from_html(html_content)
        
        result = {
            'success': True,
            'original_length': len(html_content),
            'extracted_length': len(extracted_text),
            'extracted_text': extracted_text
        }
        
        # Save to file if requested
        if save_to:
            from pathlib import Path
            save_path = Path(save_to)
            save_path.write_text(extracted_text, encoding='utf-8')
            result['saved_to'] = str(save_path)
        
        click.echo(format_output(result, output_format))
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


def _extract_text_from_html(html_content: str) -> str:
    """Extract clean text from HTML content."""
    # Remove script and style elements
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove extra blank lines
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text