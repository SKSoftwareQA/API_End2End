import pytest
from playwright.sync_api import Playwright, APIRequestContext
import json
from datetime import datetime
import random

# Constants
BASE_URL = "https://gorest.co.in"
AUTH_TOKEN = "b0c9a5f84c72ad9b0dc9097d47b86b4be872a0e2867a9f61615b060d33fbd1f4"

# Fixtures
@pytest.fixture(scope="session")
def api_context(playwright: Playwright) -> APIRequestContext:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    request_context = playwright.request.new_context(
        base_url=BASE_URL,
        extra_http_headers=headers
    )
    yield request_context
    request_context.dispose()

@pytest.fixture(scope="class")
def user_data():
    class UserData:
        user_id = None
        user_email = None
        user_name = None
    return UserData()

def generate_unique_email():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"user{timestamp}@example.com"

def generate_random_name():
    first_names = ["John", "Jane", "Michael", "Emma", "David"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

class TestGoRestAPI:
    def test_01_create_user(self, api_context: APIRequestContext, user_data):
        """Test creating a new user"""
        payload = {
            "name": generate_random_name(),
            "gender": "male",
            "email": generate_unique_email(),
            "status": "active"
        }

        response = api_context.post(
            "/public/v2/users",
            data=json.dumps(payload)
        )

        assert response.status == 201, f"Failed to create user. Response: {response.text()}"
        response_data = response.json()

        # Store user data for subsequent tests
        user_data.user_id = response_data["id"]
        user_data.user_email = response_data["email"]
        user_data.user_name = response_data["name"]

        # Verify response data
        assert response_data["name"] == payload["name"]
        assert response_data["email"] == payload["email"]
        assert response_data["gender"] == payload["gender"]
        assert response_data["status"] == payload["status"]

    def test_02_get_user(self, api_context: APIRequestContext, user_data):
        """Test retrieving user details"""
        response = api_context.get(f"/public/v2/users", params={"id": user_data.user_id})
        assert response.status == 200, f"Failed to get user. Response: {response.text()}"

        users = response.json()
        user = next((u for u in users if u["id"] == user_data.user_id), None)
        assert user is not None, "User not found"
        assert user["email"] == user_data.user_email
        assert user["name"] == user_data.user_name

    def test_03_update_user(self, api_context: APIRequestContext, user_data):
        """Test updating user details"""
        new_name = generate_random_name()
        new_email = generate_unique_email()
        
        response = api_context.patch(
            f"/public/v2/users/{user_data.user_id}",
            params={
                "name": new_name,
                "email": new_email
            },
            data=json.dumps({"status": "active"})
        )
        assert response.status == 200, f"Failed to update user. Response: {response.text()}"

        response_data = response.json()
        user_data.user_name = response_data["name"]
        user_data.user_email = response_data["email"]

    def test_04_verify_update(self, api_context: APIRequestContext, user_data):
        """Test verifying user update"""
        response = api_context.get(f"/public/v2/users", params={"id": user_data.user_id})
        assert response.status == 200, f"Failed to verify user update. Response: {response.text()}"

        users = response.json()
        user = next((u for u in users if u["id"] == user_data.user_id), None)
        assert user is not None, "Updated user not found"
        assert user["name"] == user_data.user_name
        assert user["email"] == user_data.user_email

    def test_05_delete_user(self, api_context: APIRequestContext, user_data):
        """Test deleting user"""
        response = api_context.delete(f"/public/v2/users/{user_data.user_id}")
        assert response.status == 204, f"Failed to delete user. Response: {response.text()}"

    def test_06_verify_deletion(self, api_context: APIRequestContext, user_data):
        """Test verifying user deletion"""
        response = api_context.get(f"/public/v2/users", params={"id": user_data.user_id})
        assert response.status == 200, "Failed to verify user deletion"
        users = response.json()
        assert len(users) == 0, "User still exists after deletion"

    @pytest.mark.parametrize("invalid_payload", [
        {
            "name": "",
            "gender": "male",
            "email": "invalid_email",
            "status": "active"
        },
        {
            "name": "Test User",
            "gender": "invalid",
            "email": generate_unique_email(),
            "status": "active"
        },
        {
            "name": "Test User",
            "gender": "male",
            "status": "active"
            # Missing email
        }
    ])
    def test_07_negative_scenarios(self, api_context: APIRequestContext, invalid_payload):
        """Test negative scenarios with invalid data"""
        response = api_context.post(
            "/public/v2/users",
            data=json.dumps(invalid_payload)
        )
        assert response.status in [400, 422], f"Expected error status code. Response: {response.text()}"