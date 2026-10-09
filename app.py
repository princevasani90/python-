from fastapi import FastAPI, Form
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

app = FastAPI()


# =========================
# Database Configuration
# =========================

DATABASE_URL = "sqlite:///./todo.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# =========================
# Todo Model
# =========================

class Todo(Base):

    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(
        String(150),
        nullable=False
    )

    description = Column(
        String(300),
        nullable=True
    )

    priority = Column(
        String(20),
        nullable=False
    )

    # New task = False
    is_completed = Column(
        Boolean,
        default=False,
        nullable=False
    )

    due_date = Column(
        Date,
        nullable=False
    )


# =========================
# Create Database
# =========================

Base.metadata.create_all(bind=engine)


# =========================
# Get All Tasks
# =========================

@app.get("/tasks")
def get_tasks():

    db = SessionLocal()

    tasks = db.query(Todo).all()

    data = []

    for task in tasks:

        data.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "is_completed": task.is_completed,
            "due_date": str(task.due_date)
        })

    db.close()

    return data


# =========================
# Add Task
# =========================

@app.post("/add")
def add_task(

    title: str = Form(...),

    description: str = Form(""),

    priority: str = Form(...),

    due_date: str = Form(...)

):

    db = SessionLocal()

    try:

        # Convert 2026/05/24 -> 2026-05-24
        due_date = due_date.replace("/", "-")

        date_value = datetime.strptime(
            due_date,
            "%Y-%m-%d"
        ).date()

        task = Todo(

            title=title,

            description=description,

            priority=priority,

            # New task is incomplete
            is_completed=False,

            due_date=date_value

        )

        db.add(task)

        db.commit()

        db.refresh(task)

        result = {

            "message": "Task added successfully",

            "id": task.id,

            "is_completed": task.is_completed

        }

        return result

    except ValueError:

        return {
            "message": "Invalid date format. Use YYYY-MM-DD"
        }

    finally:

        db.close()


# =========================
# Toggle Task
# =========================

@app.put("/toggle/{id}")
def toggle_task(id: int):

    db = SessionLocal()

    try:

        task = db.query(Todo).filter(
            Todo.id == id
        ).first()

        if not task:

            return {
                "message": "Task not found"
            }

        # False -> True
        # True -> False

        task.is_completed = not task.is_completed

        db.commit()

        db.refresh(task)

        return {

            "message": "Task status updated",

            "id": task.id,

            "is_completed": task.is_completed

        }

    finally:

        db.close()


# =========================
# Update Task
# =========================

@app.put("/update/{id}")
def update_task(

    id: int,

    title: str = Form(...),

    description: str = Form(""),

    priority: str = Form(...),

    due_date: str = Form(...)

):

    db = SessionLocal()

    try:

        task = db.query(Todo).filter(
            Todo.id == id
        ).first()

        if not task:

            return {
                "message": "Task not found"
            }

        # Convert date format
        due_date = due_date.replace("/", "-")

        date_value = datetime.strptime(
            due_date,
            "%Y-%m-%d"
        ).date()

        task.title = title

        task.description = description

        task.priority = priority

        task.due_date = date_value

        # IMPORTANT:
        # is_completed ને અહીં change નથી કરતા.
        # Update કરતી વખતે completion status same રહેશે.

        db.commit()

        db.refresh(task)

        return {

            "message": "Task updated successfully",

            "id": task.id,

            "is_completed": task.is_completed

        }

    except ValueError:

        return {
            "message": "Invalid date format. Use YYYY-MM-DD"
        }

    finally:

        db.close()


# =========================
# Delete Task
# =========================

@app.delete("/delete/{id}")
def delete_task(id: int):

    db = SessionLocal()

    try:

        task = db.query(Todo).filter(
            Todo.id == id
        ).first()

        if not task:

            return {
                "message": "Task not found"
            }

        db.delete(task)

        db.commit()

        return {

            "message": "Task deleted successfully",

            "id": id

        }

    finally:

        db.close()


# =========================
# Run Application
# =========================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )