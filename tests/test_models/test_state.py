#!/usr/bin/python3
"""Unit tests for the State class."""
import os
import unittest
import models
from models.base_model import BaseModel, Base
from models.state import State


class TestState(unittest.TestCase):
    """Tests the State class."""

    def test_docstrings(self):
        """Module and class are documented."""
        self.assertTrue(len(models.state.__doc__) > 10)
        self.assertTrue(len(State.__doc__) > 10)

    def test_inheritance(self):
        """State inherits from BaseModel and Base, in this order."""
        self.assertIsInstance(State(), BaseModel)
        self.assertEqual(State.__mro__[1:3], (BaseModel, Base))

    def test_tablename(self):
        """The table name is states."""
        self.assertEqual(State.__tablename__, "states")

    def test_columns(self):
        """The mapped columns exist."""
        columns = State.__table__.columns
        names = [
            "id", "created_at", "updated_at", "name",
        ]
        for name in names:
            self.assertIn(name, columns)

    def test_column_nullability(self):
        """Mandatory columns can not be null."""
        columns = State.__table__.columns
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
        obj = State(name='California')
        for key, value in dict(name='California').items():
            self.assertEqual(getattr(obj, key), value)

    def test_to_dict_class(self):
        """to_dict stores the class name."""
        self.assertEqual(State().to_dict()["__class__"], "State")

    def test_str(self):
        """__str__ starts with the class name."""
        self.assertTrue(str(State()).startswith("[State]"))

    @unittest.skipIf(os.getenv("HBNB_TYPE_STORAGE") == "db", "FileStorage")
    def test_cities_getter(self):
        """cities returns the City instances linked to the State."""
        from models.city import City
        state = State(name="California")
        city = City(name="SF", state_id=state.id)
        other = City(name="LA", state_id="other")
        models.storage.new(city)
        models.storage.new(other)
        self.assertEqual(state.cities, [city])
        models.storage.delete(city)
        models.storage.delete(other)

    @unittest.skipUnless(os.getenv("HBNB_TYPE_STORAGE") == "db", "DBStorage")
    def test_cities_relationship(self):
        """cities is a relationship that cascades deletes."""
        rel = State.__mapper__.relationships["cities"]
        self.assertIn("delete", rel.cascade)
        self.assertEqual(rel.backref, "state")


if __name__ == "__main__":
    unittest.main()
