from typing import Optional

import uvicorn
import json 
import pandas as pd
from sqlalchemy import Boolean,JSON,Date
from sqlalchemy import func
from datetime import datetime

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
from pydantic import BaseModel, conlist

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
contact = Table(
    "contact",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("name", String, index=True),
    Column("email", String),
    Column("msg", String),
    Column("visited", Boolean),
)
Experience = Table(
    "experience",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("name", String, index=True),
    Column("desc", String, index=True),
    Column("skills", JSON),
    Column("startDate", String),
    Column("endDate", Boolean),
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

class ContactObj(BaseModel):
    name:str
    email:str
    msg:str

class ExperienceInput(BaseModel):
    name: str
    desc: str
    skills: conlist(str)
    startDate: str
    endDate: str

class resp(BaseModel):
    item:conlist(ExperienceInput)

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

class Contact(Base):
    __tablename__ = "Contact"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String)
    msg = Column(String)
    visited = Column(Boolean) 

class Experience(Base):
    __tablename__ = "Experience"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    desc = Column(String, index=True)
    skills = Column(JSON)
    startDate = Column(Date)
    endDate = Column(Date)

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
        else:
            raise HTTPException(status_code=404, detail="Data Not Found")
        return {"message": "Data Updated"}

@app.get("/GetAdminData")
async def getData():
    async with database.transaction():
        db = SessionLocal()
        components = db.query(Component).all()
    return components
@app.delete("/Del_Componet/{id}")
async def getData(id:int):
    async with database.transaction():
        db = SessionLocal()
        components = db.query(Component).filter(Component.id==id).first()
        db.delete(components)
        db.commit()
    return {"msg":"Deleted successfully"}

@app.post('/contact')
async def postContact(ContactObj:ContactObj):
    result=Contact(name=ContactObj.name,msg=ContactObj.msg,email=ContactObj.email , visited=False)
    async with database.transaction():
        db = SessionLocal()
        db.add(result)
        db.commit()
        db.refresh(result)
        return result
        
@app.get('/contact')
async def mark_all_contacts_visited():
    async with database.transaction():
        db = SessionLocal()
        # Fetch all contacts
        contacts = db.query(Contact).all()
        
        # Update the visited attribute for each contact
        for contact in contacts:
            contact.visited = True
        
        # Commit the changes to the database
        db.commit()

        
        # Return the updated contacts
        return db.query(Contact).all()
    
@app.get('/contact-count')
async def count():
    async with database.transaction():
        db = SessionLocal()
        count = db.query(func.count()).filter(Contact.visited == False).scalar()
        return {"count":count}

@app.post("/experience")
async def create_experience(experience_input: resp):
    db = SessionLocal()
    experiences = []
    for exp_input in experience_input.item:
        # Convert startDate and endDate strings to Python date objects
        start_date = datetime.strptime(exp_input.startDate, "%d-%m-%Y").date()
        end_date = datetime.strptime(exp_input.endDate, "%d-%m-%Y").date()
        
        experience_db = Experience(
            name=exp_input.name,
            desc=exp_input.desc,
            skills=exp_input.skills,
            startDate=start_date,
            endDate=end_date
        )
        db.add(experience_db)
        db.commit()
        db.refresh(experience_db)
        experiences.append(experience_db)
    return experiences

@app.get('/get-exp')
async def getExperience():
    db=SessionLocal()
    result = db.query(Experience).order_by(Experience.startDate).all()
    return result

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
