#!/usr/bin/python3
"""Defines the City class."""
from os import getenv
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import BaseModel, Base


class City(BaseModel, Base):
    """Represents a city (table cities)."""
    __tablename__ = "cities"
    name = Column(String(128), nullable=False)
    state_id = Column(String(60), ForeignKey("states.id"), nullable=False)
    if getenv("HBNB_TYPE_STORAGE") == "db":
        places = relationship("Place", backref="cities", cascade="all, delete")
