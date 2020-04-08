import json
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import binascii, hashlib, os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    pwdhash = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(128))
    notifications = db.Column(db.Integer, nullable=False)
        
# Event model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    time = db.Column(db.DateTime(128), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(128))
    organization = db.Column(db.Integer, db.ForeignKey("organization.id"))
    
    org = db.relationship("Organization", back_populates="event")
    
# Organization model
class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    
    event = db.relationship("Event", back_populates="org")
    
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
\

