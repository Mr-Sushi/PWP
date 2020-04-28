import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from sqlalchemy import event
from sqlalchemy.engine import Engine
#from flask_cors import CORS
#from flask_jwt_extended import JWTManager
db = SQLAlchemy()


#https://flask.palletsprojects.com/en/1.0.x/tutorial/factory/



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        # SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "test.db"),
        DATABASE=os.path.join(app.instance_path, 'eventhub.sqlite'),
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
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

    # a simple page that says hello
    @app.route('/client/')
    def client_site():
        return app.send_static_file("html/client.html")

    return app


app = create_app()
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

#jwt = JWTManager(app)
"""



@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()



@app.route("/profiles/<resource>/")
def send_profile_html(resource):
    return "Random string"
    # return send_from_directory(app.static_folder, "{}.html".format(resource))


@app.route("/eventhub/link-relations/")
def send_link_relations_html():
    return "some string"
    # return send_from_directory(app.static_folder, "links-relations.html")




"""