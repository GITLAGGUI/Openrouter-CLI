"""Command modules for OpenRouter CLI."""

from .file import file
from .code import code
from .web import web
from .chat import chat
from .config import config
from .history import history
from .html_generator import html
from .debug_agent import debug

__all__ = ['file', 'code', 'web', 'chat', 'config', 'history', 'html', 'debug']