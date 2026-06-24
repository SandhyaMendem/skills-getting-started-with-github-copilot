import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module
from src.app import app


BASELINE_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities state before and after each test."""
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(BASELINE_ACTIVITIES))
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(BASELINE_ACTIVITIES))


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


def test_list_activities(client):
    # Arrange
    # No special setup needed for this endpoint.

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert activities["Chess Club"]["participants"][0] == "michael@mergington.edu"


def test_signup_for_activity_succeeds(client):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up newstudent@mergington.edu for Chess Club"
    }
    assert email in app_module.activities["Chess Club"]["participants"]


def test_duplicate_signup_is_rejected(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_signup_for_nonexistent_activity_fails(client):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        "/activities/Nonexistent%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
