import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_get_activities_returns_activity_data():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_student_to_activity():
    # Arrange
    client = TestClient(app)
    email = "new-student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_student():
    # Arrange
    client = TestClient(app)
    email = "michael@mergington.edu"
    original_participants = activities["Chess Club"]["participants"][:]

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }
    assert activities["Chess Club"]["participants"] == original_participants


def test_signup_returns_not_found_for_unknown_activity():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.post(
        "/activities/Unknown%20Activity/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_student_from_activity():
    # Arrange
    client = TestClient(app)
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_returns_not_found_for_absent_student():
    # Arrange
    client = TestClient(app)
    email = "absent-student@mergington.edu"
    original_participants = activities["Chess Club"]["participants"][:]

    # Act
    response = client.delete(
        "/activities/Chess%20Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert activities["Chess Club"]["participants"] == original_participants


def test_unregister_returns_not_found_for_unknown_activity():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.delete(
        "/activities/Unknown%20Activity/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}