from typing import List

import uvicorn

from fastapi import FastAPI, HTTPException,Depends
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import model as md
from database import engine, SessionLocal
from sqlalchemy.orm import Session
# import databases
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Annotated

md.Base.metadata.create_all(bind=engine)
def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

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
async def create_component(title: str, summary: str, link: str,db:db_dependency):
    component = md.Component(title=title,summary=summary,link=link)
    db.add(component)
    db.commit()
    db.refresh(component)
    return component

# GET API endpoint to fetch all data from the Component table
@app.get("/components/", response_model=None)
async def read_components(db:db_dependency):
    result=db.query(md.Component).all()
    return result

# GET API endpoint to fetch data for a specific component by ID
@app.get("/components/{component_id}", response_model=None)
async def read_component(component_id: int,db:db_dependency):
    return db.query(md.Component).filter(md.Component.id==component_id).first()

# DELETE API endpoint to delete a component by ID
@app.delete("/components/{component_id}")
async def delete_component(component_id: int,db:db_dependency):
    component = db.query(md.Component).filter(md.Component.id == component_id).first()
    if component is None:
        raise HTTPException(status_code=404, detail="Component not found")
    db.delete(component)
    db.commit()
    return {"message": "Component deleted successfully"}

@app.put('/components/{component_id}')
async def update_component(component_id: int,db:db_dependency,title: str, summary: str, link: str):
    component = db.query(md.Component).filter(md.Component.id == component_id).first()
    component.title=title
    component.summary=summary
    component.link=link
    if component is None:
        raise HTTPException(status_code=404, detail="Component not found")
    # db.(component)
    db.commit()
    return {"message": "Component updated successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
