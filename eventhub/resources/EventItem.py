from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, Response, current_app
from Eventhub import db
from ..models import Event, User
from ..utils import InventoryBuilder, MasonBuilder, create_error_response
import json
from jsonschema import validate, ValidationError


LINK_RELATIONS_URL = "/eventhub/link-relations/"

USER_PROFILE = "/profiles/user/"
ERROR_PROFILE = "/profiles/error/"
ORG_PROFILE = "/profiles/org/"
EVENT_PROFILE = "/profiles/EVENT/"

MASON = "application/vnd.mason+json"


class EventItem(Resource):
    """
    Resource class for particular event
    """
    def get(self, id):
        """
        get details for particular event 
        Parameters:
            - id: Integer, event ID
        Response:(tbc)
            - 404: create_error_response and alert "No event was found with the id {}"
            - 200: Return information of the event (returns a Mason document)
        """
        api = Api(current_app)
        event_db = Event.query.filter_by(id=id).first()
        if event_db is None:
            return create_error_response(404, "Event not found",
                                         "Event ID {} was not found".format(
                                             id)
                                         )
        
        if event_db.creator is None:
            return create_error_response(404, "Event not found",
                                         "Event ID {} was not found".format(
                                             id)
                                         )

        body = InventoryBuilder(
            id=event_db.id,
            name=event_db.name,
            time=event_db.time,
            description=event_db.description,
            location=event_db.location,
            organization = event_db.organization
        )
        
        body.add_namespace("eventhub", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(eventItem, id=id))
        body.add_control("profile", EVENT_PROFILE)
        body.add_control_delete_event(id)
        body.add_control_edit_event(id)
        body.add_control_all_events()
        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, id):
        """
        modify information of a event
        Parameters:
            - id: Integer, id of event
            - name: String, name of event
            - time: DateTime, time of event
            - description: String, description of event
            - location: String, location of event
            - organization: string, organization that the event belongs to
        Response:
            - 415: create_error_response and alert "Unsupported media type Requests should be JSON"
            - 404: create_error_response and alert "Not found No event was found with the id {}"
            - 400: create_error_response and alert "Invalid JSON document"
            - 204: success to edit
        """
        api = Api(current_app)
        if not request.json:
            return create_error_response(415, "Unsupported media type",
                                         "Requests must be JSON"
                                         )

        body = Event(
            id=id,
            name=request.json["name"],
            time=request.json["time"],
            description=request.json["description"],
            location=request.json["location"],
            organization=request.json["organization"],
        )

        event_db = Event.query.filter_by(id=id).first()
        if event_db is None:
            return create_error_response(404, "Event not found",
                                         "Event ID {} was not found".format(
                                             id)
                                         )

        try:
            validate(request.json, InventoryBuilder.event_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        
        event_db.id = body.id
        event_db.name = body.name
        event_db.time = body.time
        event_db.location = body.location
        event_db.description = body.description
        event_db.organization = body.organization
        db.session.commit()

        return Response(status=204, headers={
            "URL": api.url_for(EventItem, id=id)
        })
    def delete(self,id):
        """
        delete information of an event
        Parameters:
            -id: Integer, id of the event
        Response:
            -404: create_error_response and alert "Event not found"
            -401: create_error_response and alert "API key is missing or invalid"
            -204: success to delete
        """
        api = Api(current_app)
        event_db = Event.query.filter_by(id=id).first()
        if event_db is None:
                return create_error_response(404, "Event not found",
                                         "Event ID {} was not found".format(
                                             id)
                                         )
        ## How to add response 401??
        Event.query.filter(Event.id==id).delete()
        db.session.commit()
        return Response(status = 204,headers={
            "URL": api.url_for(EventItem, id=id)
        })
