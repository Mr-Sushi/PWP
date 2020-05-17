import os
import pytest
import tempfile
import time
import sys
from datetime import datetime
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from eventhub import  db,app
from eventhub.models import Event, User, Organization, OrgsAndUsers, EventsAndUsers

sys.path.append('../')

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
    
# based on http://flask.pocoo.org/docs/1.0/testing/ and https://lovelace.oulu.fi/ohjelmoitava-web/programmable-web-project-spring-2020/testing-flask-applications/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    #app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.config["TESTING"] = True
    
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
        name="org1",
    )

def _get_event():
    return Event(
        name="Test event",
        time = "05.05.2020",
        description="Something",
        location="Oulu",
        organization="1"
    )

def _get_association():
    return OrgsAndUsers(
        user_id = 1,
        org_id = 1
    )

def _get_following():
    return EventsAndUsers(
        user_id = 1,
        event_id = 1
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
    association = _get_association()
    following = _get_following()
    db_handle.session.add(user)
    db_handle.session.add(organization)
    db_handle.session.add(event)
    db_handle.session.add(following)
    db_handle.session.add(association)
    db_handle.session.commit()
    
    # Check that everything exists
    assert User.query.count() == 1
    assert Organization.query.count() == 1
    assert Event.query.count() == 1
    
    # Check relationships
    db_organization = Organization.query.first()
    db_event = Event.query.first()
    db_user = User.query.first()
    assert db_event.organization == db_organization.id

    assert following.event_id == db_event.id
    assert following.user_id == db_user.id

    assert association.org_id == db_organization.id
    assert association.user_id == db_user.id

#test uniqueness
def test_org_name_unique(db_handle):
    """
    the name of organization must be unique
    """
    organization = _get_org()
    db_handle.session.add(organization)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

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

# test the variable type of each entity
def test_user_values(db_handle):
    """
    Notifications is integer.
    """
    
    user = _get_user()
    user.notifications = "something"
    db_handle.session.add(user)
    with pytest.raises(StatementError):
        db_handle.session.commit()
    
    db_handle.session.rollback()
    
def test_event_values(db_handle):
    """
    The organization is integer.
    """
    
    event = _get_event()
    event.time = "12:05"
    event.organization = "something"
    db_handle.session.add(event)
    with pytest.raises(StatementError):
        db_handle.session.commit()
        
    db_handle.session.rollback()
    
def test_edit_instances(db_handle):
    """
    Edit the instances.
    """
    user = User.query.filter_by(id=1).first()
    user.name = "edited_name"
    db_handle.session.commit()
    user = User.query.filter_by(id=1).first()
    assert user.name == "edited_name"
        
def test_delete_instances(db_handle):
    """
    Delete the instances.
    """
    user = User.query.filter_by(id=1).first()
    organization = Organization.query.filter_by(id=1).first()
    event = Event.query.filter_by(id=1).first()
    assert user
    assert organization
    assert event
    db_handle.session.delete(user)
    db_handle.session.delete(organization)
    db_handle.session.delete(event)
    db_handle.session.commit()
    user = User.query.filter_by(id=1).first()
    organization = Organization.query.filter_by(id=1).first()
    event = Event.query.filter_by(id=1).first()
    assert user is None
    assert organization is None
    assert event is None

    
def test_event_ondelete_organization(db_handle):
    """
    When an organization is deleted, the event's foreign key is null.
    """
    
    event = _get_event()
    #event = Event.query.filter_by(id=1).first()
    organization = _get_org()
    #organization = Organization.query.filter_by(id=1).first()
    event.organization = organization.id
    
    db_handle.session.add(event)
    db_handle.session.add(organization)
    db_handle.session.commit()
    db_handle.session.delete(organization)
    db_handle.session.commit()
    assert event.organization is None


def test_following_ondelete_event(db_handle):
    """
    When an event or user is deleted, the "following" relationship is deleted, too.
    """
    user = _get_user()
    #because event already exists, so no need to add the event
    #event = _get_event()
    following = _get_following()
    db_handle.session.add(user)
    #db.session.add(event)
    db_handle.session.add(following)
    db_handle.session.commit()
    assert EventsAndUsers.query.filter_by(event_id=1).first()
    event = Event.query.filter_by(id=1).first()
    db_handle.session.delete(event)
    db_handle.session.commit()
    following = EventsAndUsers.query.filter_by(event_id=1).first()
    assert following is None

def test_associations_ondelete_org(db_handle):
    """
    When an organization or user is deleted, the "association" relationship is deleted, too.
    """
    assert User.query.filter_by(id=1).first()
    #user = _get_user()
    org = _get_org()
    association = _get_association()
    #db_handle.session.add(user)
    db_handle.session.add(org)
    db_handle.session.add(association)
    db_handle.session.commit()
    assert association
    db_handle.session.delete(org)
    db_handle.session.commit()
    association_1 = OrgsAndUsers.query.filter_by(org_id=1).first()
    assert association_1 is None


User.query.delete()
Organization.query.delete()
Event.query.delete()
EventsAndUsers.query.delete()
OrgsAndUsers.query.delete()
