from datetime import datetime, timedelta, timezone
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import models, schemas, auth
from .database import engine, get_db
from .config import settings

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Management API",
    description="A FastAPI-based RESTful API for task management with JWT authentication",
    version="1.0.0",
)

logger.info("Task Management API starting")

@app.post("/auth/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Attempting to register user: {user.email}")
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        logger.warning(f"Registration failed: Email already registered - {user.email}")
        raise HTTPException(
            status_code=400, detail="Email already registered"
        )
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User registered successfully: {user.email}")
    return db_user


@app.post("/auth/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    logger.info(f"Attempting to log in user: {form_data.username}")
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Login failed: Incorrect email or password for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info(f"User logged in successfully: {user.email}")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/tasks/", response_model=schemas.Task)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    logger.info(f"User {current_user.email} attempting to create task: {task.title}")
    if task.due_date < datetime.now(timezone.utc):
        logger.warning(f"Task creation failed: Due date in the past - {task.due_date}")
        raise HTTPException(
            status_code=400, detail="Due date must be in the future"
        )
    db_task = models.Task(**task.model_dump(), owner_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    logger.info(f"Task created successfully with ID: {db_task.id} by user: {current_user.email}")
    return db_task


@app.get("/tasks/", response_model=List[schemas.Task])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    completed: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    logger.info(f"User {current_user.email} attempting to read tasks with filter completed={completed}")
    query = db.query(models.Task).filter(models.Task.owner_id == current_user.id)
    if completed is not None:
        query = query.filter(models.Task.is_completed == completed)
    tasks = query.offset(skip).limit(limit).all()
    logger.info(f"Returned {len(tasks)} tasks for user: {current_user.email}")
    return tasks


@app.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    logger.info(f"User {current_user.email} attempting to read task with ID: {task_id}")
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_id == current_user.id
    ).first()
    if task is None:
        logger.warning(f"Task not found with ID: {task_id} for user: {current_user.email}")
        raise HTTPException(status_code=404, detail="Task not found")
    logger.info(f"Task with ID: {task_id} found for user: {current_user.email}")
    return task


@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    logger.info(f"User {current_user.email} attempting to update task with ID: {task_id}")
    db_task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_id == current_user.id
    ).first()
    if db_task is None:
        logger.warning(f"Task not found for update with ID: {task_id} for user: {current_user.email}")
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_update.due_date and task_update.due_date < datetime.now(timezone.utc):
        logger.warning(f"Task update failed: Due date in the past - {task_update.due_date}")
        raise HTTPException(
            status_code=400, detail="Due date must be in the future"
        )
    
    update_data = task_update.model_dump(exclude_unset=True)
    logger.info(f"Updating task {task_id} with data: {update_data} for user: {current_user.email}")
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    logger.info(f"Task with ID: {task_id} updated successfully for user: {current_user.email}")
    return db_task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    logger.info(f"User {current_user.email} attempting to delete task with ID: {task_id}")
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_id == current_user.id
    ).first()
    if task is None:
        logger.warning(f"Task not found for deletion with ID: {task_id} for user: {current_user.email}")
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    logger.info(f"Task with ID: {task_id} deleted successfully for user: {current_user.email}")
    return None 