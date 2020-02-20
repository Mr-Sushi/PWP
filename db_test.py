import os
import pytest
import tempfile
import time
from datetime import datetime
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

import app
from app import User, Event, Organization

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
    
# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.app.config["TESTING"] = True
    
    with app.app.app_context():
        app.db.create_all()
        
    yield app.db
    
    app.db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)
    
def _get_user():
    return User(
        name="Test User",
        email="test.email@something.xyz",
        pwdhash="hash",
        location="Oulu",
        notifications="1"
    )
    
def _get_org():
    return Organization(
        name="OTiT",
    )
    
def _get_event():
    return Event(
        name="Test event",
        time="Today",
        description="hash",
        location="Oulu",
        organization="1"
    )
    
def test_create_instances(db_handle):
    """
    Tests that we can create one instance of each model and save them to the
    database using valid values for all columns. After creation, test that 
    everything can be found from database, and that all relationships have been
    saved correctly.
    """

    # Create everything
    user = _get_user()
    organization = _get_org() # create org first for event foreign key
    event = _get_event()
    db_handle.session.add(user)
    db_handle.session.add(organization)
    db_handle.session.add(event)
    db_handle.session.commit()
    
    # Check that everything exists
    assert User.query.count() == 1
    assert Organization.query.count() == 1
    assert Event.query.count() == 1
    db_user = User.query.first()
    db_organization = Organization.query.first()
    db_event = Event.query.first()
    
    # Check all relationships (both sides)
    assert db_event.organization == db_organization
    assert db_organization in db_event.organization
        
def test_something(db_handle):
    # update an existing model instance (x 3)
    
    user = _get_user()
    organization = _get_org()
    event = _get_event()
    
def test_something(db_handle):
    # remove an existing model from the database (x 3)
    
def test_something(db_handle):
    # ValueError (x 3)
    
def test_something(db_handle):
    # KeyError (x 3)
    
def test_something(db_handle):
    # IntegrityError (x 3)