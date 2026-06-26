"""Tests for POST /activities/{activity_name}/signup endpoint"""
import pytest


def test_signup_successful(client, reset_activities):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Basketball%20Team/signup?email=test@mergington.edu"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up" in data["message"]
    assert "test@mergington.edu" in data["message"]
    assert "Basketball Team" in data["message"]


def test_signup_adds_participant_to_list(client, reset_activities):
    """Test that signup adds participant to activity's participant list"""
    # Get initial state
    response = client.get("/activities")
    initial_data = response.json()
    initial_count = len(initial_data["Soccer Club"]["participants"])
    
    # Sign up
    client.post("/activities/Soccer%20Club/signup?email=newstudent@mergington.edu")
    
    # Check updated state
    response = client.get("/activities")
    updated_data = response.json()
    updated_count = len(updated_data["Soccer Club"]["participants"])
    
    assert updated_count == initial_count + 1
    assert "newstudent@mergington.edu" in updated_data["Soccer Club"]["participants"]


def test_signup_activity_not_found(client, reset_activities):
    """Test signup for non-existent activity returns 404"""
    response = client.post(
        "/activities/Nonexistent%20Club/signup?email=test@mergington.edu"
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_duplicate_participant_returns_400(client, reset_activities):
    """Test that duplicate signup returns 400 error"""
    # Try to sign up someone already registered
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael@mergington.edu"
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_when_activity_full_returns_400(client, reset_activities):
    """Test that signup fails when activity is at capacity"""
    # Create a small activity with limited capacity
    # First, we need to fill up an activity
    # Let's use Debate Team which has max 15 and currently 1 participant
    
    # Fill it up to capacity
    for i in range(14):  # Need 14 more to reach capacity of 15
        response = client.post(
            f"/activities/Debate%20Team/signup?email=student{i}@mergington.edu"
        )
        assert response.status_code == 200
    
    # Now try to sign up one more (should fail)
    response = client.post(
        "/activities/Debate%20Team/signup?email=overflow@mergington.edu"
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "full" in data["detail"].lower()


def test_signup_multiple_different_activities(client, reset_activities):
    """Test signing up for multiple different activities"""
    student = "versatile@mergington.edu"
    
    # Sign up for multiple activities
    activities = ["Basketball Team", "Soccer Club", "Music Ensemble"]
    
    for activity in activities:
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={student}"
        )
        assert response.status_code == 200
    
    # Verify student is in all activities
    response = client.get("/activities")
    data = response.json()
    
    for activity in activities:
        assert student in data[activity]["participants"]


def test_signup_returns_success_message_format(client, reset_activities):
    """Test that signup response has expected message format"""
    response = client.post(
        "/activities/Art%20Club/signup?email=artist@mergington.edu"
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Message should mention the email and activity name
    message = data["message"]
    assert "artist@mergington.edu" in message
    assert "Art Club" in message


def test_signup_maintains_other_participants(client, reset_activities):
    """Test that signup doesn't affect other participants in the activity"""
    # Get initial participants
    response = client.get("/activities")
    initial_data = response.json()
    initial_participants = initial_data["Chess Club"]["participants"].copy()
    
    # Sign up new person
    client.post("/activities/Chess%20Club/signup?email=newchessplayer@mergington.edu")
    
    # Check that original participants are still there
    response = client.get("/activities")
    updated_data = response.json()
    updated_participants = updated_data["Chess Club"]["participants"]
    
    for original in initial_participants:
        assert original in updated_participants
