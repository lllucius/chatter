"""Refactored generate_all.py with improved separation of concerns and error handling."""

import argparse
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.subprocess import run_command  # noqa: E402


def generate_documentation(
    output_dir: Path, docs_format: str = "all"
) -> tuple[bool, list[str]]:
    """
    Generate OpenAPI documentation.

    Returns:
        Tuple of (success, list of generated files)
    """
    print("\n📚 Generating OpenAPI Documentation...")

    docs_output = output_dir / "docs" / "api"
    cmd = [
        sys.executable,
        "-m",
        "chatter",
        "docs",
        "generate",
        "--output",
        str(docs_output),
        "--format",
        docs_format,
    ]

    success, stdout, stderr = run_command(
        cmd, "OpenAPI documentation generation", check=False
    )

    if not success:
        return False, []

    # Verify documentation files were created
    expected_files = []
    if docs_format in ["json", "all"]:
        expected_files.extend(["openapi.json", "openapi-v0.1.0.json"])
    if docs_format in ["yaml", "all"]:
        expected_files.extend(["openapi.yaml", "openapi-v0.1.0.yaml"])

    generated_files = []
    for file in expected_files:
        file_path = docs_output / file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"   ✅ {file} ({size:,} bytes)")
            generated_files.append(str(file_path))
        else:
            print(f"   ❌ Missing: {file}")
            success = False

    return success, generated_files


def generate_python_sdk() -> tuple[bool, list[str]]:
    """
    Generate Python SDK using the new modular approach.

    Returns:
        Tuple of (success, list of generated files)
    """
    print("\n🐍 Generating Python SDK...")

    try:
        from scripts.sdk.python_sdk import PythonSDKGenerator
        from scripts.utils.config import get_default_python_config

        # Get project root and configuration
        project_root = Path(__file__).parent.parent
        config = get_default_python_config(project_root)

        # Generate SDK
        generator = PythonSDKGenerator(config)
        success = generator.generate_with_cleanup()

        generated_files = []
        if success:
            # Validate and get file list
            if generator.validate():
                print("✅ Python SDK validation passed")
                # Get list of generated files
                if config.output_dir.exists():
                    generated_files = [
                        str(f)
                        for f in config.output_dir.rglob("*")
                        if f.is_file() and not f.name.startswith(".")
                    ]
            else:
                print("⚠️  Python SDK validation failed")
                success = False

        return success, generated_files

    except Exception as e:
        print(f"❌ Python SDK generation failed: {e}")
        return False, []


def generate_typescript_sdk() -> tuple[bool, list[str]]:
    """
    Generate TypeScript SDK using the new modular approach.

    Returns:
        Tuple of (success, list of generated files)
    """
    print("\n📦 Generating TypeScript SDK...")

    try:
        from scripts.sdk.typescript_sdk import TypeScriptSDKGenerator
        from scripts.utils.config import get_default_typescript_config

        # Get project root and configuration
        project_root = Path(__file__).parent.parent
        config = get_default_typescript_config(project_root)

        # Generate SDK
        generator = TypeScriptSDKGenerator(config)
        success = generator.generate_with_cleanup()

        generated_files = []
        if success:
            # Validate and get file list
            if generator.validate():
                print("✅ TypeScript SDK validation passed")
                # Get list of generated files
                if config.output_dir.exists():
                    generated_files = [
                        str(f)
                        for f in config.output_dir.rglob("*")
                        if f.is_file() and not f.name.startswith(".")
                    ]
            else:
                print("⚠️  TypeScript SDK validation failed")
                success = False

        return success, generated_files

    except Exception as e:
        print(f"❌ TypeScript SDK generation failed: {e}")
        return False, []


def clean_output_directories(output_dir: Path) -> None:
    """Clean output directories if requested."""
    import shutil

    print("🧹 Cleaning output directories...")

    docs_dir = output_dir / "docs" / "api"
    sdk_dir = output_dir / "sdk"

    for dir_path in [docs_dir, sdk_dir]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"   Cleaned: {dir_path}")


def print_summary(
    success: bool,
    args: argparse.Namespace,
    docs_files: list[str],
    python_files: list[str],
    typescript_files: list[str],
) -> None:
    """Print generation summary."""
    print("\n" + "=" * 60)

    if success:
        print("🎉 Workflow completed successfully!")

        if not args.sdk_only and not args.ts_only and docs_files:
            print(
                f"\n📚 Documentation generated ({len(docs_files)} files):"
            )
            print(
                f"   📁 Location: {Path(args.output_dir) / 'docs' / 'api'}"
            )
            print(f"   🔗 Formats: {args.docs_format}")

        if not args.docs_only:
            if not args.ts_only and python_files:
                project_root = Path(__file__).parent.parent
                print(
                    f"\n🐍 Python SDK generated ({len(python_files)} files):"
                )
                print(
                    f"   📁 Location: {project_root / 'sdk' / 'python'}"
                )
                print("   📦 Package: chatter-sdk")

            if typescript_files:
                project_root = Path(__file__).parent.parent
                print(
                    f"\n📦 TypeScript SDK generated ({len(typescript_files)} files):"
                )
                print(
                    f"   📁 Location: {project_root / 'frontend' / 'src' / 'sdk'}"
                )
                print("   📦 Package: chatter-sdk (TypeScript)")

        print("\n📋 Next steps:")
        if not args.docs_only:
            if not args.ts_only and python_files:
                project_root = Path(__file__).parent.parent
                print(
                    f"   • Test the Python SDK: cd {project_root / 'sdk' / 'python'} && pip install -e ."
                )
                print(
                    "   • Run Python examples: python examples/basic_usage.py"
                )
            if typescript_files:
                print(
                    "   • Test the TypeScript SDK: cd frontend && npm start"
                )
        if not args.sdk_only and not args.ts_only and docs_files:
            print("   • View docs: python -m chatter docs serve")
        print("   • Package for release: python -m build")

    else:
        print("❌ Workflow completed with errors!")
        print(
            "   Please check the error messages above and fix any issues."
        )


def main():
    """Main workflow function with improved error handling and modularity."""
    parser = argparse.ArgumentParser(
        description="Automated OpenAPI docs and SDK generation workflow"
    )
    parser.add_argument(
        "--docs-only",
        action="store_true",
        help="Generate only documentation, skip SDK",
    )
    parser.add_argument(
        "--sdk-only",
        action="store_true",
        help="Generate only SDK, skip documentation",
    )
    parser.add_argument(
        "--ts-only",
        action="store_true",
        help="Generate only TypeScript SDK, skip Python SDK and documentation",
    )
    parser.add_argument(
        "--python-only",
        action="store_true",
        help="Generate only Python SDK, skip TypeScript SDK and documentation",
    )
    parser.add_argument(
        "--output-dir",
        default="./",
        help="Base output directory (default: current directory)",
    )
    parser.add_argument(
        "--docs-format",
        choices=["json", "yaml", "all"],
        default="all",
        help="Documentation format to generate",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean output directories before generating",
    )

    args = parser.parse_args()

    # Get project root and change to it
    project_root = Path(__file__).parent.parent
    output_path = Path(args.output_dir)

    print(
        "🚀 Starting Chatter Documentation and SDK Generation Workflow"
    )
    print(f"📁 Project root: {project_root}")
    print(f"📂 Output directory: {output_path}")

    success = True
    docs_files: list[str] = []
    python_files: list[str] = []
    typescript_files: list[str] = []

    # Clean directories if requested
    if args.clean:
        clean_output_directories(output_path)

    # Generate documentation
    if not args.sdk_only and not args.ts_only and not args.python_only:
        docs_success, docs_files = generate_documentation(
            output_path, args.docs_format
        )
        success = success and docs_success

    # Generate SDKs
    if not args.docs_only:
        # Generate Python SDK
        if not args.ts_only:
            python_success, python_files = generate_python_sdk()
            success = success and python_success

        # Generate TypeScript SDK
        if not args.python_only:
            ts_success, typescript_files = generate_typescript_sdk()
            success = success and ts_success

    # Print summary
    print_summary(
        success, args, docs_files, python_files, typescript_files
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
