from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from app.main import app
from app.database import Base, engine, get_db
from sqlalchemy.orm import sessionmaker
import pytest
from app import models

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def setup_database():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    # Get a database session
    db = TestingSessionLocal()
    try:
        # Clear all data from tables
        db.query(models.User).delete()
        db.query(models.Task).delete()
        db.commit()
        yield
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)

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
    # First register the user
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    
    # Then try to login
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_create_task():
    # First register and login to get token
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    login_response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]
    
    # Create task
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
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
    # First register and login to get token
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "testpassword"}
    )
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