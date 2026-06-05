import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore activities state between tests."""
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


class TestGetActivities:
    """Test GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self):
        # Arrange

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert isinstance(data["Chess Club"]["participants"], list)


class TestSignupForActivity:
    """Test POST /activities/{activity_name}/signup endpoint."""

    def test_signup_for_activity(self):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{quote(activity_name, safe='')}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]
        assert (
            response.json()["message"]
            == f"Signed up {email} for {activity_name}"
        )

    def test_signup_duplicate_returns_400(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{quote(activity_name, safe='')}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "Student is already signed up for this activity"
        )


class TestUnregisterParticipant:
    """Test DELETE /activities/{activity_name}/participants endpoint."""

    def test_unregister_participant(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{quote(activity_name, safe='')}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]
        assert (
            response.json()["message"]
            == f"Removed {email} from {activity_name}"
        )

    def test_unregister_missing_participant_returns_404(self):
        # Arrange
        activity_name = "Chess Club"
        email = "missing@example.com"

        # Act
        response = client.delete(
            f"/activities/{quote(activity_name, safe='')}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"
