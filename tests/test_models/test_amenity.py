#!/usr/bin/python3
"""Unit tests for the Amenity class."""
import os
import unittest
import models
from models.base_model import BaseModel, Base
from models.amenity import Amenity


class TestAmenity(unittest.TestCase):
    """Tests the Amenity class."""

    def test_docstrings(self):
        """Module and class are documented."""
        self.assertTrue(len(models.amenity.__doc__) > 10)
        self.assertTrue(len(Amenity.__doc__) > 10)

    def test_inheritance(self):
        """Amenity inherits from BaseModel and Base, in this order."""
        self.assertIsInstance(Amenity(), BaseModel)
        self.assertEqual(Amenity.__mro__[1:3], (BaseModel, Base))

    def test_tablename(self):
        """The table name is amenities."""
        self.assertEqual(Amenity.__tablename__, "amenities")

    def test_columns(self):
        """The mapped columns exist."""
        columns = Amenity.__table__.columns
        names = [
            "id", "created_at", "updated_at", "name",
        ]
        for name in names:
            self.assertIn(name, columns)

    def test_column_nullability(self):
        """Mandatory columns can not be null."""
        columns = Amenity.__table__.columns
        names = [
            "name",
        ]
        for name in names:
            self.assertFalse(columns[name].nullable)
        names = []
        for name in names:
            self.assertTrue(columns[name].nullable)

    def test_kwargs(self):
        """Attributes can be given as keyword arguments."""
        obj = Amenity(name='Wifi')
        for key, value in dict(name='Wifi').items():
            self.assertEqual(getattr(obj, key), value)

    def test_to_dict_class(self):
        """to_dict stores the class name."""
        self.assertEqual(Amenity().to_dict()["__class__"], "Amenity")

    def test_str(self):
        """__str__ starts with the class name."""
        self.assertTrue(str(Amenity()).startswith("[Amenity]"))


if __name__ == "__main__":
    unittest.main()
