from flask import Flask, request, abort, Response, current_app
from flask_restful import Api
import json
import hashlib
import os
import binascii


def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

class MasonBuilder(dict):
    """
    The class for Mason objects.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios. Only one string in @messages at a 
        time, although multiple-error-messaging is also supported by Mason.
        
        Parameters:
        title: String, title for the error
        details: String, description for the error
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. 
        Parameters:
        namespace: String, the namespace prefix
        uri: String, the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Only certain properties are 
        allowed for kwargs so we can also add some checking here.
        Parameters:
        control_name: String, name of the control (including namespace if any)
        href: String, ttarget URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href

LINK_RELATIONS_URL = "/eventhub/link-relations/"
USER_PROFILE = "/profiles/user/"
MASON = "application/vnd.mason+json"
EVENT_PROFILE = "/profiles/event/"
ORG_PROFILE = "/profiles/organization"

ERROR_PROFILE = "/profiles/error/"

def create_error_response(status_code, title, message=None):
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    body.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(body), status_code, mimetype=MASON)

class InventoryBuilder(MasonBuilder):
    
    @staticmethod
    def event_schema():
        schema = {
            "type": "object",
            "required": ["name","time", "description","organization"]
        }
        schema["properties"] = {}
        props = schema["properties"]
        """
        props["id"] = {
            "description": "index of the event",
            "type": "number"
        }
        """
        props["name"] = {
            "description": "name of the event",
            "type": "string"
        }
        props["time"] = {
            "description": "time of the event",
            "type": "string"
        }
        props["description"] = {
            "description": "description of the event",
            "type": "string"
        }
        props["location"] = {
            "description": "location of the event",
            "type": "string"
        }
        props["organization"] = {
            "description": "organization that hosts the event",
            "type": "number"
        }





        return schema

    @staticmethod
    def user_schema():
        schema = {
            "type": "object",
            "required": ["name", "email","password","notifications"]
        }
        props = schema["properties"] = {}
        """
        props["id"] = {
            "description": "id for user",
            "type": "number"
        }
        """
        props["name"] = {
            "description": "name of the user",
            "type": "string"
        }
        props["email"] = {
            "description": "email of the user",
            "type": "string"
        }
        props["password"]= {
            "description": "password of the user",
            "type": "string"
        }
        props["location"] = {
            "description": "locaiton of the user",
            "type": "string"
        }
        props["notifications"] = {
            "description": "whether or not the user receives notifications",
            "type": "number"
        }
        return schema

    

    @staticmethod
    def org_schema():
        schema = {
            "type": "object",
            "required": ["name"]
        }
    
        props = schema["properties"] = {}
        """
        props["id"] = {
            "description": "id for organization",
            "type": "number"
        }
        """
        props["name"] = {
            "description": "name of the organization",
            "type": "string"
        }
        return schema

    # controls for events
    def add_control_delete_event(self, id):
        from .resources.EventItem import EventItem
        api = Api(current_app)
        self.add_control(
            "delete",
            href=api.url_for(EventItem, id=id),
            method="DELETE",
            title="Delete this event"
        )

    def add_control_edit_event(self, id):
        from .resources.EventItem import EventItem
        api = Api(current_app)
        self.add_control(
            "edit",
            href=api.url_for(EventItem, id=id),
            method="Put",
            encoding="json",
            title="Edit a event",
            schema=self.event_schema()
        )

    def add_control_add_event(self):

        self.add_control(
            "create-event",
            "/api/events/",
            method="POST",
            encoding="json",
            title="Create event",
            schema=self.event_schema()
        )

    def add_control_all_events(self):
        self.add_control(
            "events-all",
            "/api/events/",
            method="GET",
            title="Get all events"
        )
    
    # controls for users
    def add_control_delete_user(self, id):
        from .resources.UserItem import UserItem
        api = Api(current_app)
        self.add_control(
            "delete",
            href=api.url_for(UserItem, id=id),
            method="DELETE",
            title="Delete this user"
        )

    def add_control_edit_user(self, id):
        from .resources.UserItem import UserItem

        api = Api(current_app)

        self.add_control(
            "edit",
            href=api.url_for(UserItem, id=id),
            method="Put",
            encoding="json",
            title="Edit a user",
            schema=self.user_schema()
        )
    
    def add_control_add_user(self):

        self.add_control(
            "create-user",
            "/api/users/",
            method="POST",
            encoding="json",
            title="Add a new user",
            schema=self.event_schema()
        )

    def add_control_all_users(self):
        self.add_control(
            "users-all",
            "/api/users/",
            method="GET",
            title="get all users"
        )

    # controls for organizations
    def add_control_delete_org(self, id):
        from .resources.OrgItem import OrgItem
        api = Api(current_app)
        self.add_control(
            "delete",
            href=api.url_for(OrgItem, id=id),
            method="DELETE",
            title="Delete this organization"
        )

    def add_control_edit_org(self, id):
        from .resources.OrgItem import OrgItem

        api = Api(current_app)

        self.add_control(
            "edit",
            href=api.url_for(OrgItem, id=id),
            method="Put",
            encoding="json",
            title="Edit an organization",
            schema=self.org_schema()
        )
    
    def add_control_add_org(self):

        self.add_control(
            "create-organization",
            "/api/organizations/",
            method="POST",
            encoding="json",
            title="Add a new organization",
            schema=self.org_schema()
        )

    def add_control_all_orgs(self):
        self.add_control(
            "orgs-all",
            "/api/orgs/",
            method="GET",
            title="get all organizations"
        )