import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from app.config import settings

# Test database URL
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def sample_project_data():
    """Sample project data for testing"""
    return {
        "name": "Test Project",
        "repo_url": "https://github.com/test/test-repo"
    }

@pytest.fixture
def sample_code_data():
    """Sample code data for agent testing"""
    return {
        "files": [
            {
                "path": "app/main.py",
                "content": "import os\npassword = 'hardcoded123'\nquery = 'SELECT * FROM users WHERE id=' + user_input",
                "language": "python",
                "lines": 3
            }
        ],
        "language": "python",
        "framework": "fastapi",
        "total_files": 1,
        "total_lines": 3
    }
