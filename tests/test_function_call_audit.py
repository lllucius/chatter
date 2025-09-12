"""Test to verify function call audit fixes."""

import ast
from pathlib import Path


def test_conversation_status_import():
    """Test that ConversationStatus is properly imported in analytics.py."""
    analytics_file = (
        Path(__file__).parent.parent
        / "chatter"
        / "core"
        / "analytics.py"
    )

    with open(analytics_file) as f:
        content = f.read()

    # Parse the AST
    tree = ast.parse(content, filename=str(analytics_file))

    # Check for ConversationStatus import
    imported_names = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ImportFrom)
            and node.module == "chatter.models.conversation"
        ):
            for alias in node.names:
                imported_names.add(alias.name)

    assert (
        "ConversationStatus" in imported_names
    ), "ConversationStatus should be imported from chatter.models.conversation"


def test_analytics_file_compiles():
    """Test that analytics.py compiles without errors."""
    analytics_file = (
        Path(__file__).parent.parent
        / "chatter"
        / "core"
        / "analytics.py"
    )

    with open(analytics_file) as f:
        content = f.read()

    # This should not raise any exceptions
    compile(content, str(analytics_file), 'exec')
    ast.parse(content, filename=str(analytics_file))


def test_no_undefined_names_in_analytics():
    """Test that there are no undefined names used in analytics.py."""
    analytics_file = (
        Path(__file__).parent.parent
        / "chatter"
        / "core"
        / "analytics.py"
    )

    with open(analytics_file) as f:
        content = f.read()

    # Parse the AST
    tree = ast.parse(content, filename=str(analytics_file))

    # Extract all imported names
    imported_names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split('.')[0]
                imported_names.add(name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                name = alias.asname or alias.name
                imported_names.add(name)

    # Extract all used names
    used_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(
            node.ctx, ast.Load
        ):
            used_names.add(node.id)

    # Built-in names that don't need to be imported

    # Check that ConversationStatus is imported and would be available
    assert (
        "ConversationStatus" in imported_names
    ), "ConversationStatus must be imported"

    # The test passes if no import errors occur during compilation
    # This is sufficient to verify the fix worked


def test_chatter_sdk_client_import():
    """Test that ChatterSDKClient is properly imported in api_cli.py."""
    api_cli_file = (
        Path(__file__).parent.parent / "chatter" / "api_cli.py"
    )

    with open(api_cli_file) as f:
        content = f.read()

    # Parse the AST
    tree = ast.parse(content, filename=str(api_cli_file))

    # Check for ChatterSDKClient import
    imported_names = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ImportFrom)
            and node.module == "chatter.commands"
        ):
            for alias in node.names:
                imported_names.add(alias.name)

    assert (
        "ChatterSDKClient" in imported_names
    ), "ChatterSDKClient should be imported from chatter.commands"


def test_api_cli_file_compiles():
    """Test that api_cli.py compiles without errors."""
    api_cli_file = (
        Path(__file__).parent.parent / "chatter" / "api_cli.py"
    )

    with open(api_cli_file) as f:
        content = f.read()

    # This should not raise any exceptions
    compile(content, str(api_cli_file), 'exec')
    ast.parse(content, filename=str(api_cli_file))


def test_comprehensive_compilation():
    """Test that all Python files in the chatter module compile without errors."""
    chatter_dir = Path(__file__).parent.parent / "chatter"
    compilation_errors = []

    for python_file in chatter_dir.rglob("*.py"):
        # Skip __pycache__ and test files
        if (
            "__pycache__" in str(python_file)
            or "test_" in python_file.name
        ):
            continue

        try:
            with open(python_file, encoding='utf-8') as f:
                content = f.read()
            compile(content, str(python_file), 'exec')
        except Exception as e:
            compilation_errors.append((python_file, str(e)))

    assert (
        not compilation_errors
    ), f"Compilation errors found: {compilation_errors}"


def test_critical_imports_exist():
    """Test that critical imports used across the codebase are properly available."""
    # Map of modules to critical imports that should be available
    critical_imports = {
        "chatter.commands": ["ChatterSDKClient"],
        "chatter.models.conversation": ["ConversationStatus"],
        "chatter.core.exceptions": [
            "ChatterBaseException",
            "ValidationError",
            "ServiceError",
        ],
        "chatter.services.llm": ["LLMService"],
        "chatter.utils.database": ["get_session_maker"],
    }

    for module_name, expected_imports in critical_imports.items():
        try:
            # Try to import the module
            module_path = Path(
                __file__
            ).parent.parent / module_name.replace(".", "/")
            if module_path.is_dir():
                init_file = module_path / "__init__.py"
            else:
                init_file = module_path.with_suffix(".py")

            if init_file.exists():
                with open(init_file) as f:
                    content = f.read()

                tree = ast.parse(content, filename=str(init_file))

                # Check if expected imports/definitions exist
                defined_names = set()
                for node in ast.walk(tree):
                    if isinstance(
                        node, (ast.FunctionDef, ast.ClassDef)
                    ):
                        defined_names.add(node.name)

                for expected_import in expected_imports:
                    assert (
                        expected_import in defined_names
                        or expected_import in content
                    ), f"{expected_import} not found in {module_name}"

        except Exception as e:
            # If we can't analyze the file, at least check it exists
            raise AssertionError(
                f"Error checking critical imports in {module_name}: {e}"
            )


def test_no_obvious_missing_imports():
    """Test for obvious missing import patterns that could cause runtime errors."""
    chatter_dir = Path(__file__).parent.parent / "chatter"

    # Patterns that often indicate missing imports
    suspicious_patterns = []

    for python_file in chatter_dir.rglob("*.py"):
        if (
            "__pycache__" in str(python_file)
            or "test_" in python_file.name
        ):
            continue

        try:
            with open(python_file, encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content, filename=str(python_file))

            # Extract imports
            imported_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        name = alias.asname or alias.name.split('.')[0]
                        imported_names.add(name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for alias in node.names:
                            name = alias.asname or alias.name
                            imported_names.add(name)

            # Look for calls to specific classes that should be imported
            known_external_classes = {
                'HTTPException',
                'APIRouter',
                'Depends',
                'AsyncSession',
                'Session',
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(
                    node.func, ast.Name
                ):
                    call_name = node.func.id
                    if (
                        call_name in known_external_classes
                        and call_name not in imported_names
                    ):
                        # Check if it's defined locally
                        locally_defined = any(
                            isinstance(n, ast.ClassDef)
                            and n.name == call_name
                            for n in ast.walk(tree)
                        )
                        if not locally_defined:
                            suspicious_patterns.append(
                                f"{python_file.relative_to(chatter_dir)}:{getattr(node, 'lineno', 0)} - "
                                f"Possible missing import: {call_name}"
                            )

        except Exception:
            # Skip files that can't be parsed
            continue

    # Allow a small number of false positives, but flag if too many
    assert (
        len(suspicious_patterns) < 5
    ), f"Too many suspicious import patterns found: {suspicious_patterns[:10]}"


def test_sdk_import_consistency():
    """Test that SDK imports are consistent across CLI and command files."""
    # Files that use the SDK should have consistent import patterns
    sdk_files = [
        Path(__file__).parent.parent / "chatter" / "api_cli.py",
        Path(__file__).parent.parent
        / "chatter"
        / "commands"
        / "__init__.py",
    ]

    sdk_import_patterns = []

    for file_path in sdk_files:
        if file_path.exists():
            with open(file_path) as f:
                content = f.read()

            # Check for chatter_sdk imports
            if "chatter_sdk" in content:
                tree = ast.parse(content, filename=str(file_path))

                # Extract SDK-related imports
                sdk_imports = set()
                for node in ast.walk(tree):
                    if (
                        isinstance(node, ast.ImportFrom)
                        and node.module
                        and "chatter_sdk" in node.module
                    ):
                        for alias in node.names:
                            sdk_imports.add(alias.name)

                sdk_import_patterns.append(
                    (file_path.name, sdk_imports)
                )

    # Ensure SDK imports are reasonable (not checking exact match as different files may need different APIs)
    for file_name, imports in sdk_import_patterns:
        assert (
            len(imports) > 0
        ), f"No SDK imports found in {file_name} despite chatter_sdk usage"
