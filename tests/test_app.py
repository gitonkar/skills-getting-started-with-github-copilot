import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesAPI:
    """Test suite for the Mergington High School Activities API"""

    def test_get_activities_success(self):
        """Test GET /activities returns all activities with correct structure"""
        # Arrange - No special setup needed for this endpoint

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0  # Should have pre-loaded activities

        # Check structure of first activity
        first_activity = next(iter(activities.values()))
        assert "description" in first_activity
        assert "schedule" in first_activity
        assert "max_participants" in first_activity
        assert "participants" in first_activity
        assert isinstance(first_activity["participants"], list)

    def test_post_signup_success(self):
        """Test successful signup for an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "test@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert f"Signed up {email} for {activity_name}" in result["message"]

    def test_post_signup_activity_not_found(self):
        """Test signup for non-existent activity returns 404"""
        # Arrange
        activity_name = "NonExistentActivity"
        email = "test@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]

    def test_post_signup_duplicate(self):
        """Test duplicate signup returns 400"""
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Already signed up

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "Student already signed up" in result["detail"]

    def test_post_signup_activity_full(self):
        """Test signup when activity is full returns 400"""
        # Arrange - Need to fill an activity first
        activity_name = "Gym Class"
        # Gym Class has max 30, currently 2 participants
        emails = [f"student{i}@mergington.edu" for i in range(28)]  # Add 28 more to fill

        # Fill the activity
        for email in emails:
            client.post(f"/activities/{activity_name}/signup?email={email}")

        # Now try to add one more
        email = "last@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "Activity is full" in result["detail"]

    def test_delete_signup_success(self):
        """Test successful unregister from an activity"""
        # Arrange
        activity_name = "Art Club"
        email = "isabella@mergington.edu"  # Already signed up

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert f"Unregistered {email} from {activity_name}" in result["message"]

    def test_delete_signup_activity_not_found(self):
        """Test unregister from non-existent activity returns 404"""
        # Arrange
        activity_name = "NonExistentActivity"
        email = "test@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]

    def test_delete_signup_participant_not_found(self):
        """Test unregister when participant not signed up returns 404"""
        # Arrange
        activity_name = "Debate Team"
        email = "notsignedup@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Participant not found" in result["detail"]

    def test_get_root_redirect(self):
        """Test GET / redirects to static index.html"""
        # Arrange - No setup needed

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code in [302, 307]  # Allow both redirect codes
        assert response.headers["location"] == "/static/index.html"