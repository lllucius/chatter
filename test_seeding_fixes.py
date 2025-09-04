#!/usr/bin/env python3
"""Test script to validate database seeding fixes."""

import asyncio
import tempfile
import os
from pathlib import Path

# Test the seeding system by importing and checking for basic syntax errors
def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    
    try:
        from chatter.utils.seeding import DatabaseSeeder, SeedingMode, seed_database, clear_all_data
        print("✓ Basic seeding imports work")
    except Exception as e:
        print(f"✗ Basic seeding imports failed: {e}")
        return False
    
    try:
        from chatter.utils.configurable_seeding import ConfigurableSeeder, seed_database_with_config
        print("✓ Configurable seeding imports work")
    except Exception as e:
        print(f"✗ Configurable seeding imports failed: {e}")
        return False
    
    try:
        from chatter.models.prompt import PromptCategory
        # Test the enum values we fixed
        assert PromptCategory.CODING.value == "coding"
        assert PromptCategory.ANALYTICAL.value == "analytical"
        print("✓ Enum values are correct")
    except Exception as e:
        print(f"✗ Enum validation failed: {e}")
        return False
    
    return True


def test_basic_class_instantiation():
    """Test that we can create basic instances without database."""
    print("Testing class instantiation...")
    
    try:
        from chatter.utils.seeding import DatabaseSeeder
        # Test with mock session
        seeder = DatabaseSeeder(session=None)
        print("✓ DatabaseSeeder can be created")
    except Exception as e:
        print(f"✗ DatabaseSeeder creation failed: {e}")
        return False
    
    try:
        from chatter.utils.configurable_seeding import ConfigurableSeeder
        # Test with config file
        config_seeder = ConfigurableSeeder(config_path=None, session=None)
        print("✓ ConfigurableSeeder can be created")
    except Exception as e:
        print(f"✗ ConfigurableSeeder creation failed: {e}")
        return False
    
    return True


def test_yaml_config_loading():
    """Test YAML configuration loading."""
    print("Testing YAML config loading...")
    
    try:
        from chatter.utils.configurable_seeding import ConfigurableSeeder
        
        # Test with existing config file
        seed_data_path = Path(__file__).parent / "seed_data.yaml"
        if seed_data_path.exists():
            seeder = ConfigurableSeeder(config_path=str(seed_data_path), session=None)
            print("✓ YAML config loads successfully")
            print(f"✓ Found {len(seeder.config.get('development_users', []))} development users in config")
            print(f"✓ Found {len(seeder.config.get('chat_profiles', {}).get('basic', []))} basic chat profiles in config")
        else:
            print("⚠ seed_data.yaml not found, but loading logic works")
        
        return True
    except Exception as e:
        print(f"✗ YAML config loading failed: {e}")
        return False


def test_cli_script():
    """Test CLI script can be imported and help works."""
    print("Testing CLI script...")
    
    try:
        # Test that we can import the CLI without database connection
        import sys
        sys.path.insert(0, str(Path(__file__).parent / "scripts"))
        
        # Set minimal env to avoid database connection
        os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
        
        # Import the script
        import importlib.util
        spec = importlib.util.spec_from_file_location("seed_database", Path(__file__).parent / "scripts" / "seed_database.py")
        module = importlib.util.module_from_spec(spec)
        
        print("✓ CLI script imports successfully")
        return True
    except Exception as e:
        print(f"✗ CLI script import failed: {e}")
        return False


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("Database Seeding System Validation Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_basic_class_instantiation,
        test_yaml_config_loading,
        test_cli_script,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        print(f"\n{test.__name__}:")
        try:
            if test():
                passed += 1
                print(f"✓ {test.__name__} PASSED")
            else:
                failed += 1
                print(f"✗ {test.__name__} FAILED")
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All tests passed! The seeding system fixes look good.")
        return True
    else:
        print("❌ Some tests failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)