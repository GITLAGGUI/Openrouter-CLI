"""
Loading animation utilities for OpenRouter CLI
"""

import sys
import time
import threading
from typing import Optional


class LoadingAnimation:
    """Simple loading animation for CLI operations."""
    
    def __init__(self, message: str = "Processing", style: str = "dots"):
        self.message = message
        self.style = style
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        
        # Animation styles (Windows-compatible)
        self.animations = {
            'dots': ['.', '..', '...', '....', '.....', '....', '...', '..'],
            'spinner': ['|', '/', '-', '\\'],
            'arrows': ['<', '^', '>', 'v'],
            'pulse': ['o', 'O', 'o', 'O'],
            'simple': ['.', '..', '...', '....', '.....'],
            'modern': ['[=   ]', '[==  ]', '[=== ]', '[ ===]', '[  ==]', '[   =]'],
            'progress': ['▓', '▓▓', '▓▓▓', '▓▓▓▓', '▓▓▓▓▓']
        }
    
    def _animate(self):
        """Animation loop with better encoding handling."""
        frames = self.animations.get(self.style, self.animations['dots'])
        idx = 0
        
        while self.is_running:
            try:
                frame = frames[idx % len(frames)]
                # Use safe encoding for Windows console
                output = f'\r{frame} {self.message}'
                sys.stdout.write(output)
                sys.stdout.flush()
                time.sleep(0.15)  # Slightly slower for better visibility
                idx += 1
            except UnicodeEncodeError:
                # Fallback to simple dots if encoding fails
                frame = '.' * ((idx % 5) + 1)
                sys.stdout.write(f'\r{frame} {self.message}')
                sys.stdout.flush()
                time.sleep(0.15)
                idx += 1
    
    def start(self):
        """Start the loading animation."""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._animate, daemon=True)
            self.thread.start()
    
    def stop(self, clear: bool = True):
        """Stop the loading animation."""
        if self.is_running:
            self.is_running = False
            if self.thread:
                self.thread.join(timeout=0.2)
            
            if clear:
                # Clear the line
                sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
                sys.stdout.flush()
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


def with_loading(message: str = "Processing", style: str = "dots"):
    """Decorator to add loading animation to functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with LoadingAnimation(message, style):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Simple functions for quick use
def show_loading(message: str = "Processing", style: str = "dots") -> LoadingAnimation:
    """Create and start a loading animation."""
    loader = LoadingAnimation(message, style)
    loader.start()
    return loader


def ai_thinking_animation(message: str = "AI is thinking") -> LoadingAnimation:
    """Create AI thinking animation."""
    return show_loading(message, "dots")


def file_processing_animation(message: str = "Processing file") -> LoadingAnimation:
    """Create file processing animation."""
    return show_loading(message, "spinner")


def web_fetching_animation(message: str = "Fetching content") -> LoadingAnimation:
    """Create web fetching animation."""
    return show_loading(message, "arrows")