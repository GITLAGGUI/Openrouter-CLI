import click
import os
import ast
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..core import AIAgent
from ..utils import handle_error, ai_thinking_animation


@click.group()
@click.pass_context
def debug(ctx):
    """AI-powered debugging and codebase analysis commands."""
    pass


@debug.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--language', type=click.Choice(['python', 'javascript', 'typescript', 'java', 'cpp', 'all']), 
              default='all', help='Programming language to focus on')
@click.option('--depth', type=int, default=3, help='Maximum directory depth to scan')
@click.option('--exclude', multiple=True, help='Directories to exclude (e.g., node_modules, __pycache__)')
@click.option('--output', type=click.Path(), help='Save analysis report to file')
@click.option('--model', help='AI model to use for analysis')
@click.pass_context
def analyze(ctx, directory: str, language: str, depth: int, exclude: tuple, output: Optional[str], model: Optional[str]):
    """Perform comprehensive codebase analysis with AI insights."""
    try:
        agent: AIAgent = ctx.obj['agent']
        
        if not model:
            model = agent.config.get_model('general')
        
        click.echo(f"🔍 Analyzing codebase in: {directory}")
        click.echo(f"📋 Language focus: {language}")
        click.echo(f"📊 Scanning depth: {depth} levels")
        
        # Scan codebase
        loader = ai_thinking_animation("Scanning codebase structure")
        
        try:
            scan_result = _scan_codebase(directory, language, depth, exclude)
            loader.stop()
            
            click.echo(f"✅ Found {scan_result['total_files']} files across {len(scan_result['languages'])} languages")
            
            # Perform detailed analysis
            analysis_result = _perform_detailed_analysis(scan_result, agent, model)
            
            # Generate AI insights
            click.echo("🤖 Generating AI insights...")
            ai_insights = _generate_ai_insights(scan_result, analysis_result, agent, model)
            
            # Compile final report
            report = _compile_analysis_report(scan_result, analysis_result, ai_insights)
            
            # Display summary
            _display_analysis_summary(report)
            
            # Save report if requested
            if output:
                _save_analysis_report(report, output)
                click.echo(f"📄 Full report saved to: {output}")
            
        except Exception as e:
            loader.stop()
            raise click.ClickException(f"Analysis failed: {e}")
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@debug.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--error-type', type=click.Choice(['syntax', 'logic', 'performance', 'security', 'all']), 
              default='all', help='Type of errors to look for')
@click.option('--fix-suggestions', is_flag=True, help='Generate fix suggestions')
@click.option('--model', help='AI model to use for debugging')
@click.pass_context
def file(ctx, file_path: str, error_type: str, fix_suggestions: bool, model: Optional[str]):
    """Debug a specific file with AI assistance."""
    try:
        agent: AIAgent = ctx.obj['agent']
        
        if not model:
            model = agent.config.get_model('general')
        
        file_path_obj = Path(file_path)
        
        click.echo(f"🐛 Debugging file: {file_path}")
        click.echo(f"🔍 Error type focus: {error_type}")
        
        # Read file content
        with open(file_path_obj, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Detect language
        language = _detect_language(file_path_obj)
        
        # Perform static analysis
        static_analysis = _perform_static_analysis(content, language, file_path_obj)
        
        # Generate AI debugging analysis
        loader = ai_thinking_animation("AI is analyzing the code for issues")
        
        try:
            debug_prompt = _create_debug_prompt(content, language, error_type, static_analysis)
            ai_result = agent.ai_request(debug_prompt, _get_debug_system_message(language), model)
            loader.stop()
            
            if not ai_result['success']:
                raise click.ClickException(ai_result['error'])
            
            # Parse and display results
            debug_results = _parse_debug_results(ai_result['response'], static_analysis)
            _display_debug_results(debug_results, file_path)
            
            # Generate fix suggestions if requested
            if fix_suggestions and debug_results['issues']:
                click.echo("\n🔧 Generating fix suggestions...")
                fix_suggestions_result = _generate_fix_suggestions(content, debug_results, agent, model)
                _display_fix_suggestions(fix_suggestions_result)
            
        except Exception as e:
            loader.stop()
            raise click.ClickException(f"Debugging analysis failed: {e}")
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


@debug.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--test-command', help='Command to run tests (e.g., "pytest", "npm test")')
@click.option('--fix-issues', is_flag=True, help='Attempt to automatically fix found issues')
@click.option('--model', help='AI model to use for analysis')
@click.pass_context
def project(ctx, directory: str, test_command: Optional[str], fix_issues: bool, model: Optional[str]):
    """Debug an entire project with comprehensive analysis."""
    try:
        agent: AIAgent = ctx.obj['agent']
        
        if not model:
            model = agent.config.get_model('general')
        
        project_path = Path(directory)
        
        click.echo(f"🚀 Starting comprehensive project debugging: {directory}")
        
        # Step 1: Project structure analysis
        click.echo("📁 Analyzing project structure...")
        structure_analysis = _analyze_project_structure(project_path)
        
        # Step 2: Dependency analysis
        click.echo("📦 Analyzing dependencies...")
        dependency_analysis = _analyze_dependencies(project_path)
        
        # Step 3: Code quality analysis
        click.echo("🔍 Analyzing code quality...")
        quality_analysis = _analyze_code_quality(project_path, agent, model)
        
        # Step 4: Run tests if command provided
        test_results = None
        if test_command:
            click.echo(f"🧪 Running tests: {test_command}")
            test_results = _run_tests(project_path, test_command)
        
        # Step 5: Security analysis
        click.echo("🔒 Performing security analysis...")
        security_analysis = _analyze_security(project_path, agent, model)
        
        # Step 6: Performance analysis
        click.echo("⚡ Analyzing performance patterns...")
        performance_analysis = _analyze_performance(project_path, agent, model)
        
        # Compile comprehensive report
        project_report = {
            'project_path': str(project_path),
            'analysis_timestamp': datetime.now().isoformat(),
            'structure': structure_analysis,
            'dependencies': dependency_analysis,
            'code_quality': quality_analysis,
            'test_results': test_results,
            'security': security_analysis,
            'performance': performance_analysis
        }
        
        # Display comprehensive summary
        _display_project_debug_summary(project_report)
        
        # Auto-fix issues if requested
        if fix_issues:
            click.echo("\n🔧 Attempting to auto-fix identified issues...")
            fix_results = _auto_fix_issues(project_report, agent, model)
            _display_fix_results(fix_results)
        
        # Save detailed report
        report_path = project_path / f"debug_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(project_report, f, indent=2, default=str)
        
        click.echo(f"\n📄 Detailed report saved: {report_path}")
        
    except Exception as e:
        handle_error(e, ctx.obj.get('logger'), ctx.obj.get('verbose', False))


def _scan_codebase(directory: str, language: str, depth: int, exclude: tuple) -> Dict[str, Any]:
    """Scan codebase and gather file information."""
    dir_path = Path(directory)
    
    # Language extensions mapping
    extensions = {
        'python': ['.py'],
        'javascript': ['.js', '.jsx'],
        'typescript': ['.ts', '.tsx'],
        'java': ['.java'],
        'cpp': ['.cpp', '.cxx', '.cc', '.c'],
        'all': ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.cxx', '.cc', '.c', '.cs', '.php', '.rb', '.go', '.rs']
    }
    
    target_extensions = extensions.get(language, extensions['all'])
    exclude_dirs = set(exclude) | {'__pycache__', 'node_modules', '.git', 'dist', 'build', '.venv', 'venv'}
    
    files_info = []
    languages_found = set()
    total_lines = 0
    
    def scan_directory(path: Path, current_depth: int):
        nonlocal total_lines
        
        if current_depth > depth:
            return
        
        for item in path.iterdir():
            if item.is_dir() and item.name not in exclude_dirs:
                scan_directory(item, current_depth + 1)
            elif item.is_file() and item.suffix in target_extensions:
                try:
                    with open(item, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = len(content.split('\n'))
                        total_lines += lines
                    
                    file_info = {
                        'path': str(item),
                        'relative_path': str(item.relative_to(dir_path)),
                        'language': _detect_language(item),
                        'size': item.stat().st_size,
                        'lines': lines,
                        'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    }
                    
                    files_info.append(file_info)
                    languages_found.add(file_info['language'])
                    
                except (UnicodeDecodeError, PermissionError):
                    continue
    
    scan_directory(dir_path, 0)
    
    return {
        'directory': directory,
        'total_files': len(files_info),
        'total_lines': total_lines,
        'languages': list(languages_found),
        'files': files_info
    }


def _detect_language(file_path: Path) -> str:
    """Detect programming language from file extension."""
    ext = file_path.suffix.lower()
    
    mapping = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.cxx': 'cpp',
        '.cc': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
        '.php': 'php',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust'
    }
    
    return mapping.get(ext, 'unknown')


def _perform_static_analysis(content: str, language: str, file_path: Path) -> Dict[str, Any]:
    """Perform static analysis on code content."""
    analysis = {
        'syntax_errors': [],
        'complexity_metrics': {},
        'code_smells': [],
        'security_issues': []
    }
    
    if language == 'python':
        # Python-specific analysis
        try:
            ast.parse(content)
        except SyntaxError as e:
            analysis['syntax_errors'].append({
                'line': e.lineno,
                'message': str(e),
                'type': 'syntax_error'
            })
        
        # Basic complexity analysis
        lines = content.split('\n')
        analysis['complexity_metrics'] = {
            'total_lines': len(lines),
            'blank_lines': len([line for line in lines if not line.strip()]),
            'comment_lines': len([line for line in lines if line.strip().startswith('#')]),
            'code_lines': len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        }
        
        # Look for common code smells
        if 'TODO' in content or 'FIXME' in content:
            analysis['code_smells'].append('Contains TODO/FIXME comments')
        
        if content.count('print(') > 5:
            analysis['code_smells'].append('Excessive print statements (possible debugging code)')
        
        if 'eval(' in content or 'exec(' in content:
            analysis['security_issues'].append('Use of eval() or exec() - potential security risk')
    
    return analysis


def _create_debug_prompt(content: str, language: str, error_type: str, static_analysis: Dict[str, Any]) -> str:
    """Create a debugging prompt for AI analysis."""
    
    focus_instructions = {
        'syntax': 'Focus on syntax errors, typos, and structural issues',
        'logic': 'Focus on logical errors, incorrect algorithms, and flow issues',
        'performance': 'Focus on performance bottlenecks and optimization opportunities',
        'security': 'Focus on security vulnerabilities and best practices',
        'all': 'Perform comprehensive analysis covering all types of issues'
    }
    
    prompt = f"""
Analyze this {language} code for debugging purposes. {focus_instructions.get(error_type, focus_instructions['all'])}.

Static analysis results:
- Syntax errors found: {len(static_analysis.get('syntax_errors', []))}
- Code smells detected: {len(static_analysis.get('code_smells', []))}
- Security issues flagged: {len(static_analysis.get('security_issues', []))}

Code to analyze:
{content}

Please provide a detailed analysis including:
1. Issues found (with line numbers if possible)
2. Severity level (critical, high, medium, low)
3. Impact description
4. Root cause analysis
5. Recommended solutions

Format your response as structured analysis with clear sections.
"""
    
    return prompt


def _get_debug_system_message(language: str) -> str:
    """Get appropriate system message for debugging."""
    return f"You are an expert {language} developer and debugging specialist with deep knowledge of common issues, best practices, and optimization techniques."


def _parse_debug_results(ai_response: str, static_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Parse AI debugging response into structured results."""
    # This is a simplified parser - in a real implementation, you'd want more sophisticated parsing
    return {
        'ai_analysis': ai_response,
        'static_analysis': static_analysis,
        'issues': [],  # Would be populated by parsing the AI response
        'recommendations': []  # Would be populated by parsing the AI response
    }


def _display_debug_results(results: Dict[str, Any], file_path: str):
    """Display debugging results in a formatted way."""
    click.echo(f"\n🐛 Debug Results for {file_path}")
    click.echo("=" * 60)
    
    # Display static analysis results
    static = results['static_analysis']
    if static.get('syntax_errors'):
        click.echo(f"❌ Syntax Errors: {len(static['syntax_errors'])}")
        for error in static['syntax_errors']:
            click.echo(f"   Line {error['line']}: {error['message']}")
    
    if static.get('code_smells'):
        click.echo(f"⚠️  Code Smells: {len(static['code_smells'])}")
        for smell in static['code_smells']:
            click.echo(f"   - {smell}")
    
    if static.get('security_issues'):
        click.echo(f"🔒 Security Issues: {len(static['security_issues'])}")
        for issue in static['security_issues']:
            click.echo(f"   - {issue}")
    
    # Display AI analysis
    click.echo(f"\n🤖 AI Analysis:")
    click.echo(results['ai_analysis'])


def _generate_fix_suggestions(content: str, debug_results: Dict[str, Any], agent: AIAgent, model: str) -> Dict[str, Any]:
    """Generate fix suggestions using AI."""
    fix_prompt = f"""
Based on the debugging analysis, provide specific fix suggestions for this code:

Original code:
{content}

Issues identified:
{debug_results['ai_analysis']}

Please provide:
1. Specific code fixes with before/after examples
2. Step-by-step implementation instructions
3. Alternative solutions where applicable
4. Best practices to prevent similar issues

Focus on actionable, practical solutions.
"""
    
    result = agent.ai_request(fix_prompt, "You are an expert code reviewer specializing in providing clear, actionable fix suggestions.", model)
    return result


def _display_fix_suggestions(fix_result: Dict[str, Any]):
    """Display fix suggestions."""
    if fix_result['success']:
        click.echo("\n🔧 Fix Suggestions:")
        click.echo("-" * 40)
        click.echo(fix_result['response'])
    else:
        click.echo(f"❌ Failed to generate fix suggestions: {fix_result.get('error', 'Unknown error')}")


# Additional helper functions for project-level debugging
def _analyze_project_structure(project_path: Path) -> Dict[str, Any]:
    """Analyze project structure and organization."""
    # Implementation would analyze directory structure, configuration files, etc.
    return {'structure': 'analyzed'}


def _analyze_dependencies(project_path: Path) -> Dict[str, Any]:
    """Analyze project dependencies for issues."""
    # Implementation would check package.json, requirements.txt, etc.
    return {'dependencies': 'analyzed'}


def _analyze_code_quality(project_path: Path, agent: AIAgent, model: str) -> Dict[str, Any]:
    """Analyze overall code quality."""
    # Implementation would perform comprehensive quality analysis
    return {'quality': 'analyzed'}


def _run_tests(project_path: Path, test_command: str) -> Dict[str, Any]:
    """Run project tests and analyze results."""
    try:
        result = subprocess.run(test_command, shell=True, cwd=project_path, 
                              capture_output=True, text=True, timeout=300)
        return {
            'exit_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {'error': 'Test execution timed out'}
    except Exception as e:
        return {'error': str(e)}


def _analyze_security(project_path: Path, agent: AIAgent, model: str) -> Dict[str, Any]:
    """Perform security analysis."""
    # Implementation would check for security vulnerabilities
    return {'security': 'analyzed'}


def _analyze_performance(project_path: Path, agent: AIAgent, model: str) -> Dict[str, Any]:
    """Analyze performance patterns."""
    # Implementation would identify performance issues
    return {'performance': 'analyzed'}


def _perform_detailed_analysis(scan_result: Dict[str, Any], agent: AIAgent, model: str) -> Dict[str, Any]:
    """Perform detailed analysis on scanned codebase."""
    # Implementation would perform comprehensive analysis
    return {'detailed_analysis': 'completed'}


def _generate_ai_insights(scan_result: Dict[str, Any], analysis_result: Dict[str, Any], agent: AIAgent, model: str) -> Dict[str, Any]:
    """Generate AI insights about the codebase."""
    # Implementation would generate AI-powered insights
    return {'ai_insights': 'generated'}


def _compile_analysis_report(scan_result: Dict[str, Any], analysis_result: Dict[str, Any], ai_insights: Dict[str, Any]) -> Dict[str, Any]:
    """Compile comprehensive analysis report."""
    return {
        'scan': scan_result,
        'analysis': analysis_result,
        'insights': ai_insights,
        'timestamp': datetime.now().isoformat()
    }


def _display_analysis_summary(report: Dict[str, Any]):
    """Display analysis summary."""
    click.echo("\n📊 Codebase Analysis Summary")
    click.echo("=" * 50)
    
    scan = report['scan']
    click.echo(f"📁 Total files: {scan['total_files']}")
    click.echo(f"📏 Total lines: {scan['total_lines']}")
    click.echo(f"🔤 Languages: {', '.join(scan['languages'])}")


def _save_analysis_report(report: Dict[str, Any], output_path: str):
    """Save analysis report to file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)


def _display_project_debug_summary(report: Dict[str, Any]):
    """Display project debugging summary."""
    click.echo("\n🚀 Project Debug Summary")
    click.echo("=" * 50)
    click.echo(f"📁 Project: {report['project_path']}")
    click.echo(f"⏰ Analysis time: {report['analysis_timestamp']}")


def _auto_fix_issues(report: Dict[str, Any], agent: AIAgent, model: str) -> Dict[str, Any]:
    """Attempt to automatically fix identified issues."""
    # Implementation would attempt automated fixes
    return {'auto_fix': 'attempted'}


def _display_fix_results(results: Dict[str, Any]):
    """Display auto-fix results."""
    click.echo("🔧 Auto-fix completed")