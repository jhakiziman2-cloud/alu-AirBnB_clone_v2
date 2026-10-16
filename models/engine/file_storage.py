#!/usr/bin/python3
"""Defines the FileStorage class (JSON file persistence)."""
import json


class FileStorage:
    """Serializes instances to a JSON file and deserializes them back."""
    __file_path = "file.json"
    __objects = {}

    @staticmethod
    def _classes():
        """Return a dictionary mapping class names to model classes."""
        from models.base_model import BaseModel
        from models.user import User
        from models.state import State
        from models.city import City
        from models.amenity import Amenity
        from models.place import Place
        from models.review import Review
        return {"BaseModel": BaseModel, "User": User, "State": State,
                "City": City, "Amenity": Amenity, "Place": Place,
                "Review": Review}

    def all(self, cls=None):
        """Return the dictionary of objects, optionally filtered by class.

        Args:
            cls: a class (or class name) used to filter the objects.
        """
        if cls is None:
            return FileStorage.__objects
        if isinstance(cls, str):
            cls = self._classes().get(cls)
        return {key: obj for key, obj in FileStorage.__objects.items()
                if cls is not None and type(obj) is cls}

    def new(self, obj):
        """Add obj to the objects dictionary."""
        if obj is not None:
            key = "{}.{}".format(type(obj).__name__, obj.id)
            FileStorage.__objects[key] = obj

    def save(self):
        """Serialize the objects dictionary to the JSON file."""
        data = {key: obj.to_dict()
                for key, obj in FileStorage.__objects.items()}
        with open(FileStorage.__file_path, "w", encoding="utf-8") as file:
            json.dump(data, file)

    def reload(self):
        """Deserialize the JSON file into the objects dictionary."""
        try:
            with open(FileStorage.__file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (FileNotFoundError, ValueError):
            return
        classes = self._classes()
        for key, value in data.items():
            cls = classes.get(value.get("__class__"))
            if cls is not None:
                FileStorage.__objects[key] = cls(**value)

    def delete(self, obj=None):
        """Delete obj from the objects dictionary if it is inside."""
        if obj is None:
            return
        key = "{}.{}".format(type(obj).__name__, obj.id)
        FileStorage.__objects.pop(key, None)

    def close(self):
        """Reload the storage from the JSON file."""
        self.reload()
