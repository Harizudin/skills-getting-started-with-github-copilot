"""Tests for DELETE /activities/{activity_name}/unregister endpoint"""
import pytest


def test_unregister_successful(client, reset_activities):
    """Test successful unregistration from an activity"""
    response = client.delete(
        "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered" in data["message"]
    assert "michael@mergington.edu" in data["message"]


def test_unregister_removes_participant(client, reset_activities):
    """Test that unregister removes participant from activity's list"""
    # Get initial state
    response = client.get("/activities")
    initial_data = response.json()
    initial_count = len(initial_data["Chess Club"]["participants"])
    
    # Unregister
    client.delete(
        "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
    )
    
    # Check updated state
    response = client.get("/activities")
    updated_data = response.json()
    updated_count = len(updated_data["Chess Club"]["participants"])
    
    assert updated_count == initial_count - 1
    assert "michael@mergington.edu" not in updated_data["Chess Club"]["participants"]


def test_unregister_activity_not_found(client, reset_activities):
    """Test unregister for non-existent activity returns 404"""
    response = client.delete(
        "/activities/Nonexistent%20Club/unregister?email=test@mergington.edu"
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_participant_not_found(client, reset_activities):
    """Test that unregistering non-participant returns 400"""
    response = client.delete(
        "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "not registered" in data["detail"]


def test_unregister_from_empty_activity(client, reset_activities):
    """Test unregister from activity with no participants returns 400"""
    response = client.delete(
        "/activities/Basketball%20Team/unregister?email=anyone@mergington.edu"
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "not registered" in data["detail"]


def test_unregister_does_not_affect_other_participants(client, reset_activities):
    """Test that unregistering one person doesn't affect others"""
    # Gym Class has john@mergington.edu and olivia@mergington.edu
    response = client.get("/activities")
    initial_data = response.json()
    initial_participants = initial_data["Gym Class"]["participants"].copy()
    
    # Unregister john
    client.delete("/activities/Gym%20Class/unregister?email=john@mergington.edu")
    
    # Check that olivia is still there
    response = client.get("/activities")
    updated_data = response.json()
    updated_participants = updated_data["Gym Class"]["participants"]
    
    assert "olivia@mergington.edu" in updated_participants
    assert "john@mergington.edu" not in updated_participants


def test_unregister_then_signup_again(client, reset_activities):
    """Test that person can sign up again after unregistering"""
    email = "michael@mergington.edu"
    
    # Unregister
    response = client.delete(
        "/activities/Chess%20Club/unregister?email=" + email
    )
    assert response.status_code == 200
    
    # Verify unregistered
    response = client.get("/activities")
    data = response.json()
    assert email not in data["Chess Club"]["participants"]
    
    # Sign up again
    response = client.post(
        f"/activities/Chess%20Club/signup?email={email}"
    )
    assert response.status_code == 200
    
    # Verify registered
    response = client.get("/activities")
    data = response.json()
    assert email in data["Chess Club"]["participants"]


def test_unregister_multiple_participants(client, reset_activities):
    """Test unregistering multiple participants one by one"""
    activity = "Art Club"
    
    # Get initial participants
    response = client.get("/activities")
    initial_data = response.json()
    initial_participants = initial_data[activity]["participants"].copy()
    
    # Unregister all
    for participant in initial_participants:
        response = client.delete(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={participant}"
        )
        assert response.status_code == 200
    
    # Verify all removed
    response = client.get("/activities")
    final_data = response.json()
    assert len(final_data[activity]["participants"]) == 0


def test_unregister_returns_success_message_format(client, reset_activities):
    """Test that unregister response has expected message format"""
    response = client.delete(
        "/activities/Programming%20Class/unregister?email=emma@mergington.edu"
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Message should mention the email and activity name
    message = data["message"]
    assert "emma@mergington.edu" in message
    assert "Programming Class" in message
