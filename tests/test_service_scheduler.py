"""Tests for tool server scheduler service."""

import asyncio
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest

from chatter.models.toolserver import ServerStatus
from chatter.services.scheduler import (
    ToolServerScheduler,
)


@pytest.mark.unit
class TestToolServerScheduler:
    """Test ToolServerScheduler functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.scheduler = ToolServerScheduler()

    def test_scheduler_initialization(self):
        """Test scheduler initialization."""
        # Assert
        assert self.scheduler.running is False
        assert self.scheduler.health_check_interval == 300
        assert self.scheduler.auto_update_interval == 3600
        assert self.scheduler.cleanup_interval == 86400
        assert self.scheduler._tasks == []

    @pytest.mark.asyncio
    async def test_scheduler_start(self):
        """Test starting the scheduler."""
        # Arrange
        with patch('asyncio.create_task') as mock_create_task:
            mock_task = Mock()
            mock_create_task.return_value = mock_task

            # Act
            await self.scheduler.start()

        # Assert
        assert self.scheduler.running is True
        assert mock_create_task.call_count == 3
        assert len(self.scheduler._tasks) == 3

    @pytest.mark.asyncio
    async def test_scheduler_start_already_running(self):
        """Test starting scheduler when already running."""
        # Arrange
        self.scheduler.running = True

        with patch('asyncio.create_task') as mock_create_task:
            # Act
            await self.scheduler.start()

        # Assert
        mock_create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_scheduler_stop(self):
        """Test stopping the scheduler."""
        # Arrange
        mock_task1 = Mock()
        mock_task1.cancel = Mock()
        mock_task2 = Mock()
        mock_task2.cancel = Mock()
        mock_task3 = Mock()
        mock_task3.cancel = Mock()

        self.scheduler.running = True
        self.scheduler._tasks = [mock_task1, mock_task2, mock_task3]

        # Act
        await self.scheduler.stop()

        # Assert
        assert self.scheduler.running is False
        mock_task1.cancel.assert_called_once()
        mock_task2.cancel.assert_called_once()
        mock_task3.cancel.assert_called_once()

    @pytest.mark.asyncio
    async def test_scheduler_stop_not_running(self):
        """Test stopping scheduler when not running."""
        # Arrange
        self.scheduler.running = False
        mock_task = Mock()
        mock_task.cancel = Mock()
        self.scheduler._tasks = [mock_task]

        # Act
        await self.scheduler.stop()

        # Assert
        mock_task.cancel.assert_not_called()

    @pytest.mark.asyncio
    async def test_health_check_loop(self):
        """Test health check loop functionality."""
        # Arrange
        self.scheduler.running = True
        self.scheduler.health_check_interval = 0.1  # Fast for testing

        call_count = 0

        async def mock_perform_health_checks():
            nonlocal call_count
            call_count += 1
            if call_count >= 2:  # Stop after 2 calls
                self.scheduler.running = False

        with patch.object(
            self.scheduler,
            '_perform_health_checks',
            mock_perform_health_checks,
        ):
            # Act
            await self.scheduler._health_check_loop()

        # Assert
        assert call_count >= 2

    @pytest.mark.asyncio
    async def test_health_check_loop_exception_handling(self):
        """Test health check loop handles exceptions."""
        # Arrange
        self.scheduler.running = True
        self.scheduler.health_check_interval = 0.1

        call_count = 0

        async def mock_perform_health_checks():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Health check error")
            elif call_count >= 2:
                self.scheduler.running = False

        with patch.object(
            self.scheduler,
            '_perform_health_checks',
            mock_perform_health_checks,
        ):
            # Act
            await self.scheduler._health_check_loop()

        # Assert
        assert call_count >= 2  # Should continue after exception

    @pytest.mark.asyncio
    async def test_perform_health_checks(self):
        """Test performing health checks."""
        # Arrange
        mock_session = AsyncMock()
        mock_servers = [
            Mock(id="server1", url="http://server1.com"),
            Mock(id="server2", url="http://server2.com"),
        ]

        with patch(
            'chatter.services.scheduler.get_session_maker'
        ) as mock_get_session:
            mock_get_session.return_value.return_value.__aenter__.return_value = (
                mock_session
            )
            mock_session.execute.return_value.scalars.return_value.all.return_value = (
                mock_servers
            )

            with patch.object(
                self.scheduler, '_check_server_health'
            ) as mock_check:
                mock_check.return_value = True

                # Act
                await self.scheduler._perform_health_checks()

        # Assert
        assert mock_check.call_count == 2
        mock_check.assert_any_call(mock_session, mock_servers[0])
        mock_check.assert_any_call(mock_session, mock_servers[1])

    @pytest.mark.asyncio
    async def test_check_server_health_healthy(self):
        """Test checking healthy server."""
        # Arrange
        mock_session = AsyncMock()
        mock_server = Mock(id="server1", url="http://healthy.com")

        with patch(
            'chatter.services.scheduler.ToolServerService'
        ) as mock_service:
            mock_service_instance = Mock()
            mock_service_instance.health_check = AsyncMock(
                return_value=True
            )
            mock_service.return_value = mock_service_instance

            # Act
            result = await self.scheduler._check_server_health(
                mock_session, mock_server
            )

        # Assert
        assert result is True
        mock_service_instance.health_check.assert_called_once_with(
            mock_server.url
        )

    @pytest.mark.asyncio
    async def test_check_server_health_unhealthy(self):
        """Test checking unhealthy server."""
        # Arrange
        mock_session = AsyncMock()
        mock_server = Mock(
            id="server1",
            url="http://unhealthy.com",
            status=ServerStatus.RUNNING,
        )

        with patch(
            'chatter.services.scheduler.ToolServerService'
        ) as mock_service:
            mock_service_instance = Mock()
            mock_service_instance.health_check = AsyncMock(
                return_value=False
            )
            mock_service.return_value = mock_service_instance

            # Act
            result = await self.scheduler._check_server_health(
                mock_session, mock_server
            )

        # Assert
        assert result is False
        mock_service_instance.health_check.assert_called_once_with(
            mock_server.url
        )
        assert mock_server.status == ServerStatus.UNHEALTHY

    @pytest.mark.asyncio
    async def test_auto_update_loop(self):
        """Test auto update loop functionality."""
        # Arrange
        self.scheduler.running = True
        self.scheduler.auto_update_interval = 0.1

        call_count = 0

        async def mock_perform_auto_updates():
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                self.scheduler.running = False

        with patch.object(
            self.scheduler,
            '_perform_auto_updates',
            mock_perform_auto_updates,
        ):
            # Act
            await self.scheduler._auto_update_loop()

        # Assert
        assert call_count >= 2

    @pytest.mark.asyncio
    async def test_perform_auto_updates(self):
        """Test performing auto updates."""
        # Arrange
        mock_session = AsyncMock()
        outdated_server = Mock(
            id="server1",
            url="http://server1.com",
            auto_update=True,
            last_update=datetime.now(UTC) - timedelta(hours=25),
        )

        with patch(
            'chatter.services.scheduler.get_session_maker'
        ) as mock_get_session:
            mock_get_session.return_value.return_value.__aenter__.return_value = (
                mock_session
            )
            mock_session.execute.return_value.scalars.return_value.all.return_value = [
                outdated_server
            ]

            with patch.object(
                self.scheduler, '_update_server'
            ) as mock_update:
                mock_update.return_value = True

                # Act
                await self.scheduler._perform_auto_updates()

        # Assert
        mock_update.assert_called_once_with(
            mock_session, outdated_server
        )

    @pytest.mark.asyncio
    async def test_cleanup_loop(self):
        """Test cleanup loop functionality."""
        # Arrange
        self.scheduler.running = True
        self.scheduler.cleanup_interval = 0.1

        call_count = 0

        async def mock_perform_cleanup():
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                self.scheduler.running = False

        with patch.object(
            self.scheduler, '_perform_cleanup', mock_perform_cleanup
        ):
            # Act
            await self.scheduler._cleanup_loop()

        # Assert
        assert call_count >= 2

    @pytest.mark.asyncio
    async def test_perform_cleanup(self):
        """Test performing cleanup."""
        # Arrange
        mock_session = AsyncMock()
        old_server = Mock(
            id="server1",
            created_at=datetime.now(UTC) - timedelta(days=8),
            status=ServerStatus.STOPPED,
        )

        with patch(
            'chatter.services.scheduler.get_session_maker'
        ) as mock_get_session:
            mock_get_session.return_value.return_value.__aenter__.return_value = (
                mock_session
            )
            mock_session.execute.return_value.scalars.return_value.all.return_value = [
                old_server
            ]

            # Act
            await self.scheduler._perform_cleanup()

        # Assert
        mock_session.delete.assert_called_once_with(old_server)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_server_success(self):
        """Test successful server update."""
        # Arrange
        mock_session = AsyncMock()
        mock_server = Mock(id="server1", url="http://server1.com")

        with patch(
            'chatter.services.scheduler.ToolServerService'
        ) as mock_service:
            mock_service_instance = Mock()
            mock_service_instance.update_server = AsyncMock(
                return_value=True
            )
            mock_service.return_value = mock_service_instance

            # Act
            result = await self.scheduler._update_server(
                mock_session, mock_server
            )

        # Assert
        assert result is True
        mock_service_instance.update_server.assert_called_once_with(
            mock_server.url
        )

    @pytest.mark.asyncio
    async def test_update_server_failure(self):
        """Test failed server update."""
        # Arrange
        mock_session = AsyncMock()
        mock_server = Mock(id="server1", url="http://server1.com")

        with patch(
            'chatter.services.scheduler.ToolServerService'
        ) as mock_service:
            mock_service_instance = Mock()
            mock_service_instance.update_server = AsyncMock(
                side_effect=Exception("Update failed")
            )
            mock_service.return_value = mock_service_instance

            # Act
            result = await self.scheduler._update_server(
                mock_session, mock_server
            )

        # Assert
        assert result is False


@pytest.mark.integration
class TestSchedulerIntegration:
    """Integration tests for scheduler."""

    @pytest.mark.asyncio
    async def test_scheduler_lifecycle(self):
        """Test complete scheduler lifecycle."""
        # Arrange
        test_scheduler = ToolServerScheduler()
        test_scheduler.health_check_interval = 0.1
        test_scheduler.auto_update_interval = 0.1
        test_scheduler.cleanup_interval = 0.1

        # Act
        await test_scheduler.start()
        assert test_scheduler.running is True

        # Let it run briefly
        await asyncio.sleep(0.2)

        await test_scheduler.stop()
        assert test_scheduler.running is False

    def test_global_scheduler_instance(self):
        """Test global scheduler instance."""
        # Act
        global_scheduler = scheduler

        # Assert
        assert global_scheduler is not None
        assert isinstance(global_scheduler, ToolServerScheduler)

    @pytest.mark.asyncio
    async def test_scheduler_error_recovery(self):
        """Test scheduler recovers from errors."""
        # Arrange
        test_scheduler = ToolServerScheduler()
        test_scheduler.health_check_interval = 0.1

        error_count = 0
        original_method = test_scheduler._perform_health_checks

        async def failing_health_checks():
            nonlocal error_count
            error_count += 1
            if error_count <= 2:
                raise Exception(f"Simulated error {error_count}")
            else:
                test_scheduler.running = False

        test_scheduler._perform_health_checks = failing_health_checks

        # Act
        await test_scheduler.start()

        # Let it run and encounter errors
        await asyncio.sleep(0.5)

        await test_scheduler.stop()

        # Assert
        assert error_count >= 3  # Should have retried after errors

    @pytest.mark.asyncio
    async def test_concurrent_scheduler_operations(self):
        """Test concurrent scheduler operations."""
        # Arrange
        test_scheduler = ToolServerScheduler()
        test_scheduler.health_check_interval = 0.1
        test_scheduler.auto_update_interval = 0.1
        test_scheduler.cleanup_interval = 0.1

        # Act
        # Start scheduler multiple times concurrently
        await asyncio.gather(
            test_scheduler.start(),
            test_scheduler.start(),
            test_scheduler.start(),
        )

        # Assert
        assert test_scheduler.running is True
        assert (
            len(test_scheduler._tasks) == 3
        )  # Should only create tasks once

        # Cleanup
        await test_scheduler.stop()


@pytest.mark.unit
class TestSchedulerUtilities:
    """Test scheduler utility functions."""

    def test_scheduler_configuration(self):
        """Test scheduler configuration options."""
        # Arrange & Act
        scheduler = ToolServerScheduler()

        # Assert
        assert scheduler.health_check_interval > 0
        assert scheduler.auto_update_interval > 0
        assert scheduler.cleanup_interval > 0
        assert (
            scheduler.health_check_interval
            < scheduler.auto_update_interval
        )
        assert (
            scheduler.auto_update_interval < scheduler.cleanup_interval
        )

    def test_scheduler_interval_customization(self):
        """Test customizing scheduler intervals."""
        # Arrange
        scheduler = ToolServerScheduler()

        # Act
        scheduler.health_check_interval = 60
        scheduler.auto_update_interval = 1800
        scheduler.cleanup_interval = 43200

        # Assert
        assert scheduler.health_check_interval == 60
        assert scheduler.auto_update_interval == 1800
        assert scheduler.cleanup_interval == 43200

    def test_scheduler_task_management(self):
        """Test scheduler task management."""
        # Arrange
        scheduler = ToolServerScheduler()

        # Act & Assert
        assert len(scheduler._tasks) == 0
        assert scheduler.running is False

        # Simulate adding tasks
        mock_task = Mock()
        scheduler._tasks.append(mock_task)
        assert len(scheduler._tasks) == 1
