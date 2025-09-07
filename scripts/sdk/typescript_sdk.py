"""TypeScript SDK generator using OpenAPI Generator CLI."""

import json
import subprocess
from pathlib import Path

from scripts.utils.config import TypeScriptSDKConfig, get_openapi_generator_config
from scripts.utils.files import ensure_directory, clean_temp_files


class TypeScriptSDKGenerator:
    """Generates TypeScript SDK from OpenAPI specification."""

    def __init__(self, config: TypeScriptSDKConfig) -> None:
        """Initialize TypeScript SDK generator.

        Args:
            config: Configuration for TypeScript SDK generation
        """
        self.config = config
        self.temp_files: list[Path] = []

    def generate_with_cleanup(self) -> bool:
        """Generate TypeScript SDK with cleanup of temporary files.

        Returns:
            True if generation was successful, False otherwise
        """
        try:
            return self._generate()
        finally:
            clean_temp_files(self.temp_files)

    def _generate(self) -> bool:
        """Generate TypeScript SDK using OpenAPI Generator CLI.

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
            config_file = self.config.output_dir / "generator-config.json"
            with open(config_file, 'w') as f:
                json.dump(generator_config, f, indent=2)
            self.temp_files.append(config_file)

            # Build OpenAPI Generator command
            cmd = [
                "npx", "@openapitools/openapi-generator-cli", "generate",
                "-i", str(openapi_spec),
                "-g", "typescript-fetch",
                "-o", str(self.config.output_dir),
                "-c", str(config_file),
                "--skip-validate-spec",  # Skip spec validation for OpenAPI 3.1
                "--additional-properties",
                f"npmName={self.config.npm_name},"
                f"npmVersion={self.config.package_version},"
                f"supportsES6={str(self.config.supports_es6).lower()}"
            ]

            print(f"📦 Generating TypeScript SDK in {self.config.output_dir}")
            print(f"   Using spec: {openapi_spec}")

            # Run the generator
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.config.project_root
            )

            if result.returncode != 0:
                print("❌ OpenAPI Generator failed:")
                print(f"   STDOUT: {result.stdout}")
                print(f"   STDERR: {result.stderr}")
                return False

            print("✅ TypeScript SDK generation completed")
            return True

        except Exception as e:
            print(f"❌ TypeScript SDK generation failed: {e}")
            return False

    def validate(self) -> bool:
        """Validate that the generated TypeScript SDK is complete and functional.

        Returns:
            True if SDK validation passes, False otherwise
        """
        try:
            # Check if output directory exists
            if not self.config.output_dir.exists():
                print("❌ SDK output directory does not exist")
                return False

            # Check for essential TypeScript SDK files
            essential_files = [
                "package.json",
                "src/index.ts",
                "src/runtime.ts"
            ]

            missing_files = []
            for file_path in essential_files:
                full_path = self.config.output_dir / file_path
                if not full_path.exists():
                    missing_files.append(file_path)

            if missing_files:
                print(f"❌ Missing essential SDK files: {missing_files}")
                return False

            # Check for API modules
            apis_dir = self.config.output_dir / "src" / "apis"
            if apis_dir.exists():
                api_files = list(apis_dir.glob("*.ts"))
                if not api_files:
                    print("❌ No API modules found in generated SDK")
                    return False

            # Check for model modules
            models_dir = self.config.output_dir / "src" / "models"
            if models_dir.exists():
                model_files = list(models_dir.glob("*.ts"))
                if not model_files:
                    print("❌ No model modules found in generated SDK")
                    return False

            # Validate package.json content
            package_json = self.config.output_dir / "package.json"
            if package_json.exists():
                try:
                    with open(package_json) as f:
                        pkg_data = json.load(f)

                    # Check essential package.json fields
                    if pkg_data.get("name") != self.config.npm_name:
                        print(f"❌ Package name mismatch: expected {self.config.npm_name}, got {pkg_data.get('name')}")
                        return False

                    if not pkg_data.get("version"):
                        print("❌ Package version missing")
                        return False

                except json.JSONDecodeError as e:
                    print(f"❌ Invalid package.json: {e}")
                    return False

            print("✅ TypeScript SDK validation passed")
            return True

        except Exception as e:
            print(f"❌ TypeScript SDK validation failed: {e}")
            return False

    def _find_openapi_spec(self) -> Path | None:
        """Find OpenAPI specification file.

        Returns:
            Path to OpenAPI spec file, or None if not found
        """
        # Look for spec files in standard locations (prefer 3.0 compatible version)
        possible_locations = [
            self.config.project_root / "docs" / "api" / "openapi-3.0.json",
            self.config.project_root / "docs" / "api" / "openapi.json",
            self.config.project_root / "docs" / "api" / "openapi-3.0.yaml",
            self.config.project_root / "docs" / "api" / "openapi.yaml",
            self.config.project_root / "openapi-3.0.json",
            self.config.project_root / "openapi.json",
            self.config.project_root / "openapi-3.0.yaml",
            self.config.project_root / "openapi.yaml"
        ]

        for spec_path in possible_locations:
            if spec_path.exists():
                return spec_path

        return None
