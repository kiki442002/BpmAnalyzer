"""
Utility module for path management.
Detects if running from executable bundle or interpreter.
"""

import os
import sys
from pathlib import Path
import platform


def is_bundled():
    """Check if running from PyInstaller bundle."""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def get_patterns_dir():
    """
    Get the patterns directory path.
    
    - If running from interpreter: ./patterns (relative to project root)
    - If bundled on macOS: ~/Library/Application Support/BpmAnalyzer/patterns
    - If bundled on Windows: %APPDATA%/BpmAnalyzer/patterns
    - If bundled on Linux: ~/.local/share/BpmAnalyzer/patterns
    
    Creates directory if it doesn't exist.
    """
    if is_bundled():
        # Running from PyInstaller bundle
        system = platform.system()
        
        if system == "Darwin":  # macOS
            patterns_dir = Path.home() / "Library" / "Application Support" / "BpmAnalyzer" / "patterns"
        elif system == "Windows":
            appdata = os.getenv("APPDATA")
            if appdata:
                patterns_dir = Path(appdata) / "BpmAnalyzer" / "patterns"
            else:
                patterns_dir = Path.home() / "AppData" / "Roaming" / "BpmAnalyzer" / "patterns"
        else:  # Linux
            patterns_dir = Path.home() / ".local" / "share" / "BpmAnalyzer" / "patterns"
    else:
        # Running from interpreter (development)
        patterns_dir = Path(__file__).parent / "patterns"
    
    # Create directory if it doesn't exist
    patterns_dir.mkdir(parents=True, exist_ok=True)
    
    return patterns_dir


def get_patterns_relative():
    """Get patterns directory as relative path for loading."""
    patterns_dir = get_patterns_dir()
    return str(patterns_dir)


if __name__ == "__main__":
    print(f"Bundled: {is_bundled()}")
    print(f"Patterns dir: {get_patterns_dir()}")
