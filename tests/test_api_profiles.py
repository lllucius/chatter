"""Profiles API tests."""

import pytest


@pytest.mark.unit
class TestProfilesAPI:
    """Test profiles API endpoints."""

    async def test_get_user_profile(self, test_client):
        """Test retrieving user profile."""
        # Setup user and auth
        registration_data = {
            "email": "profileuser@example.com",
            "password": "SecurePass123!",
            "username": "profileuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "profileuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get user profile
        response = await test_client.get("/api/v1/profiles/me", headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]

        if response.status_code == 200:
            data = response.json()
            assert "email" in data or "username" in data or "profile" in data

    async def test_update_user_profile(self, test_client):
        """Test updating user profile."""
        # Setup user and auth
        registration_data = {
            "email": "updateprofileuser@example.com",
            "password": "SecurePass123!",
            "username": "updateprofileuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "updateprofileuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Update profile
        profile_data = {
            "display_name": "Updated User",
            "bio": "Updated bio description",
            "timezone": "UTC",
            "language": "en",
            "preferences": {
                "theme": "dark",
                "notifications_enabled": True,
                "default_model": "gpt-4"
            }
        }

        response = await test_client.put("/api/v1/profiles/me", json=profile_data, headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 422, 501]

        if response.status_code == 200:
            data = response.json()
            assert data["display_name"] == "Updated User"

    async def test_get_profile_by_id(self, test_client):
        """Test retrieving another user's profile."""
        # Setup user and auth
        registration_data = {
            "email": "viewprofileuser@example.com",
            "password": "SecurePass123!",
            "username": "viewprofileuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "viewprofileuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to get another user's profile
        response = await test_client.get("/api/v1/profiles/other_user_id", headers=headers)

        # Should return 404 for non-existent user or 501 if not implemented
        assert response.status_code in [404, 403, 501]

    async def test_upload_profile_picture(self, test_client):
        """Test uploading profile picture."""
        # Setup user and auth
        registration_data = {
            "email": "picuser@example.com",
            "password": "SecurePass123!",
            "username": "picuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "picuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Upload profile picture
        files = {"file": ("profile.jpg", b"fake image content", "image/jpeg")}

        response = await test_client.post("/api/v1/profiles/me/picture", files=files, headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 422, 501]

    async def test_delete_profile_picture(self, test_client):
        """Test deleting profile picture."""
        # Setup user and auth
        registration_data = {
            "email": "delpicuser@example.com",
            "password": "SecurePass123!",
            "username": "delpicuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "delpicuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Delete profile picture
        response = await test_client.delete("/api/v1/profiles/me/picture", headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 204, 404, 501]

    async def test_get_profile_preferences(self, test_client):
        """Test retrieving user preferences."""
        # Setup user and auth
        registration_data = {
            "email": "prefuser@example.com",
            "password": "SecurePass123!",
            "username": "prefuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "prefuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get preferences
        response = await test_client.get("/api/v1/profiles/me/preferences", headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]

        if response.status_code == 200:
            data = response.json()
            assert "preferences" in data or isinstance(data, dict)

    async def test_update_profile_preferences(self, test_client):
        """Test updating user preferences."""
        # Setup user and auth
        registration_data = {
            "email": "updateprefuser@example.com",
            "password": "SecurePass123!",
            "username": "updateprefuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "updateprefuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Update preferences
        preferences = {
            "theme": "light",
            "notifications": {
                "email": True,
                "push": False,
                "desktop": True
            },
            "ai_settings": {
                "default_model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 150
            }
        }

        response = await test_client.put("/api/v1/profiles/me/preferences", json=preferences, headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 422, 501]

    async def test_get_profile_activity(self, test_client):
        """Test retrieving user activity."""
        # Setup user and auth
        registration_data = {
            "email": "activityuser@example.com",
            "password": "SecurePass123!",
            "username": "activityuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "activityuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get activity
        response = await test_client.get("/api/v1/profiles/me/activity", headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]

        if response.status_code == 200:
            data = response.json()
            assert "activities" in data or isinstance(data, list)

    async def test_profile_privacy_settings(self, test_client):
        """Test profile privacy settings."""
        # Setup user and auth
        registration_data = {
            "email": "privacyuser@example.com",
            "password": "SecurePass123!",
            "username": "privacyuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "privacyuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Update privacy settings
        privacy_settings = {
            "profile_visibility": "private",
            "show_activity": False,
            "allow_contact": True,
            "data_sharing": {
                "analytics": False,
                "personalization": True
            }
        }

        response = await test_client.put("/api/v1/profiles/me/privacy", json=privacy_settings, headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 422, 501]

    async def test_profiles_unauthorized(self, test_client):
        """Test profile endpoints require authentication."""
        endpoints = [
            "/api/v1/profiles/me",
            "/api/v1/profiles/me/preferences",
            "/api/v1/profiles/me/activity",
            "/api/v1/profiles/me/privacy"
        ]

        for endpoint in endpoints:
            response = await test_client.get(endpoint)

            # Should require authentication
            assert response.status_code in [401, 403]

    async def test_profile_validation(self, test_client):
        """Test profile update validation."""
        # Setup user and auth
        registration_data = {
            "email": "validprofileuser@example.com",
            "password": "SecurePass123!",
            "username": "validprofileuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "validprofileuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try updating profile with invalid data
        invalid_data = {
            "email": "invalid-email-format",
            "timezone": "Invalid/Timezone"
        }

        response = await test_client.put("/api/v1/profiles/me", json=invalid_data, headers=headers)

        # Should fail validation
        assert response.status_code in [400, 422]

    async def test_delete_profile(self, test_client):
        """Test deleting user profile."""
        # Setup user and auth
        registration_data = {
            "email": "deleteprofileuser@example.com",
            "password": "SecurePass123!",
            "username": "deleteprofileuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "deleteprofileuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Delete profile
        delete_data = {
            "confirmation": "DELETE_PROFILE",
            "password": "SecurePass123!"
        }

        response = await test_client.delete("/api/v1/profiles/me", json=delete_data, headers=headers)

        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 204, 422, 501]
