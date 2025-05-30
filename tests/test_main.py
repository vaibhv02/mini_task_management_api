from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from app.main import app
from app.database import Base, engine
from sqlalchemy.orm import sessionmaker

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

client = TestClient(app)

def test_register_user():
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_login():
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_create_task():
    # First login to get token
    login_response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]
    
    # Create task
    future_date = datetime.utcnow() + timedelta(days=1)
    response = client.post(
        "/tasks/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Task",
            "description": "Test Description",
            "due_date": future_date.isoformat()
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert "id" in data

def test_get_tasks():
    # First login to get token
    login_response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]
    
    # Get tasks
    response = client.get(
        "/tasks/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list) 