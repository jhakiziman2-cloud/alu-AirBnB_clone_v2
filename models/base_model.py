#!/usr/bin/python3
"""Defines the BaseModel class and the SQLAlchemy declarative Base."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import models

Base = declarative_base()


class BaseModel:
    """Base class that defines the attributes and methods shared by models.

    Attributes:
        id (str): unique identifier (primary key).
        created_at (datetime): creation date and time.
        updated_at (datetime): last update date and time.
    """
    id = Column(String(60), primary_key=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        """Initialize a new instance from optional keyword arguments."""
        self.id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at
        for key, value in kwargs.items():
            if key == "__class__":
                continue
            if key in ("created_at", "updated_at") and isinstance(value, str):
                value = datetime.fromisoformat(value)
            try:
                setattr(self, key, value)
            except AttributeError:
                pass

    def __str__(self):
        """Return the string representation of the instance."""
        attrs = dict(self.__dict__)
        attrs.pop("_sa_instance_state", None)
        return "[{}] ({}) {}".format(type(self).__name__, self.id, attrs)

    def save(self):
        """Update updated_at, add the instance to storage and save it."""
        self.updated_at = datetime.utcnow()
        models.storage.new(self)
        models.storage.save()

    def to_dict(self):
        """Return a dictionary representation of the instance."""
        new_dict = dict(self.__dict__)
        new_dict.pop("_sa_instance_state", None)
        new_dict["__class__"] = type(self).__name__
        for key in ("created_at", "updated_at"):
            if isinstance(new_dict.get(key), datetime):
                new_dict[key] = new_dict[key].isoformat()
        return new_dict

    def delete(self):
        """Delete the current instance from the storage."""
        models.storage.delete(self)
