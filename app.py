from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import binascii, hashlib, os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Generate password hash
# https://www.vitoshacademy.com/hashing-passwords-in-python/
def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

# Add user
@app.route("/user/add/", methods=["GET", "POST"]) 
def add_user():
    if request.method == "POST":
        try:
            email = request.form["email"]
            user = User.query.filter_by(email=email).first()
            if user:
                return "This email is already in use", 409
            else:
                name = request.form["name"]
                email = request.form["email"]
                password = request.form["password"]
                pwdhash = hash_password(password)
                location = request.form["location"]
                notifications = int(request.form["notifications"])
                user = User(
                    name=name,
                    email=email,
                    pwdhash=pwdhash,
                    location=location,
                    notifications=notifications
                )
                db.session.add(user)
                db.session.commit()
        except (KeyError):
            return "Incomplete request: missing fields", 400
        except (IntegrityError):
            return "Integrity error", 400
        except (ValueError):
            return "Notifications must be integer (1 = enabled; 0 = disabled)", 400
    else:
        pass
    return "Add user"

# Edit user
@app.route("/user/edit/", methods=["GET", "POST"]) 
def edit_user():
    if request.method == "POST":
        try:
            user_id = int(request.form["user"])
            user = User.query.filter_by(id=user_id).first()
            if user:
                if request.form["name"]:
                    user.name = request.form["name"]
                else:
                    pass
                if request.form["email"]:
                    user.email = request.form["email"]
                else:
                    pass
                if request.form["password"]:
                    user.pwdhash = hash_password(request.form["password"])
                else:
                    pass
                if request.form["location"]:
                    user.location = request.form["location"]
                else:
                    pass
                if request.form["notifications"]:
                    user.notifications = int(request.form["notifications"])
                else:
                    pass # the last else must be there if you don't want an intendation error
                db.session.commit()
            else:
                return "User not found", 404
        except (KeyError):
            return "Incomplete request: missing fields", 400
        except (IntegrityError):
            return "Integrity error", 400
        except (ValueError):
            return "User ID and notifications (1 = enabled; 0 = disabled) must be integers", 400
    else:
        pass
    return "Edit user"
    
# Delete user
@app.route("/user/delete/", methods=["GET", "POST"]) 
def delete_user():
    if request.method == "POST":
        try:
            user_id = int(request.form["user"])
            user = User.query.filter_by(id=user_id).first()
            if user:
                db.session.delete(user)
                db.session.commit()
            else:
                return "User not found", 404
        except (ValueError):
            return "User ID must be integer", 400
        except (KeyError):
            return "User ID missing", 400
    return "Delete user"

# Add event
@app.route("/event/add/", methods=["GET", "POST"]) 
def add_event():
    if request.method == "POST":
        # submit the form
        try:
            name = request.form["name"]
            time = request.form["time"]
            description = request.form["description"]
            location = request.form["location"]
            organization = int(request.form["organization"])
        except (ValueError):
            return "Organization ID must be integer", 400
        else:
            try:
                event = Event(
                    name=name,
                    time=time,
                    description=description,
                    location=location,
                    organization=organization
                )
            except (ValueError):
                return "Incomplete request: missing fields", 400
            else:
                db.session.add(event)
                db.session.commit()
    else:
        pass
    return "Add event"

# Edit event
@app.route("/event/edit/", methods=["GET", "POST"]) 
def edit_event():
    if request.method == "POST":
        try:
            event_id = request.form["event"]
            event = Event.query.filter_by(id=event_id).first()
            if event:
                try:
                    if request.form["name"]:
                        event.name = request.form["name"]
                    if request.form["time"]:
                        event.time = request.form["time"]
                    if request.form["description"]:
                        event.description = request.form["description"]
                    if request.form["location"]:
                        event.location = request.form["location"]
                    if request.form["organization"]:
                        event.organization = int(request.form["organization"])
                except (ValueError):
                    return "Organization ID must be integer", 400
                else:
                    db.session.commit()
            else:
                return "Event not found", 404
        except (KeyError):
            return "Incomplete request: missing fields", 400
        except (ValueError):
            return "Inappropriate value", 400
    else:
        pass
    return "Edit event"
    
# Delete event
@app.route("/event/delete/", methods=["GET", "POST"]) 
def delete_event():
    if request.method == "POST":
        try:
            event_id = int(request.form["event"])
            event = Event.query.filter_by(id=event_id).first()
            if event:
                db.session.delete(event)
                db.session.commit()
            else:
                return "Event not found", 404
        except (ValueError):
            return "Event ID must be integer", 400
        except (KeyError):
            return "Imcomplete request: missing fields", 400
    return "Delete event"

# Add org
@app.route("/org/add/", methods=["GET", "POST"]) 
def add_org():
    if request.method == "POST":
        try:
            # submit the form
            name = request.form["name"]
            org = Organization(
                name=name
            )
        except (KeyError):
            return "Incomplete request: missing fields", 400
        else:
            db.session.add(org)
            db.session.commit()
    return "Add organization"

# Edit org
@app.route("/org/edit/", methods=["GET", "POST"]) 
def edit_org():
    if request.method == "POST":
        try:
            org_id = int(request.form["org"])
            organization = Organization.query.filter_by(id=org_id).first()
            if organization:
                if request.form["name"]:
                    organization.name = request.form["name"]
            else:
                return "Organization not found", 404
        except (KeyError):
            return "Incomplete request: missing fields", 400
        except (ValueError):
            return "Organization ID must be integer", 400
        else:
            db.session.commit()
    return "Edit organization"
    
# Delete org
@app.route("/org/delete/", methods=["GET", "POST"]) 
def delete_org():
    if request.method == "POST":
        try:
            org_id = int(request.form["org"])
            organization = Organization.query.filter_by(id=org_id).first()
            if organization:
                db.session.delete(organization)
                db.session.commit()
            else:
                return "Organization not found", 404
        except (ValueError):
            return "Organization ID must be integer", 400
        except (KeyError):
            return "Incomplete request: missing fields", 400
    return "Delete organization"

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    pwdhash = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(128))
    notifications = db.Column(db.Integer, nullable=False)
        
# Event model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    time = db.Column(db.String(128), nullable=False)
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