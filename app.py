from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
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
                return 0;
            else:
                name = request.form["name"]
                email = request.form["email"]
                password = request.form["password"]
                pwdhash = hash_password(password)
                location = request.form["location"]
                notifications = request.form["notifications"]
                user = User(
                    name=name,
                    email=email,
                    pwdhash=pwdhash,
                    location=location,
                    notifications=notifications
                )
                db.session.add(user)
                db.session.commit()
        except KeyError:
            return "Missing query parameter: email", 400
    else:
        pass
    return "asd"

# Edit user
@app.route("/user/edit/")
def edit_user():
    if request.method == "POST":
        try:
            user_id = request_form["user"]
            user = User.query.filter_by(id=user_id).first()
            if user:
                name = request.form["name"]
                email = request.form["email"]
                # password = request.form["password"]
                # the user has to update the password each time they update their information
                # it should not behave like this but maybe we can overlook it for now
                # pwdhash = hash_password(password)
                location = request.form["location"]
                notifications = request.form["notifications"]
                user = User(
                    name=name,
                    email=email,
                    #pwdhash=pwdhash,
                    location=location,
                    notifications=notifications
                )
                db.session.add(user)
                db.session.commit()
            else:
                abort(404)
        except (KeyError, ValueError, IntegrityError):
            abort(400)
    else:
        pass
    return 0
    
# Delete user
@app.route("/user/delete/")
def delete_user():
    if request.method == "POST":
        try:
            user_id = request_form["user"]
            user = User.query.filter_by(id=user_id).first()
            if user:
                db.session.delete(user)
                db.session.commit()
            else:
                abort(404)  
        except (KeyError, ValueError, IntegrityError):
            abort(400)
    return 0

# Add event
@app.route("/event/add/")
def add_event():
    if request.method == "POST":
        # submit the form
        name = request.form["name"]
        time = request.form["time"]
        description = request.form["description"]
        location = request.form["location"]
        organization = request.form["organization"]
        event = Event(
            name=name,
            time=time,
            description=description,
            location=location,
            organization=organization
        )
        db.session.add(event)
        db.session.commit()
    else:
        pass
    return 0

# Edit event
@app.route("/event/edit/")
def edit_event():
    if request.method == "POST":
        try:
            event_id = request_form["event"]
            event = Event.query.filter_by(id=event_id).first()
            if event:
                name = request.form["name"]
                time = request.form["time"]
                description = request.form["description"]
                location = request.form["location"]
                organization = request.form["organization"]
                event = Event(
                    name=name,
                    time=time,
                    description=description,
                    location=location,
                    organization=organization
                )
                db.session.add(event)
                db.session.commit()
            else:
                abort(404)
        except (KeyError, ValueError, IntegrityError):
            abort(400)
    else:
        pass
    return 0
    
# Delete event
@app.route("/event/delete/")
def delete_event():
    if request.method == "POST":
        try:
            event_id = request_form["event"]
            event = Event.query.filter_by(id=event_id).first()
            if event:
                db.session.delete(event)
                db.session.commit()
            else:
                abort(404)  
        except (KeyError, ValueError, IntegrityError):
            abort(400)
    return 0

# Add org
@app.route("/org/add/")
def add_org():
    if request.method == "POST":
        # submit the form
        org_name = request.form["organization"]
        org = Organization(
            name=org_name
        )
        db.session.add(org)
        db.session.commit()
    return 0

# Edit org
@app.route("/org/edit/")
def edit_org():
    if request.method == "POST":
        try:
            org_id = request_form["org"]
            organization = Organization.query.filter_by(id=org_id).first()
            if organization:
                org_name = request.form["organization"]
                org = Organization(
                    name=org_name
                )
                db.session.add(org)
                db.session.commit()
            else:
                abort(404)  
        except (KeyError, ValueError, IntegrityError):
            abort(400)
    return 0
    
# Delete org
@app.route("/org/delete/")
def delete_org():
    if request.method == "POST":
        try:
            org_id = request_form["org"]
            organization = Organization.query.filter_by(id=org_id).first()
            if organization:
                db.session.delete(organization)
                db.session.commit()
            else:
                abort(404)
        except (KeyError, ValueError, IntegrityError):
            abort(400)
    return 0

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    pwdhash = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(128))
    notifications = db.Column(db.Boolean, nullable=False)
    #following = db.Column(db.String(255), db.ForeignKey("event.id"))
    
    follow = db.relationship("Event", back_populates="user")
        
# Event model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    time = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(128))
    organization = db.Column(db.Integer, db.ForeignKey("organization.id"))
    
    org = db.relationship("Organization", back_populates="event")
    user = db.relationship("User", back_populates="follow")
    
# Organization model
class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    
    event = db.relationship("Event", back_populates="org")
    
# Users associated to organizations
associations = db.Table("associations",
    db.Column("user_id", db.Integer, db.ForeignKey("user", primary_key=True)),
    db.Column("organization_id", db.Integer, db.ForeignKey("organization", primary_key=True))
)

# Users following events
following = db.Table("following",
    db.Column("user", db.Integer, db.ForeignKey("user.id", primary_key=True)),
    db.Column("event", db.Integer, db.ForeignKey("event.id", primary_key=True))
)