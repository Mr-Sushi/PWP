import os
import pytest
import tempfile
import time
from datetime import datetime
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from eventhub import  db ,app
from eventhub.models import Event, User, Organization

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
    # app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    # app.app.config["TESTING"] = True
    app.config["TESTING"] = True
    
    # with app.app.app_context():
    with app.app_context():
        db.create_all()
        
    yield db
    
    db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)
    
def _get_user():
    return User(
        name="Test User",
        email="db_test.email@something.xyz",
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
        description="Something",
        location="Oulu",
    )
    
def test_create_instances(db_handle):
    """
    Create one instance of each model and save them to the database using valid
    values. Everything is found from the database and the relationships have
    been saved correclty.
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
    
    # Check relationships
    db_organization = Organization.query.first()
    db_event = Event.query.first()
    assert db_event.organization == db_organization.id
    
def test_user_unique_email(db_handle):
    """
    Another user can't be created with the same email.
    """
    
    user_1 = _get_user()
    user_2 = _get_user()
    db_handle.session.add(user_1)
    db_handle.session.add(user_2)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
        
    db_handle.session.rollback()
    
def test_user_values(db_handle):
    """
    Notifications is integer.
    """
    
    user = _get_user()
    user.notifications = "something"
    db_handle.session.add(user)
    with pytest.raises(StatementError):
        db_handle.session.commit()
        # Doesn't raise StatementError?
        
    db_handle.session.rollback()
    
def test_event_values(db_handle):
    """
    Events must have correct date formatting and the organization is integer.
    """
    
    event = _get_event()
    event.time = "something"
    event.organization = "something"
    db_handle.session.add(event)
    with pytest.raises(StatementError):
        db_handle.session.commit()
        
    db_handle.session.rollback()
    
def test_edit_instances(db_handle):
    """
    Edit the instances.
    """
    
    user = User.query.first().update(_get_user())
    organization = Organization.query.first().update(_get_org())
    event = Event.query.first().update(_get_event())
    # user = _get_user()
    # organization = _get_org()
    # event = _get_event()

    db_handle.session.commit()
        
def test_delete_instances(db_handle):
    """
    Delete the instances.
    """
    
    user = _get_user()
    organization = _get_org()
    event = _get_event()
    db_handle.session.add(user)
    db_handle.session.add(organization)
    db_handle.session.add(event)
    db_handle.session.commit()
    db_handle.session.delete(user)
    db_handle.session.delete(organization)
    db_handle.session.delete(event)
    db_handle.session.commit()
    
def test_measurement_ondelete_organization(db_handle):
    """
    When an organization is deleted, the event's foreign key is null.
    """
    
    event = _get_event()
    organization = _get_org()
    event.organization = organization.id
    db_handle.session.add(event)
    db_handle.session.add(organization)
    db_handle.session.commit()
    db_handle.session.delete(organization)
    db_handle.session.commit()
    assert event.organization is None