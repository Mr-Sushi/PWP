from flask_restful import Resource, Api
#import pdb; pdb.set_trace()

from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, Response, current_app

from .EventItem import EventItem
from eventhub.models import Event, User
from eventhub.utils import InventoryBuilder, MasonBuilder, create_error_response
import json
from eventhub import db
from jsonschema import validate, ValidationError

LINK_RELATIONS_URL = "/eventhub/link-relations/"

USER_PROFILE = "/profiles/user/"
ORG_PROFILE = "/profiles/org/"
EVENT_PROFILE = "/profiles/event/"
ERROR_PROFILE = "/profiles/error/"

MASON = "application/vnd.mason+json"

class EventCollection(Resource):
    """
    Resource class for events collection
    """
    def get(self):
        """
        get information as follows
        Information:
            - id: Integer, id of event
            - name: String, name of event
            - time: DateTime, time of event
            - description: String, description of event
            - location: String, location of event
            - organization: string, organization that the event belongs to
        Response:
            - 400: KeyError, ValueError
            - 200: Return information of all events (as a Mason document)
        """
        api = Api(current_app)
        
        try:
            events = Event.query.all()
            body = InventoryBuilder(event_list=[])
            
            #add creator id
            for item in events:
                """
                if (item.creator_id != None):
                    #create a dictionary
                    creator = {}
                    creator["id"] = item.creator_id

                    creator_user = User.query.filter_by(id=item.creator_id).first
                    creator_name = creator_user.name
                    creator["name"] = creator_name
                """
                event = MasonBuilder(
                        name=item.name, 
                        time = item.time,
                        description=item.description, 
                        location = item.location, 
                        organization = item.organization,
                        #creator = item.creator
                )
                event.add_control("self", api.url_for(EventItem, id=item.id))
                event.add_control("profile", "/profiles/event/")
                body["event_list"].append(event)

            body.add_namespace("eventhub", LINK_RELATIONS_URL)
            body.add_control_all_events()
            body.add_control_add_event()

            return Response(json.dumps(body), 200, mimetype=MASON)
        except (KeyError, ValueError):
            abort(400)
    
    def post(self):
        """
        post information for new event 
        Parameters:
            - name: String, name of the event
            - time: String, time of the event
            - description: String, description of event
            - location: String, location of the event
            - organization: Integer, organization that the event belongs to
            - creator_id: Integer, creator's id of the event
        Response:
            - 415: create_error_response and alert "Unsupported media type. Requests must be JSON"
            - 400: create_error_response and alert "Invalid JSON document" 
            - 409: create_error_response and alert "Already exists. Event with id '{}' already exists."
            - 201: success to post
        """
        api = Api(current_app)
        if not request.json:
            return create_error_response(415, "Unsupported media type","Requests must be JSON")

        try:
            validate(request.json, InventoryBuilder.event_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))
        
        # user = User.query.filter_by(id=request.json["creator_id"]).first()
      
        event = Event(
            name = request.json["name"],
            time = request.json["time"],
            description = request.json["description"],
            location = request.json["location"],
            organization = request.json["organization"],
            #creator_id = request.json["creator_id"]
        )

        event.creator = user

        try:
            db.session.add(event)
            db.session.commit()
            #print(api.url_for(EventItem, id=event.id))
                
            events = Event.query.all()
            
            event.id = len(events)

        except IntegrityError:
            return create_error_response(409, "Already exists",
                                               "Event with id '{}' already exists.".format(event.id)
                                               )
    
        return Response(status=201)