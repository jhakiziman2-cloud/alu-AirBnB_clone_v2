#!/usr/bin/python3
"""Unit tests for the BaseModel class."""
import os
import unittest
from datetime import datetime
import models
from models.base_model import BaseModel

DB = os.getenv("HBNB_TYPE_STORAGE") == "db"


class TestBaseModel(unittest.TestCase):
    """Tests the BaseModel class."""

    def test_docstrings(self):
        """Module, class and methods are documented."""
        self.assertTrue(len(models.base_model.__doc__) > 10)
        self.assertTrue(len(BaseModel.__doc__) > 10)
        for name in ("__init__", "__str__", "save", "to_dict", "delete"):
            self.assertTrue(len(getattr(BaseModel, name).__doc__) > 10)

    def test_id_is_unique_string(self):
        """Each instance gets a different string id."""
        first, second = BaseModel(), BaseModel()
        self.assertIsInstance(first.id, str)
        self.assertNotEqual(first.id, second.id)

    def test_dates_are_datetimes(self):
        """created_at and updated_at are datetime objects."""
        obj = BaseModel()
        self.assertIsInstance(obj.created_at, datetime)
        self.assertIsInstance(obj.updated_at, datetime)

    def test_kwargs_attributes(self):
        """kwargs become instance attributes."""
        obj = BaseModel(name="California", number=3)
        self.assertEqual(obj.name, "California")
        self.assertEqual(obj.number, 3)

    def test_kwargs_dates_are_parsed(self):
        """ISO date strings in kwargs are converted to datetime."""
        obj = BaseModel(created_at="2020-01-02T03:04:05.000006")
        self.assertEqual(obj.created_at, datetime(2020, 1, 2, 3, 4, 5, 6))

    def test_kwargs_class_is_ignored(self):
        """The __class__ key is not set as an attribute."""
        obj = BaseModel(__class__="Other")
        self.assertEqual(type(obj).__name__, "BaseModel")

    def test_kwargs_id_is_kept(self):
        """An id passed in kwargs is preserved."""
        self.assertEqual(BaseModel(id="abc").id, "abc")

    def test_str(self):
        """__str__ has the expected format without SQLAlchemy state."""
        obj = BaseModel()
        text = str(obj)
        self.assertTrue(text.startswith("[BaseModel] ({})".format(obj.id)))
        self.assertNotIn("_sa_instance_state", text)

    def test_to_dict(self):
        """to_dict returns the expected keys and formats."""
        obj = BaseModel(name="x")
        data = obj.to_dict()
        self.assertEqual(data["__class__"], "BaseModel")
        self.assertEqual(data["name"], "x")
        self.assertEqual(data["created_at"], obj.created_at.isoformat())
        self.assertNotIn("_sa_instance_state", data)

    def test_to_dict_is_a_copy(self):
        """to_dict does not alter the instance."""
        obj = BaseModel()
        obj.to_dict()
        self.assertIsInstance(obj.created_at, datetime)

    def test_to_dict_roundtrip(self):
        """An instance can be rebuilt from its to_dict output."""
        obj = BaseModel(name="x")
        clone = BaseModel(**obj.to_dict())
        self.assertEqual(clone.to_dict(), obj.to_dict())

    @unittest.skipIf(DB, "BaseModel is not mapped to a table")
    def test_save_updates_updated_at(self):
        """save() refreshes updated_at and stores the object."""
        obj = BaseModel()
        before = obj.updated_at
        obj.save()
        self.assertGreater(obj.updated_at, before)
        self.assertIn("BaseModel." + obj.id, models.storage.all())
        obj.delete()

    @unittest.skipIf(DB, "BaseModel is not mapped to a table")
    def test_new_not_called_by_init(self):
        """Creating an instance does not add it to storage."""
        obj = BaseModel()
        self.assertNotIn("BaseModel." + obj.id, models.storage.all())

    @unittest.skipIf(DB, "BaseModel is not mapped to a table")
    def test_delete(self):
        """delete() removes the instance from storage."""
        obj = BaseModel()
        obj.save()
        obj.delete()
        self.assertNotIn("BaseModel." + obj.id, models.storage.all())


if __name__ == "__main__":
    unittest.main()
