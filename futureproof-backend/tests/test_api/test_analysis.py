import pytest
from fastapi import status

def test_get_analysis_not_found(client):
    """Test getting analysis for non-existent project"""
    response = client.get("/api/v1/analysis/99999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_analysis_status(client, sample_project_data):
    """Test getting analysis status"""
    # Create project
    create_response = client.post("/api/v1/projects/", json=sample_project_data)
    project_id = create_response.json()["id"]
    
    # Get status
    response = client.get(f"/api/v1/analysis/{project_id}/status")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "project_id" in data
    assert "total_tasks" in data
    assert "progress_percentage" in data
