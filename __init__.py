#https://flask.palletsprojects.com/en/1.0.x/tutorial/factory/
import os
from flask import Flask
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from sqlalchemy import event
from sqlalchemy.engine import Engine
from eventhub.utils import InventoryBuilder, MasonBuilder, create_error_response
db = SQLAlchemy()
import json





def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "test.db"),
        DATABASE=os.path.join(app.instance_path, 'eventhub.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    )

    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
    
    db = SQLAlchemy(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    @app.route('/profiles/<resource>/')
    def send_profile(resource):
        return 'profiles'

    @app.route("/eventhub/link-relations/")
    def something():
        return 'link-relations'

    @app.route('/api/')
    def EntryPoint():
        body = {
                "@controls": {
                    "events-all": {
                        "href": "/api/events/",
                        "title": "All events"
                    },
                    "organizations-all": {
                        "href": "/api/orgs/",
                        "title": "All organizations"
                    },
                    "users-all": {
                        "href": "/api/users/",
                        "title": "All users"
                    }
                }
            }
        return json.dumps(body)

    # client
    @app.route('/client/')
    @cross_origin()
    def client_site():
        return app.send_static_file("html/client.html")

    return app

app = create_app()
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
#CORS(app)

app.app_context().push()

#db.init_app(app)
#db = SQLAlchemy(app)

from eventhub.resources.EventCollection import EventCollection
from eventhub.resources.EventItem import EventItem
from eventhub.resources.OrgCollection import OrgCollection
from eventhub.resources.OrgItem import OrgItem
from eventhub.resources.UserCollection import UserCollection
from eventhub.resources.UserItem import UserItem

from eventhub.resources.UserEvent import EventsByUser, UsersByEvent
from eventhub.resources.UserOrg import OrgsByUser, UsersOfOrg

api = Api(app)


#     Add resource path
api.add_resource(EventCollection, "/api/events/")
api.add_resource(UserCollection, "/api/users/")
api.add_resource(OrgCollection, "/api/orgs/")
api.add_resource(EventItem, "/api/events/<id>/")
api.add_resource(UserItem, "/api/users/<id>/")
api.add_resource(OrgItem, "/api/orgs/<id>/")

api.add_resource(EventsByUser, "/api/users/<user_id>/events/")
api.add_resource(UsersByEvent, "/api/events/<event_id>/users/")
api.add_resource(OrgsByUser, "/api/users/<user_id>/orgs/")
api.add_resource(UsersOfOrg,"/api/orgs/<org_id>/users/")

