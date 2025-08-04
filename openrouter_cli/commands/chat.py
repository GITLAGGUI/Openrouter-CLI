import click
import sys
import json
import shlex
from typing import Optional

from ..core import AIAgent
from ..core.tools import ToolsManager
from ..utils import handle_error, format_output, ai_thinking_animation


@click.group()
@click.pass_context
def chat(ctx):
    """AI chat interface for direct interaction."""
    pass


@chat.command()
@click.option('--model', help='AI model to use for chat')
@click.option('--system', help='System message to set context')
@click.option('--max-turns', type=int, default=50, help='Maximum conversation turns')
@click.pass_context
def interactive(ctx, model: Optional[str], system: Optional[str], max_turns: int):
    """Start an interactive chat session with the AI."""
    try:
        agent: AIAgent = ctx.obj['agent']
        logger = ctx.obj['logger']
        
        # Initialize tools manager
        tools_manager = ToolsManager(agent, logger)
        
        if not model:
            model = agent.config.get_model('general')
        
        click.echo(f"OpenRouter CLI Interactive Chat")
        click.echo(f"Model: {model}")
        click.echo("=" * 50)
        click.echo("Commands:")
        click.echo("  /help     - Show available commands")
        click.echo("  /tools    - List available tools")
        click.echo("  /tools <tool_name> - Get help for a specific tool")
        click.echo("  /tools <tool_name> [params] - Execute a tool")
        click.echo("  /model <name> - Switch AI model")
        click.echo("  /clear    - Clear conversation history")
        click.echo("  /history  - Show conversation history")
        click.echo("  /exit     - End the chat session")
        click.echo("=" * 50)
        
        conversation_history = []
        turn_count = 0
        
        # Add system message if provided
        if system:
            conversation_history.append({"role": "system", "content": system})
        
        while turn_count < max_turns:
            try:
                # Get user input
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['/exit', '/quit']:
                    break
                elif user_input.lower() == '/help':
                    _show_chat_help()
                    continue
                elif user_input.lower() == '/clear':
                    conversation_history = []
                    if system:
                        conversation_history.append({"role": "system", "content": system})
                    click.echo("Conversation history cleared.")
                    continue
                elif user_input.lower() == '/history':
                    _show_conversation_history(conversation_history)
                    continue
                elif user_input.lower().startswith('/model '):
                    new_model = user_input[7:].strip()
                    if new_model:
                        model = new_model
                        click.echo(f"Switched to model: {model}")
                    continue
                elif user_input.startswith('/tools'):
                    _handle_tools_command(user_input, tools_manager)
                    continue
                
                # Add user message to history
                conversation_history.append({"role": "user", "content": user_input})
                
                # Check if user is requesting HTML/website creation
                if any(keyword in user_input.lower() for keyword in ['website', 'html', 'web page', 'landing page', 'e-commerce', 'portfolio', 'blog']):
                    # Extract the request for HTML generation
                    html_prompt = user_input
                    
                    # Generate filename from prompt
                    from ..commands.html_generator import _generate_filename_from_prompt
                    filename = _generate_filename_from_prompt(html_prompt) + '.html'
                    
                    # Create HTML content using AI
                    enhanced_prompt = f"""
Create a complete, modern HTML file based on this request: {html_prompt}

Requirements:
- Complete HTML5 structure with semantic elements
- Modern, responsive design
- Embedded CSS styles
- Professional appearance
- Clean, well-commented code
- SEO-friendly meta tags

Provide only the complete HTML file content, no additional explanations.
"""
                    
                    # Show loading animation
                    loader = ai_thinking_animation("AI is generating HTML file")
                    
                    try:
                        completion = agent.client.chat.completions.create(
                            model=model,
                            messages=[{"role": "system", "content": "You are an expert web developer specializing in modern HTML, CSS, and responsive design."}, 
                                     {"role": "user", "content": enhanced_prompt}],
                            temperature=0.7,
                            max_tokens=4000
                        )
                        
                        loader.stop()
                        
                        if completion and completion.choices and len(completion.choices) > 0:
                            html_content = completion.choices[0].message.content
                            
                            # Extract HTML from response if wrapped in code blocks
                            import re
                            html_match = re.search(r'```html\n(.*?)\n```', html_content, re.DOTALL | re.IGNORECASE)
                            if html_match:
                                html_content = html_match.group(1)
                            elif '```' in html_content:
                                # Remove any code block markers
                                html_content = re.sub(r'```[a-zA-Z]*\n?', '', html_content)
                                html_content = html_content.replace('```', '')
                            
                            # Save HTML file
                            try:
                                with open(filename, 'w', encoding='utf-8') as f:
                                    f.write(html_content)
                                
                                # Create metadata file
                                import json
                                from datetime import datetime
                                metadata = {
                                    'filename': filename,
                                    'generated_at': datetime.now().isoformat(),
                                    'prompt': html_prompt,
                                    'model_used': model,
                                    'file_size': len(html_content)
                                }
                                
                                metadata_filename = filename.replace('.html', '.json')
                                with open(metadata_filename, 'w', encoding='utf-8') as f:
                                    json.dump(metadata, f, indent=2)
                                
                                ai_response = f"HTML file created successfully: {filename}\nMetadata saved: {metadata_filename}\nFile size: {len(html_content)} characters\n\nYour website has been generated and saved locally. You can open {filename} in your browser to view it."
                                
                                # Ask if user wants to open in browser
                                if click.confirm("Would you like to open the file in your default browser?", default=False):
                                    import webbrowser
                                    import os
                                    webbrowser.open(f"file://{os.path.abspath(filename)}")
                                
                            except Exception as e:
                                ai_response = f"Error saving HTML file: {e}\n\nGenerated HTML content:\n{html_content[:500]}{'...' if len(html_content) > 500 else ''}"
                        else:
                            ai_response = "Error: No HTML content generated"
                    
                    except Exception as e:
                        loader.stop()
                        ai_response = f"Error generating HTML: {e}"
                
                else:
                    # Regular chat interaction
                    # Make AI request with full conversation history
                    messages = conversation_history.copy()
                    
                    # Show loading animation while AI processes
                    loader = ai_thinking_animation("AI is thinking")
                    
                    try:
                        completion = agent.client.chat.completions.create(
                            model=model,
                            messages=messages,
                            temperature=0.7,
                            max_tokens=4000
                        )
                        
                        loader.stop()  # Stop loading animation
                        
                        if completion and completion.choices and len(completion.choices) > 0:
                            ai_response = completion.choices[0].message.content
                        else:
                            ai_response = "Error: No response from AI model"
                    
                    except Exception as e:
                        loader.stop()  # Stop loading animation on error
                        ai_response = f"Error: {e}"
                
                # Add AI response to history and display
                if ai_response:
                    conversation_history.append({"role": "assistant", "content": ai_response})
                    click.echo(f"\nAI: {ai_response}")
                else:
                    click.echo(f"\nError: No response from AI model")
                    # Remove the user message from history since AI didn't respond
                    conversation_history.pop()
                
                turn_count += 1
                
            except KeyboardInterrupt:
                break
            except EOFError:
                break
        
        click.echo(f"\nChat session ended after {turn_count} turns.")
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@chat.command()
@click.argument('question', type=str)
@click.option('--model', help='AI model to use')
@click.option('--system', help='System message to set context')
@click.option('--format', 'output_format', default='human',
              type=click.Choice(['human', 'json', 'yaml']),
              help='Output format')
@click.pass_context
def ask(ctx, question: str, model: Optional[str], system: Optional[str], output_format: str):
    """Ask a single question and get an AI response."""
    try:
        agent: AIAgent = ctx.obj['agent']
        
        if not model:
            model = agent.config.get_model('general')
        
        # Make AI request
        ai_response = agent.ai_request(question, system or "", model)
        
        if 'error' in ai_response:
            raise click.ClickException(ai_response['error'])
        
        if output_format == 'human':
            click.echo(ai_response['response'])
        else:
            click.echo(format_output(ai_response, output_format))
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@chat.command()
@click.argument('prompt', type=str)
@click.option('--model', help='AI model to use')
@click.option('--system', help='System message to set context')
@click.option('--temperature', type=float, default=0.7, help='Response creativity (0.0-2.0)')
@click.option('--max-tokens', type=int, default=4000, help='Maximum response length')
@click.option('--format', 'output_format', default='human',
              type=click.Choice(['human', 'json', 'yaml']),
              help='Output format')
@click.pass_context
def prompt(ctx, prompt: str, model: Optional[str], system: Optional[str], 
           temperature: float, max_tokens: int, output_format: str):
    """Execute a custom prompt with advanced parameters."""
    try:
        agent: AIAgent = ctx.obj['agent']
        
        if not model:
            model = agent.config.get_model('general')
        
        # Prepare messages
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        # Make AI request with custom parameters
        try:
            completion = agent.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            ai_response = {
                'success': True,
                'response': completion.choices[0].message.content,
                'model': model,
                'usage': dict(completion.usage) if completion.usage else None,
                'parameters': {
                    'temperature': temperature,
                    'max_tokens': max_tokens
                }
            }
            
        except Exception as e:
            raise click.ClickException(f"AI request failed: {e}")
        
        if output_format == 'human':
            click.echo(ai_response['response'])
        else:
            click.echo(format_output(ai_response, output_format))
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


def _show_chat_help():
    """Show help for interactive chat commands."""
    help_text = """
Available Commands:
  /help           - Show this help message
  /exit, /quit    - End the chat session
  /clear          - Clear conversation history
  /history        - Show conversation history
  /model <name>   - Switch to a different AI model
  /tools          - List all available tools
  /tools <tool>   - Get help for a specific tool
  /tools <tool> [params] - Execute a tool with parameters

File Creation Examples:
  /tools fs_create path="website.html" prompt="Create a modern e-commerce website"
  /tools fs_create path="app.py" prompt="Create a Flask web application"
  /tools fs_create path="style.css" prompt="Create modern CSS for a landing page"

Available Models:
  qwen/qwen3-coder:free      - Specialized for coding tasks
  z-ai/glm-4.5-air:free      - General purpose AI model
  openrouter/horizon-beta:free - Experimental advanced model
  deepseek/deepseek-r1-0528:free - Deep reasoning model

Examples:
  /model qwen/qwen3-coder:free
  /tools fs_read path="script.py"
  /tools code_analyze path="main.py" detailed=true
  /tools web_fetch url="https://example.com" extract_text=true
"""
    click.echo(help_text)


def _handle_tools_command(user_input: str, tools_manager: ToolsManager):
    """Handle /tools commands."""
    try:
        parts = shlex.split(user_input)
        
        if len(parts) == 1:  # Just "/tools"
            tools_info = tools_manager.list_tools()
            click.echo("\nAvailable Tools:")
            click.echo("=" * 40)
            
            for category, tools in tools_info['categories'].items():
                click.echo(f"\n{category}:")
                for tool in tools:
                    click.echo(f"  {tool['name']} - {tool['description']}")
            
            click.echo(f"\nTotal: {tools_info['total_tools']} tools")
            click.echo("\nUse '/tools <tool_name>' for detailed help")
            click.echo("Use '/tools <tool_name> [params]' to execute")
            
        elif len(parts) == 2:  # "/tools <tool_name>"
            tool_name = parts[1]
            help_info = tools_manager.get_tool_help(tool_name)
            
            if 'error' in help_info:
                click.echo(f"Error: {help_info['error']}")
                return
            
            click.echo(f"\nTool: {help_info['name']}")
            click.echo("=" * 40)
            click.echo(f"Description: {help_info['description']}")
            click.echo(f"Category: {help_info['category']}")
            
            if help_info['parameters']:
                click.echo("\nParameters:")
                for param_name, param_info in help_info['parameters'].items():
                    required = "Required" if param_info.get('required', False) else "Optional"
                    click.echo(f"  {param_name} ({param_info['type']}) - {required}")
                    click.echo(f"    {param_info['description']}")
            
            click.echo(f"\nExample: {help_info['usage_example']}")
            
        else:  # "/tools <tool_name> param1=value1 param2=value2"
            tool_name = parts[1]
            
            # Parse parameters
            params = {}
            for param_str in parts[2:]:
                if '=' in param_str:
                    key, value = param_str.split('=', 1)
                    # Try to parse as JSON for complex types
                    try:
                        if value.lower() in ['true', 'false']:
                            params[key] = value.lower() == 'true'
                        elif value.isdigit():
                            params[key] = int(value)
                        elif value.replace('.', '').isdigit():
                            params[key] = float(value)
                        else:
                            # Remove quotes if present
                            params[key] = value.strip('"\'')
                    except:
                        params[key] = value.strip('"\'')
            
            click.echo(f"\nExecuting tool: {tool_name}")
            if params:
                click.echo(f"Parameters: {params}")
            
            result = tools_manager.execute_tool(tool_name, **params)
            
            if 'error' in result:
                click.echo(f"Error: {result['error']}")
            else:
                click.echo("Tool executed successfully")
                _display_tool_result(result, tool_name)
                
    except Exception as e:
        click.echo(f"Error parsing tools command: {e}")


def _display_tool_result(result: dict, tool_name: str):
    """Display tool execution result in a formatted way."""
    try:
        if tool_name.startswith('fs_'):
            # File operation results
            if 'file_path' in result:
                click.echo(f"File: {result['file_path']}")
            if 'content' in result:
                content = result['content']
                if len(content) > 500:
                    click.echo(f"Content (first 500 chars):\n{content[:500]}...")
                else:
                    click.echo(f"Content:\n{content}")
            if 'metadata' in result:
                meta = result['metadata']
                click.echo(f"Size: {meta.get('size', 'N/A')} bytes, Lines: {meta.get('lines', 'N/A')}")
            if 'results' in result:
                click.echo(f"Found {len(result['results'])} files")
                for file_info in result['results'][:5]:  # Show first 5
                    click.echo(f"  {file_info['filename']} ({file_info['size']} bytes)")
        
        elif tool_name.startswith('code_'):
            # Code analysis results
            if 'analysis' in result:
                analysis = result['analysis']
                click.echo(f"Language: {analysis.get('language', 'Unknown')}")
                click.echo(f"Lines: {analysis.get('lines_of_code', 0)} (total: {analysis.get('total_lines', 0)})")
                if 'functions' in analysis:
                    click.echo(f"Functions: {len(analysis['functions'])}")
                if 'classes' in analysis:
                    click.echo(f"Classes: {len(analysis['classes'])}")
            if 'review' in result:
                click.echo(f"Code Review:\n{result['review']}")
        
        elif tool_name.startswith('web_'):
            # Web operation results
            if 'status_code' in result:
                click.echo(f"Status: {result['status_code']}")
            if 'content_type' in result:
                click.echo(f"Type: {result['content_type']}")
            if 'extracted_text' in result:
                text = result['extracted_text']
                if len(text) > 300:
                    click.echo(f"Extracted text (first 300 chars):\n{text[:300]}...")
                else:
                    click.echo(f"Extracted text:\n{text}")
        
        elif tool_name.startswith('ai_'):
            # AI tool results
            if 'response' in result:
                click.echo(f"AI Response:\n{result['response']}")
            if 'summary' in result:
                click.echo(f"Summary:\n{result['summary']}")
        
        else:
            # Generic result display
            for key, value in result.items():
                if key not in ['success', 'error']:
                    if isinstance(value, str) and len(value) > 200:
                        click.echo(f"{key}: {value[:200]}...")
                    else:
                        click.echo(f"{key}: {value}")
                        
    except Exception as e:
        # Fallback to JSON display
        click.echo(f"Result:\n{json.dumps(result, indent=2, default=str)}")


def _show_conversation_history(history):
    """Show the conversation history."""
    click.echo("\nConversation History:")
    click.echo("-" * 30)
    
    for i, message in enumerate(history):
        role = message['role']
        content = message['content']
        
        if role == 'system':
            click.echo(f"System: {content[:100]}{'...' if len(content) > 100 else ''}")
        elif role == 'user':
            click.echo(f"User: {content[:100]}{'...' if len(content) > 100 else ''}")
        elif role == 'assistant':
            click.echo(f"AI: {content[:100]}{'...' if len(content) > 100 else ''}")
    
    click.echo("-" * 30)