#!/usr/bin/env python3
"""
SystemScope — Local System Intelligence Dashboard
Entry point.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.ui.main_window import main

if __name__ == "__main__":
    main()
