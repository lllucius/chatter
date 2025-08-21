#!/usr/bin/env python3
"""Test script for CLI commands."""

import subprocess
import sys
from pathlib import Path

def run_command(cmd):
    """Run a CLI command and return the result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=Path(__file__).parent
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def test_cli():
    """Test CLI commands."""
    print("🔍 Testing Chatter CLI commands...")
    
    commands = [
        "python -m chatter --help",
        "python -m chatter profiles --help",
        "python -m chatter conversations --help", 
        "python -m chatter documents --help",
        "python -m chatter auth --help",
        "python -m chatter analytics --help",
        "python -m chatter prompts --help",
        "python -m chatter version",
    ]
    
    for cmd in commands:
        print(f"\n📋 Testing: {cmd}")
        returncode, stdout, stderr = run_command(cmd)
        
        if returncode == 0:
            print("✅ Command successful")
            if "help" not in cmd and stdout:
                print(f"Output: {stdout[:200]}...")
        else:
            print(f"❌ Command failed (exit code: {returncode})")
            if stderr:
                print(f"Error: {stderr[:200]}...")

if __name__ == "__main__":
    test_cli()