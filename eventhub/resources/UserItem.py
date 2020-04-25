from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, Response, current_app
from eventhub.models import Event, User
from eventhub.utils import InventoryBuilder, MasonBuilder, create_error_response, hash_password
from eventhub import db
import json
from jsonschema import validate, ValidationError

LINK_RELATIONS_URL = "/eventhub/link-relations/"

USER_PROFILE = "/profiles/user/"
ORG_PROFILE = "/profile/org/"
EVENT_PROFILE = "/profiles/event/"
ERROR_PROFILE = "/profiles/error/"

MASON = "application/vnd.mason+json"

class UserItem(Resource):
    # Resource class for single user

    api = Api(current_app)

    def get(self, id):
        """
        get information for one user
        Parameters:
            - id: Integer, id of user
        Response:
            - 404: create_error_response and message "User not found" "User ID {} not found."
            - 200: Return the user's information (a Mason document).
        """
        
        id = int(id)
        api = Api(current_app)
        #User.query.all()
        user_db = User.query.filter_by(id=id).first()
        #print(user_db)
            
        if user_db is None:
            return create_error_response(404, "User not found",
                                         "User ID {} was not found".format(id)
                                         )
                                        
        body = InventoryBuilder(
            name=user_db.name,
            email=user_db.email,
            location=user_db.location,
            notifications=user_db.notifications
        )
        body.add_namespace("eventhub", LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(UserItem, id=id))
        body.add_control("profile", USER_PROFILE)
        body.add_control_delete_user(id)
        body.add_control_edit_user(id)
        body.add_control_all_users()
        return Response(json.dumps(body), 200, mimetype=MASON)


    def put(self, id):
        """
        modify information for particular user
        Parameters:
            - id: Integer, id of user
            - name: String, name of user
            - email: String, email of user
            - password: String, password of user
            - location: String, location of user
            - notifications: Integer, whether the user choose to receive notifications or not
        Response:
            - 415: create_user_error_response and message "Unsupported media type Requests must be JSON"
            - 400: create_user_error_response and message "Invalid JSON document"
            - 404: create_user_error_response and message "User not found" "User ID {} not found."
            - 204: success to edit
        """
        api = Api(current_app)
        #print(request.json)
        if not request.json:
            return creat_error_response(415, "Unsupported media type",
                                         "Requests must be JSON"
                                         )
        try:
            validate(request.json, InventoryBuilder.user_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        password = request.json["password"]
        user = User(
            name=request.json["name"],
            email=request.json["email"],
            pwdhash=hash_password(password),
            location=request.json["location"],
            notifications=request.json["notifications"]
        )

        user_db = User.query.filter_by(id=id).first()
        if user_db is None:
            return create_error_response(404, "User not found",
                                         "User ID {} was not found".format(id)
                                         )

        #not necessary: user_db.id = id
        user_db.name = user.name
        user_db.email = user.email
        user_db.pwdhash = user.pwphash
        user_db.location = user.location
        user_db.notifications = user.notifications
        db.session.commit()

        return Response(status=204)

    def delete(self, id):
        """
        delete user's informtation
        Parameters:
            - id: Integer, user id
        Response:
            - 404: create_error_response and send message "User not found" "User ID {} not found."
            - 204: delete successfully
        """
       
        api = Api(current_app)
        user_db = User.query.filter_by(id=id).first()


        if user_db is None:
            return create_error_response(404, "User not found",
                                         "User ID {} was not found".format(id)
                                         )

        #print(user)

        db.session.delete(user)
        db.session.commit()
    
        return Response(status=204)


