# OpenRouter CLI - Enhanced Features Guide

## Overview

The OpenRouter CLI has been enhanced with powerful new features including automatic HTML generation, AI-powered debugging, and global accessibility. This guide covers all the new capabilities.

## 🌟 New Features

### 1. Automatic HTML File Generation

The CLI now automatically detects when you're requesting website creation and generates properly named HTML files instead of just displaying code in the terminal.

#### Interactive Chat with HTML Generation

When you use the interactive chat and mention keywords like "website", "html", "web page", "landing page", "e-commerce", "portfolio", or "blog", the AI will automatically:

1. Generate a complete HTML file
2. Create a meaningful filename based on your request
3. Save the file with proper metadata
4. Offer to open it in your browser

**Example:**
```bash
openrouter-cli chat interactive
```

Then type: "create a modern e-commerce website with product listings"

The AI will automatically:
- Generate `ecommerce_product_listings_20241201_1430.html`
- Create `ecommerce_product_listings_20241201_1430.json` with metadata
- Offer to open the file in your browser

#### Dedicated HTML Commands

**Generate HTML Files:**
```bash
# Basic HTML generation
openrouter-cli html generate "Create a portfolio website for a web developer"

# Advanced options
openrouter-cli html generate "Create an e-commerce site" \
  --template ecommerce \
  --framework bootstrap \
  --include-css \
  --include-js \
  --filename my-store

# Available templates: basic, ecommerce, portfolio, blog, landing
# Available frameworks: none, bootstrap, tailwind
```

**Enhance Existing HTML:**
```bash
openrouter-cli html enhance mysite.html \
  --instruction "Add a contact form with validation"
```

**List HTML Files:**
```bash
# List all HTML files in current directory
openrouter-cli html list .

# Recursive search
openrouter-cli html list ./projects --recursive
```

### 2. AI-Powered Debugging Agent

The new debugging agent can analyze your entire codebase, identify issues, and suggest fixes.

#### Analyze Entire Codebase
```bash
# Comprehensive codebase analysis
openrouter-cli debug analyze ./my-project

# Focus on specific language
openrouter-cli debug analyze ./my-project --language python

# Save detailed report
openrouter-cli debug analyze ./my-project --output analysis-report.json
```

#### Debug Specific Files
```bash
# Debug a specific file
openrouter-cli debug file script.py

# Focus on specific error types
openrouter-cli debug file script.py --error-type security

# Get fix suggestions
openrouter-cli debug file script.py --fix-suggestions

# Available error types: syntax, logic, performance, security, all
```

#### Project-Level Debugging
```bash
# Comprehensive project debugging
openrouter-cli debug project ./my-app

# Include test execution
openrouter-cli debug project ./my-app --test-command "pytest"

# Auto-fix issues (experimental)
openrouter-cli debug project ./my-app --fix-issues
```

### 3. Global Accessibility

The CLI is now globally accessible from any directory on your system.

**Installation:**
```bash
# Install in editable mode (recommended for development)
pip install -e .

# Or install normally
pip install .
```

**Usage from any directory:**
```bash
# Works from anywhere
cd ~/Desktop
openrouter-cli chat interactive

cd ~/Documents/projects
openrouter-cli html generate "Create a landing page"

cd /any/directory
openrouter-cli debug analyze .
```

## 🔧 Enhanced Interactive Chat

The interactive chat now has intelligent context awareness:

### Automatic HTML Generation
When you mention website-related keywords, the chat automatically switches to HTML generation mode:

**Triggers:**
- "website", "html", "web page"
- "landing page", "e-commerce"
- "portfolio", "blog"

**Example Conversation:**
```
You: create a modern portfolio website for a photographer
AI: ✅ HTML file created successfully: modern_portfolio_photographer_20241201_1430.html
📊 Metadata saved: modern_portfolio_photographer_20241201_1430.json
📏 File size: 15,847 characters

🌐 Your website has been generated and saved locally. You can open modern_portfolio_photographer_20241201_1430.html in your browser to view it.

Would you like to open the file in your default browser? [y/N]: y
```

### Enhanced Tools Integration
The chat still supports all the original `/tools` commands:

```
/tools fs_create path="app.py" prompt="Create a Flask web application"
/tools code_analyze path="main.py" detailed=true
/tools web_fetch url="https://example.com" extract_text=true
```

## 📁 File Organization

### HTML Files
Generated HTML files follow a consistent naming pattern:
- `{meaningful_keywords}_{timestamp}.html`
- Accompanying metadata: `{filename}.json`

**Example:**
- Request: "create an e-commerce website with shopping cart"
- Generated: `ecommerce_shopping_cart_20241201_1430.html`
- Metadata: `ecommerce_shopping_cart_20241201_1430.json`

### Debug Reports
Debug analysis generates comprehensive reports:
- `debug_report_{timestamp}.json` for project analysis
- Detailed analysis with recommendations
- Auto-fix suggestions where applicable

## 🎯 Use Cases

### Web Development
```bash
# Quick prototyping
openrouter-cli chat interactive
> "create a responsive landing page for a tech startup"

# Professional development
openrouter-cli html generate "Create a corporate website with contact forms" \
  --template landing \
  --framework bootstrap \
  --include-css \
  --include-js
```

### Code Debugging
```bash
# Before committing code
openrouter-cli debug analyze ./src --language python

# Debugging specific issues
openrouter-cli debug file problematic_script.py --error-type logic --fix-suggestions

# Project health check
openrouter-cli debug project . --test-command "npm test"
```

### Learning and Exploration
```bash
# Analyze open source projects
git clone https://github.com/example/project
openrouter-cli debug analyze ./project

# Learn from generated code
openrouter-cli html generate "create a modern CSS grid layout example"
```

## 🔧 Configuration

The CLI maintains all existing configuration options while adding new capabilities:

```bash
# Initialize configuration (if not already done)
openrouter-cli config init

# Check system health
openrouter-cli doctor

# View available models
openrouter-cli config models
```

## 🚀 Advanced Features

### Template System
The HTML generator includes multiple templates:

- **basic**: Clean, simple HTML pages
- **ecommerce**: Modern online stores with product listings
- **portfolio**: Professional portfolio websites
- **blog**: Blog-style websites with articles
- **landing**: High-converting landing pages

### Framework Integration
Support for popular CSS frameworks:

- **Bootstrap 5**: Modern responsive framework
- **Tailwind CSS**: Utility-first CSS framework
- **Custom CSS**: Hand-crafted styles

### Intelligent Naming
The system generates meaningful filenames by:
1. Extracting key concepts from your request
2. Filtering out common words
3. Adding timestamps for uniqueness
4. Ensuring valid filename characters

## 📊 Metadata and Tracking

Every generated HTML file includes metadata:

```json
{
  "filename": "ecommerce_product_catalog_20241201_1430.html",
  "generated_at": "2024-12-01T14:30:45.123456",
  "prompt": "create an e-commerce website with product catalog",
  "template": "ecommerce",
  "framework": "bootstrap",
  "model_used": "qwen/qwen3-coder:free",
  "file_size": 15847,
  "features": {
    "responsive": true,
    "embedded_css": true,
    "embedded_js": false
  }
}
```

## 🔍 Debugging Capabilities

The debug agent provides:

### Static Analysis
- Syntax error detection
- Code complexity metrics
- Security vulnerability scanning
- Code smell identification

### AI-Powered Analysis
- Logic error detection
- Performance bottleneck identification
- Best practice recommendations
- Architecture suggestions

### Project-Level Insights
- Dependency analysis
- Test coverage assessment
- Security audit
- Performance profiling

## 🎨 Examples

### Complete Workflow Example

1. **Create a website:**
```bash
openrouter-cli chat interactive
> "create a portfolio website for a graphic designer with dark theme"
```

2. **Enhance it:**
```bash
openrouter-cli html enhance portfolio_graphic_designer_dark_20241201_1430.html \
  --instruction "add a contact form with email validation"
```

3. **Debug any issues:**
```bash
openrouter-cli debug file portfolio_graphic_designer_dark_20241201_1430.html \
  --error-type all \
  --fix-suggestions
```

### Development Workflow Example

1. **Analyze existing project:**
```bash
openrouter-cli debug analyze ./my-app --output analysis.json
```

2. **Debug specific issues:**
```bash
openrouter-cli debug file src/main.py --error-type performance --fix-suggestions
```

3. **Generate documentation website:**
```bash
openrouter-cli html generate "create a documentation website for my Python library" \
  --template basic \
  --include-css
```

## 🔧 Troubleshooting

### Common Issues

**CLI not found globally:**
```bash
# Reinstall in editable mode
pip uninstall openrouter-cli
pip install -e .
```

**HTML generation not working:**
- Ensure you're using keywords like "website", "html", "web page"
- Check your API key configuration: `openrouter-cli config init`

**Debug analysis failing:**
- Ensure the directory exists and contains code files
- Check file permissions
- Verify the programming language is supported

### Getting Help

```bash
# General help
openrouter-cli --help

# Command-specific help
openrouter-cli html --help
openrouter-cli debug --help

# System diagnostics
openrouter-cli doctor
```

## 🎉 Summary

The enhanced OpenRouter CLI now provides:

✅ **Automatic HTML file generation** with intelligent naming
✅ **AI-powered debugging** for comprehensive code analysis  
✅ **Global accessibility** from any directory
✅ **Professional templates** for different website types
✅ **Framework integration** (Bootstrap, Tailwind)
✅ **Metadata tracking** for all generated files
✅ **Enhanced interactive chat** with context awareness
✅ **Project-level analysis** with detailed reports

The CLI has evolved from a simple chat interface to a comprehensive development tool that bridges the gap between AI assistance and practical file generation, making it perfect for rapid prototyping, learning, and professional development workflows.