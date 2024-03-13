from typing import List

import uvicorn

from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import databases
from fastapi.middleware.cors import CORSMiddleware

# Define your database URL for PostgresSQL
DATABASE_URL = "postgresql://postgres:9920@localhost:5432/Portfolio"

database = databases.Database(DATABASE_URL)
metadata = MetaData()

# Define the Component table
components = Table(
    "components",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("title", String, index=True),
    Column("summary", String),
    Column("link", String),
)

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("name", String, index=True),
    Column("email", String, unique=True, index=True),
    Column("password", String),
)

engine = create_engine(DATABASE_URL)
metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Component(Base):
    __tablename__ = "components"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    summary = Column(String)
    link = Column(String)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

app = FastAPI()

# CORS settings
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# POST API endpoint to accept data for the Component table
@app.post("/components/")
async def create_component(title: str, summary: str, link: str):
    component = Component(title=title, summary=summary, link=link)
    async with database.transaction():
        db = SessionLocal()
        db.add(component)
        db.commit()
        db.refresh(component)
    return component

# GET API endpoint to fetch all data from the Component table
@app.get("/components/", response_model=None)
async def read_components():
    async with database.transaction():
        db = SessionLocal()
        components = db.query(Component).all()
    return components

# GET API endpoint to fetch data for a specific component by ID
@app.get("/components/{component_id}", response_model=None)
async def read_component(component_id: int):
    async with database.transaction():
        db = SessionLocal()
        component = db.query(Component).filter(Component.id == component_id).first()
    if component is None:
        raise HTTPException(status_code=404, detail="Component not found")
    return component

# DELETE API endpoint to delete a component by ID
@app.delete("/components/{component_id}")
async def delete_component(component_id: int):
    async with database.transaction():
        db = SessionLocal()
        component = db.query(Component).filter(Component.id == component_id).first()
        if component is None:
            raise HTTPException(status_code=404, detail="Component not found")
        db.delete(component)
        db.commit()
    return {"message": "Component deleted successfully"}

# POST API endpoint to create a new user
# @app.post("/users/")
# async def create_user(name: str, email: str, password: str):
#     user = User(name=name, email=email, password=password)
#     async with database.transaction():
#         db = SessionLocal()
#         db.add(user)
#         db.commit()
#         db.refresh(user)
#     return user

# # GET API endpoint to fetch data for a specific user by ID
# @app.get("/users/{user_id}", response_model=User)
# async def read_user(user_id: int):
#     async with database.transaction():
#         db = SessionLocal()
#         user = db.query(User).filter(User.id == user_id).first()
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

# # GET API endpoint to fetch all users
# @app.get("/users/", response_model=List[User])
# async def read_users():
#     async with database.transaction():
#         db = SessionLocal()
#         users = db.query(User).all()
#     return users

# # DELETE API endpoint to delete a user by ID
# @app.delete("/users/{user_id}")
# async def delete_user(user_id: int):
#     async with database.transaction():
#         db = SessionLocal()
#         user = db.query(User).filter(User.id == user_id).first()
#         if user is None:
#             raise HTTPException(status_code=404, detail="User not found")
#         db.delete(user)
#         db.commit()
#     return {"message": "User deleted successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
