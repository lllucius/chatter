import re

def fix_exception_chaining(file_path):
    with open(file_path) as f:
        content = f.read()

    # Pattern to match exception raises that need "from e" or "from None"
    patterns = [
        (r'raise (\w+Error)\((.*?)\)\s*$', r'raise \1(\2) from e'),
        (r'raise (\w+Error)\((.*?)\)$', r'raise \1(\2) from e'),
        (r'except (TimeoutError):\s*raise (\w+Error)\((.*?)\)', r'except \1 as e:\n                    raise \2(\3) from e'),
        (r'except (TimeoutError, OSError):\s*raise (\w+Error)\((.*?)\)', r'except \1:\n                raise \2(\3) from None'),
    ]

    modified = False
    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        if new_content != content:
            content = new_content
            modified = True

    # Manual fixes for specific cases
    fixes = [
        ('raise ValueError(\n                    f"Failed to install plugin files: {str(e)}"\n                )',
         'raise ValueError(\n                    f"Failed to install plugin files: {str(e)}"\n                ) from e'),

        ('raise ValueError(\n                    f"Failed to create plugin instance: {str(e)}"\n                )',
         'raise ValueError(\n                    f"Failed to create plugin instance: {str(e)}"\n                ) from e'),

        ('raise RuntimeError(\n                        "Plugin initialization timed out"\n                    )',
         'raise RuntimeError(\n                        "Plugin initialization timed out"\n                    ) from None'),

        ('raise ValueError(f"Invalid plugin path: {e}")',
         'raise ValueError(f"Invalid plugin path: {e}") from e'),

        ('raise ImportError(f"Invalid plugin paths: {e}")',
         'raise ImportError(f"Invalid plugin paths: {e}") from e'),

        ('raise ImportError(f"Cannot access plugin file: {e}")',
         'raise ImportError(f"Cannot access plugin file: {e}") from e'),

        ('raise ImportError("Plugin loading timed out or failed")',
         'raise ImportError("Plugin loading timed out or failed") from None'),

        ('raise ImportError(f"Error loading plugin module: {e}")',
         'raise ImportError(f"Error loading plugin module: {e}") from e'),

        ('raise ImportError(f"Failed to load plugin: {e}")',
         'raise ImportError(f"Failed to load plugin: {e}") from e'),
    ]

    for old, new in fixes:
        if old in content:
            content = content.replace(old, new)
            modified = True

    if modified:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Fixed exception chaining in {file_path}")

# Fix the plugins.py file
fix_exception_chaining('chatter/services/plugins.py')
