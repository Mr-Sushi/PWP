from flask_restful import Resource, Api


from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, Response, current_app
from .OrgItem import OrgItem
from eventhub.models import Organization
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

class OrgCollection(Resource):
    """
    Resource class for collection of organizations
    """
    def get(self):
        """
        get information as follows
        Information:
            - name: name of the organization
        Response:
            - 400: KeyError, ValueError
            - 200: Return information of all organizations as a Mason document
        """
        api = Api(current_app)
        
        try:
            orgs = Organization.query.all()
            body = InventoryBuilder(orgs_list=[])
            
            for item in orgs:
                org = MasonBuilder(
                      name=item.name,
                )
                org.add_control("self", api.url_for(OrgItem, id=item.id))
                org.add_control("profile", "/profiles/org/")
                body["orgs_list"].append(org)

            body.add_namespace("eventhub", LINK_RELATIONS_URL)
            body.add_control_all_orgs()
            body.add_control_add_org()

            return Response(json.dumps(body), 200, mimetype=MASON)
        except (KeyError, ValueError):
            abort(400)

    def post(self):
        """
        post information for new organization
        Parameters:
            - name: String, name of the organization
        Response:
            - 415: create_error_response and alert "Unsupported media type. Requests must be JSON"
            - 400: create_error_response and alert "Invalid JSON document" 
            - 409: create_error_response and alert "Already exists. Event with id '{}' already exists."
            - 201: succeed to post
        """
        api = Api(current_app)
        if not request.json:
            return create_error_response(415, "Unsupported media type","Requests must be JSON")

        try:
            validate(request.json, InventoryBuilder.org_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))
        
      
        org = Organization(name = request.json["name"])

        try:
            organizations = Organization.query.all()
            db.session.add(org)
            db.session.commit()

        except IntegrityError:
            return create_error_response(409, "Already exists",
                                               "Organization with id '{}' already exists.".format(org.id)
                                               )
    
        return Response(status=201)