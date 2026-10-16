#!/usr/bin/python3
"""Unit tests for the DBStorage class (use MySQLdb to check the database)."""
import os
import unittest
import models
from models.state import State
from models.city import City
from models.user import User
from models.place import Place
from models.review import Review
from models.amenity import Amenity

DB = os.getenv("HBNB_TYPE_STORAGE") == "db"
if DB:
    import MySQLdb


@unittest.skipUnless(DB, "DBStorage tests only run with HBNB_TYPE_STORAGE=db")
class TestDBStorage(unittest.TestCase):
    """Tests the DBStorage class against a real MySQL database."""

    def setUp(self):
        """Open a raw MySQLdb connection (isolated from SQLAlchemy)."""
        self.conn = MySQLdb.connect(host=os.getenv("HBNB_MYSQL_HOST"),
                                    user=os.getenv("HBNB_MYSQL_USER"),
                                    passwd=os.getenv("HBNB_MYSQL_PWD"),
                                    db=os.getenv("HBNB_MYSQL_DB"))
        self.conn.autocommit(True)
        self.cur = self.conn.cursor()

    def tearDown(self):
        """Close the raw connection."""
        self.cur.close()
        self.conn.close()

    def count(self, table):
        """Return the number of rows of a table."""
        self.cur.execute("SELECT COUNT(*) FROM {}".format(table))
        return self.cur.fetchone()[0]

    def test_docstrings(self):
        """Module, class and methods are documented."""
        from models.engine import db_storage
        self.assertTrue(len(db_storage.__doc__) > 10)
        self.assertTrue(len(db_storage.DBStorage.__doc__) > 10)
        for name in ("all", "new", "save", "delete", "reload"):
            self.assertTrue(
                len(getattr(db_storage.DBStorage, name).__doc__) > 10)

    def test_storage_type(self):
        """models.storage is a DBStorage instance."""
        from models.engine.db_storage import DBStorage
        self.assertIsInstance(models.storage, DBStorage)

    def test_save_adds_a_row(self):
        """Saving a State adds exactly one row."""
        before = self.count("states")
        state = State(name="California")
        state.save()
        self.assertEqual(self.count("states"), before + 1)
        state.delete()
        models.storage.save()

    def test_delete_removes_a_row(self):
        """Deleting a State removes exactly one row."""
        state = State(name="Nevada")
        state.save()
        before = self.count("states")
        state.delete()
        models.storage.save()
        self.assertEqual(self.count("states"), before - 1)

    def test_delete_none(self):
        """delete(None) does nothing."""
        before = self.count("states")
        models.storage.delete(None)
        models.storage.save()
        self.assertEqual(self.count("states"), before)

    def test_all_returns_dict(self):
        """all() returns <class>.<id> keys and objects as values."""
        state = State(name="Texas")
        state.save()
        everything = models.storage.all()
        self.assertIs(everything["State." + state.id], state)
        state.delete()
        models.storage.save()

    def test_all_with_class(self):
        """all(cls) only returns that class."""
        state = State(name="Texas")
        state.save()
        city = City(name="Austin", state_id=state.id)
        city.save()
        self.assertTrue(all(type(o) is City
                            for o in models.storage.all(City).values()))
        self.assertIn("City." + city.id, models.storage.all(City))
        self.assertNotIn("City." + city.id, models.storage.all(State))
        state.delete()
        models.storage.save()

    def test_cascade_delete(self):
        """Deleting a State deletes its Cities and their Places."""
        state = State(name="Oregon")
        state.save()
        city = City(name="Portland", state_id=state.id)
        city.save()
        user = User(email="a@b.c", password="p")
        user.save()
        place = Place(name="House", city_id=city.id, user_id=user.id)
        place.save()
        review = Review(text="ok", place_id=place.id, user_id=user.id)
        review.save()
        self.assertEqual(state.cities, [city])
        state.delete()
        user.delete()
        models.storage.save()
        for cls, obj in ((State, state), (City, city), (Place, place),
                         (Review, review), (User, user)):
            self.assertNotIn("{}.{}".format(cls.__name__, obj.id),
                             models.storage.all(cls))

    def test_many_to_many(self):
        """Linking amenities adds rows to place_amenity."""
        state = State(name="Utah")
        state.save()
        city = City(name="Provo", state_id=state.id)
        city.save()
        user = User(email="a@b.c", password="p")
        user.save()
        place = Place(name="House", city_id=city.id, user_id=user.id)
        place.save()
        wifi, oven = Amenity(name="Wifi"), Amenity(name="Oven")
        wifi.save()
        oven.save()
        before = self.count("place_amenity")
        place.amenities.append(wifi)
        place.amenities.append(oven)
        models.storage.save()
        self.assertEqual(self.count("place_amenity"), before + 2)
        state.delete()
        user.delete()
        wifi.delete()
        oven.delete()
        models.storage.save()
        self.assertEqual(self.count("place_amenity"), before)

    def test_defaults(self):
        """Place integer columns default to 0 in the database."""
        state = State(name="Idaho")
        state.save()
        city = City(name="Boise", state_id=state.id)
        city.save()
        user = User(email="a@b.c", password="p")
        user.save()
        place = Place(name="House", city_id=city.id, user_id=user.id)
        place.save()
        self.cur.execute("SELECT number_rooms, price_by_night, latitude "
                         "FROM places WHERE id=%s", (place.id,))
        self.assertEqual(self.cur.fetchone(), (0, 0, None))
        state.delete()
        user.delete()
        models.storage.save()


if __name__ == "__main__":
    unittest.main()
