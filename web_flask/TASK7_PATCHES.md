# models/engine/file_storage.py  (add to class FileStorage)
    def close(self):
        """Call reload() to deserialize the JSON file to objects."""
        self.reload()

# models/engine/db_storage.py  (add to class DBStorage)
    def close(self):
        """Call remove() on the private session attribute."""
        self.__session.remove()

# models/state.py  (add ONLY for the FileStorage branch, inside class State)
    if getenv('HBNB_TYPE_STORAGE') != 'db':
        @property
        def cities(self):
            """Return the list of City objects linked to this State."""
            from models import storage
            from models.city import City
            return [c for c in storage.all(City).values()
                    if c.state_id == self.id]
