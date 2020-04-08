from flask_restful import Resource, Api


from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, Response, current_app
from .OrgItem import OrgItem
from ..models import Org
from ..utils import InventoryBuilder, MasonBuilder, create_error_response
import json
from Eventhub import db
from jsonschema import validate, ValidationError

LINK_RELATIONS_URL = "/eventhub/link-relations/"

USER_PROFILE = "/profiles/user/"
ORG_PROFILE = "/profiles/org/"
EVENT_PROFILE = "/profiles/event/"
ERROR_PROFILE = "/profiles/error/"

MASON = "application/vnd.mason+json"

class OrganizationCollection(Resource):
    """
    Resource class for collection of organizations
    """
    
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
        organizations = Organization.query.all()
        org.id = len(organizations)+1

        try:
            organizations = Organization.query.all()
            org.id = len(organizations)+1
            db.session.add(org)
            db.session.commit()

        except IntegrityError:
            return create_error_response(409, "Already exists",
                                               "Organization with id '{}' already exists.".format(org.id)
                                               )
    
        return Response(status=201, headers={"URL": api.url_for(OrgItem, id=org.id)})