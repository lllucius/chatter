"""File and directory utilities for SDK generation."""

import json
import shutil
from pathlib import Path
from typing import Any


def ensure_directory(path: Path, clean: bool = False) -> None:
    """Ensure a directory exists, optionally cleaning it first."""
    if clean and path.exists():
        print(f"🧹 Cleaning directory: {path}")
        shutil.rmtree(path)

    path.mkdir(parents=True, exist_ok=True)
    print(f"📁 Directory ready: {path}")


def save_json(
    data: dict[str, Any], path: Path, indent: int = 2
) -> None:
    """Save data as JSON to a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
    print(f"💾 Saved JSON: {path}")


def save_text(content: str, path: Path) -> None:
    """Save text content to a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"💾 Saved file: {path}")


def clean_temp_files(paths: list[Path]) -> None:
    """Clean up temporary files."""
    for path in paths:
        if path.exists():
            path.unlink()
            print(f"🗑️  Cleaned temp file: {path}")


def verify_files_exist(
    base_dir: Path, expected_files: list[str], file_type: str = "files"
) -> list[str]:
    """
    Verify that expected files exist and return a list of missing files.

    Args:
        base_dir: Base directory to check files in
        expected_files: List of relative file paths to check
        file_type: Description of the file type for logging

    Returns:
        List of missing file paths
    """
    missing_files = []

    print(f"🔍 Verifying {file_type} in {base_dir}:")

    for file_path in expected_files:
        full_path = base_dir / file_path

        if full_path.exists():
            if full_path.is_file():
                if file_path.endswith('.py') or file_path.endswith(
                    '.ts'
                ):
                    # Count lines for code files
                    try:
                        with open(full_path, encoding='utf-8') as f:
                            lines = len(f.readlines())
                        print(f"   ✅ {file_path} ({lines} lines)")
                    except Exception:
                        size = full_path.stat().st_size
                        print(f"   ✅ {file_path} ({size:,} bytes)")
                else:
                    # Show size for other files
                    size = full_path.stat().st_size
                    print(f"   ✅ {file_path} ({size:,} bytes)")
            elif full_path.is_dir():
                # Count files in directory
                file_count = len(list(full_path.glob("*")))
                print(f"   ✅ {file_path}/ ({file_count} files)")
            else:
                print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ Missing: {file_path}")
            missing_files.append(file_path)

    return missing_files


def get_generated_files_info(sdk_dir: Path) -> dict[str, Any]:
    """Get information about generated SDK files."""
    info = {
        "total_files": 0,
        "total_size": 0,
        "file_types": {},
        "largest_files": [],
    }

    if not sdk_dir.exists():
        return info

    files = list(sdk_dir.rglob("*"))
    files = [f for f in files if f.is_file()]

    info["total_files"] = len(files)

    for file_path in files:
        try:
            size = file_path.stat().st_size
            info["total_size"] += size

            suffix = file_path.suffix or "no_extension"
            info["file_types"][suffix] = (
                info["file_types"].get(suffix, 0) + 1
            )

            info["largest_files"].append(
                (str(file_path.relative_to(sdk_dir)), size)
            )
        except Exception:
            continue

    # Sort largest files by size (descending)
    info["largest_files"].sort(key=lambda x: x[1], reverse=True)
    info["largest_files"] = info["largest_files"][:10]  # Top 10

    return info
