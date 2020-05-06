import json
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import binascii, hashlib, os
from sqlalchemy import CheckConstraint

from eventhub import db

# Users associated to organizations
associations = db.Table("associations",
    db.Column("user", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("organization", db.Integer, db.ForeignKey("organization.id"), primary_key=True)
)

# Users following events
following = db.Table("following",
    db.Column("user", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("event", db.Integer, db.ForeignKey("event.id"), primary_key=True)
)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    pwdhash = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(128))
    notifications = db.Column(db.Integer, nullable=False)
    CheckConstraint(notifications ==0 or notifications ==1, name='check1')

    followed_events = db.relationship('Event', secondary=following)#,back_populates='users1')
    """
    related_orgs = db.relationship('Organization', secondary=associations, lazy='subquery',
        backref=db.backref('users2', lazy=True))
        """
    related_orgs = db.relationship('Organization',secondary=associations)#,back_populates='users2')
        
# Event model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    time = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(128))
    organization = db.Column(db.Integer, db.ForeignKey("organization.id"))
    
    org = db.relationship("Organization", back_populates="event")

    users1 = db.relationship('User',secondary=following)#,back_populates='followed_events')

    # users2 = db.relationship('User', secondary=following, lazy='subquery',
        # backref=db.backref('followed_events', lazy=True))
    
    
# Organization model
class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    
    event = db.relationship("Event", back_populates="org")

    #users1 = db.relationship('User', secondary=associations, lazy='subquery',
        #backref=db.backref('related_orgs', lazy=True))
    users2 = db.relationship('User',secondary=associations)#back_populates='related_orgs')

db.create_all()