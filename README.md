# AirBnB clone - MySQL (alu-AirBnB_clone_v2)

Second iteration of the HBNB (AirBnB clone) project: the command interpreter
now creates objects from parameters and the same code base can persist data
either in a JSON file (`FileStorage`) or in a MySQL database through
SQLAlchemy (`DBStorage`).

## Environment variables

| Variable | Meaning |
|---|---|
| `HBNB_ENV` | `dev` or `test` (tables are dropped at start-up when `test`) |
| `HBNB_MYSQL_USER` / `HBNB_MYSQL_PWD` | MySQL credentials |
| `HBNB_MYSQL_HOST` / `HBNB_MYSQL_DB` | MySQL host and database name |
| `HBNB_TYPE_STORAGE` | `file` (default, FileStorage) or `db` (DBStorage) |

## Requirements

Ubuntu 20.04, Python 3.8, MySQL 8.0, `SQLAlchemy 1.4.x`, `mysqlclient`
(`MySQLdb`), `pycodestyle 2.7.*`.

## Set-up

```
cat setup_mysql_dev.sql  | mysql -hlocalhost -uroot -p
cat setup_mysql_test.sql | mysql -hlocalhost -uroot -p
```

## Usage

```
# FileStorage
echo 'create State name="California"' | ./console.py

# DBStorage
echo 'create State name="California"' | \
HBNB_MYSQL_USER=hbnb_dev HBNB_MYSQL_PWD=hbnb_dev_pwd \
HBNB_MYSQL_HOST=localhost HBNB_MYSQL_DB=hbnb_dev_db \
HBNB_TYPE_STORAGE=db ./console.py
```

`create <Class> <key>=<value> ...` accepts strings (`name="My_house"`,
underscores become spaces, `\"` is a double quote), floats (`latitude=37.77`)
and integers (`number_rooms=4`). Invalid parameters are skipped.

Other commands: `show`, `destroy`, `all`, `count`, `update`, `quit`, `EOF`,
and the `<Class>.all()`, `.count()`, `.show(id)`, `.destroy(id)`,
`.update(id, attr, value)` forms.

## Tests

```
python3 -m unittest discover tests

HBNB_ENV=test HBNB_MYSQL_USER=hbnb_test HBNB_MYSQL_PWD=hbnb_test_pwd \
HBNB_MYSQL_HOST=localhost HBNB_MYSQL_DB=hbnb_test_db HBNB_TYPE_STORAGE=db \
python3 -m unittest discover tests
```

Tests that only make sense for one storage engine are skipped for the other
with `unittest.skipIf` / `skipUnless`.

## Files

| File | Description |
|---|---|
| `console.py` | command interpreter |
| `models/base_model.py` | `BaseModel` and SQLAlchemy `Base` |
| `models/{user,state,city,amenity,place,review}.py` | models (tables and relationships) |
| `models/engine/file_storage.py` | JSON storage with `all(cls)` and `delete()` |
| `models/engine/db_storage.py` | MySQL storage (SQLAlchemy) |
| `models/__init__.py` | selects the storage from `HBNB_TYPE_STORAGE` |
| `setup_mysql_dev.sql`, `setup_mysql_test.sql` | MySQL users and databases |
| `main_delete.py`, `main_place_amenities.py` | demo scripts |

## Authors

This project builds on the original AirBnB clone codebase and its initial
authors (see `AUTHORS`). Add your name and your teammates' names there.
