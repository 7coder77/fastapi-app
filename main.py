from typing import Optional

import uvicorn
import json
import pandas as pd

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from starlette.responses import StreamingResponse
import shutil
import os
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import databases
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DATABASE_URL = "sqlite:///./test.db"

database = databases.Database(DATABASE_URL)
metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("name", String, index=True),
    Column("email", String, unique=True, index=True),
    Column("password", String, unique=True, index=True),
)

components = Table(
    "components",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("title", String, index=True),
    Column("summary", String),
    Column("link", String),
)

engine = create_engine(DATABASE_URL)
metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Val_User(BaseModel):
    username:str
    password:str

class ComponentSchema(BaseModel):
    title: str
    summary: str
    link: str
class ComponentSchemaUpdate(BaseModel):
    id: int
    title: str
    summary: str
    link: str

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, unique=True, index=True)

class Component(Base):
    __tablename__ = "components"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    summary = Column(String)
    link = Column(String)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello Aniruddha"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.get("/downloadfile/{filename}")
async def download_file(filename: str):
    # Check if the file exists
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="File not found")

    # Open the file and return it as a StreamingResponse
    file_path = os.path.abspath(filename)
    return StreamingResponse(open(file_path, "rb"), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={filename}"})

@app.post("/users/")
async def create_user(name: str, email: str, password:str):
    user = User(name=name, email=email,password=password)
    async with database.transaction():
        db = SessionLocal()
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@app.get("/users/{user_id}")
async def read_user(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)

@app.get("/users/")
async def read_users(skip: int = 0, limit: int = 10):
    query = users.select().offset(skip).limit(limit)
    return await database.fetch_all(query)

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    async with database.transaction():
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return {"message": f"User {user_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")

@app.post("/Auth_user")
async def auth_user(jsn:Val_User):
    print("--------")
    print("inside fun",jsn.password)
    # query = users.select().where(users.c.password == jsn.password)
    # user_data=database.fetch_one(query)
    db = SessionLocal()
    user_data = db.query(User).filter(User.name == jsn.username  ,User.password == jsn.password).first()
    print(user_data)
    print("check logs---->>>>")
    if user_data:
        return {"res": "true", "message": "Authentication successful"}
    else:
        raise HTTPException(status_code=401, detail="Authentication failed")

@app.post("/components")
async def create_component(component:ComponentSchema):
    component = Component(title=component.title, summary=component.summary, link=component.link)
    async with database.transaction():
        db = SessionLocal()
        db.add(component)
        db.commit()
        db.refresh(component)
    return component
@app.put("/components")
async def create_component(component:ComponentSchemaUpdate):
    async with database.transaction():
        db=SessionLocal()
        result=db.query(Component).filter(Component.id==component.id).first()
        if result:
            # Convert the SQLAlchemy result into a Pandas DataFrame
            df = pd.DataFrame([vars(result)])  # Convert the result object to a dictionary and then to a DataFrame
            print(df)
            # Convert the DataFrame to JSON and print it
            result.title = component.title
            result.summary = component.summary
            result.link = component.link
            db.commit()
        return result

@app.get("/GetAdminData")
async def getData():
    async with database.transaction():
        db = SessionLocal()
        components = db.query(Component).all()
    return components

origins = ["*"]           
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__=="__main__":
    uvicorn.run("main:app",reload=True)
