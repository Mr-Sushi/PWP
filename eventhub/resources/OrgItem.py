from flask_restful import Resource, Api

from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, Response, current_app
from ... import db
# mainly subfunctions
from ..models import Organization
from ..utils import InventoryBuilder, MasonBuilder, create_error_response
import json
from jsonschema import validate, ValidationError


LINK_RELATIONS_URL = "/eventhub/link-relations/"

USER_PROFILE = "/profiles/user/"
ORG_PROFILE = "/profile/org/"
EVENT_PROFILE = "/profiles/event/"
ERROR_PROFILE = "/profiles/error/"

MASON = "application/vnd.mason+json"

class OrgItem(Resource):
    """
    Resource class for particular organization
    """
    def get(self, id):
        """
        get details for particular organization
        Parameters:
            - id: Integer, event ID
        Response:(tbc)
            - 404: create_error_response and message "No organization was found with the id {}"
            - 200: Return information of the organization (returns a Mason document)
        """
        api = Api(current_app)
        org_db = Organization.query.filter_by(id=id).first()
        if org_db is None:
            return create_error_response(404, "Not found",
                                         "No organization was found with the id {}".format(id)
                                         )
        
        body = InventoryBuilder(
            id=org_db.id,
            name=org_db.name
        )
        #check after finishing utils.py
        body.add_namespace("eventhub", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(OrgItem, id=id))
        body.add_control("profile", ORG_PROFILE)
        body.add_control_delete_org(id)
        body.add_control_edit_org(id)
        body.add_control_all_orgs()
        return Response(json.dumps(body), 200, mimetype=MASON)

        
    def put(self, id):
        """
        edit information of an organization
        Parameters:
            - id: Integer, id of the organization
            - name: String, name of the organization
        Response:
            - 415: create_error_response and message "Unsupported media type Requests should be JSON"
            - 404: create_error_response and message "No organization was found with the id {}"
            - 400: create_error_response and message "Invalid JSON document"
            - 204: success to edit
        """
        api = Api(current_app)
        if not request.json:
            return create_error_response(415, "Unsupported media type",
                                         "Requests must be JSON"
                                         )

        body = Organization(
            id=id,
            name=request.json["name"]
        )

        org_db = Event.query.filter_by(id=id).first()
        if org_db is None:
            return create_error_response(404, "Not found",
                                         "No organization was found with the id {}".format(
                                             id)
                                         )

        try:
            validate(request.json, InventoryBuilder.orga_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        
        org_db.id = body.id
        org_db.name = body.name
        db.session.commit()

        return Response(status=204, headers={"URL": api.url_for(OrgItem, id=org_db.id)})

    def delete(self,id):
        """
        # delete information of an organization
        # Parameters:
        #     -id: Integer, id of the event
        # Response:
        #     -404: create_error_response and alert "Organization not found"
        #     -401: create_error_response and alert "API key is missing or invalid"
        #     -204: success to delete
        """
        api = Api(current_app)
        org_db = Organization.query.filter_by(id=id).first()
        if orgt_db is None:
                return create_error_response(404, "Not found",
                                            "Organization not found"
                                            )
        ## How to add response 401??--How to know if the client has sufficient permission?
        db.session.delete(org_db)
        db.session.commit()
        return Response(status = 204})
