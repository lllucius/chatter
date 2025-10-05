"""Test SDK Configuration for API key authentication.

This test verifies that the SDK Configuration class properly handles
API key authentication using the access_token parameter.
"""

import sys

# Add SDK to path
sys.path.insert(0, '/home/runner/work/chatter/chatter/sdk/python')

from chatter_sdk import Configuration


def test_configuration_with_access_token():
    """Test that Configuration properly handles access_token for API key auth.
    
    This is the correct way to configure the SDK for API key authentication.
    The access_token parameter should be used to pass the API key.
    """
    api_key = "sk_test_abc123"
    config = Configuration(
        host="http://localhost:8000",
        access_token=api_key
    )
    
    # Get auth settings
    auth_settings = config.auth_settings()
    
    # Verify CustomHTTPBearer is present
    assert "CustomHTTPBearer" in auth_settings, \
        "CustomHTTPBearer should be present in auth_settings when access_token is set"
    
    # Verify the auth setting structure
    bearer_setting = auth_settings["CustomHTTPBearer"]
    assert bearer_setting["type"] == "bearer"
    assert bearer_setting["in"] == "header"
    assert bearer_setting["key"] == "Authorization"
    assert bearer_setting["value"] == f"Bearer {api_key}"
    
    print("✅ Configuration with access_token works correctly")


def test_configuration_with_api_key_dict_does_not_work():
    """Test that using api_key dict parameter does not work for bearer auth.
    
    This test documents that the api_key parameter (which accepts a dict)
    is NOT the correct way to configure API key authentication.
    It is only used for API key authentication schemes (not bearer tokens).
    """
    api_key = "sk_test_xyz789"
    config = Configuration(
        host="http://localhost:8000",
        api_key={"HTTPBearer": api_key}
    )
    
    # Get auth settings
    auth_settings = config.auth_settings()
    
    # Verify CustomHTTPBearer is NOT present (because access_token is not set)
    assert "CustomHTTPBearer" not in auth_settings, \
        "CustomHTTPBearer should NOT be present when only api_key dict is set"
    
    # Verify auth_settings is empty
    assert len(auth_settings) == 0, \
        "Auth settings should be empty when only api_key dict is set"
    
    print("✅ Configuration with api_key dict does not create bearer auth (as expected)")


def test_configuration_access_token_property():
    """Test that access_token can be set via property after initialization."""
    config = Configuration(host="http://localhost:8000")
    
    # Initially, auth_settings should be empty
    auth_settings = config.auth_settings()
    assert "CustomHTTPBearer" not in auth_settings
    
    # Set access_token via property
    api_key = "sk_test_property_set"
    config.access_token = api_key
    
    # Now auth_settings should include CustomHTTPBearer
    auth_settings = config.auth_settings()
    assert "CustomHTTPBearer" in auth_settings
    assert auth_settings["CustomHTTPBearer"]["value"] == f"Bearer {api_key}"
    
    print("✅ Setting access_token via property works correctly")


if __name__ == "__main__":
    test_configuration_with_access_token()
    test_configuration_with_api_key_dict_does_not_work()
    test_configuration_access_token_property()
    print("\n✅ All SDK configuration tests passed!")
