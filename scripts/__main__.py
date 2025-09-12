"""Allow scripts package to be run as a module."""

if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Add project root to Python path
    project_root = Path(__file__).parent.parent.resolve()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from scripts.generate_sdks import main

    sys.exit(main())
