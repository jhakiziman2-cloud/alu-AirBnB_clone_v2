#!/usr/bin/python3
"""Defines the State class."""
from os import getenv
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
import models
from models.base_model import BaseModel, Base


class State(BaseModel, Base):
    """Represents a state (table states)."""
    __tablename__ = "states"
    name = Column(String(128), nullable=False)
    if getenv("HBNB_TYPE_STORAGE") == "db":
        cities = relationship("City", backref="state", cascade="all, delete")
    else:
        @property
        def cities(self):
            """Return the list of City instances linked to this State."""
            from models.city import City
            return [city for city in models.storage.all(City).values()
                    if city.state_id == self.id]
