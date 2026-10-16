#!/usr/bin/python3
"""Unit tests for the Review class."""
import os
import unittest
import models
from models.base_model import BaseModel, Base
from models.review import Review


class TestReview(unittest.TestCase):
    """Tests the Review class."""

    def test_docstrings(self):
        """Module and class are documented."""
        self.assertTrue(len(models.review.__doc__) > 10)
        self.assertTrue(len(Review.__doc__) > 10)

    def test_inheritance(self):
        """Review inherits from BaseModel and Base, in this order."""
        self.assertIsInstance(Review(), BaseModel)
        self.assertEqual(Review.__mro__[1:3], (BaseModel, Base))

    def test_tablename(self):
        """The table name is reviews."""
        self.assertEqual(Review.__tablename__, "reviews")

    def test_columns(self):
        """The mapped columns exist."""
        columns = Review.__table__.columns
        names = [
            "id", "created_at", "updated_at", "text", "place_id", "user_id",
        ]
        for name in names:
            self.assertIn(name, columns)

    def test_column_nullability(self):
        """Mandatory columns can not be null."""
        columns = Review.__table__.columns
        names = [
            "text", "place_id", "user_id",
        ]
        for name in names:
            self.assertFalse(columns[name].nullable)
        names = []
        for name in names:
            self.assertTrue(columns[name].nullable)

    def test_kwargs(self):
        """Attributes can be given as keyword arguments."""
        obj = Review(text='Nice', place_id='p', user_id='u')
        for key, value in dict(text='Nice', place_id='p', user_id='u').items():
            self.assertEqual(getattr(obj, key), value)

    def test_to_dict_class(self):
        """to_dict stores the class name."""
        self.assertEqual(Review().to_dict()["__class__"], "Review")

    def test_str(self):
        """__str__ starts with the class name."""
        self.assertTrue(str(Review()).startswith("[Review]"))

    def test_foreign_keys(self):
        """place_id and user_id are foreign keys."""
        columns = Review.__table__.columns
        self.assertEqual([f.target_fullname
                          for f in columns["place_id"].foreign_keys],
                         ["places.id"])
        self.assertEqual([f.target_fullname
                          for f in columns["user_id"].foreign_keys],
                         ["users.id"])


if __name__ == "__main__":
    unittest.main()
