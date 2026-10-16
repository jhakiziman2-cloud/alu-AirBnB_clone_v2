#!/usr/bin/python3
"""Defines the User class."""
from os import getenv
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from models.base_model import BaseModel, Base


class User(BaseModel, Base):
    """Represents a user of the application (table users)."""
    __tablename__ = "users"
    email = Column(String(128), nullable=False)
    password = Column(String(128), nullable=False)
    first_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)
    if getenv("HBNB_TYPE_STORAGE") == "db":
        places = relationship("Place", backref="user", cascade="all, delete")
        reviews = relationship("Review", backref="user",
                               cascade="all, delete")
