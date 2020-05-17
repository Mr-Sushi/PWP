import json
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import binascii, hashlib, os
from sqlalchemy import CheckConstraint

from eventhub import db
"""
# Users associated to organizations
associations = db.Table("associations",
    db.Column("user", db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    db.Column("organization", db.Integer, db.ForeignKey("organization.id", ondelete="CASCADE"), primary_key=True)
)

# Users following events
following = db.Table("following",
    db.Column("user", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("event", db.Integer, db.ForeignKey("event.id"), primary_key=True)
)
"""
class EventsAndUsers(db.Model):
    __tablename__ = "following"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id", ondelete="CASCADE"),primary_key=True)

    user1 = db.relationship("User", back_populates="events")
    event = db.relationship("Event", back_populates="users1")

class OrgsAndUsers(db.Model):
    __tablename__ = "associations"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey("organization.id", ondelete="CASCADE"),primary_key=True)

    user2 = db.relationship("User", back_populates="orgs")
    org = db.relationship("Organization", back_populates="users2")


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    pwdhash = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(128))
    notifications = db.Column(db.Integer,CheckConstraint('notifications IN (0, 1)'), nullable=False)

    #followed_events = db.relationship('Event', secondary=following)#,back_populates='users1')
    """
    related_orgs = db.relationship('Organization', secondary=associations, lazy='subquery',
        backref=db.backref('users2', lazy=True))
        """
    #related_orgs = db.relationship("Organization",secondary=associations)#,back_populates='users2')

    events = db.relationship("EventsAndUsers", back_populates="user1", cascade="all,delete-orphan")#delete-orphan
    orgs = db.relationship("OrgsAndUsers", back_populates="user2", cascade="all,delete-orphan")

        
# Event model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128),nullable=False)
    time = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(128))
    organization = db.Column(db.Integer, db.ForeignKey("organization.id", ondelete="CASCADE"))
    
    org = db.relationship("Organization", back_populates="event")

    #users1 = db.relationship("User",secondary=following)#,back_populates='followed_events')

    users1 = db.relationship("EventsAndUsers", back_populates="event", cascade="all,delete-orphan")
    
    
# Organization model
class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True,nullable=False)
    
    event = db.relationship("Event", back_populates="org")

    #users1 = db.relationship('User', secondary=associations, lazy='subquery',
        #backref=db.backref('related_orgs', lazy=True))
    #users2 = db.relationship('User',secondary=associations)#back_populates='related_orgs')
    users2 = db.relationship("OrgsAndUsers", back_populates="org", cascade="all,delete-orphan")

db.create_all()