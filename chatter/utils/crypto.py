"""Cryptography utilities for secure data handling."""

import base64
import os
from typing import Any

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class CryptoError(Exception):
    """Cryptography related error."""
    pass


class SecretManager:
    """Manager for encrypting and decrypting sensitive data."""
    
    def __init__(self, key: str | None = None):
        """Initialize with encryption key.
        
        Args:
            key: Base64 encoded encryption key. If None, generates from environment.
        """
        if key is None:
            key = self._get_or_generate_key()
        
        try:
            self._key = key.encode() if isinstance(key, str) else key
            self._fernet = Fernet(self._key)
        except Exception as e:
            raise CryptoError(f"Failed to initialize encryption: {e}") from e
    
    def _get_or_generate_key(self) -> str:
        """Get encryption key from environment or generate new one."""
        # Try to get from environment
        env_key = os.environ.get("CHATTER_ENCRYPTION_KEY")
        if env_key:
            return env_key
        
        # Generate from password + salt
        password = os.environ.get("CHATTER_SECRET_PASSWORD", "default-dev-password").encode()
        salt = os.environ.get("CHATTER_SECRET_SALT", "default-dev-salt").encode()
        
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        
        logger.warning(
            "Using derived encryption key. Set CHATTER_ENCRYPTION_KEY in production."
        )
        return key.decode()
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data.
        
        Args:
            data: String to encrypt
            
        Returns:
            Base64 encoded encrypted data
        """
        try:
            encrypted = self._fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            raise CryptoError(f"Failed to encrypt data: {e}") from e
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data.
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            
        Returns:
            Decrypted string
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self._fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            raise CryptoError(f"Failed to decrypt data: {e}") from e
    
    def encrypt_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Encrypt sensitive fields in a dictionary.
        
        Args:
            data: Dictionary with potential sensitive fields
            
        Returns:
            Dictionary with sensitive fields encrypted
        """
        sensitive_fields = {
            'password', 'secret', 'token', 'key', 'client_secret',
            'oauth_client_secret', 'api_key', 'access_token', 'refresh_token'
        }
        
        result = {}
        for key, value in data.items():
            if isinstance(value, str) and any(field in key.lower() for field in sensitive_fields):
                result[key] = self.encrypt(value)
                result[f"{key}_encrypted"] = True
            else:
                result[key] = value
                
        return result
    
    def decrypt_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Decrypt sensitive fields in a dictionary.
        
        Args:
            data: Dictionary with encrypted sensitive fields
            
        Returns:
            Dictionary with sensitive fields decrypted
        """
        result = {}
        for key, value in data.items():
            if key.endswith('_encrypted'):
                continue  # Skip encryption markers
                
            encryption_marker = f"{key}_encrypted"
            if encryption_marker in data and data[encryption_marker]:
                if isinstance(value, str):
                    result[key] = self.decrypt(value)
                else:
                    result[key] = value
            else:
                result[key] = value
                
        return result


# Global instance
_secret_manager: SecretManager | None = None


def get_secret_manager() -> SecretManager:
    """Get global secret manager instance."""
    global _secret_manager
    if _secret_manager is None:
        _secret_manager = SecretManager()
    return _secret_manager


def encrypt_secret(data: str) -> str:
    """Encrypt a secret string."""
    return get_secret_manager().encrypt(data)


def decrypt_secret(encrypted_data: str) -> str:
    """Decrypt a secret string."""
    return get_secret_manager().decrypt(encrypted_data)