#!/usr/bin/python3
"""Starts a Flask web application for states and a single state."""
from flask import Flask, render_template
from models import storage
from models.state import State

app = Flask(__name__)


@app.teardown_appcontext
def teardown(exc):
    """Remove the current SQLAlchemy Session."""
    storage.close()


@app.route('/states', strict_slashes=False)
@app.route('/states/<id>', strict_slashes=False)
def states(id=None):
    """Display all states, or one state and its cities if id is given."""
    all_states = storage.all(State)
    if id is None:
        items = sorted(all_states.values(), key=lambda s: s.name)
        return render_template('9-states.html', states=items, state=None)
    state = all_states.get('State.' + id)
    return render_template('9-states.html', states=None, state=state,
                           found=state is not None)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
