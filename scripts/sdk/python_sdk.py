"""Python SDK generator using OpenAPI Generator CLI."""

import json
import re
import subprocess
from pathlib import Path

from scripts.utils.config import (
    PythonSDKConfig,
    get_openapi_generator_config,
)
from scripts.utils.files import clean_temp_files, ensure_directory


class PythonSDKGenerator:
    """Generates Python SDK from OpenAPI specification."""

    def __init__(self, config: PythonSDKConfig) -> None:
        """Initialize Python SDK generator.

        Args:
            config: Configuration for Python SDK generation
        """
        self.config = config
        self.temp_files: list[Path] = []

    def generate_with_cleanup(self) -> bool:
        """Generate Python SDK with cleanup of temporary files.

        Returns:
            True if generation was successful, False otherwise
        """
        try:
            return self._generate()
        finally:
            clean_temp_files(self.temp_files)

    def _generate(self) -> bool:
        """Generate Python SDK using OpenAPI Generator CLI.

        Returns:
            True if generation was successful, False otherwise
        """
        try:
            # Ensure output directory exists
            ensure_directory(self.config.output_dir, clean=True)

            # Get OpenAPI spec path (prefer JSON format)
            openapi_spec = self._find_openapi_spec()
            if not openapi_spec:
                print("❌ OpenAPI specification file not found")
                return False

            # Create generator configuration
            generator_config = get_openapi_generator_config(self.config)

            # Create temporary config file
            config_file = (
                self.config.output_dir / "generator-config.json"
            )
            with open(config_file, "w") as f:
                json.dump(generator_config, f, indent=2)
            self.temp_files.append(config_file)

            # Build OpenAPI Generator command
            cmd = [
                "npx",
                "@openapitools/openapi-generator-cli",
                "generate",
                "-i",
                str(openapi_spec),
                "-g",
                "python",
                "-o",
                str(self.config.output_dir),
                "-c",
                str(config_file),
                "--skip-validate-spec",  # Skip spec validation for OpenAPI 3.1
                "--additional-properties",
                f"packageName={self.config.package_name},"
                f"projectName={self.config.project_name},"
                f"packageVersion={self.config.package_version}",
            ]

            print(
                f"🐍 Generating Python SDK in {self.config.output_dir}"
            )
            print(f"   Using spec: {openapi_spec}")

            # Run the generator
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.config.project_root,
            )

            if result.returncode != 0:
                print("❌ OpenAPI Generator failed:")
                print(f"   STDOUT: {result.stdout}")
                print(f"   STDERR: {result.stderr}")
                return False

            print("✅ Python SDK generation completed")

            # Post-process pyproject.toml to fix license field
            if self._fix_license_field():
                print("✅ Applied license field fix")
            else:
                print("⚠️  Failed to apply license field fix")

            # Post-process generated models to fix datetime serialization
            if self._fix_datetime_serialization():
                print("✅ Applied datetime serialization fix")
            else:
                print("⚠️  Failed to apply datetime serialization fix")

            return True

        except Exception as e:
            print(f"❌ Python SDK generation failed: {e}")
            return False

    def validate(self) -> bool:
        """Validate that the generated Python SDK is complete and functional.

        Returns:
            True if SDK validation passes, False otherwise
        """
        try:
            # Check if output directory exists
            if not self.config.output_dir.exists():
                print("❌ SDK output directory does not exist")
                return False

            # Check for essential Python SDK files
            essential_files = [
                "setup.py",
                f"{self.config.package_name}/__init__.py",
                f"{self.config.package_name}/api_client.py",
                f"{self.config.package_name}/configuration.py",
                "requirements.txt",
            ]

            missing_files = []
            for file_path in essential_files:
                full_path = self.config.output_dir / file_path
                if not full_path.exists():
                    missing_files.append(file_path)

            if missing_files:
                print(
                    f"❌ Missing essential SDK files: {missing_files}"
                )
                return False

            # Check for API modules
            api_dir = (
                self.config.output_dir
                / self.config.package_name
                / "api"
            )
            if api_dir.exists():
                api_files = list(api_dir.glob("*.py"))
                if not api_files:
                    print("❌ No API modules found in generated SDK")
                    return False

            # Check for model modules
            models_dir = (
                self.config.output_dir
                / self.config.package_name
                / "models"
            )
            if models_dir.exists():
                model_files = list(models_dir.glob("*.py"))
                if not model_files:
                    print("❌ No model modules found in generated SDK")
                    return False

            print("✅ Python SDK validation passed")
            return True

        except Exception as e:
            print(f"❌ Python SDK validation failed: {e}")
            return False

    def _find_openapi_spec(self) -> Path | None:
        """Find OpenAPI specification file.

        Returns:
            Path to OpenAPI spec file, or None if not found
        """
        # Look for spec files in standard locations (prefer 3.0 compatible version)
        possible_locations = [
            self.config.project_root
            / "docs"
            / "api"
            / "openapi-3.0.json",
            self.config.project_root / "docs" / "api" / "openapi.json",
            self.config.project_root
            / "docs"
            / "api"
            / "openapi-3.0.yaml",
            self.config.project_root / "docs" / "api" / "openapi.yaml",
            self.config.project_root / "openapi-3.0.json",
            self.config.project_root / "openapi.json",
            self.config.project_root / "openapi-3.0.yaml",
            self.config.project_root / "openapi.yaml",
        ]

        for spec_path in possible_locations:
            if spec_path.exists():
                return spec_path

        return None

    def _fix_datetime_serialization(self) -> bool:
        """Fix datetime serialization in generated models.

        This method automatically adds mode='json' to model_dump() calls
        in models that have datetime fields to ensure proper JSON serialization.

        Returns:
            True if fix was applied successfully, False otherwise
        """
        try:
            models_dir = (
                self.config.output_dir
                / self.config.package_name
                / "models"
            )
            if not models_dir.exists():
                print("❌ Models directory not found for datetime fix")
                return False

            fixed_files = 0
            total_files = 0

            # Process all model files
            for model_file in models_dir.glob("*.py"):
                if model_file.name == "__init__.py":
                    continue

                total_files += 1
                if self._fix_datetime_in_file(model_file):
                    fixed_files += 1

            print(
                f"📝 Processed {total_files} model files, applied datetime fix to {fixed_files} files"
            )
            return True

        except Exception as e:
            print(f"❌ Failed to fix datetime serialization: {e}")
            return False

    def _fix_datetime_in_file(self, file_path: Path) -> bool:
        """Fix datetime serialization in a specific model file.

        Args:
            file_path: Path to the model file to fix

        Returns:
            True if the file was modified, False otherwise
        """
        try:
            with open(file_path) as f:
                content = f.read()

            original_content = content

            # Check if this file has datetime fields and to_dict methods
            has_datetime = (
                'datetime' in content
                and 'from datetime import datetime' in content
            )
            has_to_dict = 'def to_dict(self)' in content
            has_model_dump = 'self.model_dump(' in content

            if not (has_datetime and has_to_dict and has_model_dump):
                return False

            # Fix model_dump calls that don't have mode='json'

            # Pattern to match model_dump calls without mode='json'
            pattern = r'(\s+_dict = self\.model_dump\(\s*)(.*?)(exclude_none=True,?)(\s*\))'

            def replacement(match):
                full_call = match.group(0)
                start = match.group(1)
                middle = match.group(2)
                exclude_none = match.group(3)
                end = match.group(4)

                # Check if mode='json' is already present
                if (
                    "mode='json'" in full_call
                    or 'mode="json"' in full_call
                ):
                    return full_call  # No change needed

                # Extract the base indentation from the start
                base_indent = ''
                for char in start:
                    if char in [' ', '\t']:
                        base_indent += char
                    else:
                        break

                # Add mode='json' parameter with proper indentation
                if exclude_none.strip():
                    # Add mode='json' on a new line with proper indentation
                    mode_line = f"\n{base_indent}    mode='json',"
                    new_call = (
                        start + middle + exclude_none + mode_line + end
                    )
                else:
                    new_call = start + middle + "mode='json'," + end

                return new_call

            content = re.sub(
                pattern, replacement, content, flags=re.DOTALL
            )

            # Only write if content changed
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                return True

            return False

        except Exception as e:
            print(f"❌ Failed to fix datetime in {file_path}: {e}")
            return False

    def _fix_license_field(self) -> bool:
        """Fix the license field in pyproject.toml to use the correct format.

        OpenAPI Generator creates license = "NoLicense" by default, which is
        not a valid SPDX identifier and causes errors with modern setuptools.
        This method updates it to the proper format: license = {text = "MIT"}

        Returns:
            True if fix was applied successfully, False otherwise
        """
        try:
            pyproject_path = self.config.output_dir / "pyproject.toml"
            if not pyproject_path.exists():
                print("❌ pyproject.toml not found")
                return False

            with open(pyproject_path) as f:
                content = f.read()

            original_content = content

            # Replace invalid license formats with the correct table format
            # Match both "NoLicense" and simple string licenses
            content = re.sub(
                r'^license\s*=\s*"(?:NoLicense|[^"]+)"',
                'license = {text = "MIT"}',
                content,
                flags=re.MULTILINE
            )

            # Only write if content changed
            if content != original_content:
                with open(pyproject_path, 'w') as f:
                    f.write(content)
                print("📝 Updated license field in pyproject.toml")
                return True

            return False

        except Exception as e:
            print(f"❌ Failed to fix license field: {e}")
            return False
