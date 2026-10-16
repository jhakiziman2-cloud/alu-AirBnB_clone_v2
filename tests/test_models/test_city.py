#!/usr/bin/python3
"""Unit tests for the City class."""
import os
import unittest
import models
from models.base_model import BaseModel, Base
from models.city import City


class TestCity(unittest.TestCase):
    """Tests the City class."""

    def test_docstrings(self):
        """Module and class are documented."""
        self.assertTrue(len(models.city.__doc__) > 10)
        self.assertTrue(len(City.__doc__) > 10)

    def test_inheritance(self):
        """City inherits from BaseModel and Base, in this order."""
        self.assertIsInstance(City(), BaseModel)
        self.assertEqual(City.__mro__[1:3], (BaseModel, Base))

    def test_tablename(self):
        """The table name is cities."""
        self.assertEqual(City.__tablename__, "cities")

    def test_columns(self):
        """The mapped columns exist."""
        columns = City.__table__.columns
        names = [
            "id", "created_at", "updated_at", "name", "state_id",
        ]
        for name in names:
            self.assertIn(name, columns)

    def test_column_nullability(self):
        """Mandatory columns can not be null."""
        columns = City.__table__.columns
        names = [
            "name", "state_id",
        ]
        for name in names:
            self.assertFalse(columns[name].nullable)
        names = []
        for name in names:
            self.assertTrue(columns[name].nullable)

    def test_kwargs(self):
        """Attributes can be given as keyword arguments."""
        obj = City(name='SF', state_id='abc')
        for key, value in dict(name='SF', state_id='abc').items():
            self.assertEqual(getattr(obj, key), value)

    def test_to_dict_class(self):
        """to_dict stores the class name."""
        self.assertEqual(City().to_dict()["__class__"], "City")

    def test_str(self):
        """__str__ starts with the class name."""
        self.assertTrue(str(City()).startswith("[City]"))

    def test_state_id_foreign_key(self):
        """state_id is a foreign key to states.id."""
        keys = [fk.target_fullname
                for fk in City.__table__.columns["state_id"].foreign_keys]
        self.assertEqual(keys, ["states.id"])


if __name__ == "__main__":
    unittest.main()
