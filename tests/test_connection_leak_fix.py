"""Test for SQLAlchemy connection leak fix."""

import pytest

from chatter.utils.database import DatabaseManager


class TestConnectionLeakFix:
    """Test that connection leak causing methods have been removed."""

    def test_problematic_methods_removed(self):
        """Test that the problematic methods that caused connection leaks are removed."""
        db_manager = DatabaseManager()
        
        # These methods should no longer exist as they caused connection leaks
        assert not hasattr(db_manager, '_attempt_connection'), \
            "_attempt_connection method should be removed (caused connection leaks)"
        
        assert not hasattr(db_manager, 'get_connection_with_retry'), \
            "get_connection_with_retry method should be removed (caused connection leaks)"
        
        assert not hasattr(db_manager, 'get_connection_with_timeout'), \
            "get_connection_with_timeout method should be removed (caused connection leaks)"

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

    def test_async_context_manager_pattern(self):
        """Test that DatabaseManager follows proper async context manager pattern."""
        db_manager = DatabaseManager()
        
        # Should be usable as async context manager
        assert hasattr(db_manager, '__aenter__')
        assert hasattr(db_manager, '__aexit__')
        
        # Verify the methods are callable
        assert callable(getattr(db_manager, '__aenter__'))
        assert callable(getattr(db_manager, '__aexit__'))