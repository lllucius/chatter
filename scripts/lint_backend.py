#!/usr/bin/env python3
"""Backend code quality and security analysis script."""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n🔍 {description}")
    print(f"Running: {' '.join(command)}")
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
            
        if result.returncode == 0:
            print(f"✅ {description} passed")
            return True
        else:
            print(f"❌ {description} failed with exit code {result.returncode}")
            return False
            
    except FileNotFoundError:
        print(f"❌ Command not found: {command[0]}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run backend linting and security checks")
    parser.add_argument("--fix", action="store_true", help="Automatically fix issues where possible")
    parser.add_argument("--security-only", action="store_true", help="Run only security checks")
    parser.add_argument("--lint-only", action="store_true", help="Run only linting checks")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Change to repository root
    repo_root = Path(__file__).parent.parent
    print(f"Working directory: {repo_root}")
    
    success = True
    
    if not args.security_only:
        print("\n" + "="*50)
        print("🛠️  LINTING AND FORMATTING")
        print("="*50)
        
        # Ruff check and fix
        ruff_cmd = ["ruff", "check", "chatter", "tests", "scripts"]
        if args.fix:
            ruff_cmd.append("--fix")
        if args.verbose:
            ruff_cmd.append("--verbose")
        success &= run_command(ruff_cmd, "Ruff linting")
        
        # Black formatting
        black_cmd = ["black"]
        if not args.fix:
            black_cmd.append("--check")
        if args.verbose:
            black_cmd.append("--verbose")
        black_cmd.extend(["chatter", "tests", "scripts"])
        success &= run_command(black_cmd, "Black formatting")
        
        # isort import sorting
        isort_cmd = ["isort"]
        if not args.fix:
            isort_cmd.append("--check-only")
        if args.verbose:
            isort_cmd.append("--verbose")
        isort_cmd.extend(["chatter", "tests", "scripts"])
        success &= run_command(isort_cmd, "Import sorting")
        
        # MyPy type checking
        mypy_cmd = ["mypy", "chatter"]
        if args.verbose:
            mypy_cmd.append("--verbose")
        success &= run_command(mypy_cmd, "MyPy type checking")
    
    if not args.lint_only:
        print("\n" + "="*50)
        print("🔒 SECURITY ANALYSIS")
        print("="*50)
        
        # Bandit security analysis
        bandit_cmd = [
            "bandit", 
            "-r", "chatter", 
            "-f", "json",
            "-o", "bandit-report.json"
        ]
        if args.verbose:
            bandit_cmd.extend(["-v"])
        
        # Also show console output
        bandit_console_cmd = ["bandit", "-r", "chatter"]
        if args.verbose:
            bandit_console_cmd.append("-v")
        success &= run_command(bandit_console_cmd, "Bandit security analysis")
        
        # Generate JSON report
        run_command(bandit_cmd, "Generating Bandit JSON report")
        
        # Safety dependency vulnerability check
        safety_cmd = [
            "safety", "scan", 
            "--output", "json",
            "--save-json", "safety-report.json"
        ]
        success &= run_command(safety_cmd, "Safety dependency vulnerability check")
    
    print("\n" + "="*50)
    if success:
        print("✅ All checks passed!")
        sys.exit(0)
    else:
        print("❌ Some checks failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()