from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="openrouter-cli",
    version="1.0.0",
    author="OpenRouter CLI Team",
    author_email="support@openrouter-cli.dev",
    description="AI-powered CLI tool using OpenRouter for file operations, code analysis, and web interactions",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/openrouter-cli/openrouter-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Tools",
        "Topic :: Utilities",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Text Processing",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.910",
        ],
    },
    entry_points={
        "console_scripts": [
            "openrouter-cli=openrouter_cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "openrouter_cli": ["*.yaml", "*.yml", "*.json"],
    },
    keywords="ai, cli, openrouter, file-operations, code-analysis, web-scraping, chatbot",
    project_urls={
        "Bug Reports": "https://github.com/openrouter-cli/openrouter-cli/issues",
        "Source": "https://github.com/openrouter-cli/openrouter-cli",
        "Documentation": "https://openrouter-cli.readthedocs.io/",
    },
)