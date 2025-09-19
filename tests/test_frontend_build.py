"""Test frontend build and dependency resolution."""

import subprocess
from pathlib import Path


def test_sdk_build():
    """Test that the TypeScript SDK can be built successfully."""
    sdk_path = Path(__file__).parent.parent / "sdk" / "typescript"

    # Check if SDK directory exists
    assert sdk_path.exists(), f"SDK directory not found at {sdk_path}"

    # Check if package.json exists
    package_json = sdk_path / "package.json"
    assert (
        package_json.exists()
    ), f"package.json not found at {package_json}"

    # Try to build the SDK
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=sdk_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"SDK build failed: {result.stderr}"

    # Check if dist directory was created
    dist_path = sdk_path / "dist"
    assert (
        dist_path.exists()
    ), f"Dist directory not created at {dist_path}"

    # Check if main files exist
    assert (
        dist_path / "index.js"
    ).exists(), "index.js not found in dist"
    assert (
        dist_path / "index.d.ts"
    ).exists(), "index.d.ts not found in dist"


def test_frontend_dependency_resolution():
    """Test that frontend can resolve chatter-sdk dependency."""
    frontend_path = Path(__file__).parent.parent / "frontend"

    # Check if frontend directory exists
    assert (
        frontend_path.exists()
    ), f"Frontend directory not found at {frontend_path}"

    # Check if package.json exists
    package_json = frontend_path / "package.json"
    assert (
        package_json.exists()
    ), f"package.json not found at {package_json}"

    # Run npm ls to check if chatter-sdk is properly linked
    result = subprocess.run(
        ["npm", "ls", "chatter-sdk"],
        cwd=frontend_path,
        capture_output=True,
        text=True,
    )

    assert (
        result.returncode == 0
    ), f"chatter-sdk dependency not resolved: {result.stderr}"
    assert (
        "chatter-sdk@0.1.0" in result.stdout
    ), f"Unexpected chatter-sdk version: {result.stdout}"
