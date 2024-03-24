from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from database import Base

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