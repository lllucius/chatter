#!/usr/bin/env python3
"""
Refactored Python SDK generation script using modular architecture.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.sdk.python_sdk import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
