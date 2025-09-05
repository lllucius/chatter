"""Tests for cryptography utilities."""

import base64
import os
import unittest.mock
import pytest
from cryptography.fernet import Fernet

from chatter.utils.crypto import (
    CryptoError,
    SecretManager,
    get_secret_manager,
    encrypt_secret,
    decrypt_secret,
)


class TestSecretManager:
    """Test SecretManager functionality."""

    def test_init_with_key(self):
        """Test initialization with provided key."""
        key = Fernet.generate_key().decode()
        manager = SecretManager(key=key)
        assert manager._key == key.encode()

    def test_init_with_invalid_key(self):
        """Test initialization with invalid key raises error."""
        with pytest.raises(CryptoError, match="Failed to initialize encryption"):
            SecretManager(key="invalid-key")

    def test_init_without_key_uses_environment(self):
        """Test initialization without key uses environment variables."""
        test_key = Fernet.generate_key().decode()
        with unittest.mock.patch.dict(os.environ, {"CHATTER_ENCRYPTION_KEY": test_key}):
            manager = SecretManager()
            assert manager._key == test_key.encode()

    def test_init_without_key_derives_from_password(self):
        """Test initialization derives key from password when no env key."""
        with unittest.mock.patch.dict(os.environ, {
            "CHATTER_ENCRYPTION_KEY": "",
            "CHATTER_SECRET_PASSWORD": "test-password",
            "CHATTER_SECRET_SALT": "test-salt"
        }, clear=True):
            manager = SecretManager()
            # Should successfully initialize with derived key
            assert manager._key is not None

    def test_encrypt_decrypt_string(self):
        """Test basic string encryption and decryption."""
        manager = SecretManager()
        test_data = "sensitive information"
        
        encrypted = manager.encrypt(test_data)
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == test_data
        assert encrypted != test_data
        assert isinstance(encrypted, str)

    def test_encrypt_empty_string(self):
        """Test encrypting empty string."""
        manager = SecretManager()
        encrypted = manager.encrypt("")
        decrypted = manager.decrypt(encrypted)
        assert decrypted == ""

    def test_encrypt_unicode_string(self):
        """Test encrypting unicode string."""
        manager = SecretManager()
        test_data = "unicode: 🔒🔑 密码 пароль"
        
        encrypted = manager.encrypt(test_data)
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == test_data

    def test_decrypt_invalid_data_raises_error(self):
        """Test decrypting invalid data raises CryptoError."""
        manager = SecretManager()
        with pytest.raises(CryptoError, match="Failed to decrypt data"):
            manager.decrypt("invalid-encrypted-data")

    def test_encrypt_with_different_managers_incompatible(self):
        """Test that data encrypted with one manager can't be decrypted with another."""
        # Create managers with different keys
        key1 = Fernet.generate_key().decode()
        key2 = Fernet.generate_key().decode()
        
        manager1 = SecretManager(key=key1)
        manager2 = SecretManager(key=key2)
        
        test_data = "secret data"
        encrypted = manager1.encrypt(test_data)
        
        with pytest.raises(CryptoError, match="Failed to decrypt data"):
            manager2.decrypt(encrypted)

    def test_encrypt_dict_with_sensitive_fields(self):
        """Test encrypting dictionary with sensitive fields."""
        manager = SecretManager()
        data = {
            "username": "testuser",
            "password": "secret123",
            "api_key": "abc123",
            "client_secret": "xyz789",
            "normal_field": "not_sensitive",
            "oauth_token": "token123",
        }
        
        encrypted_data = manager.encrypt_dict(data)
        
        # Check that sensitive fields are encrypted
        assert encrypted_data["password"] != "secret123"
        assert encrypted_data["password_encrypted"] is True
        assert encrypted_data["api_key"] != "abc123"
        assert encrypted_data["api_key_encrypted"] is True
        assert encrypted_data["client_secret"] != "xyz789"
        assert encrypted_data["client_secret_encrypted"] is True
        
        # Check that non-sensitive fields are not encrypted
        assert encrypted_data["username"] == "testuser"
        assert encrypted_data["normal_field"] == "not_sensitive"
        assert "username_encrypted" not in encrypted_data

    def test_decrypt_dict_with_encrypted_fields(self):
        """Test decrypting dictionary with encrypted fields."""
        manager = SecretManager()
        original_data = {
            "username": "testuser",
            "password": "secret123",
            "api_key": "abc123",
            "normal_field": "not_sensitive",
        }
        
        encrypted_data = manager.encrypt_dict(original_data)
        decrypted_data = manager.decrypt_dict(encrypted_data)
        
        # Should restore original data
        assert decrypted_data["username"] == "testuser"
        assert decrypted_data["password"] == "secret123"
        assert decrypted_data["api_key"] == "abc123"
        assert decrypted_data["normal_field"] == "not_sensitive"
        
        # Encryption markers should not be in final result
        assert "password_encrypted" not in decrypted_data
        assert "api_key_encrypted" not in decrypted_data

    def test_encrypt_decrypt_dict_preserves_non_string_values(self):
        """Test that non-string values are preserved in dict operations."""
        manager = SecretManager()
        data = {
            "username": "testuser",
            "password": "secret123",
            "count": 42,
            "active": True,
            "metadata": {"nested": "data"},
            "tags": ["tag1", "tag2"]
        }
        
        encrypted_data = manager.encrypt_dict(data)
        decrypted_data = manager.decrypt_dict(encrypted_data)
        
        assert decrypted_data["count"] == 42
        assert decrypted_data["active"] is True
        assert decrypted_data["metadata"] == {"nested": "data"}
        assert decrypted_data["tags"] == ["tag1", "tag2"]

    def test_encrypt_dict_case_insensitive_field_detection(self):
        """Test that sensitive field detection is case-insensitive."""
        manager = SecretManager()
        data = {
            "PASSWORD": "secret123",
            "Api_Key": "abc123",
            "CLIENT_SECRET": "xyz789",
            "AccessToken": "token123",
        }
        
        encrypted_data = manager.encrypt_dict(data)
        
        assert encrypted_data["PASSWORD"] != "secret123"
        assert encrypted_data["PASSWORD_encrypted"] is True
        assert encrypted_data["Api_Key"] != "abc123"
        assert encrypted_data["Api_Key_encrypted"] is True

    def test_decrypt_dict_with_missing_encryption_markers(self):
        """Test decrypting dict when encryption markers are missing."""
        manager = SecretManager()
        data = {
            "username": "testuser",
            "password": "plaintext_password",  # Not actually encrypted
        }
        
        decrypted_data = manager.decrypt_dict(data)
        
        # Should preserve data as-is when no encryption markers
        assert decrypted_data["username"] == "testuser"
        assert decrypted_data["password"] == "plaintext_password"


class TestGlobalSecretManager:
    """Test global secret manager functions."""

    def test_get_secret_manager_singleton(self):
        """Test that get_secret_manager returns the same instance."""
        manager1 = get_secret_manager()
        manager2 = get_secret_manager()
        assert manager1 is manager2

    def test_encrypt_secret_function(self):
        """Test the global encrypt_secret function."""
        test_data = "secret data"
        encrypted = encrypt_secret(test_data)
        decrypted = decrypt_secret(encrypted)
        
        assert decrypted == test_data
        assert encrypted != test_data

    def test_decrypt_secret_function(self):
        """Test the global decrypt_secret function."""
        manager = get_secret_manager()
        test_data = "secret data"
        encrypted = manager.encrypt(test_data)
        
        decrypted = decrypt_secret(encrypted)
        assert decrypted == test_data


class TestCryptoError:
    """Test CryptoError exception."""

    def test_crypto_error_inheritance(self):
        """Test that CryptoError inherits from Exception."""
        error = CryptoError("test message")
        assert isinstance(error, Exception)
        assert str(error) == "test message"


class TestSecurityBestPractices:
    """Test security-related behaviors."""

    def test_encrypted_data_is_not_deterministic(self):
        """Test that encrypting the same data twice produces different results."""
        manager = SecretManager()
        test_data = "sensitive data"
        
        encrypted1 = manager.encrypt(test_data)
        encrypted2 = manager.encrypt(test_data)
        
        # Should be different due to random IV/nonce
        assert encrypted1 != encrypted2
        
        # But both should decrypt to the same value
        assert manager.decrypt(encrypted1) == test_data
        assert manager.decrypt(encrypted2) == test_data

    def test_key_derivation_with_different_passwords(self):
        """Test that different passwords produce different keys."""
        with unittest.mock.patch.dict(os.environ, {
            "CHATTER_ENCRYPTION_KEY": "",
            "CHATTER_SECRET_PASSWORD": "password1",
            "CHATTER_SECRET_SALT": "salt"
        }, clear=True):
            manager1 = SecretManager()
            key1 = manager1._key

        with unittest.mock.patch.dict(os.environ, {
            "CHATTER_ENCRYPTION_KEY": "",
            "CHATTER_SECRET_PASSWORD": "password2", 
            "CHATTER_SECRET_SALT": "salt"
        }, clear=True):
            manager2 = SecretManager()
            key2 = manager2._key

        assert key1 != key2

    def test_key_derivation_with_different_salts(self):
        """Test that different salts produce different keys."""
        with unittest.mock.patch.dict(os.environ, {
            "CHATTER_ENCRYPTION_KEY": "",
            "CHATTER_SECRET_PASSWORD": "password",
            "CHATTER_SECRET_SALT": "salt1"
        }, clear=True):
            manager1 = SecretManager()
            key1 = manager1._key

        with unittest.mock.patch.dict(os.environ, {
            "CHATTER_ENCRYPTION_KEY": "",
            "CHATTER_SECRET_PASSWORD": "password",
            "CHATTER_SECRET_SALT": "salt2"
        }, clear=True):
            manager2 = SecretManager()
            key2 = manager2._key

        assert key1 != key2

    @unittest.mock.patch("chatter.utils.crypto.logger")
    def test_warning_logged_when_using_derived_key(self, mock_logger):
        """Test that a warning is logged when using derived key."""
        with unittest.mock.patch.dict(os.environ, {
            "CHATTER_ENCRYPTION_KEY": "",
            "CHATTER_SECRET_PASSWORD": "password",
            "CHATTER_SECRET_SALT": "salt"
        }, clear=True):
            SecretManager()
            
        mock_logger.warning.assert_called_once_with(
            "Using derived encryption key. Set CHATTER_ENCRYPTION_KEY in production."
        )


@pytest.mark.integration
class TestCryptoIntegration:
    """Integration tests for crypto utilities."""

    def test_full_encryption_decryption_workflow(self):
        """Test complete workflow with realistic data."""
        manager = SecretManager()
        
        # Simulate user configuration data
        user_config = {
            "user_id": "12345",
            "username": "testuser",
            "email": "test@example.com",
            "oauth_client_secret": "very_secret_oauth_key",
            "api_key": "sk-1234567890abcdef",
            "last_login": "2024-01-01T00:00:00Z",
            "preferences": {
                "theme": "dark",
                "notifications": True
            }
        }
        
        # Encrypt sensitive data
        encrypted_config = manager.encrypt_dict(user_config)
        
        # Simulate storage/retrieval
        # ...
        
        # Decrypt when needed
        decrypted_config = manager.decrypt_dict(encrypted_config)
        
        # Verify data integrity
        assert decrypted_config["user_id"] == "12345"
        assert decrypted_config["username"] == "testuser"
        assert decrypted_config["oauth_client_secret"] == "very_secret_oauth_key"
        assert decrypted_config["api_key"] == "sk-1234567890abcdef"
        assert decrypted_config["preferences"]["theme"] == "dark"

    def test_cross_manager_incompatibility_security(self):
        """Test that different managers provide security isolation."""
        key1 = Fernet.generate_key().decode()
        key2 = Fernet.generate_key().decode()
        
        manager1 = SecretManager(key=key1)
        manager2 = SecretManager(key=key2)
        
        secret_data = "highly_confidential_information"
        encrypted_by_1 = manager1.encrypt(secret_data)
        
        # Manager 2 should not be able to decrypt data encrypted by manager 1
        with pytest.raises(CryptoError):
            manager2.decrypt(encrypted_by_1)

    def test_large_data_encryption(self):
        """Test encryption of large data payloads."""
        manager = SecretManager()
        
        # Create large string (1KB)
        large_data = "x" * 1024
        
        encrypted = manager.encrypt(large_data)
        decrypted = manager.decrypt(encrypted)
        
        assert decrypted == large_data
        assert len(encrypted) > len(large_data)  # Encrypted should be larger due to encoding