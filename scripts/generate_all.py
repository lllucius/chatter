#!/usr/bin/env python3
"""
Automated workflow for generating OpenAPI docs and Python SDK.
This script can be used in CI/CD pipelines or as a standalone automation tool.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list, description: str) -> bool:
    """Run a command and return True if successful."""
    print(f"🔧 {description}...")
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {' '.join(cmd)}")
        print(f"   Exit code: {e.returncode}")
        print(f"   stdout: {e.stdout}")
        print(f"   stderr: {e.stderr}")
        return False


def main():
    """Main workflow function."""
    parser = argparse.ArgumentParser(
        description="Automated OpenAPI docs and SDK generation workflow"
    )
    parser.add_argument(
        "--docs-only",
        action="store_true",
        help="Generate only documentation, skip SDK"
    )
    parser.add_argument(
        "--sdk-only",
        action="store_true",
        help="Generate only SDK, skip documentation"
    )
    parser.add_argument(
        "--output-dir",
        default="./",
        help="Base output directory (default: current directory)"
    )
    parser.add_argument(
        "--docs-format",
        choices=["json", "yaml", "all"],
        default="all",
        help="Documentation format to generate"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean output directories before generating"
    )

    args = parser.parse_args()

    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print("🚀 Starting Chatter Documentation and SDK Generation Workflow")
    print(f"📁 Project root: {project_root}")
    print(f"📂 Output directory: {args.output_dir}")

    success = True

    # Clean directories if requested
    if args.clean:
        print("🧹 Cleaning output directories...")
        docs_dir = Path(args.output_dir) / "docs" / "api"
        sdk_dir = Path(args.output_dir) / "sdk"

        if docs_dir.exists():
            import shutil
            shutil.rmtree(docs_dir)
            print(f"   Cleaned: {docs_dir}")

        if sdk_dir.exists():
            import shutil
            shutil.rmtree(sdk_dir)
            print(f"   Cleaned: {sdk_dir}")

    # Generate documentation
    if not args.sdk_only:
        print("\n📚 Generating OpenAPI Documentation...")

        docs_output = Path(args.output_dir) / "docs" / "api"
        cmd = [
            sys.executable, "-m", "chatter", "docs", "generate",
            "--output", str(docs_output),
            "--format", args.docs_format
        ]

        if not run_command(cmd, "OpenAPI documentation generation"):
            success = False

        # Verify documentation files were created
        expected_files = []
        if args.docs_format in ["json", "all"]:
            expected_files.extend(["openapi.json", "openapi-v0.1.0.json"])
        if args.docs_format in ["yaml", "all"]:
            expected_files.extend(["openapi.yaml", "openapi-v0.1.0.yaml"])

        for file in expected_files:
            file_path = docs_output / file
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"   ✅ {file} ({size:,} bytes)")
            else:
                print(f"   ❌ Missing: {file}")
                success = False

    # Generate SDK
    if not args.docs_only:
        print("\n🐍 Generating Python SDK...")

        cmd = [
            sys.executable, "-m", "chatter", "docs", "sdk",
            "--language", "python",
            "--output", str(Path(args.output_dir) / "sdk")
        ]

        if not run_command(cmd, "Python SDK generation"):
            success = False

        # Verify SDK files were created
        sdk_dir = project_root / "sdk" / "python"  # The CLI uses project_root internally
        expected_sdk_files = [
            "setup.py", "README.md", "requirements.txt",
            "chatter_sdk/__init__.py", "examples/basic_usage.py"
        ]

        for file in expected_sdk_files:
            file_path = sdk_dir / file
            if file_path.exists():
                if file.endswith(".py"):
                    with open(file_path) as f:
                        lines = len(f.readlines())
                    print(f"   ✅ {file} ({lines} lines)")
                else:
                    size = file_path.stat().st_size
                    print(f"   ✅ {file} ({size:,} bytes)")
            else:
                print(f"   ❌ Missing: {file}")
                success = False

    # Summary
    print("\n" + "="*60)
    if success:
        print("🎉 Workflow completed successfully!")

        if not args.sdk_only:
            print("\n📚 Documentation generated:")
            print(f"   📁 Location: {Path(args.output_dir) / 'docs' / 'api'}")
            print(f"   🔗 Formats: {args.docs_format}")

        if not args.docs_only:
            print("\n🐍 Python SDK generated:")
            print(f"   📁 Location: {project_root / 'sdk' / 'python'}")
            print("   📦 Package: chatter-sdk")

        print("\n📋 Next steps:")
        if not args.docs_only:
            print(f"   • Test the SDK: cd {project_root / 'sdk' / 'python'} && pip install -e .")
            print("   • Run examples: python examples/basic_usage.py")
        if not args.sdk_only:
            print("   • View docs: python -m chatter docs serve")
        print("   • Package for release: python -m build")

        return 0
    else:
        print("❌ Workflow completed with errors!")
        print("   Please check the error messages above and fix any issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
