# Function Signature Audit

This document describes the function signature audit system for the Chatter codebase, which helps prevent runtime errors caused by missing imports, undefined functions, and other signature-related issues.

## Background

Function call signature mismatches can cause runtime failures that are difficult to detect during development. These issues typically manifest as:

- `NameError: name 'SomeClass' is not defined` - Missing imports
- `TypeError: function() takes X arguments but Y were given` - Signature mismatches
- Import errors for optional dependencies

The audit system was developed following PR #472, which fixed a missing `ChatterSDKClient` import that would have caused runtime failures.

## Audit Framework

### Automated Tests

The test suite includes comprehensive function signature validation:

```bash
# Run all audit tests
pytest tests/test_function_call_audit.py -v
```

**Key Tests:**
- `test_comprehensive_compilation()` - Ensures all Python files compile
- `test_critical_imports_exist()` - Verifies critical imports are available
- `test_no_obvious_missing_imports()` - Catches common import patterns
- `test_sdk_import_consistency()` - Validates SDK import patterns

### Development Audit Script

Use the development audit script for quick validation during development:

```bash
# Basic audit
python scripts/audit_function_signatures.py

# Verbose output showing all checked files
python scripts/audit_function_signatures.py --verbose
```

**What it checks:**
- Compilation of all Python files
- Known problematic patterns from previous issues
- Critical file integrity
- SDK import consistency

## Common Issues and Solutions

### Missing Imports

**Problem:** Class or function used without proper import
```python
# ❌ This will fail at runtime
def some_function():
    client = ChatterSDKClient()  # NameError if not imported
```

**Solution:** Add proper import
```python
# ✅ Correct approach
from chatter.commands import ChatterSDKClient

def some_function():
    client = ChatterSDKClient()
```

### Optional Dependencies

**Problem:** Import failures for optional dependencies
```python
# ❌ Will fail if openpyxl not installed
from openpyxl import Workbook
```

**Solution:** Use try/except for optional imports
```python
# ✅ Graceful handling of optional dependencies
try:
    from openpyxl import Workbook
    HAS_EXCEL_SUPPORT = True
except ImportError:
    HAS_EXCEL_SUPPORT = False
    Workbook = None
```

### Circular Imports

**Problem:** Circular import dependencies
```python
# ❌ Can cause import failures
from chatter.services.llm import LLMService
```

**Solution:** Use TYPE_CHECKING for type hints
```python
# ✅ Avoid circular imports for type checking
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chatter.services.llm import LLMService
```

## Integration with CI/CD

### Pre-commit Hooks

Add the audit script to your pre-commit hooks:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: function-signature-audit
        name: Function Signature Audit
        entry: python scripts/audit_function_signatures.py
        language: system
        pass_filenames: false
        always_run: true
```

### GitHub Actions

Include in your CI pipeline:

```yaml
# .github/workflows/test.yml
- name: Function Signature Audit
  run: python scripts/audit_function_signatures.py
```

## Best Practices

### 1. Import Organization

Follow this import order:
```python
# Standard library imports
import os
import sys

# Third-party imports  
from fastapi import APIRouter
from sqlalchemy.orm import Session

# Local application imports
from chatter.core.exceptions import ChatterBaseException
from chatter.services.llm import LLMService
```

### 2. Lazy Imports

Use lazy imports for optional or heavy dependencies:
```python
def export_to_excel(data):
    try:
        from openpyxl import Workbook
    except ImportError:
        raise ImportError("openpyxl required for Excel export")
    
    # Use Workbook here
```

### 3. Type Checking Imports

Separate runtime and type-checking imports:
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chatter.services.heavy_service import HeavyService

def my_function(service: 'HeavyService') -> None:
    # Function implementation
    pass
```

### 4. Validation During Development

Run the audit regularly during development:
```bash
# Quick check
python scripts/audit_function_signatures.py

# After making changes to imports
pytest tests/test_function_call_audit.py
```

## Extending the Audit System

### Adding New Checks

To add new validation patterns:

1. **Add to test suite:**
```python
def test_new_pattern():
    """Test for new problematic pattern."""
    # Implementation here
```

2. **Add to audit script:**
```python
def check_new_pattern(self) -> List[Tuple[Path, int, str]]:
    """Check for new problematic pattern."""
    # Implementation here
```

### Custom Validation Rules

For project-specific validation:

```python
# In audit script
CUSTOM_RULES = {
    "CustomClass": "project.module.custom",
    "SpecialFunction": "project.utils.special"
}

def check_custom_patterns(self):
    # Validate custom patterns
    pass
```

## Troubleshooting

### Common False Positives

The audit system may flag legitimate patterns:

1. **Classes defined in same file:**
   - These are not issues - the audit should skip them
   
2. **Dynamic imports:**
   - Use `# type: ignore` comments for intentional dynamic imports
   
3. **Optional dependencies:**
   - Ensure they're in try/except blocks to avoid false positives

### Performance Considerations

For large codebases:
- Use `--verbose` sparingly in automated systems
- Consider running only on changed files in CI
- Cache results for repeated runs

## History

- **PR #472:** Fixed missing ChatterSDKClient import in api_cli.py
- **Initial Audit:** Comprehensive signature validation system
- **Current State:** All 100+ Python files pass validation

This audit system helps maintain code quality and prevents runtime failures related to function signatures and imports.