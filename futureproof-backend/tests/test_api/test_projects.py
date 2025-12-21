import pytest
from fastapi import status

def test_create_project(client, sample_project_data):
    """Test project creation"""
    response = client.post("/api/v1/projects/", json=sample_project_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == sample_project_data["name"]
    assert data["repo_url"] == sample_project_data["repo_url"]
    assert data["status"] == "pending"
    assert "id" in data

def test_list_projects(client, sample_project_data):
    """Test listing projects"""
    # Create a project first
    client.post("/api/v1/projects/", json=sample_project_data)
    
    # List projects
    response = client.get("/api/v1/projects/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert "projects" in data
    assert len(data["projects"]) > 0

def test_get_project(client, sample_project_data):
    """Test getting a specific project"""
    # Create project
    create_response = client.post("/api/v1/projects/", json=sample_project_data)
    project_id = create_response.json()["id"]
    
    # Get project
    response = client.get(f"/api/v1/projects/{project_id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == sample_project_data["name"]

def test_get_nonexistent_project(client):
    """Test getting a project that doesn't exist"""
    response = client.get("/api/v1/projects/99999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_project(client, sample_project_data):
    """Test deleting a project"""
    # Create project
    create_response = client.post("/api/v1/projects/", json=sample_project_data)
    project_id = create_response.json()["id"]
    
    # Delete project
    response = client.delete(f"/api/v1/projects/{project_id}")
    
    assert response.status_code == status.HTTP_200_OK
    
    # Verify deletion
    get_response = client.get(f"/api/v1/projects/{project_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
