"""Tests for GET /activities endpoint"""
import pytest


def test_get_activities_returns_all_activities(client, reset_activities):
    """Test that GET /activities returns all activities"""
    response = client.get("/activities")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should have 12 activities
    assert len(data) == 12
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_activity_structure(client, reset_activities):
    """Test that activity objects have correct structure"""
    response = client.get("/activities")
    data = response.json()
    
    activity = data["Chess Club"]
    
    # Check required fields
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    
    # Check types
    assert isinstance(activity["description"], str)
    assert isinstance(activity["schedule"], str)
    assert isinstance(activity["max_participants"], int)
    assert isinstance(activity["participants"], list)


def test_activity_participants_are_emails(client, reset_activities):
    """Test that participants are email strings"""
    response = client.get("/activities")
    data = response.json()
    
    chess_club = data["Chess Club"]
    participants = chess_club["participants"]
    
    assert len(participants) == 2
    assert "michael@mergington.edu" in participants
    assert "daniel@mergington.edu" in participants
    
    # Verify all participants have email format
    for participant in participants:
        assert "@" in participant


def test_empty_activity_has_empty_participants(client, reset_activities):
    """Test that activities with no participants have empty list"""
    response = client.get("/activities")
    data = response.json()
    
    basketball = data["Basketball Team"]
    assert basketball["participants"] == []


def test_participant_count_accuracy(client, reset_activities):
    """Test that participant counts are accurate"""
    response = client.get("/activities")
    data = response.json()
    
    for activity_name, activity in data.items():
        max_participants = activity["max_participants"]
        current_count = len(activity["participants"])
        
        # Current count should never exceed max
        assert current_count <= max_participants, \
            f"{activity_name} has {current_count} but max is {max_participants}"
