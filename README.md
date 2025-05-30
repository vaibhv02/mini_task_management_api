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

## API Endpoints

### Authentication Endpoints

#### Register a New User
- **POST** `/auth/register`
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "yourpassword"
  }
  ```

#### Login
- **POST** `/auth/login`
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "yourpassword"
  }
  ```
- **Response:** Returns JWT access token
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```

### Authentication

The API uses FastAPI's built-in OAuth2 password flow for authentication. After logging in, FastAPI automatically handles the authentication for protected endpoints. You don't need to manually include any tokens in your requests.

### Task Management Endpoints

#### Create a New Task
- **POST** `/tasks/`
- **Request Body:**
  ```json
  {
    "title": "Complete project documentation",
    "description": "Write comprehensive API documentation",
    "status": "pending",
    "priority": "high"
  }
  ```

#### List Tasks
- **GET** `/tasks/`
- **Query Parameters:**
  - `status`: Filter by status (pending/in_progress/completed)
  - `priority`: Filter by priority (low/medium/high)

#### Get a Specific Task
- **GET** `/tasks/{task_id}`

#### Update a Task
- **PUT** `/tasks/{task_id}`
- **Request Body:**
  ```json
  {
    "title": "Updated task title",
    "status": "completed"
  }
  ```

#### Delete a Task
- **DELETE** `/tasks/{task_id}`

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
