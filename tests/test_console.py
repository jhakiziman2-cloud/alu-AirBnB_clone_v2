#!/usr/bin/python3
"""Unit tests for the console (command interpreter)."""
import os
import unittest
from io import StringIO
from unittest.mock import patch
import models
from console import HBNBCommand

DB = os.getenv("HBNB_TYPE_STORAGE") == "db"
if DB:
    import MySQLdb


def run(command):
    """Run one console command and return what it printed."""
    with patch("sys.stdout", new=StringIO()) as out:
        HBNBCommand().onecmd(command)
    return out.getvalue().strip()


class TestConsoleDocs(unittest.TestCase):
    """Tests that do not depend on the storage engine."""

    def test_docstrings(self):
        """Module, class and commands are documented."""
        import console
        self.assertTrue(len(console.__doc__) > 10)
        self.assertTrue(len(HBNBCommand.__doc__) > 10)
        for name in dir(HBNBCommand):
            if name.startswith("do_") or name in ("default", "emptyline"):
                self.assertTrue(len(getattr(HBNBCommand, name).__doc__) > 10)

    def test_create_errors(self):
        """create validates the class name."""
        self.assertEqual(run("create"), "** class name missing **")
        self.assertEqual(run("create Nope"), "** class doesn't exist **")

    def test_show_errors(self):
        """show validates its arguments."""
        self.assertEqual(run("show"), "** class name missing **")
        self.assertEqual(run("show Nope"), "** class doesn't exist **")
        self.assertEqual(run("show State"), "** instance id missing **")
        self.assertEqual(run("show State 123"), "** no instance found **")

    def test_destroy_errors(self):
        """destroy validates its arguments."""
        self.assertEqual(run("destroy"), "** class name missing **")
        self.assertEqual(run("destroy Nope 1"), "** class doesn't exist **")
        self.assertEqual(run("destroy State"), "** instance id missing **")
        self.assertEqual(run("destroy State 1"), "** no instance found **")

    def test_all_error(self):
        """all validates the class name."""
        self.assertEqual(run("all Nope"), "** class doesn't exist **")

    def test_count_errors(self):
        """count validates its arguments."""
        self.assertEqual(run("count"), "** class name missing **")
        self.assertEqual(run("count Nope"), "** class doesn't exist **")

    def test_unknown_syntax(self):
        """Unknown commands are reported."""
        self.assertIn("Unknown syntax", run("hello"))

    def test_quit_and_eof(self):
        """quit and EOF stop the interpreter."""
        self.assertTrue(HBNBCommand().onecmd("quit"))
        with patch("sys.stdout", new=StringIO()):
            self.assertTrue(HBNBCommand().onecmd("EOF"))

    def test_emptyline(self):
        """An empty line prints nothing."""
        self.assertEqual(run(""), "")

    def test_parse_value_string(self):
        """Strings: underscores become spaces, escaped quotes are kept."""
        parse = HBNBCommand._parse_value
        self.assertEqual(parse('"My_little_house"'), "My little house")
        self.assertEqual(parse('"say_\\"hi\\""'), 'say "hi"')
        self.assertEqual(parse('""'), "")

    def test_parse_value_numbers(self):
        """Floats contain a dot, integers are the default case."""
        parse = HBNBCommand._parse_value
        self.assertEqual(parse("4"), 4)
        self.assertIsInstance(parse("4"), int)
        self.assertEqual(parse("-122.431297"), -122.431297)
        self.assertIsInstance(parse("3.0"), float)

    def test_parse_value_invalid(self):
        """Unrecognized values are rejected."""
        parse = HBNBCommand._parse_value
        for bad in ('"abc', 'abc"', '"a"b"', "abc", "1.2.3", '"', '"abc\\"'):
            self.assertIsNone(parse(bad), bad)


@unittest.skipIf(DB, "FileStorage console tests")
class TestConsoleFileStorage(unittest.TestCase):
    """Tests the console with FileStorage."""

    def setUp(self):
        """Isolate the objects and the JSON file."""
        from models.engine.file_storage import FileStorage
        self.fs = FileStorage
        self.path = FileStorage._FileStorage__file_path
        self.saved = dict(FileStorage._FileStorage__objects)
        FileStorage._FileStorage__objects.clear()
        if os.path.exists(self.path):
            os.rename(self.path, self.path + ".bak")

    def tearDown(self):
        """Restore the objects and the JSON file."""
        if os.path.exists(self.path):
            os.remove(self.path)
        if os.path.exists(self.path + ".bak"):
            os.rename(self.path + ".bak", self.path)
        self.fs._FileStorage__objects.clear()
        self.fs._FileStorage__objects.update(self.saved)

    def test_create_prints_id_and_stores(self):
        """create prints the new id and stores the object."""
        new_id = run("create State")
        self.assertIn("State." + new_id, models.storage.all())

    def test_create_with_string_param(self):
        """A string parameter is set with underscores as spaces."""
        new_id = run('create State name="New_York"')
        self.assertEqual(models.storage.all()["State." + new_id].name,
                         "New York")

    def test_create_with_all_types(self):
        """Strings, integers and floats are converted properly."""
        new_id = run('create Place city_id="0001" user_id="0001" '
                     'name="My_little_house" number_rooms=4 '
                     'price_by_night=300 latitude=37.773972 '
                     'longitude=-122.431297')
        place = models.storage.all()["Place." + new_id]
        self.assertEqual(place.name, "My little house")
        self.assertEqual(place.number_rooms, 4)
        self.assertIsInstance(place.number_rooms, int)
        self.assertEqual(place.latitude, 37.773972)
        self.assertEqual(place.longitude, -122.431297)
        self.assertEqual(place.city_id, "0001")

    def test_create_skips_invalid_params(self):
        """Invalid parameters are skipped, valid ones are kept."""
        new_id = run('create State name="Ohio" bad=abc oops "x=1 =3 '
                     'quote="a"b" value=1.2.3')
        state = models.storage.all()["State." + new_id]
        self.assertEqual(state.name, "Ohio")
        for attr in ("bad", "oops", "quote", "value"):
            self.assertNotIn(attr, state.__dict__)

    def test_create_escaped_quotes(self):
        """Escaped double quotes are kept inside the value."""
        new_id = run('create State name="The_\\"Golden\\"_State"')
        self.assertEqual(models.storage.all()["State." + new_id].name,
                         'The "Golden" State')

    def test_create_is_saved_to_file(self):
        """create writes the object to the JSON file."""
        new_id = run('create State name="Iowa"')
        with open(self.path) as file:
            self.assertIn("State." + new_id, file.read())

    def test_show(self):
        """show prints the object."""
        new_id = run('create State name="Iowa"')
        self.assertIn("[State] ({})".format(new_id),
                      run("show State " + new_id))

    def test_destroy(self):
        """destroy removes the object."""
        new_id = run("create State name=\"Iowa\"")
        run("destroy State " + new_id)
        self.assertNotIn("State." + new_id, models.storage.all())

    def test_all_and_count(self):
        """all prints a list and count prints the number of objects."""
        run('create State name="A"')
        run('create State name="B"')
        run('create City name="C" state_id="x"')
        self.assertEqual(run("count State"), "2")
        self.assertEqual(run("State.count()"), "2")
        self.assertEqual(run("all State").count("[State]"), 2)
        self.assertEqual(run("all").count("] ("), 3)
        self.assertEqual(run("City.all()").count("[City]"), 1)

    def test_update(self):
        """update sets an attribute."""
        new_id = run('create State name="A"')
        run('update State {} name "New York"'.format(new_id))
        self.assertEqual(models.storage.all()["State." + new_id].name,
                         "New York")
        run('State.update("{}", "name", "Texas")'.format(new_id))
        self.assertEqual(models.storage.all()["State." + new_id].name,
                         "Texas")
        run('State.update("{}", {{"name": "Utah", "x": 1}})'.format(new_id))
        state = models.storage.all()["State." + new_id]
        self.assertEqual((state.name, state.x), ("Utah", 1))

    def test_update_errors(self):
        """update validates attribute and value."""
        new_id = run('create State name="A"')
        self.assertEqual(run("update State " + new_id),
                         "** attribute name missing **")
        self.assertEqual(run("update State {} name".format(new_id)),
                         "** value missing **")

    def test_update_protected_attribute(self):
        """id can not be updated."""
        new_id = run('create State name="A"')
        run("update State {} id 1".format(new_id))
        self.assertIn("State." + new_id, models.storage.all())

    def test_class_show_and_destroy(self):
        """<Class>.show(id) and <Class>.destroy(id) work."""
        new_id = run('create State name="A"')
        self.assertIn(new_id, run('State.show("{}")'.format(new_id)))
        run('State.destroy("{}")'.format(new_id))
        self.assertNotIn("State." + new_id, models.storage.all())


@unittest.skipUnless(DB, "DBStorage console tests")
class TestConsoleDBStorage(unittest.TestCase):
    """Tests the console with DBStorage (rows counted with MySQLdb)."""

    def setUp(self):
        """Open a raw MySQLdb connection."""
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

    def test_create_state_adds_a_record(self):
        """create State name=... adds exactly one row to states."""
        before = self.count("states")
        new_id = run('create State name="California"')
        self.assertEqual(self.count("states"), before + 1)
        self.cur.execute("SELECT name FROM states WHERE id=%s", (new_id,))
        self.assertEqual(self.cur.fetchone()[0], "California")
        run("destroy State " + new_id)
        self.assertEqual(self.count("states"), before)

    def test_create_user_adds_a_record(self):
        """create User adds exactly one row to users."""
        before = self.count("users")
        new_id = run('create User email="a@b.c" password="pwd" '
                     'first_name="Bob"')
        self.assertEqual(self.count("users"), before + 1)
        run("destroy User " + new_id)
        self.assertEqual(self.count("users"), before)

    def test_all_shows_created_state(self):
        """all State lists the new state."""
        new_id = run('create State name="Maine"')
        self.assertIn(new_id, run("all State"))
        run("destroy State " + new_id)


if __name__ == "__main__":
    unittest.main()
