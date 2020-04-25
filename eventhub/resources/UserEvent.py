from flask_restful import Resource, Api


from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, Response, current_app
from .UserItem import UserItem
from eventhub import db
from eventhub.models import Event, User, following
from eventhub.utils import InventoryBuilder, MasonBuilder, create_error_response
import json

from jsonschema import validate, ValidationError
from .EventItem import EventItem

LINK_RELATIONS_URL = "/eventhub/link-relations/"

USER_PROFILE = "/profiles/user/"
ORG_PROFILE = "/profile/org/"
EVENT_PROFILE = "/profiles/event/"
ERROR_PROFILE = "/profiles/error/"

MASON = "application/vnd.mason+json"

class EventsByUser(Resource):
    def get(self, user_id):
        """
        Get all the events information for a user
        Parameters:
            - id: Integer, user id
        Response:
            - 404: "User not found", "User ID {} was not found"
            - 400: KeyError and ValueError (something else was found)
            - 200: Return the events information
        """
        api = Api(current_app)
        body = InventoryBuilder(items=[])
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return create_error_response(404, "Not found",
                                        "User ID {} was not found".format(user_id))
        body["user"] = {"user_id":user.id,"name":user.name}

        body.add_namespace("eventhub", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(UserItem, id=user_id))
        body.add_control("profile", USER_PROFILE)
        body.add_control_delete_user(user_id)
        body.add_control_edit_user(user_id)
        body.add_control_all_users()
        try:
            # find all the events
            followed_events = Event.query.filter(User.followed_events.any(id=user_id)).all()
            # for each event, find specific information
            for i in followed_events:
                event = InventoryBuilder()
                event["name"] = i.name
                event["time"] = i.time
                event["description"] = i.description
                event["location"] = i.location
                event["organization"] = i.organization

                event.add_namespace("eventhub", LINK_RELATIONS_URL)
                event.add_control("self", api.url_for(EventItem, id=i.id))
                event.add_control("profile", EVENT_PROFILE)
                event.add_control_delete_event(i.id)
                event.add_control_edit_event(i.id)
                event.add_control_all_events()
                body["items"].append(event)  

            return Response(json.dumps(body), 200, mimetype=MASON)
        except (KeyError, ValueError):
            abort(400)


class UsersByEvent(Resource):
    def get(self, event_id):
        """
        Get all the users' email for a event
        Parameters:
            - id: Integer, event id
        Response:
            - 404: "Event not found", "Event ID {} was not found"
            - 400: KeyError and ValueError (something else was found)
            - 200: Return the users' email addresses
        """
        api = Api(current_app)
        body = InventoryBuilder(items=[])
        event = Event.query.filter_by(id=event_id).first()
        if event is None:
            return create_error_response(404, "Event not found",
                                        "Event ID {} was not found".format(event_id))
        body["event"] = {"event_id":event.id,"name":event.name}

        body.add_namespace("eventhub", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(EventItem, id=event_id))
        body.add_control("profile", EVENT_PROFILE)
        body.add_control_delete_event(event_id)
        body.add_control_edit_event(event_id)
        body.add_control_all_events()
        try:
            # find all the users
            followers = User.query.filter(Event.users1.any(id=event.id)).all()
            # for each user, find the id and email
            for i in followers:
                user = InventoryBuilder()
                user["email"] = i.email

                user.add_namespace("eventhub", LINK_RELATIONS_URL)
                user.add_control("self", api.url_for(UserItem, id=i.id))
                user.add_control("profile", USER_PROFILE)
                user.add_control_delete_user(i.id)
                user.add_control_edit_user(i.id)
                user.add_control_all_users()
                body["items"].append(user)  

            return Response(json.dumps(body), 200, mimetype=MASON)
        except (KeyError, ValueError):
            abort(400)
