#!/usr/bin/python3
"""Unit tests for the FileStorage class."""
import json
import os
import unittest
import models
from models.base_model import BaseModel
from models.state import State
from models.city import City
from models.engine.file_storage import FileStorage

DB = os.getenv("HBNB_TYPE_STORAGE") == "db"


@unittest.skipIf(DB, "FileStorage tests are not relevant for DBStorage")
class TestFileStorage(unittest.TestCase):
    """Tests the FileStorage class."""

    def setUp(self):
        """Isolate the storage from the real JSON file."""
        self.path = FileStorage._FileStorage__file_path
        self.backup = None
        if os.path.exists(self.path):
            os.rename(self.path, self.path + ".bak")
            self.backup = self.path + ".bak"
        self.saved = dict(FileStorage._FileStorage__objects)
        FileStorage._FileStorage__objects.clear()

    def tearDown(self):
        """Restore the real JSON file and objects."""
        if os.path.exists(self.path):
            os.remove(self.path)
        if self.backup:
            os.rename(self.backup, self.path)
        FileStorage._FileStorage__objects.clear()
        FileStorage._FileStorage__objects.update(self.saved)

    def test_docstrings(self):
        """Module, class and methods are documented."""
        self.assertTrue(len(models.engine.file_storage.__doc__) > 10)
        self.assertTrue(len(FileStorage.__doc__) > 10)
        for name in ("all", "new", "save", "reload", "delete"):
            self.assertTrue(len(getattr(FileStorage, name).__doc__) > 10)

    def test_storage_type(self):
        """models.storage is a FileStorage instance."""
        self.assertIsInstance(models.storage, FileStorage)

    def test_all_returns_dict(self):
        """all() returns the dictionary of objects."""
        self.assertIsInstance(models.storage.all(), dict)

    def test_all_with_class_filters(self):
        """all(cls) only returns objects of that class."""
        state = State(name="CA")
        city = City(name="SF", state_id=state.id)
        models.storage.new(state)
        models.storage.new(city)
        self.assertEqual(models.storage.all(State),
                         {"State." + state.id: state})
        self.assertEqual(models.storage.all(City),
                         {"City." + city.id: city})
        self.assertEqual(len(models.storage.all()), 2)

    def test_all_with_class_name(self):
        """all() also accepts a class name."""
        state = State(name="CA")
        models.storage.new(state)
        self.assertEqual(len(models.storage.all("State")), 1)
        self.assertEqual(models.storage.all("Unknown"), {})

    def test_all_with_class_without_objects(self):
        """all(cls) returns an empty dict when there is no object."""
        self.assertEqual(models.storage.all(State), {})

    def test_new(self):
        """new() adds an object with the <class>.<id> key."""
        obj = BaseModel()
        models.storage.new(obj)
        self.assertIs(models.storage.all()["BaseModel." + obj.id], obj)

    def test_new_none(self):
        """new(None) does nothing."""
        models.storage.new(None)
        self.assertEqual(models.storage.all(), {})

    def test_save_writes_json(self):
        """save() writes the serialized objects to the file."""
        obj = State(name="CA")
        models.storage.new(obj)
        models.storage.save()
        with open(self.path) as file:
            data = json.load(file)
        self.assertEqual(data["State." + obj.id], obj.to_dict())

    def test_reload(self):
        """reload() rebuilds the objects from the file."""
        obj = State(name="CA")
        models.storage.new(obj)
        models.storage.save()
        FileStorage._FileStorage__objects.clear()
        models.storage.reload()
        loaded = models.storage.all()["State." + obj.id]
        self.assertIsInstance(loaded, State)
        self.assertEqual(loaded.to_dict(), obj.to_dict())

    def test_reload_without_file(self):
        """reload() does nothing when the file does not exist."""
        models.storage.reload()
        self.assertEqual(models.storage.all(), {})

    def test_reload_with_invalid_json(self):
        """reload() ignores an invalid file."""
        with open(self.path, "w") as file:
            file.write("not json")
        models.storage.reload()
        self.assertEqual(models.storage.all(), {})

    def test_delete(self):
        """delete() removes the object from the objects dictionary."""
        first, second = State(name="a"), State(name="b")
        models.storage.new(first)
        models.storage.new(second)
        models.storage.delete(first)
        self.assertEqual(models.storage.all(State),
                         {"State." + second.id: second})

    def test_delete_none(self):
        """delete(None) does nothing."""
        obj = State(name="a")
        models.storage.new(obj)
        models.storage.delete()
        models.storage.delete(None)
        self.assertEqual(len(models.storage.all()), 1)

    def test_delete_unknown_object(self):
        """delete() of an unknown object does not fail."""
        models.storage.delete(State(name="a"))
        self.assertEqual(models.storage.all(), {})

    def test_instance_delete(self):
        """BaseModel.delete() uses the storage delete()."""
        obj = State(name="a")
        obj.save()
        obj.delete()
        self.assertEqual(models.storage.all(State), {})


if __name__ == "__main__":
    unittest.main()
