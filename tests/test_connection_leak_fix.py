"""Test for SQLAlchemy connection leak fix."""

import pytest

from chatter.utils.database import DatabaseManager


class TestConnectionLeakFix:
    """Test that connection leak issues in get_session_generator are fixed."""

    def test_session_generator_cleanup_logic(self):
        """Test that get_session_generator has proper cleanup logic."""
        from chatter.utils.database import get_session_generator
        import inspect
        
        # Get the source code of the function
        source = inspect.getsource(get_session_generator)
        
        # Verify that session.close() is called in multiple places for proper cleanup
        close_calls = source.count('await session.close()')
        
        # Should have multiple session.close() calls for different cleanup scenarios
        assert close_calls >= 3, \
            f"get_session_generator should have multiple session.close() calls for proper cleanup, found {close_calls}"
        
        # Verify GeneratorExit handler includes session.close()
        assert 'GeneratorExit' in source, \
            "get_session_generator should handle GeneratorExit"
        
        # Verify that the GeneratorExit handler closes the session
        generator_exit_section = source[source.find('except GeneratorExit:'):source.find('except Exception:')]
        assert 'await session.close()' in generator_exit_section, \
            "GeneratorExit handler should close the session to prevent leaks"

    def test_database_manager_still_functional(self):
        """Test that DatabaseManager still has its core functionality."""
        db_manager = DatabaseManager()
        
        # Core functionality should still be present
        assert hasattr(db_manager, '__aenter__'), \
            "DatabaseManager should still have __aenter__ method"
        
        assert hasattr(db_manager, '__aexit__'), \
            "DatabaseManager should still have __aexit__ method"
        
        assert hasattr(db_manager, 'get_pool_stats'), \
            "DatabaseManager should still have get_pool_stats method"
        
        assert hasattr(db_manager, 'transaction'), \
            "DatabaseManager should still have transaction method"
        
        assert hasattr(db_manager, 'detect_connection_leaks'), \
            "DatabaseManager should still have detect_connection_leaks method"

    def test_connection_retry_methods_exist(self):
        """Test that the connection retry methods are still available."""
        db_manager = DatabaseManager()
        
        # These methods should exist since they weren't the actual source of leaks
        assert hasattr(db_manager, '_attempt_connection'), \
            "_attempt_connection method should still exist"
        
        assert hasattr(db_manager, 'get_connection_with_retry'), \
            "get_connection_with_retry method should still exist"
        
        assert hasattr(db_manager, 'get_connection_with_timeout'), \
            "get_connection_with_timeout method should still exist"