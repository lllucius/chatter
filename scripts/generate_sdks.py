#!/usr/bin/env python3
"""SDK generation script for Chatter API.

This script provides a simple way to regenerate Python and TypeScript SDKs
from the OpenAPI specification.
"""

import argparse
import os
import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scripts.sdk import PythonSDKGenerator  # noqa: E402
from scripts.utils.config import (  # noqa: E402
    get_default_python_config,
    get_default_typescript_config,
)

# Import standalone generators
sys.path.insert(0, str(project_root))
from generate_ts_apis import main as generate_apis_main  # noqa: E402
from generate_ts_models import (  # noqa: E402
    main as generate_models_main,
)


def generate_python_sdk(
    project_root: Path, verbose: bool = False
) -> bool:
    """Generate Python SDK.

    Args:
        project_root: Root directory of the project
        verbose: Enable verbose output

    Returns:
        True if generation was successful, False otherwise
    """
    if verbose:
        print("🐍 Starting Python SDK generation...")

    config = get_default_python_config(project_root)
    generator = PythonSDKGenerator(config)

    success = generator.generate_with_cleanup()

    if success:
        if verbose:
            print(
                f"✅ Python SDK generated successfully in {config.output_dir}"
            )
        # Validate the generated SDK
        if generator.validate():
            if verbose:
                print("✅ Python SDK validation passed")
            return True
        else:
            print("❌ Python SDK validation failed")
            return False
    else:
        print("❌ Python SDK generation failed")
        return False


def generate_typescript_sdk(
    project_root: Path, verbose: bool = False
) -> bool:
    """Generate TypeScript SDK.

    Args:
        project_root: Root directory of the project
        verbose: Enable verbose output

    Returns:
        True if generation was successful, False otherwise
    """
    if verbose:
        print("📦 Starting TypeScript SDK generation...")

    config = get_default_typescript_config(project_root)

    try:
        # Clean output directories for models and apis
        models_dir = config.output_dir / "src" / "models"
        apis_dir = config.output_dir / "src" / "apis"

        if models_dir.exists():
            if verbose:
                print("🧹 Cleaning models directory...")
            import shutil

            shutil.rmtree(models_dir)

        if apis_dir.exists():
            if verbose:
                print("🧹 Cleaning APIs directory...")
            import shutil

            shutil.rmtree(apis_dir)

        # Change to project directory for the generators
        original_cwd = Path.cwd()
        os.chdir(project_root)

        # Generate TypeScript models
        if verbose:
            print("🔧 Generating TypeScript models...")
        generate_models_main()

        # Generate TypeScript APIs
        if verbose:
            print("🔧 Generating TypeScript API clients...")
        generate_apis_main()

    except Exception as e:
        print(f"❌ TypeScript SDK generation failed: {e}")
        return False
    finally:
        # Restore original working directory
        os.chdir(original_cwd)

    if verbose:
        print(
            f"✅ TypeScript SDK generated successfully in {config.output_dir}"
        )

    # Validate the generated SDK
    if validate_typescript_sdk(config, verbose):
        if verbose:
            print("✅ TypeScript SDK validation passed")
        return True
    else:
        print("❌ TypeScript SDK validation failed")
        return False


def validate_typescript_sdk(config, verbose: bool = False) -> bool:
    """Validate that the generated TypeScript SDK is complete and functional.

    Args:
        config: TypeScript SDK configuration
        verbose: Enable verbose output

    Returns:
        True if SDK validation passes, False otherwise
    """
    try:
        # Check if output directory exists
        if not config.output_dir.exists():
            print("❌ SDK output directory does not exist")
            return False

        # Check for essential TypeScript SDK files
        essential_files = ["src/index.ts", "src/runtime.ts"]

        missing_files = []
        for file_path in essential_files:
            full_path = config.output_dir / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        if missing_files:
            print(f"❌ Missing essential SDK files: {missing_files}")
            return False

        # Check for API modules
        apis_dir = config.output_dir / "src" / "apis"
        if apis_dir.exists():
            api_files = list(apis_dir.glob("*.ts"))
            if not api_files:
                print("❌ No API modules found in generated SDK")
                return False
            if verbose:
                print(f"✅ Found {len(api_files)} API modules")

        # Check for model modules
        models_dir = config.output_dir / "src" / "models"
        if models_dir.exists():
            model_files = list(models_dir.glob("*.ts"))
            if not model_files:
                print("❌ No model modules found in generated SDK")
                return False
            if verbose:
                print(f"✅ Found {len(model_files)} model modules")

        return True

    except Exception as e:
        print(f"❌ TypeScript SDK validation failed: {e}")
        return False


def main() -> int:
    """Main entry point for SDK generation."""
    parser = argparse.ArgumentParser(
        description="Generate Python and/or TypeScript SDKs from OpenAPI specification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/generate_sdks.py --python      # Generate Python SDK only
  python scripts/generate_sdks.py --typescript  # Generate TypeScript SDK only
  python scripts/generate_sdks.py --all         # Generate both SDKs
  python scripts/generate_sdks.py               # Generate both SDKs (default)

  # Alternative module execution:
  python -m scripts --python                    # Generate Python SDK only
  python -m scripts --all                       # Generate both SDKs
        """.strip(),
    )

    parser.add_argument(
        "--python", action="store_true", help="Generate Python SDK only"
    )

    parser.add_argument(
        "--typescript",
        action="store_true",
        help="Generate TypeScript SDK only",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate both Python and TypeScript SDKs",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    # Determine what to generate
    generate_python = args.python or args.all
    generate_typescript = args.typescript or args.all

    # If no specific SDK is requested, generate both by default
    if not (args.python or args.typescript or args.all):
        generate_python = True
        generate_typescript = True

    project_root = Path(__file__).parent.parent.resolve()

    if args.verbose:
        print(f"🏠 Project root: {project_root}")
        print(
            f"🔧 Generating: Python={generate_python}, TypeScript={generate_typescript}"
        )
        print()

    success_count = 0
    total_count = 0

    # Generate Python SDK
    if generate_python:
        total_count += 1
        if generate_python_sdk(project_root, args.verbose):
            success_count += 1
        else:
            if not args.verbose:
                print("❌ Python SDK generation failed")

    # Generate TypeScript SDK
    if generate_typescript:
        total_count += 1
        if generate_typescript_sdk(project_root, args.verbose):
            success_count += 1
        else:
            if not args.verbose:
                print("❌ TypeScript SDK generation failed")

    # Summary
    if args.verbose:
        print()
        print(
            f"📊 Summary: {success_count}/{total_count} SDKs generated successfully"
        )

    if success_count == total_count:
        if not args.verbose:
            print(f"✅ Successfully generated {total_count} SDK(s)")
        return 0
    else:
        if not args.verbose:
            print(
                f"❌ Failed to generate {total_count - success_count} out of {total_count} SDK(s)"
            )
        return 1


if __name__ == "__main__":
    sys.exit(main())
