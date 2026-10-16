#!/usr/bin/python3
"""Unit tests for the User class."""
import os
import unittest
import models
from models.base_model import BaseModel, Base
from models.user import User


class TestUser(unittest.TestCase):
    """Tests the User class."""

    def test_docstrings(self):
        """Module and class are documented."""
        self.assertTrue(len(models.user.__doc__) > 10)
        self.assertTrue(len(User.__doc__) > 10)

    def test_inheritance(self):
        """User inherits from BaseModel and Base, in this order."""
        self.assertIsInstance(User(), BaseModel)
        self.assertEqual(User.__mro__[1:3], (BaseModel, Base))

    def test_tablename(self):
        """The table name is users."""
        self.assertEqual(User.__tablename__, "users")

    def test_columns(self):
        """The mapped columns exist."""
        columns = User.__table__.columns
        names = [
            "id", "created_at", "updated_at", "email", "password",
            "first_name", "last_name",
        ]
        for name in names:
            self.assertIn(name, columns)

    def test_column_nullability(self):
        """Mandatory columns can not be null."""
        columns = User.__table__.columns
        names = [
            "email", "password",
        ]
        for name in names:
            self.assertFalse(columns[name].nullable)
        names = [
            "first_name", "last_name",
        ]
        for name in names:
            self.assertTrue(columns[name].nullable)

    def test_kwargs(self):
        """Attributes can be given as keyword arguments."""
        obj = User(email='a@b.c', password='pwd')
        for key, value in dict(email='a@b.c', password='pwd').items():
            self.assertEqual(getattr(obj, key), value)

    def test_to_dict_class(self):
        """to_dict stores the class name."""
        self.assertEqual(User().to_dict()["__class__"], "User")

    def test_str(self):
        """__str__ starts with the class name."""
        self.assertTrue(str(User()).startswith("[User]"))

    @unittest.skipUnless(os.getenv("HBNB_TYPE_STORAGE") == "db", "DBStorage")
    def test_relationships(self):
        """places and reviews are relationships that cascade deletes."""
        for name in ("places", "reviews"):
            rel = User.__mapper__.relationships[name]
            self.assertIn("delete", rel.cascade)
            self.assertEqual(rel.backref, "user")


if __name__ == "__main__":
    unittest.main()
