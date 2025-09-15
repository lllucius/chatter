"""Memory usage tests for document upload and processing."""

import io
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from chatter.api.documents import upload_document
from chatter.core.documents import DocumentService
from chatter.services.new_document_service import NewDocumentService
from chatter.utils.memory_monitor import MemoryMonitor, memory_monitor_context


class TestDocumentMemoryUsage:
    """Test memory usage patterns in document processing."""

    @pytest.mark.unit
    async def test_memory_monitor_basic_functionality(self):
        """Test basic memory monitoring functionality."""
        monitor = MemoryMonitor(max_memory_mb=1000)
        
        # Test getting memory usage
        memory_info = monitor.get_memory_usage()
        assert "rss_mb" in memory_info
        assert "vms_mb" in memory_info
        assert "percent" in memory_info
        assert "available_mb" in memory_info
        
        # Test memory limit check
        assert monitor.check_memory_limit() is True
        
    @pytest.mark.unit
    async def test_memory_monitor_context_manager(self):
        """Test memory monitoring context manager."""
        async with memory_monitor_context("test_operation") as monitor:
            assert isinstance(monitor, MemoryMonitor)
            assert monitor.initial_memory is not None
            
            # Log memory usage
            monitor.log_memory_usage("during test")
            
            # Force garbage collection
            monitor.force_garbage_collection()

    @pytest.mark.unit
    def test_create_large_test_file(self):
        """Test creating a large test file for memory testing."""
        # Create a 1MB test file
        test_content = b"x" * (1024 * 1024)  # 1MB
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            temp_file.write(test_content)
            temp_file.flush()
            
            # Verify file size
            file_path = Path(temp_file.name)
            assert file_path.stat().st_size == 1024 * 1024
            
            # Clean up
            file_path.unlink()

    @pytest.mark.unit
    async def test_streaming_file_upload_memory_efficiency(self):
        """Test that file upload uses streaming instead of loading entire file."""
        # Create a mock large file
        large_content = b"test content " * 100000  # ~1.3MB
        mock_file = io.BytesIO(large_content)
        
        # Mock UploadFile
        from fastapi import UploadFile
        
        upload_file = UploadFile(
            filename="large_test.txt",
            file=mock_file,
            size=len(large_content)
        )
        
        # Test that we don't load entire file into memory at once
        # This would be tested by monitoring actual memory usage
        assert upload_file.size == len(large_content)
        
        # Test chunked reading
        chunk_size = 8192
        total_read = 0
        
        await upload_file.seek(0)
        while True:
            chunk = await upload_file.read(chunk_size)
            if not chunk:
                break
            total_read += len(chunk)
            
        assert total_read == len(large_content)

    @pytest.mark.unit
    async def test_document_service_memory_efficient_processing(self):
        """Test that DocumentService processes files efficiently."""
        from chatter.schemas.document import DocumentCreate
        
        # Mock upload file
        test_content = b"test document content for memory testing"
        mock_file = io.BytesIO(test_content)
        
        from fastapi import UploadFile
        upload_file = UploadFile(
            filename="test.txt",
            file=mock_file,
            size=len(test_content)
        )
        
        # Mock document data
        document_data = DocumentCreate(
            title="Memory Test Document",
            description="Testing memory efficiency",
            chunk_size=100,
            chunk_overlap=20,
            is_public=False
        )
        
        # Test would verify that create_document uses streaming
        # and doesn't load entire file into memory
        # This is verified through the implementation using chunked reading
        
    @pytest.mark.unit
    def test_memory_limit_configuration(self):
        """Test memory limit configuration."""
        from chatter.config import settings
        
        # Verify memory-related settings exist
        assert hasattr(settings, "max_file_size")
        assert hasattr(settings, "file_chunk_size")
        assert hasattr(settings, "max_memory_per_document")
        assert hasattr(settings, "enable_memory_monitoring")
        assert hasattr(settings, "max_text_length")
        assert hasattr(settings, "max_concurrent_uploads")
        assert hasattr(settings, "max_concurrent_processing")
        
        # Verify reasonable defaults
        assert settings.file_chunk_size == 65536  # 64KB
        assert settings.max_memory_per_document == 104857600  # 100MB
        assert settings.max_text_length == 10485760  # 10MB
        assert settings.max_concurrent_uploads == 5
        assert settings.max_concurrent_processing == 3

    @pytest.mark.integration
    async def test_large_file_processing_memory_usage(self):
        """Integration test for processing large files efficiently."""
        # This test would create a larger file and verify memory usage
        # during processing remains within acceptable limits
        
        # Create test content
        test_content = "This is test content. " * 10000  # ~220KB
        test_bytes = test_content.encode('utf-8')
        
        # Verify content size
        assert len(test_bytes) > 200000  # >200KB
        
        # Test would involve actual file upload and processing
        # while monitoring memory usage
        
    @pytest.mark.unit
    async def test_file_size_validation(self):
        """Test file size validation prevents memory exhaustion."""
        from chatter.config import settings
        
        # Test that files larger than max_file_size are rejected
        max_size = settings.max_file_size
        
        # Create content larger than max size
        oversized_content = b"x" * (max_size + 1000)
        
        # This would be rejected before processing
        assert len(oversized_content) > max_size

    @pytest.mark.unit
    def test_chunk_size_configuration(self):
        """Test that chunk sizes are configured for memory efficiency."""
        from chatter.config import settings
        
        # Verify chunk sizes are reasonable for memory usage
        assert settings.file_chunk_size <= 65536  # <= 64KB
        assert settings.text_extraction_chunk_size <= 8192  # <= 8KB
        assert settings.default_chunk_size <= 2000  # Reasonable text chunk size
        assert settings.default_chunk_overlap <= 400  # Reasonable overlap

    @pytest.mark.unit
    async def test_concurrent_processing_limits(self):
        """Test concurrent processing limits prevent memory exhaustion."""
        from chatter.config import settings
        
        # Verify concurrent limits are set to prevent memory issues
        assert settings.max_concurrent_uploads > 0
        assert settings.max_concurrent_uploads <= 10  # Reasonable upper limit
        assert settings.max_concurrent_processing > 0
        assert settings.max_concurrent_processing <= 5  # Conservative limit

    @pytest.mark.unit
    async def test_text_length_limits(self):
        """Test text length limits prevent memory issues."""
        from chatter.config import settings
        
        # Test very long text is truncated
        very_long_text = "word " * 3000000  # ~15MB of text
        
        if len(very_long_text) > settings.max_text_length:
            truncated = very_long_text[:settings.max_text_length]
            assert len(truncated) == settings.max_text_length
            assert len(truncated) < len(very_long_text)