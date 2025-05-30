# Mini Task Management API Development Document

## 1. Project Overview

The Mini Task Management API is a RESTful web service built with FastAPI, designed to allow users to manage their tasks. It includes user authentication using JWT and provides standard CRUD (Create, Read, Update, Delete) operations for tasks, with tasks belonging to specific users. The API leverages modern Python technologies for efficiency and reliability.

## 2. Setup and Development Process

The development process followed these key steps:

1.  **Virtual Environment Setup:** A Python virtual environment was created using `python -m venv venv` and activated using `source venv/bin/activate` to isolate project dependencies.
2.  **Dependency Installation:** Required libraries listed in `requirements.txt` were installed using `pip install -r requirements.txt`. This included core libraries like `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`, `python-jose`, `passlib`, `alembic`, and database drivers (`psycopg2-binary`).
3.  **Environment Variables Configuration:** A `.env` file was created at the project root to manage configuration settings like `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, and `ACCESS_TOKEN_EXPIRE_MINUTES`.
    *   A secure `SECRET_KEY` was generated using `python3 -c "import secrets; print(secrets.token_hex(32))"`.
    *   A `DATABASE_URL` for a PostgreSQL database (`postgresql://taskuser:taskpassword@localhost:5432/taskdb`) was constructed after setting up a dedicated database and user.
4.  **Database Setup (PostgreSQL):** A PostgreSQL database (`taskdb`) and a dedicated user (`taskuser`) with a password (`taskpassword`) were created using `psql` commands to manage database access.
5.  **Database Migrations (Alembic):** Alembic was used to handle database schema changes. The initial setup involved running `alembic upgrade head` to create the necessary tables defined in the SQLAlchemy models.
6.  **Server Startup:** The FastAPI application was run using `uvicorn app.main:app --reload` for development, allowing automatic code reloading on changes.
7.  **API Testing:** The API endpoints were tested using the interactive Swagger UI available at `/docs`. This involved registering a user, logging in to obtain a JWT token, authorizing requests in Swagger UI, and then performing CRUD operations on tasks.

## 3. Key Decisions and Implementations

*   **Framework Choice:** FastAPI was chosen for its performance, ease of use, automatic documentation generation (Swagger UI/ReDoc), and strong typing support with Pydantic.
*   **ORM:** SQLAlchemy was selected as the ORM, providing a robust and flexible way to interact with the PostgreSQL database.
*   **Authentication:** JWT authentication was implemented using `python-jose` and `passlib` for password hashing. `OAuth2PasswordBearer` was used with FastAPI to handle the token flow.
*   **Configuration Management:** Pydantic-settings were used with a `.env` file for managing application settings, providing validation and easy loading of environment variables.
*   **Database:** PostgreSQL was chosen, offering a powerful and widely-used relational database system. SQLite was present in the initial Alembic configuration but switched to PostgreSQL for the actual development database.
*   **Validation:** Pydantic models (`schemas.py`) were used for request and response data validation, ensuring data integrity. Custom validation was implemented for the `due_date` to ensure it's in the future.

## 4. Hurdles and Solutions

During the setup and testing process, several issues were encountered and resolved:

*   **`ModuleNotFoundError: No module named 'app'` (Alembic):**
    *   **Hurdle:** Alembic's `env.py` could not import modules from the `app` directory because the project root was not in the Python path.
    *   **Solution:** Added an empty `__init__.py` file to the `app` directory to make it a Python package and ran Alembic commands with `PYTHONPATH=$PYTHONPATH:.` to include the project root in the path.
*   **`psycopg2.OperationalError: FATAL: role "user" does not exist"` (Alembic/Database Connection):**
    *   **Hurdle:** Despite the correct `DATABASE_URL` in `.env`, Alembic was trying to connect with the default "user" role.
    *   **Solution:** Identified a hardcoded `sqlalchemy.url` in `alembic.ini` that was overriding the environment variable. Commented out this line in `alembic.ini`.
*   **Environment Variables Not Loading in Alembic:**
    *   **Hurdle:** Even after commenting out the `alembic.ini` setting and adding `dotenv.load_dotenv()`, the incorrect `DATABASE_URL` was still being used. This was because an existing `DATABASE_URL` environment variable in the shell session was taking precedence.
    *   **Solution:** Modified `alembic/env.py` to explicitly load `dotenv` and settings *inside* the `run_migrations_online` function to ensure it happens within the correct context. Also, the conflicting `DATABASE_URL` environment variable in the shell was explicitly unset using `unset DATABASE_URL`.
*   **`ImportError: email-validator is not installed`:**
    *   **Hurdle:** Pydantic's email validation required the `email_validator` library, which was missing.
    *   **Solution:** Installed the required dependency using `pip install pydantic[email]`.
*   **Zsh Shell Issue with `pip install pydantic[email]`:**
    *   **Hurdle:** The square brackets in `pydantic[email]` were misinterpreted by the zsh shell as a glob pattern.
    *   **Solution:** Quoted the package name when installing: `pip install 'pydantic[email]'`.
*   **`TypeError: can't compare offset-naive and offset-aware datetimes`:**
    *   **Hurdle:** Attempting to compare a timezone-aware `due_date` from the request with a timezone-naive `datetime.utcnow()`.
    *   **Solution:** Updated the comparison in `app/main.py` to use a timezone-aware current time: `datetime.now(timezone.utc)`.
*   **Swagger UI Authorization Input:**
    *   **Hurdle:** Confusion about where to input the JWT token in the "Available authorizations" dialog when using the `OAuth2PasswordBearer` scheme.
    *   **Solution:** Identified that in this configuration, the username (email) and password should be entered directly into the dialog, and Swagger UI handles the token retrieval and usage automatically. Explained the alternative method of using the `Bearer YOUR_TOKEN` format if the UI provided a dedicated input box for the token itself.
*   **ISO 8601 Date Format Confusion:**
    *   **Hurdle:** The `YYYY-MM-DDTHH:MM:SS.sssZ` format for `due_date` is not user-friendly to input manually.
    *   **Solution:** Provided commands to generate future dates in the required format for testing purposes and explained the structure of the format.
    date -u -v+0d -v0H -v0M -v0S +"%Y-%m-%dT%H:%M:%S.000Z"


## 5. Shortcomings and Limitations

While the project meets the core requirements, potential shortcomings and areas for improvement include:

*   **Error Handling:** While we have implemented basic error handling with FastAPI's HTTPException and proper status codes, more granular error responses or custom exception handlers could be implemented for better error categorization and handling.

*   **Input Validation:** While Pydantic handles schema validation effectively, more complex business logic validation (e.g., cross-field validation, custom validation rules) could be added for more robust data validation.

*   **Database Connection Management:** For very high traffic scenarios, advanced connection pooling or database optimization might be needed. Currently, we're using basic SQLAlchemy connection management.

*   **Logging:** We have implemented basic logging throughout the application using Python's logging module, which includes:
    - Request/response logging
    - Authentication attempts
    - Task operations
    - Error logging
    However, for production, we could enhance this with:
    - Structured logging (JSON format)
    - Log aggregation tools integration
    - Log rotation and retention policies
    - Performance metrics logging

*   **Testing Coverage:** While we have included pytest in our dependencies, we could improve by:
    - Adding unit tests for individual components
    - Implementing integration tests
    - Adding API endpoint tests
    - Setting up CI/CD pipeline for automated testing

*   **Rate Limiting:** To protect against abuse, implementing rate limiting on endpoints would be important for production use.

*   **Security Enhancements:** While we have basic security measures in place, we could add:
    - Password complexity requirements
    - Account lockout after failed attempts
    - Session management
    - CORS configuration
    - Security headers

*   **Performance Optimization:** For larger scale applications, we could implement:
    - Caching mechanisms
    - Query optimization
    - Database indexing
    - Response compression

## 6. Future Scope

Based on the current project and common API features, here are potential areas for future development:

*   **Advanced Task Features:** Add features like task priorities, tags, categories, sub-tasks, or recurring tasks.
*   **User Roles and Permissions:** Implement a more granular access control system beyond just task ownership (e.g., admin users, shared tasks).
*   **Email Notifications:** Add functionality to send email notifications for upcoming task due dates or other events.
*   **Improved Error Handling:** Implement custom exception handlers for more specific error responses.
*   **Pagination and Filtering:** Enhance the task listing endpoint with more advanced pagination and filtering options (beyond just completion status).
*   **Search Functionality:** Add the ability to search tasks by keywords in the title or description.
*   **File Uploads:** If tasks needed attachments, implement secure file upload functionality.
*   **Deployment:** Containerize the application using Docker and plan deployment to a cloud platform (AWS, Google Cloud, Azure, etc.).
*   **CI/CD Pipeline:** Set up a Continuous Integration/Continuous Deployment pipeline for automated testing and deployment.
*   **Comprehensive Testing:** Increase unit and integration test coverage and potentially add end-to-end tests.
*   **Password Reset:** Implement a secure password reset mechanism.
*   **Documentation Enhancement:** Further customize the Swagger UI or provide additional documentation outside of Swagger.
*   **Frontend Integration:** Develop a simple frontend application to interact with the API.

