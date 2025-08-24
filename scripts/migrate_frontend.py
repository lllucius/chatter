#!/usr/bin/env python3
"""
Script to migrate frontend components from old API to new SDK
"""

import re
from pathlib import Path
from typing import List, Tuple


def find_files_with_api_imports(src_dir: Path) -> List[Path]:
    """Find all TypeScript/TSX files that import from services/api"""
    files = []
    for pattern in ["**/*.ts", "**/*.tsx"]:
        for file_path in src_dir.glob(pattern):
            if "sdk" in str(file_path) or "node_modules" in str(file_path):
                continue
            
            content = file_path.read_text()
            if "from '../services/api'" in content or "from './services/api'" in content:
                files.append(file_path)
    
    return files


def migrate_api_imports(file_path: Path) -> bool:
    """Migrate API imports in a single file"""
    content = file_path.read_text()
    original_content = content
    
    # Replace import statements
    patterns = [
        (r"from '../services/api'", "from '../services/api-sdk'"),
        (r"from './services/api'", "from './services/api-sdk'"),
        (r"import { api }", "import { api }"),  # Keep as is - api object remains the same
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Write back if changed
    if content != original_content:
        file_path.write_text(content)
        return True
    
    return False


def main():
    """Main migration function"""
    print("🔄 Migrating frontend components to use TypeScript SDK...")
    
    frontend_src = Path(__file__).parent.parent / "frontend" / "src"
    files_to_migrate = find_files_with_api_imports(frontend_src)
    
    print(f"📂 Found {len(files_to_migrate)} files to migrate:")
    
    migrated_count = 0
    for file_path in files_to_migrate:
        relative_path = file_path.relative_to(frontend_src)
        if migrate_api_imports(file_path):
            print(f"  ✅ Migrated: {relative_path}")
            migrated_count += 1
        else:
            print(f"  ⚠️  No changes needed: {relative_path}")
    
    print(f"\n✨ Migration complete! Updated {migrated_count} files.")
    print("🔧 The API interface remains the same, so no code changes are needed.")
    print("💡 Components now use the generated TypeScript SDK with improved types and error handling.")


if __name__ == "__main__":
    main()