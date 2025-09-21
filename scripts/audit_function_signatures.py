#!/usr/bin/env python3
"""
Development audit script for function call signature validation.

This script can be run during development to catch potential function call
signature mismatches and import issues early in the development process.

Usage:
    python scripts/audit_function_signatures.py [--verbose] [--fix]
"""

import argparse
import ast
import sys
from pathlib import Path


class DevelopmentAuditor:
    """Lightweight auditor for development use."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.base_path = Path(__file__).parent.parent
        self.issues = []

    def log(self, message: str) -> None:
        """Log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[AUDIT] {message}")

    def check_compilation(self) -> list[tuple[Path, str]]:
        """Check that all Python files compile successfully."""
        compilation_errors = []
        chatter_dir = self.base_path / "chatter"

        for python_file in chatter_dir.rglob("*.py"):
            if "__pycache__" in str(python_file):
                continue

            try:
                with open(python_file, encoding='utf-8') as f:
                    content = f.read()
                compile(content, str(python_file), 'exec')
                self.log(f"✓ {python_file.relative_to(self.base_path)}")
            except Exception as e:
                compilation_errors.append((python_file, str(e)))
                self.log(
                    f"✗ {python_file.relative_to(self.base_path)}: {e}"
                )

        return compilation_errors

    def check_known_problematic_patterns(
        self,
    ) -> list[tuple[Path, int, str]]:
        """Check for patterns that have been problematic in the past."""
        issues = []
        chatter_dir = self.base_path / "chatter"

        # Patterns based on previous issues
        problematic_calls = {
            "ChatterSDKClient": "chatter.commands",
            "ConversationStatus": "chatter.models.conversation",
        }

        for python_file in chatter_dir.rglob("*.py"):
            if "__pycache__" in str(python_file):
                continue

            try:
                with open(python_file, encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content, filename=str(python_file))

                # Extract imports
                imported_names = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        for alias in node.names:
                            imported_names.add(alias.name)

                # Check for problematic calls
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and isinstance(
                        node.func, ast.Name
                    ):
                        call_name = node.func.id
                        if call_name in problematic_calls:
                            if call_name not in imported_names:
                                # Check if it's defined locally
                                locally_defined = any(
                                    isinstance(
                                        n,
                                        (ast.ClassDef, ast.FunctionDef),
                                    )
                                    and n.name == call_name
                                    for n in ast.walk(tree)
                                )
                                if not locally_defined:
                                    expected_module = problematic_calls[
                                        call_name
                                    ]
                                    issues.append(
                                        (
                                            python_file,
                                            getattr(node, 'lineno', 0),
                                            f"{call_name} called but not imported from {expected_module}",
                                        )
                                    )

            except Exception as e:
                self.log(f"Error parsing {python_file}: {e}")

        return issues

    def check_critical_files(self) -> list[tuple[Path, str]]:
        """Check that critical files are in good shape."""
        critical_files = [
            self.base_path / "chatter" / "api_cli.py",
            self.base_path / "chatter" / "commands" / "__init__.py",
            self.base_path / "chatter" / "core" / "analytics.py",
            self.base_path / "chatter" / "services" / "llm.py",
        ]

        issues = []

        for file_path in critical_files:
            if not file_path.exists():
                issues.append((file_path, "File does not exist"))
                continue

            try:
                with open(file_path, encoding='utf-8') as f:
                    content = f.read()

                # Basic checks
                if (
                    "from chatter_sdk" in content
                    and "ChatterSDKClient" in content
                ):
                    # Check that ChatterSDKClient is either imported or defined
                    tree = ast.parse(content, filename=str(file_path))
                    has_import = any(
                        isinstance(node, ast.ImportFrom)
                        and node.module
                        and "chatter_sdk" in node.module
                        for node in ast.walk(tree)
                    )
                    has_definition = any(
                        isinstance(node, ast.ClassDef)
                        and node.name == "ChatterSDKClient"
                        for node in ast.walk(tree)
                    )

                    if not (has_import or has_definition):
                        issues.append(
                            (
                                file_path,
                                "ChatterSDKClient used but not imported or defined",
                            )
                        )

                self.log(f"✓ {file_path.relative_to(self.base_path)}")

            except Exception as e:
                issues.append((file_path, f"Error checking file: {e}"))
                self.log(
                    f"✗ {file_path.relative_to(self.base_path)}: {e}"
                )

        return issues

    def run_audit(self) -> bool:
        """Run the complete audit and return True if no issues found."""
        print("🔍 Running function signature audit...")

        # Check compilation
        compilation_errors = self.check_compilation()
        if compilation_errors:
            print(
                f"\n❌ COMPILATION ERRORS ({len(compilation_errors)}):"
            )
            for file_path, error in compilation_errors:
                print(
                    f"  {file_path.relative_to(self.base_path)}: {error}"
                )
        else:
            print("\n✅ All files compile successfully")

        # Check known problematic patterns
        pattern_issues = self.check_known_problematic_patterns()
        if pattern_issues:
            print(f"\n❌ PROBLEMATIC PATTERNS ({len(pattern_issues)}):")
            for file_path, line, issue in pattern_issues:
                print(
                    f"  {file_path.relative_to(self.base_path)}:{line} - {issue}"
                )
        else:
            print("\n✅ No known problematic patterns found")

        # Check critical files
        critical_issues = self.check_critical_files()
        if critical_issues:
            print(f"\n❌ CRITICAL FILE ISSUES ({len(critical_issues)}):")
            for file_path, issue in critical_issues:
                print(
                    f"  {file_path.relative_to(self.base_path)} - {issue}"
                )
        else:
            print("\n✅ All critical files are in good shape")

        # Summary
        total_issues = (
            len(compilation_errors)
            + len(pattern_issues)
            + len(critical_issues)
        )
        if total_issues == 0:
            print("\n🎉 Audit completed successfully! No issues found.")
            return True
        else:
            print(
                f"\n⚠️  Audit found {total_issues} issues that need attention."
            )
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Audit function call signatures"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to automatically fix issues (not implemented)",
    )

    args = parser.parse_args()

    if args.fix:
        print("❌ Automatic fixing not implemented yet")
        sys.exit(1)

    auditor = DevelopmentAuditor(verbose=args.verbose)
    success = auditor.run_audit()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
