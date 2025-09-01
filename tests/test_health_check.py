"""Basic health check tests for the Chatter application."""


import pytest


@pytest.mark.unit
class TestHealthCheck:
    """Basic health check tests to verify test setup is working."""

    def test_basic_assertion(self):
        """Test that basic assertions work."""
        assert True
        assert 1 + 1 == 2
        assert "hello" == "hello"

    def test_mock_functionality(self, mock_session):
        """Test that mock fixtures are working."""
        assert mock_session is not None
        assert hasattr(mock_session, "add")
        assert hasattr(mock_session, "commit")

    def test_sample_data_fixtures(self, sample_user_data, sample_chat_data):
        """Test that sample data fixtures are working."""
        assert sample_user_data["email"] == "test@example.com"
        assert sample_chat_data["title"] == "Test Chat"
        assert len(sample_chat_data["messages"]) == 1

    @pytest.mark.asyncio
    async def test_async_functionality(self, mock_session):
        """Test that async test functionality works."""
        await mock_session.commit()
        mock_session.commit.assert_called_once()

    def test_pytest_markers(self):
        """Test that pytest markers are properly configured."""
        # This test itself uses the @pytest.mark.unit marker
        # If markers are misconfigured, this test would fail to run
        assert True


@pytest.mark.integration
class TestBasicIntegration:
    """Basic integration test class."""

    def test_integration_marker(self):
        """Test that integration marker works."""
        assert True


# Test to verify the test discovery is working
def test_module_level():
    """Module-level test function."""
    assert True
