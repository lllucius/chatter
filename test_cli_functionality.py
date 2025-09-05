#!/usr/bin/env python3
"""
CLI testing script that validates the seeding CLI commands work correctly.
Uses a modified approach to test without requiring full database setup.
"""

import asyncio
import sys
import subprocess
import tempfile
import os
from pathlib import Path

# Add the parent directory to the path so we can import chatter modules
sys.path.insert(0, str(Path(__file__).parent))

class CLITester:
    """Tests CLI functionality for the seeding system."""
    
    def __init__(self):
        self.test_results = []
        self.errors = []
        
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log a test result."""
        status = "✅" if success else "❌"
        full_message = f"{status} {test_name}"
        if message:
            full_message += f": {message}"
        
        self.test_results.append((test_name, success, message))
        print(full_message)
        
        if not success:
            self.errors.append(full_message)
    
    def run_cli_command(self, command: list[str], expect_success: bool = True) -> tuple[bool, str]:
        """Run a CLI command and return (success, output)."""
        try:
            result = subprocess.run(
                command,
                cwd=str(Path(__file__).parent),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = (result.returncode == 0) if expect_success else (result.returncode != 0)
            output = result.stdout + result.stderr
            return success, output
            
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, f"Exception: {e}"
    
    def test_cli_help_commands(self):
        """Test that CLI help commands work."""
        help_tests = [
            (["python", "scripts/seed_database.py", "--help"], "Main help"),
            (["python", "scripts/seed_database.py", "seed", "--help"], "Seed help"),
            (["python", "scripts/seed_database.py", "status", "--help"], "Status help"), 
            (["python", "scripts/seed_database.py", "clear", "--help"], "Clear help"),
            (["python", "scripts/seed_database.py", "modes"], "List modes"),
        ]
        
        for command, description in help_tests:
            success, output = self.run_cli_command(command)
            self.log_result(f"CLI help test ({description})", success, 
                          "Command executed successfully" if success else f"Failed: {output[:100]}")
    
    def test_cli_modes_command(self):
        """Test the modes listing command."""
        success, output = self.run_cli_command(["python", "scripts/seed_database.py", "modes"])
        
        if success:
            # Check that expected mode names appear in output
            expected_modes = ["minimal", "development", "demo", "testing", "production"]
            modes_found = [mode for mode in expected_modes if mode in output.lower()]
            
            if len(modes_found) == len(expected_modes):
                self.log_result("CLI modes content", True, f"All {len(expected_modes)} modes listed")
            else:
                self.log_result("CLI modes content", False, f"Only found {len(modes_found)} of {len(expected_modes)} modes")
        else:
            self.log_result("CLI modes command", False, f"Command failed: {output}")
    
    def test_cli_import_validation(self):
        """Test that CLI script imports work by trying to import the modules."""
        test_name = "CLI import validation"
        
        try:
            # Test the key imports that the CLI script uses
            import_test_script = """
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from chatter.utils.seeding import DatabaseSeeder, SeedingMode, seed_database, clear_all_data
    from chatter.utils.configurable_seeding import seed_database_with_config
    from chatter.utils.database import init_database, check_database_connection
    from chatter.utils.logging import get_logger
    print("SUCCESS: All imports successful")
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
"""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(import_test_script)
                temp_script = f.name
            
            try:
                success, output = self.run_cli_command(["python", temp_script])
                if success and "SUCCESS" in output:
                    self.log_result(test_name, True, "All CLI imports successful")
                else:
                    self.log_result(test_name, False, f"Import failed: {output}")
            finally:
                os.unlink(temp_script)
                
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {e}")
    
    def test_cli_status_without_db(self):
        """Test status command without database connection."""
        # This should gracefully handle missing database
        success, output = self.run_cli_command(
            ["python", "scripts/seed_database.py", "status"], 
            expect_success=False  # We expect this to fail gracefully
        )
        
        # The command should exit with error but provide useful information
        if "Database connection" in output:
            self.log_result("CLI status without DB", True, "Provides database connection feedback")
        else:
            self.log_result("CLI status without DB", False, "No database connection feedback")
    
    def test_enum_usage_in_seeding(self):
        """Test that the seeding system uses correct enum values."""
        test_name = "Enum usage validation"
        
        try:
            # Check the seeding code uses correct enums
            seeding_file = Path(__file__).parent / "chatter" / "utils" / "seeding.py"
            if not seeding_file.exists():
                self.log_result(test_name, False, "Seeding file not found")
                return
                
            content = seeding_file.read_text()
            
            # Check for corrected enum references (from the fixes report)
            if "PromptCategory.CODING" in content and "PromptCategory.ANALYTICAL" in content:
                if "ProfileType.ANALYTICAL" in content and "ProfileType.CREATIVE" in content:
                    self.log_result(test_name, True, "Correct enum values found in seeding code")
                else:
                    self.log_result(test_name, False, "Incorrect ProfileType enum usage")
            else:
                self.log_result(test_name, False, "Incorrect PromptCategory enum usage")
                
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {e}")
    
    def test_config_file_handling(self):
        """Test configuration file handling."""
        test_name = "Config file handling"
        
        try:
            # Check if seed_data.yaml exists and can be loaded
            config_file = Path(__file__).parent / "seed_data.yaml"
            
            if config_file.exists():
                import yaml
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                    
                if isinstance(config, dict):
                    self.log_result(test_name, True, f"Valid YAML config with {len(config)} sections")
                else:
                    self.log_result(test_name, False, "Config file is not a valid dictionary")
            else:
                self.log_result(test_name, True, "No config file (acceptable default)")
                
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {e}")
    
    async def test_seeding_function_apis(self):
        """Test the seeding function APIs work correctly."""
        test_name = "Seeding function APIs"
        
        try:
            from chatter.utils.seeding import seed_database, clear_all_data
            from chatter.utils.configurable_seeding import seed_database_with_config
            
            # Test that functions exist and are callable
            functions = [seed_database, clear_all_data, seed_database_with_config]
            all_callable = all(callable(func) for func in functions)
            
            if all_callable:
                self.log_result(test_name, True, f"All {len(functions)} seeding functions are callable")
            else:
                self.log_result(test_name, False, "Some seeding functions are not callable")
                
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {e}")
    
    async def run_all_tests(self):
        """Run all CLI tests."""
        print("🧪 Starting CLI testing for seeding system...")
        print("=" * 60)
        
        # Test CLI help and basic functionality
        self.test_cli_help_commands()
        self.test_cli_modes_command()
        self.test_cli_import_validation()
        self.test_cli_status_without_db()
        
        # Test code correctness
        self.test_enum_usage_in_seeding()
        self.test_config_file_handling()
        
        # Test async functions
        await self.test_seeding_function_apis()
        
        # Summary
        print("=" * 60)
        total_tests = len(self.test_results)
        successful = sum(1 for _, success, _ in self.test_results if success)
        
        print(f"📊 CLI Test Summary:")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {total_tests - successful}")
        print(f"   📋 Total: {total_tests}")
        
        if self.errors:
            print("\n🚨 Failed tests:")
            for error in self.errors:
                print(f"   {error}")
            return False
        else:
            print("\n🎉 All CLI tests passed!")
            return True


async def main():
    """Main CLI testing entry point."""
    tester = CLITester()
    success = await tester.run_all_tests()
    
    if not success:
        print("\n⚠️  Some tests failed. Check the errors above.")
        return False
    else:
        print("\n✨ CLI testing completed successfully!")
        return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)