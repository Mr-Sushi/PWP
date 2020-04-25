from flask_restful import Resource, Api


from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, Response, current_app
from .UserItem import UserItem
from eventhub.models import Event, User, associations,Organization
from eventhub.utils import InventoryBuilder, MasonBuilder, create_error_response
import json
from eventhub import db
from jsonschema import validate, ValidationError
from .OrgItem import OrgItem

import sys

LINK_RELATIONS_URL = "/eventhub/link-relations/"

USER_PROFILE = "/profiles/user/"
ORG_PROFILE = "/profile/org/"
EVENT_PROFILE = "/profiles/event/"
ERROR_PROFILE = "/profiles/error/"

MASON = "application/vnd.mason+json"

from sqlalchemy.ext.declarative import DeclarativeMeta
"""
class AlchemyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)
"""


class OrgsByUser(Resource):
    
    def get(self, user_id):
        """
        Get all the assotiated organization info for a user
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
        body["user"] = {"name":user.name}

        body.add_namespace("eventhub", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(UserItem, id=user_id))
        body.add_control("profile", USER_PROFILE)
        body.add_control_delete_user(user_id)
        body.add_control_edit_user(user_id)
        body.add_control_all_users()
        try:
            # find all the organizations
            # orgs= db.session.query(User.related_orgs).filter_by(id=user_id).all()
            # orgs = User.query.with_entities(User.related_orgs).all()
            # orgs = associations.organization.query.filter_by(user=user_id).all()
            """
            users_dt = User.query.filter_by(id=user_id).first()
            orgs = users_dt.related_orgs
"""
            orgs = Organization.query.filter(User.related_orgs.any(id=user_id)).all()
            #orgs = db.session.query(orgs_info.id)
            # for each organization, find specific information
            for i in orgs:
                org = InventoryBuilder()
                #org_dt = Organization.query.filter_by(id=i).first()
                org["name"]= i.name
                #org["name"] = organization.name
                org.add_namespace("eventhub", LINK_RELATIONS_URL)
                org.add_control("self", api.url_for(OrgItem, id=i.id))
                org.add_control("profile", ORG_PROFILE)
                org.add_control_delete_org(i.id)
                org.add_control_edit_org(i.id)
                org.add_control_all_orgs()
                body["items"].append(org)  
            return Response(json.dumps(body), 200, mimetype=MASON)
        except (KeyError, ValueError):
            abort(400)


class UsersOfOrg(Resource):
    def get(self, org_id):
        """
        Get all the users' email of an organization
        Parameters:
            - id: Integer, organization id
        Response:
            - 404: "Organization not found", "Organization ID {} was not found"
            - 400: KeyError and ValueError (something else was found)
            - 200: Return the users' email addresses
        """
        api = Api(current_app)
        body = InventoryBuilder(items=[])
        org = Organization.query.filter_by(id=org_id).first()
        if org is None:
            return create_error_response(404, "Organization not found",
                                        "Organization ID {} was not found".format(user_id))
        body["organization"] = {"org_id":org.id,"name":org.name}

        body.add_namespace("eventhub", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(OrgItem, id=org_id))
        body.add_control("profile", ORG_PROFILE)
        body.add_control_delete_org(org_id)
        body.add_control_edit_org(org_id)
        body.add_control_all_orgs()
        try:
            # find all the users
            #users= db.session.query(Organization.users2).filter_by(id=org_id).all()
            related_users = User.query.filter(Organization.users2.any(id=org.id)).all()
            # for each user, find the id and email
            for i in related_users:
                user = InventoryBuilder()
                # user details
                user["email"] = i.email

                user.add_namespace("eventhub", LINK_RELATIONS_URL)
                user.add_control("self", api.url_for(UserItem, id=i))
                user.add_control("profile", USER_PROFILE)
                user.add_control_delete_user(i)
                user.add_control_edit_user(i)
                user.add_control_all_users()
                body["items"].append(user)  

            return Response(json.dumps(body), 200, mimetype=MASON)
        except (KeyError, ValueError):
            abort(400)