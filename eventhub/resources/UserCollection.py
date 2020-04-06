from flask_restful import Resource, Api

from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, Response, current_app
from .useritem import UserItem
from ..models import Event, User
from ..utils import InventoryBuilder, MasonBuilder, create_error_response, hash_password
import json
from Eventhub import db
from jsonschema import validate, ValidationError

LINK_RELATIONS_URL = "/eventhub/link-relations/"

USER_PROFILE = "/profiles/user/"
ORG_PROFILE = "/profile/org/"
EVENT_PROFILE = "/profiles/event/"
ERROR_PROFILE = "/profiles/error/"

MASON = "application/vnd.mason+json"


class UserCollection(Resource):
    # Resource class for representing all users
    def get(self):
        """
        Return information of all users (returns a Mason document) if found otherwise returns 404
        get all users information
        Response:
            - 400: KeyError and ValueError (something else was found)
            - 200: Return information of all users (returns a Mason document)
        """
        api = Api(current_app)

        try:
            users = User.query.all()
            body = InventoryBuilder(items=[])

            for i in users:
                item = MasonBuilder(
                    id = i.id,
                    name = i.name,
                    email = i.email,
                    pwdhash = i.pwdhash,
                    location = i.location,
                    notifications = i.notifications
                )
                item.add_control("self", api.url_for(
                    UserItem, id=j.id))
                item.add_control("profile", "/profiles/user/")
                body["items"].append(item)
                
            body.add_namespace("eventhub", LINK_RELATIONS_URL)
            body.add_control_all_users()
            body.add_control_add_user()
            #print(body)

            return Response(json.dumps(body), 200, mimetype=MASON)
        except (KeyError, ValueError):
            abort(400)

    def post(self):
        """
        post information for new user
        Parameters:
            - name: String, user's name
            - email: String, user's email
            - password: String, user's password
            - location: String, user's location
            - notifications: String, whether user turn on notification
        Response:
            - 415: "Unsupported media type" "Requests must be JSON"
            - 400: "Invalid JSON document"
            - 409: "Already exists" "The email address is already in use."
            - 201: succeed
        """
    
        api = Api(current_app)
        if not request.json:
            return create_error_response(415, "Unsupported media type","Requests must be JSON")
        try:
            validate(request.json, InventoryBuilder.user_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))
        
        password = request.json["password"]
        user = User(
            name=request.json['name'],
            email=reques.json['email'],
            pwdhash=hash_password(password),
            location=request.json["location"],
            notifications=request.json["notifications"]
        )

        try:
            #generate user id
            users = User.query.all()
            user.id = len(users)+1
                    
            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            return create_error_response(409, "Already exists",
                                               "The email address {} is already in use.".format(user.email))
    
        return Response(status=201, headers={"URL": api.url_for(UserItem, id=user.id)})