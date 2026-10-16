#!/usr/bin/python3
"""Command interpreter for the HBNB project."""
import cmd
import re
import shlex
import ast
import models
from models.base_model import BaseModel
from models.user import User
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.place import Place
from models.review import Review


class HBNBCommand(cmd.Cmd):
    """Command interpreter class."""
    prompt = "(hbnb) "
    classes = {"BaseModel": BaseModel, "User": User, "State": State,
               "City": City, "Amenity": Amenity, "Place": Place,
               "Review": Review}
    protected = ("id", "created_at", "updated_at", "__class__")

    @staticmethod
    def _parse_value(value):
        """Convert a raw parameter value to str, float or int.

        Return None when the value does not fit any supported syntax.
        """
        if value.startswith('"'):
            if len(value) < 2 or not value.endswith('"'):
                return None
            inner = value[1:-1]
            if inner.endswith("\\") or re.search(r'(?<!\\)"', inner):
                return None
            return inner.replace('\\"', '"').replace("_", " ")
        if "." in value:
            try:
                return float(value)
            except ValueError:
                return None
        try:
            return int(value)
        except ValueError:
            return None

    @staticmethod
    def _cast(obj, attr, value):
        """Cast value to the type of the current attribute when numeric."""
        current = getattr(obj, attr, None)
        if isinstance(current, (int, float)) and \
                not isinstance(current, bool):
            try:
                return type(current)(value)
            except (TypeError, ValueError):
                return current
        return value

    def _get_obj(self, args):
        """Validate [class, id] args and return (key, object) or None."""
        if not args:
            print("** class name missing **")
        elif args[0] not in self.classes:
            print("** class doesn't exist **")
        elif len(args) < 2:
            print("** instance id missing **")
        else:
            key = "{}.{}".format(args[0], args[1])
            objs = models.storage.all()
            if key in objs:
                return key, objs[key]
            print("** no instance found **")
        return None

    def _set_attr(self, obj, attr, value):
        """Set attr on obj (unless protected) and save it."""
        if attr in self.protected:
            return
        setattr(obj, attr, self._cast(obj, attr, value))

    def do_quit(self, arg):
        """Quit command to exit the program."""
        return True

    def do_EOF(self, arg):
        """EOF signal to exit the program."""
        print()
        return True

    def emptyline(self):
        """Do nothing on an empty line."""
        pass

    def do_create(self, arg):
        """Create an instance: create <Class> <key>=<value> ..."""
        args = arg.split()
        if not args:
            print("** class name missing **")
            return
        if args[0] not in self.classes:
            print("** class doesn't exist **")
            return
        params = {}
        for item in args[1:]:
            if "=" not in item:
                continue
            key, value = item.split("=", 1)
            value = self._parse_value(value)
            if key and value is not None:
                params[key] = value
        obj = self.classes[args[0]](**params)
        obj.save()
        print(obj.id)

    def do_show(self, arg):
        """Print the string representation: show <Class> <id>."""
        found = self._get_obj(arg.split())
        if found:
            print(found[1])

    def do_destroy(self, arg):
        """Delete an instance: destroy <Class> <id>."""
        found = self._get_obj(arg.split())
        if found:
            models.storage.delete(found[1])
            models.storage.save()

    def do_all(self, arg):
        """Print all instances, optionally of one class: all [Class]."""
        args = arg.split()
        if args and args[0] not in self.classes:
            print("** class doesn't exist **")
            return
        cls = self.classes[args[0]] if args else None
        objs = models.storage.all(cls)
        print("[{}]".format(", ".join(str(obj) for obj in objs.values())))

    def do_count(self, arg):
        """Print the number of instances of a class: count <Class>."""
        args = arg.split()
        if not args:
            print("** class name missing **")
        elif args[0] not in self.classes:
            print("** class doesn't exist **")
        else:
            print(len(models.storage.all(self.classes[args[0]])))

    def do_update(self, arg):
        """Update an instance: update <Class> <id> <attribute> <value>."""
        try:
            args = shlex.split(arg)
        except ValueError:
            args = arg.split()
        found = self._get_obj(args)
        if not found:
            return
        if len(args) < 3:
            print("** attribute name missing **")
        elif len(args) < 4:
            print("** value missing **")
        else:
            self._set_attr(found[1], args[2], args[3])
            found[1].save()

    def default(self, line):
        """Handle <Class>.all(), .count(), .show(), .destroy(), .update()."""
        match = re.match(r"^(\w+)\.(\w+)\((.*)\)$", line.strip())
        if not match:
            print("*** Unknown syntax: {}".format(line))
            return
        name, method, rest = match.groups()
        if method in ("all", "count"):
            return getattr(self, "do_" + method)(name)
        if method in ("show", "destroy"):
            return getattr(self, "do_" + method)(
                "{} {}".format(name, rest.strip(" \"'")))
        if method == "update":
            dict_match = re.match(
                r"^\s*[\"']?([^\"',]*)[\"']?\s*,\s*(\{.*\})$", rest)
            if dict_match:
                found = self._get_obj([name, dict_match.group(1)])
                if found:
                    try:
                        values = ast.literal_eval(dict_match.group(2))
                    except (ValueError, SyntaxError):
                        return
                    for attr, value in values.items():
                        self._set_attr(found[1], attr, value)
                    found[1].save()
                return
            parts = [p.strip().strip("\"'") for p in rest.split(",", 2)]
            return self.do_update("{} {}".format(
                name, " ".join(['"{}"'.format(p) for p in parts])))
        print("*** Unknown syntax: {}".format(line))


if __name__ == "__main__":
    HBNBCommand().cmdloop()
