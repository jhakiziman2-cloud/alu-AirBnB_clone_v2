#!/usr/bin/python3
"""Unit tests for the Place class."""
import os
import unittest
import models
from models.base_model import BaseModel, Base
from models.place import Place


class TestPlace(unittest.TestCase):
    """Tests the Place class."""

    def test_docstrings(self):
        """Module and class are documented."""
        self.assertTrue(len(models.place.__doc__) > 10)
        self.assertTrue(len(Place.__doc__) > 10)

    def test_inheritance(self):
        """Place inherits from BaseModel and Base, in this order."""
        self.assertIsInstance(Place(), BaseModel)
        self.assertEqual(Place.__mro__[1:3], (BaseModel, Base))

    def test_tablename(self):
        """The table name is places."""
        self.assertEqual(Place.__tablename__, "places")

    def test_columns(self):
        """The mapped columns exist."""
        columns = Place.__table__.columns
        names = [
            "id", "created_at", "updated_at", "city_id", "user_id", "name",
            "description", "number_rooms", "number_bathrooms", "max_guest",
            "price_by_night", "latitude", "longitude",
        ]
        for name in names:
            self.assertIn(name, columns)

    def test_column_nullability(self):
        """Mandatory columns can not be null."""
        columns = Place.__table__.columns
        names = [
            "city_id", "user_id", "name", "number_rooms", "number_bathrooms",
            "max_guest", "price_by_night",
        ]
        for name in names:
            self.assertFalse(columns[name].nullable)
        names = [
            "description", "latitude", "longitude",
        ]
        for name in names:
            self.assertTrue(columns[name].nullable)

    def test_kwargs(self):
        """Attributes can be given as keyword arguments."""
        obj = Place(name='House', number_rooms=2, latitude=1.5)
        expected = dict(name='House', number_rooms=2, latitude=1.5)
        for key, value in expected.items():
            self.assertEqual(getattr(obj, key), value)

    def test_to_dict_class(self):
        """to_dict stores the class name."""
        self.assertEqual(Place().to_dict()["__class__"], "Place")

    def test_str(self):
        """__str__ starts with the class name."""
        self.assertTrue(str(Place()).startswith("[Place]"))

    def test_integer_defaults(self):
        """Integer columns default to 0."""
        columns = Place.__table__.columns
        for name in ("number_rooms", "number_bathrooms", "max_guest",
                     "price_by_night"):
            self.assertEqual(columns[name].default.arg, 0)

    def test_foreign_keys(self):
        """city_id and user_id are foreign keys."""
        columns = Place.__table__.columns
        self.assertEqual([f.target_fullname
                          for f in columns["city_id"].foreign_keys],
                         ["cities.id"])
        self.assertEqual([f.target_fullname
                          for f in columns["user_id"].foreign_keys],
                         ["users.id"])

    def test_place_amenity_table(self):
        """The place_amenity association table is defined."""
        from models.place import place_amenity
        self.assertEqual(place_amenity.name, "place_amenity")
        self.assertIs(place_amenity.metadata, Base.metadata)
        for column in place_amenity.columns:
            self.assertTrue(column.primary_key)
            self.assertFalse(column.nullable)

    @unittest.skipIf(os.getenv("HBNB_TYPE_STORAGE") == "db", "FileStorage")
    def test_reviews_getter(self):
        """reviews returns the Review instances linked to the Place."""
        from models.review import Review
        place = Place(name="p")
        mine = Review(text="t", place_id=place.id, user_id="u")
        other = Review(text="t", place_id="x", user_id="u")
        models.storage.new(mine)
        models.storage.new(other)
        self.assertEqual(place.reviews, [mine])
        models.storage.delete(mine)
        models.storage.delete(other)

    @unittest.skipIf(os.getenv("HBNB_TYPE_STORAGE") == "db", "FileStorage")
    def test_amenities_setter_and_getter(self):
        """Only Amenity objects can be linked, without duplicates."""
        from models.amenity import Amenity
        place = Place(name="p")
        amenity = Amenity(name="Wifi")
        models.storage.new(amenity)
        place.amenities = amenity
        place.amenities = amenity
        place.amenities = "not an amenity"
        place.amenities = Place()
        self.assertEqual(place.amenity_ids, [amenity.id])
        self.assertEqual(place.amenities, [amenity])
        models.storage.delete(amenity)

    @unittest.skipIf(os.getenv("HBNB_TYPE_STORAGE") == "db", "FileStorage")
    def test_amenities_append(self):
        """append() on place.amenities links the Amenity."""
        from models.amenity import Amenity
        place = Place(name="p")
        other_place = Place(name="q")
        amenity = Amenity(name="Wifi")
        models.storage.new(amenity)
        place.amenities.append(amenity)
        self.assertEqual(place.amenity_ids, [amenity.id])
        self.assertEqual(other_place.amenity_ids, [])
        models.storage.delete(amenity)

    @unittest.skipUnless(os.getenv("HBNB_TYPE_STORAGE") == "db", "DBStorage")
    def test_amenities_relationship(self):
        """amenities is a many-to-many relationship (not view only)."""
        rel = Place.__mapper__.relationships["amenities"]
        self.assertFalse(rel.viewonly)
        self.assertEqual(rel.secondary.name, "place_amenity")


if __name__ == "__main__":
    unittest.main()
