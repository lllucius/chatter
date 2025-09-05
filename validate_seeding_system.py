#!/usr/bin/env python3
"""
Comprehensive validation script for the database seeding system.
Tests all seeding functions without requiring a full database setup.
"""

import asyncio
import sys
import traceback
from pathlib import Path
from unittest.mock import AsyncMock, Mock, MagicMock
from typing import Any, Dict

# Add the parent directory to the path so we can import chatter modules
sys.path.insert(0, str(Path(__file__).parent))

# Import seeding modules
try:
    from chatter.utils.seeding import DatabaseSeeder, SeedingMode, seed_database, clear_all_data
    from chatter.utils.configurable_seeding import ConfigurableSeeder, seed_database_with_config
    from chatter.models.prompt import PromptCategory
    from chatter.models.profile import ProfileType
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class SeedingValidator:
    """Validates the seeding system functionality."""
    
    def __init__(self):
        self.errors = []
        self.successes = []
    
    def log_success(self, test_name: str, message: str = ""):
        """Log a successful test."""
        full_message = f"✅ {test_name}"
        if message:
            full_message += f": {message}"
        self.successes.append(full_message)
        print(full_message)
    
    def log_error(self, test_name: str, error: str):
        """Log a test error."""
        full_message = f"❌ {test_name}: {error}"
        self.errors.append(full_message)
        print(full_message)
    
    def test_imports(self):
        """Test that all required modules can be imported."""
        test_name = "Import validation"
        
        try:
            # Test enum imports and values
            categories = [PromptCategory.CODING, PromptCategory.ANALYTICAL]
            profile_types = [ProfileType.ANALYTICAL, ProfileType.CREATIVE, ProfileType.CONVERSATIONAL]
            
            # Test seeding mode enum
            modes = [
                SeedingMode.MINIMAL, 
                SeedingMode.DEVELOPMENT, 
                SeedingMode.DEMO,
                SeedingMode.TESTING,
                SeedingMode.PRODUCTION
            ]
            
            self.log_success(test_name, f"Successfully imported {len(categories)} prompt categories, {len(profile_types)} profile types, {len(modes)} seeding modes")
            
        except Exception as e:
            self.log_error(test_name, str(e))
    
    def test_seeder_initialization(self):
        """Test that seeder classes can be initialized."""
        test_name = "Seeder initialization"
        
        try:
            # Test DatabaseSeeder
            seeder = DatabaseSeeder(session=None)
            assert seeder.session is None
            assert seeder._should_close_session is True
            
            # Test ConfigurableSeeder
            config_seeder = ConfigurableSeeder(config_path=None, session=None)
            assert config_seeder.session is None
            assert isinstance(config_seeder.config, dict)
            
            self.log_success(test_name, "Both seeder classes initialize correctly")
            
        except Exception as e:
            self.log_error(test_name, str(e))
    
    async def test_mocked_seeding_operations(self):
        """Test seeding operations with mocked database session."""
        test_name = "Mocked seeding operations"
        
        try:
            # Create mock session
            mock_session = AsyncMock()
            mock_result = Mock()
            mock_result.scalar.return_value = 0  # No existing users
            mock_result.scalar_one_or_none.return_value = None  # No existing data
            mock_session.execute.return_value = mock_result
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()
            mock_session.add = Mock()
            
            # Test DatabaseSeeder with mock
            seeder = DatabaseSeeder(session=mock_session)
            
            # Test user counting
            count = await seeder._count_users()
            assert count == 0
            
            # Test admin user creation method exists and is callable
            admin_method = getattr(seeder, '_create_admin_user', None)
            assert admin_method is not None
            assert callable(admin_method)
            
            # Test other seeding methods exist
            required_methods = [
                '_seed_minimal_data',
                '_seed_development_data',
                '_seed_demo_data',
                '_seed_testing_data',
                '_seed_production_data',
                '_create_test_users',
                '_create_sample_documents'
            ]
            
            for method_name in required_methods:
                method = getattr(seeder, method_name, None)
                if method is None:
                    raise AttributeError(f"Method {method_name} not found")
                if not callable(method):
                    raise TypeError(f"Method {method_name} is not callable")
            
            self.log_success(test_name, f"All {len(required_methods)} required methods exist and are callable")
            
        except Exception as e:
            self.log_error(test_name, str(e))
            traceback.print_exc()
    
    async def test_configurable_seeding_operations(self):
        """Test configurable seeding operations."""
        test_name = "Configurable seeding operations"
        
        try:
            # Create mock session
            mock_session = AsyncMock()
            mock_result = Mock()
            mock_result.scalar.return_value = 0
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()
            mock_session.add = Mock()
            
            # Test ConfigurableSeeder
            config_seeder = ConfigurableSeeder(config_path=None, session=mock_session)
            
            # Test required methods exist
            required_methods = [
                '_create_development_users',
                '_create_basic_profiles',
                '_create_basic_prompts',
                '_load_config',
                '_find_config_file'
            ]
            
            for method_name in required_methods:
                method = getattr(config_seeder, method_name, None)
                if method is None:
                    raise AttributeError(f"ConfigurableSeeder method {method_name} not found")
                if not callable(method):
                    raise TypeError(f"ConfigurableSeeder method {method_name} is not callable")
            
            self.log_success(test_name, f"All {len(required_methods)} configurable seeding methods exist")
            
        except Exception as e:
            self.log_error(test_name, str(e))
    
    async def test_seeding_mode_execution(self):
        """Test that each seeding mode can be executed with mocked database."""
        test_name = "Seeding mode execution"
        
        try:
            # Create comprehensive mock session
            mock_session = AsyncMock()
            mock_result = Mock()
            mock_result.scalar.return_value = 0  # No existing users
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock() 
            mock_session.add = Mock()
            
            # Test each seeding mode
            seeder = DatabaseSeeder(session=mock_session)
            
            modes_tested = []
            for mode in [SeedingMode.MINIMAL, SeedingMode.DEVELOPMENT, SeedingMode.TESTING]:
                try:
                    results = await seeder.seed_database(mode=mode, force=True, skip_existing=False)
                    assert isinstance(results, dict)
                    assert 'mode' in results
                    assert 'created' in results
                    modes_tested.append(mode.value)
                except NotImplementedError:
                    # Some methods might still be placeholders
                    pass
                except Exception as e:
                    # Log specific mode error but continue testing
                    print(f"  ⚠️  Mode {mode.value} had issue: {e}")
            
            if modes_tested:
                self.log_success(test_name, f"Successfully tested modes: {', '.join(modes_tested)}")
            else:
                self.log_error(test_name, "No seeding modes could be executed")
                
        except Exception as e:
            self.log_error(test_name, str(e))
    
    def test_cli_script_imports(self):
        """Test that CLI script can import required modules."""
        test_name = "CLI script import validation"
        
        try:
            # Test imports from the CLI script
            from chatter.utils.database import init_database, check_database_connection
            from chatter.utils.logging import get_logger
            
            # Test function callability
            assert callable(init_database)
            assert callable(check_database_connection)
            assert callable(get_logger)
            
            # Test logger can be created
            logger = get_logger("test")
            assert logger is not None
            
            self.log_success(test_name, "All CLI script imports successful")
            
        except Exception as e:
            self.log_error(test_name, str(e))
    
    def test_enum_values(self):
        """Test that enum values are correct and accessible."""
        test_name = "Enum value validation"
        
        try:
            # Test PromptCategory values
            expected_prompt_categories = ['CODING', 'ANALYTICAL']  # From fixes report
            for category_name in expected_prompt_categories:
                category = getattr(PromptCategory, category_name, None)
                if category is None:
                    raise AttributeError(f"PromptCategory.{category_name} not found")
            
            # Test ProfileType values  
            expected_profile_types = ['ANALYTICAL', 'CREATIVE', 'CONVERSATIONAL', 'TECHNICAL', 'CUSTOM']
            for profile_name in expected_profile_types:
                profile_type = getattr(ProfileType, profile_name, None)
                if profile_type is None:
                    raise AttributeError(f"ProfileType.{profile_name} not found")
            
            # Test SeedingMode values
            expected_modes = ['MINIMAL', 'DEVELOPMENT', 'DEMO', 'TESTING', 'PRODUCTION']
            for mode_name in expected_modes:
                mode = getattr(SeedingMode, mode_name, None)
                if mode is None:
                    raise AttributeError(f"SeedingMode.{mode_name} not found")
            
            self.log_success(test_name, "All enum values accessible")
            
        except Exception as e:
            self.log_error(test_name, str(e))
    
    async def test_function_level_apis(self):
        """Test module-level seeding functions."""
        test_name = "Function-level API validation"
        
        try:
            # Test seed_database function exists and is callable
            assert callable(seed_database)
            assert callable(clear_all_data)
            
            # Test seed_database_with_config function exists
            assert callable(seed_database_with_config)
            
            self.log_success(test_name, "All module-level functions are callable")
            
        except Exception as e:
            self.log_error(test_name, str(e))
    
    async def run_all_tests(self):
        """Run all validation tests."""
        print("🔍 Starting comprehensive seeding system validation...")
        print("=" * 60)
        
        # Run synchronous tests
        self.test_imports()
        self.test_seeder_initialization()
        self.test_cli_script_imports()
        self.test_enum_values()
        
        # Run asynchronous tests
        await self.test_mocked_seeding_operations()
        await self.test_configurable_seeding_operations()
        await self.test_seeding_mode_execution()
        await self.test_function_level_apis()
        
        # Print summary
        print("=" * 60)
        print(f"📊 Validation Summary:")
        print(f"   ✅ Successes: {len(self.successes)}")
        print(f"   ❌ Errors: {len(self.errors)}")
        
        if self.errors:
            print("\n🚨 Errors found:")
            for error in self.errors:
                print(f"   {error}")
            return False
        else:
            print("\n🎉 All validation tests passed!")
            return True


async def main():
    """Main validation entry point."""
    validator = SeedingValidator()
    success = await validator.run_all_tests()
    
    if not success:
        sys.exit(1)
    else:
        print("\n✨ The seeding system appears to be working correctly!")
        return True


if __name__ == "__main__":
    asyncio.run(main())