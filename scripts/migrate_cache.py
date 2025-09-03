#!/usr/bin/env python3
"""Migration script to switch from old caching system to unified cache system.

This script helps migrate existing code to use the new unified cache system.
"""

import os
import re
import sys
from pathlib import Path


class CacheMigrator:
    """Utility to migrate cache usage to unified system."""
    
    def __init__(self, project_root: str):
        """Initialize migrator.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.changes_made = 0
        
    def migrate_imports(self, file_path: Path) -> bool:
        """Migrate cache imports to use unified cache system.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            True if changes were made
        """
        if not file_path.suffix == '.py':
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Replace old cache imports
            replacements = [
                # Model registry cache
                (
                    r'from chatter\.utils\.caching import get_registry_cache',
                    'from chatter.core.unified_model_registry_cache import get_registry_cache'
                ),
                (
                    r'from chatter\.utils\.caching import ModelRegistryCache',
                    'from chatter.core.unified_model_registry_cache import UnifiedModelRegistryCache as ModelRegistryCache'
                ),
                (
                    r'from chatter\.utils\.caching import CacheWarmer',
                    'from chatter.core.unified_model_registry_cache import CacheWarmer'
                ),
                (
                    r'from chatter\.utils\.caching import clear_registry_cache',
                    'from chatter.core.unified_model_registry_cache import clear_registry_cache'
                ),
                
                # Workflow cache
                (
                    r'from chatter\.core\.workflow_performance import workflow_cache',
                    'from chatter.core.unified_workflow_cache import get_unified_workflow_cache\nworkflow_cache = get_unified_workflow_cache()'
                ),
                (
                    r'from chatter\.core\.workflow_performance import lazy_tool_loader',
                    'from chatter.core.unified_workflow_cache import get_unified_lazy_tool_loader\nlazy_tool_loader = get_unified_lazy_tool_loader()'
                ),
                (
                    r'from chatter\.core\.workflow_performance import WorkflowCache',
                    'from chatter.core.unified_workflow_cache import UnifiedWorkflowCache as WorkflowCache'
                ),
                (
                    r'from chatter\.core\.workflow_performance import LazyToolLoader',
                    'from chatter.core.unified_workflow_cache import UnifiedLazyToolLoader as LazyToolLoader'
                ),
                
                # Redis cache service
                (
                    r'from chatter\.services\.cache import get_cache_service',
                    'from chatter.core.cache_factory import get_general_cache\n# Note: get_cache_service replaced with get_general_cache'
                ),
                (
                    r'from chatter\.services\.cache import CacheService',
                    'from chatter.core.enhanced_redis_cache import EnhancedRedisCache as CacheService'
                ),
            ]
            
            for pattern, replacement in replacements:
                content = re.sub(pattern, replacement, content)
            
            # Convert sync cache calls to async
            async_replacements = [
                # Model registry cache methods
                (r'(\s+)(\w+\.cache\.)get_default_provider\(', r'\1await \2get_default_provider('),
                (r'(\s+)(\w+\.cache\.)set_default_provider\(', r'\1await \2set_default_provider('),
                (r'(\s+)(\w+\.cache\.)get_default_model\(', r'\1await \2get_default_model('),
                (r'(\s+)(\w+\.cache\.)set_default_model\(', r'\1await \2set_default_model('),
                (r'(\s+)(\w+\.cache\.)invalidate_defaults\(', r'\1await \2invalidate_defaults('),
                (r'(\s+)(\w+\.cache\.)get_provider\(', r'\1await \2get_provider('),
                (r'(\s+)(\w+\.cache\.)set_provider\(', r'\1await \2set_provider('),
                (r'(\s+)(\w+\.cache\.)invalidate_provider\(', r'\1await \2invalidate_provider('),
                (r'(\s+)(\w+\.cache\.)get_model\(', r'\1await \2get_model('),
                (r'(\s+)(\w+\.cache\.)set_model\(', r'\1await \2set_model('),
                (r'(\s+)(\w+\.cache\.)invalidate_model\(', r'\1await \2invalidate_model('),
                (r'(\s+)(\w+\.cache\.)get_provider_list\(', r'\1await \2get_provider_list('),
                (r'(\s+)(\w+\.cache\.)set_provider_list\(', r'\1await \2set_provider_list('),
                (r'(\s+)(\w+\.cache\.)get_model_list\(', r'\1await \2get_model_list('),
                (r'(\s+)(\w+\.cache\.)set_model_list\(', r'\1await \2set_model_list('),
                (r'(\s+)(\w+\.cache\.)invalidate_list_caches\(', r'\1await \2invalidate_list_caches('),
                (r'(\s+)(\w+\.cache\.)get_cache_stats\(', r'\1await \2get_cache_stats('),
                (r'(\s+)(\w+\.cache\.)clear_cache\(', r'\1await \2clear_cache('),
                
                # Workflow cache methods
                (r'(\s+)workflow_cache\.get\(', r'\1await workflow_cache.get('),
                (r'(\s+)workflow_cache\.put\(', r'\1await workflow_cache.put('),
                (r'(\s+)workflow_cache\.clear\(', r'\1await workflow_cache.clear('),
                (r'(\s+)workflow_cache\.get_stats\(', r'\1await workflow_cache.get_stats('),
                
                # Tool loader methods  
                (r'(\s+)lazy_tool_loader\.get_tools\(', r'\1await lazy_tool_loader.get_tools('),
                (r'(\s+)lazy_tool_loader\.clear_cache\(', r'\1await lazy_tool_loader.clear_cache('),
                (r'(\s+)lazy_tool_loader\.get_stats\(', r'\1await lazy_tool_loader.get_stats('),
            ]
            
            for pattern, replacement in async_replacements:
                content = re.sub(pattern, replacement, content)
            
            # Write back if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✓ Migrated: {file_path}")
                self.changes_made += 1
                return True
            
            return False
            
        except Exception as e:
            print(f"✗ Error migrating {file_path}: {e}")
            return False
    
    def migrate_directory(self, directory: Path) -> None:
        """Migrate all Python files in a directory.
        
        Args:
            directory: Directory to migrate
        """
        for file_path in directory.rglob("*.py"):
            # Skip certain directories
            if any(part in file_path.parts for part in ['__pycache__', '.git', 'node_modules', 'venv']):
                continue
            
            self.migrate_imports(file_path)
    
    def create_backup(self, backup_dir: str = "cache_migration_backup") -> None:
        """Create backup of current state.
        
        Args:
            backup_dir: Directory name for backup
        """
        import shutil
        
        backup_path = self.project_root / backup_dir
        if backup_path.exists():
            print(f"Warning: Backup directory {backup_path} already exists")
            return
        
        print(f"Creating backup at {backup_path}")
        shutil.copytree(
            self.project_root,
            backup_path,
            ignore=shutil.ignore_patterns('__pycache__', '.git', 'node_modules', 'venv', '*.pyc')
        )
        print("✓ Backup created")
    
    def report_summary(self) -> None:
        """Report migration summary."""
        print(f"\n📊 Migration Summary:")
        print(f"   Files modified: {self.changes_made}")
        
        if self.changes_made > 0:
            print(f"\n✅ Migration completed successfully!")
            print(f"   Next steps:")
            print(f"   1. Review the changes made")
            print(f"   2. Run tests to ensure everything works")
            print(f"   3. Remove old cache implementations if no longer needed")
        else:
            print(f"\nℹ️  No cache imports found to migrate.")


def main():
    """Main migration function."""
    if len(sys.argv) != 2:
        print("Usage: python migrate_cache.py <project_root>")
        print("Example: python migrate_cache.py /path/to/chatter")
        sys.exit(1)
    
    project_root = sys.argv[1]
    
    if not os.path.exists(project_root):
        print(f"Error: Project root '{project_root}' does not exist")
        sys.exit(1)
    
    print("🚀 Starting cache migration to unified system...")
    print(f"   Project root: {project_root}")
    
    migrator = CacheMigrator(project_root)
    
    # Ask if user wants backup
    response = input("\n📦 Create backup before migration? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        migrator.create_backup()
    
    # Perform migration
    print(f"\n🔄 Migrating cache imports...")
    migrator.migrate_directory(Path(project_root) / "chatter")
    
    # Report results
    migrator.report_summary()


if __name__ == "__main__":
    main()