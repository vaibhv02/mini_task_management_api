# Mini Task Management API

A FastAPI-based RESTful API for task management with email/password authentication.

## Features

- 🔐 Simple Email/Password Authentication
- 📝 CRUD operations for Tasks
- ✅ Data validation
- 🔍 Task filtering
- 📚 Swagger documentation

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
DATABASE_URL=postgresql://user:password@localhost:5432/taskdb
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Swagger UI: `http://localhost:8000/docs`

## Authentication

### 1. Register a New User
```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
         "email": "user@example.com",
         "password": "yourpassword"
     }'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
         "email": "user@example.com",
         "password": "yourpassword"
     }'
```

The API will automatically handle authentication for protected endpoints using the provided email and password credentials.

## Task Management API Examples

### 1. Create a New Task
```bash
curl -X POST "http://localhost:8000/tasks/" \
     -H "Content-Type: application/json" \
     -d '{
         "title": "Complete project documentation",
         "description": "Write comprehensive API documentation",
         "status": "pending",
         "priority": "high"
     }'
```

### 2. List All Tasks
```bash
# Get all tasks
curl -X GET "http://localhost:8000/tasks/"

# Filter tasks by status
curl -X GET "http://localhost:8000/tasks/?status=pending"

# Filter tasks by priority
curl -X GET "http://localhost:8000/tasks/?priority=high"
```

### 3. Get a Specific Task
```bash
curl -X GET "http://localhost:8000/tasks/1"
```

### 4. Update a Task
```bash
curl -X PUT "http://localhost:8000/tasks/1" \
     -H "Content-Type: application/json" \
     -d '{
         "title": "Updated task title",
         "status": "completed"
     }'
```

### 5. Delete a Task
```bash
curl -X DELETE "http://localhost:8000/tasks/1"
```

## Task Model

Tasks have the following fields:
- `title` (string, required): Task title
- `description` (string, optional): Task description
- `status` (string, required): One of "pending", "in_progress", "completed"
- `priority` (string, required): One of "low", "medium", "high"
- `created_at` (datetime, auto-generated): Task creation timestamp
- `updated_at` (datetime, auto-generated): Last update timestamp

## Running Tests

```bash
pytest
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Validation Error
- 500: Internal Server Error
