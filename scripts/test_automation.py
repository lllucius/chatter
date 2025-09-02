#!/usr/bin/env python3
"""
Test automation scripts for continuous integration and development workflow.
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Optional


def run_command(cmd: List[str], cwd: Optional[str] = None, capture_output: bool = False) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            capture_output=capture_output, 
            text=True, 
            check=False
        )
        return result
    except Exception as e:
        print(f"Error running command: {e}")
        sys.exit(1)


def run_unit_tests(verbose: bool = False, coverage: bool = True) -> bool:
    """Run unit tests with coverage."""
    print("🔬 Running unit tests...")
    
    cmd = ["python", "-m", "pytest", "-m", "unit"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=chatter", "--cov-report=term-missing"])
    
    result = run_command(cmd)
    return result.returncode == 0


def run_integration_tests(verbose: bool = False) -> bool:
    """Run integration tests."""
    print("🔗 Running integration tests...")
    
    cmd = ["python", "-m", "pytest", "-m", "integration"]
    
    if verbose:
        cmd.append("-v")
    
    # Integration tests might take longer
    cmd.extend(["--timeout=300"])
    
    result = run_command(cmd)
    return result.returncode == 0


def run_e2e_tests(verbose: bool = False) -> bool:
    """Run end-to-end tests."""
    print("🚀 Running end-to-end tests...")
    
    cmd = ["python", "-m", "pytest", "-m", "e2e"]
    
    if verbose:
        cmd.append("-v")
    
    # E2E tests might need even more time
    cmd.extend(["--timeout=600"])
    
    result = run_command(cmd)
    return result.returncode == 0


def run_performance_tests(verbose: bool = False) -> bool:
    """Run performance tests."""
    print("⚡ Running performance tests...")
    
    cmd = ["python", "-m", "pytest", "-m", "performance"]
    
    if verbose:
        cmd.append("-v")
    
    result = run_command(cmd)
    return result.returncode == 0


def run_load_tests(duration: int = 60, users: int = 10, host: str = "http://localhost:8000") -> bool:
    """Run load tests with Locust."""
    print(f"🔥 Running load tests for {duration}s with {users} users...")
    
    # Check if locust is installed
    locust_check = run_command(["locust", "--version"], capture_output=True)
    if locust_check.returncode != 0:
        print("❌ Locust not installed. Install with: pip install locust")
        return False
    
    cmd = [
        "locust",
        "-f", "tests/load/locust_scenarios.py",
        "--host", host,
        "--users", str(users),
        "--spawn-rate", str(min(users, 5)),
        "--run-time", f"{duration}s",
        "--headless",
        "--print-stats",
        "--html", "reports/load_test_report.html"
    ]
    
    # Create reports directory
    os.makedirs("reports", exist_ok=True)
    
    result = run_command(cmd)
    return result.returncode == 0


def run_frontend_tests() -> bool:
    """Run frontend tests."""
    print("🎨 Running frontend tests...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("⚠️ Frontend directory not found, skipping frontend tests")
        return True
    
    # Check if npm is available
    npm_check = run_command(["npm", "--version"], capture_output=True)
    if npm_check.returncode != 0:
        print("❌ npm not installed, skipping frontend tests")
        return False
    
    # Install dependencies if needed
    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing frontend dependencies...")
        result = run_command(["npm", "install"], cwd=str(frontend_dir))
        if result.returncode != 0:
            print("❌ Failed to install frontend dependencies")
            return False
    
    # Run tests
    result = run_command(["npm", "test"], cwd=str(frontend_dir))
    return result.returncode == 0


def run_linting() -> bool:
    """Run code linting and formatting checks."""
    print("🧹 Running linting checks...")
    
    success = True
    
    # Run ruff (linting)
    print("Running ruff linting...")
    result = run_command(["ruff", "check", "chatter/", "tests/"])
    if result.returncode != 0:
        success = False
    
    # Run black (formatting)
    print("Running black formatting check...")
    result = run_command(["black", "--check", "chatter/", "tests/"])
    if result.returncode != 0:
        print("💡 Run 'black chatter/ tests/' to fix formatting")
        success = False
    
    # Run isort (import sorting)
    print("Running isort import check...")
    result = run_command(["isort", "--check-only", "chatter/", "tests/"])
    if result.returncode != 0:
        print("💡 Run 'isort chatter/ tests/' to fix imports")
        success = False
    
    return success


def run_type_checking() -> bool:
    """Run type checking with mypy."""
    print("🔍 Running type checking...")
    
    result = run_command(["mypy", "chatter/"])
    return result.returncode == 0


def generate_test_report() -> None:
    """Generate a comprehensive test report."""
    print("📊 Generating test report...")
    
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    
    # Run tests with detailed output
    cmd = [
        "python", "-m", "pytest",
        "--cov=chatter",
        "--cov-report=html:reports/coverage",
        "--cov-report=xml:reports/coverage.xml",
        "--junit-xml=reports/junit.xml",
        "--html=reports/test_report.html",
        "--self-contained-html"
    ]
    
    result = run_command(cmd)
    
    if result.returncode == 0:
        print("✅ Test report generated successfully!")
        print(f"📂 Reports saved in: {report_dir.absolute()}")
    else:
        print("❌ Test report generation failed")


def main():
    """Main test automation script."""
    parser = argparse.ArgumentParser(description="Chatter Test Automation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    parser.add_argument("--full", action="store_true", help="Run full test suite")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--e2e", action="store_true", help="Run E2E tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--load", action="store_true", help="Run load tests")
    parser.add_argument("--frontend", action="store_true", help="Run frontend tests only")
    parser.add_argument("--lint", action="store_true", help="Run linting only")
    parser.add_argument("--type-check", action="store_true", help="Run type checking only")
    parser.add_argument("--report", action="store_true", help="Generate test report")
    parser.add_argument("--load-duration", type=int, default=60, help="Load test duration in seconds")
    parser.add_argument("--load-users", type=int, default=10, help="Number of load test users")
    parser.add_argument("--load-host", default="http://localhost:8000", help="Load test target host")
    
    args = parser.parse_args()
    
    if not any([
        args.quick, args.full, args.unit, args.integration, args.e2e, 
        args.performance, args.load, args.frontend, args.lint, 
        args.type_check, args.report
    ]):
        # Default: run quick tests
        args.quick = True
    
    success = True
    start_time = time.time()
    
    print("🧪 Chatter Test Automation Starting...")
    print("=" * 50)
    
    # Run selected tests
    if args.lint or args.full:
        success &= run_linting()
    
    if args.type_check or args.full:
        success &= run_type_checking()
    
    if args.unit or args.quick or args.full:
        success &= run_unit_tests(verbose=args.verbose)
    
    if args.integration or args.full:
        success &= run_integration_tests(verbose=args.verbose)
    
    if args.frontend or args.full:
        success &= run_frontend_tests()
    
    if args.e2e or args.full:
        success &= run_e2e_tests(verbose=args.verbose)
    
    if args.performance or args.full:
        success &= run_performance_tests(verbose=args.verbose)
    
    if args.load:
        success &= run_load_tests(
            duration=args.load_duration,
            users=args.load_users,
            host=args.load_host
        )
    
    if args.report:
        generate_test_report()
    
    # Summary
    end_time = time.time()
    duration = end_time - start_time
    
    print("=" * 50)
    print(f"⏱️  Total execution time: {duration:.2f} seconds")
    
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()