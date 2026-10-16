#!/usr/bin/python3
"""Defines the DBStorage class (MySQL persistence through SQLAlchemy)."""
from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, scoped_session
from models.base_model import Base
from models.user import User
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.place import Place
from models.review import Review


class DBStorage:
    """Stores and retrieves model instances in a MySQL database."""
    __engine = None
    __session = None
    classes = {"User": User, "State": State, "City": City,
               "Amenity": Amenity, "Place": Place, "Review": Review}

    def __init__(self):
        """Create the engine from the HBNB_MYSQL_* environment variables."""
        url = URL.create("mysql+mysqldb",
                         username=getenv("HBNB_MYSQL_USER"),
                         password=getenv("HBNB_MYSQL_PWD"),
                         host=getenv("HBNB_MYSQL_HOST"),
                         database=getenv("HBNB_MYSQL_DB"))
        self.__engine = create_engine(url, pool_pre_ping=True)
        if getenv("HBNB_ENV") == "test":
            Base.metadata.drop_all(self.__engine)

    def all(self, cls=None):
        """Return a dictionary of all objects, optionally of one class.

        Keys are <class-name>.<object-id> and values are the objects.
        """
        if isinstance(cls, str):
            cls = self.classes.get(cls)
        targets = [cls] if cls is not None else list(self.classes.values())
        result = {}
        for target in targets:
            for obj in self.__session.query(target).all():
                result["{}.{}".format(type(obj).__name__, obj.id)] = obj
        return result

    def new(self, obj):
        """Add obj to the current database session."""
        self.__session.add(obj)

    def save(self):
        """Commit all changes of the current database session."""
        self.__session.commit()

    def delete(self, obj=None):
        """Delete obj from the current database session if not None."""
        if obj is not None:
            self.__session.delete(obj)

    def reload(self):
        """Create all tables and a new thread-safe database session."""
        Base.metadata.create_all(self.__engine)
        factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        self.__session = scoped_session(factory)

    def close(self):
        """Remove the current session."""
        self.__session.remove()
