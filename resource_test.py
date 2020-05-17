import json
import os
import pytest
import sys
import tempfile
from datetime import datetime
from jsonschema import validate
from eventhub import app, db
from eventhub.models import Event, User, Organization, EventsAndUsers, OrgsAndUsers
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# based on http://flask.pocoo.org/docs/1.0/testing/ and https://lovelace.oulu.fi/ohjelmoitava-web/programmable-web-project-spring-2020/testing-flask-applications-part-2/


o_path = os.getcwd()
sys.path.append(o_path)

@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.config["TESTING"] = True

    db.create_all()

    _populate_db()

    yield app.test_client()

    db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)


def _populate_db():
    
    # Pre-populate database with 1 event, 2 users and 2 organizations.
    
    event = Event(
        name="Test event",
        time="2020-02-02",
        description="Something",
        location="Oulu",
        organization=1
    )
    db.session.add(event)

    user1 = User(
        name = "Melody",
        email = "test1@gmail.com",
        pwdhash = "random string",
        location = "Routa",
        notifications=0
    )

    db.session.add(user1)

    user2 = User(
        name = "Stacey",
        email = "test2@gmail.com",
        pwdhash = "random string",
        location = "Monkey house",
        notifications=0
    )
    db.session.add(user2)

    org1 = Organization(name="org1")
    org2 = Organization(name="org2")

    following = EventsAndUsers(
        user_id = 1,
        event_id = 1
    )

    associations = OrgsAndUsers(
        user_id = 1,
        org_id = 1
    )

    db.session.add(org1)
    db.session.add(org2)
    db.session.add(following)
    db.session.add(associations)

    db.session.commit()


def _check_namespace(client, response):
    ns_href = response["@namespaces"]["eventhub"]["name"]
    resp = client.get(ns_href)
    assert resp.status_code == 200


def _check_control_get_method(ctrl, client, obj):
    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == 200


def _check_control_delete_method(ctrl, client, obj):
    href = obj["@controls"][ctrl]["href"]
    method = obj["@controls"][ctrl]["method"].lower()
    assert method == "delete"
    resp = client.delete(href)
    assert resp.status_code == 204


def _check_control_put_method(ctrl, client, obj, putType):
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    if putType == "event":
        body = _get_event()
    elif putType == "user":
        body = _get_user()
    elif putType == "org":
        body = _get_org()
    validate(body, schema)
    print(body)
    resp = client.put(href, json=body)
    assert resp.status_code == 204


def _check_control_post_method(ctrl, client, obj):
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    if ctrl.endswith("event"):
        body = _get_event()
    elif ctrl.endswith("user"):
        body = _get_user()
    elif ctrl.endswith("org"):
        body = _get_org()
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201


def _get_event():
    event_dict = {
        "name": "Karaoke",
        "time": "9:23",
        "description": "Something",
        "location": "Routa, Oulu",
        "organization": 1
    }
    return event_dict


def _get_org():
    return {"name": "OTiT"}
    


def _get_user(number=1):
    user_dict = {
        "name": "DanceMonkey",
        "email": "test@163.com",
        "password": "password",
        "location": "University of Oulu",
        "notifications": 0
    }

    return user_dict


class TestEventCollection(object):
    RESOURCE_URL = "/api/events/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_get_method("events-all", client, body)
        assert len(body["event_list"]) == 1
        for item in body["event_list"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "name" in item
            assert "description" in item

    def test_post(self, client):
        valid = _get_event()

        # post the event
        resp = client.post(self.RESOURCE_URL, json=valid)
        #body = json.loads(client.get(self.RESOURCE_URL).data)
        
        assert resp.status_code == 201
        post_event = Event.query.filter_by(name = valid["name"]).first()
        id = post_event.id
        string_id = str(id)
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + string_id + "/")
        resp = client.get(resp.headers["Location"])
        # make sure the event exists
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "Karaoke"
        assert body["description"] == "Something"

        # 415: invalid document type, request must be json
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # 400: send a document that doesn't fit into the schema
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400


class TestEventItem(object):
    RESOURCE_URL = "/api/events/1/"
    INVALID_URL = "/api/events/non-event-x/"
    MODIFIED_URL = "/api/events/2/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        # print(resp)
        body = json.loads(resp.data)
        assert body["name"] == "Test event"
        assert body["description"] == "Something"
        assert body["time"] == "2020-02-02"
        assert body["location"] == "Oulu"
        assert body["organization"] == 1
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("events-all", client, body)
        _check_control_put_method("edit", client, body, "event")
        _check_control_delete_method("delete", client, body)

        # 404 not found
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """
        Tests the PUT method. Checks all of the possible erroe codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the sensor can be found from a its new URI. 
        """

        valid = _get_event()

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # test with wrong url
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

        # test with valid
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        # check the correct results
        valid = _get_event()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == valid["name"] and body["description"] == valid["description"] and body["organization"] == valid["organization"]

        # 400: doesn't fit the schema
        valid = _get_event()
        valid["organization"] = "not number"
        resp = client.put(self.RESOURCE_URL,json = valid)
        assert resp.status_code == 400

        

    def test_delete(self, client):
        """Test for valid DELETE method"""
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404


class TestOrgCollection():
    RESOURCE_URL = "/api/orgs/"
    
    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_get_method("orgs-all", client, body)
        assert len(body["orgs_list"]) == 2
        for item in body["orgs_list"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "name" in item

    def test_post(self, client):
        # test with wrong content type(must be json)
        resp = client.post(self.RESOURCE_URL, data="happy")#not json
        assert resp.status_code == 415

        valid = _get_org()
        resp = client.post(self.RESOURCE_URL, json=valid)
        body = json.loads(client.get(self.RESOURCE_URL).data)
        assert resp.status_code == 201

        post_org = Organization.query.filter_by(name = valid["name"]).first()
        id = post_org.id
        string_id = str(id)
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + string_id + "/")
        
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200

        body = json.loads(resp.data)
        assert body["name"] == "OTiT"

        # 409: the name of the organization already exists
        valid = _get_org()
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        # 400 - The client is trying to send a JSON document that does not validate against the schema.
        resp = client.post(self.RESOURCE_URL, json=json.dumps({"description":"random stuff"}))
        assert resp.status_code == 400

        


class TestOrgItem(object):
    RESOURCE_URL = "/api/orgs/1/"
    INVALID_URL = "/api/orgs/non-org-x/"


    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "org1"

        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("orgs-all", client, body)
        _check_control_put_method("edit", client, body, "org")
        _check_control_delete_method("delete", client, body)
        # 404 not found
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        valid = _get_org()
        #client.put(self.RESOURCE_URL, json=valid)
        resp_put = client.put(self.RESOURCE_URL, json=valid)#("/api/orgs/1/")
        assert resp_put.status_code == 204

        #check if the data is edited successfully
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200

        # test with valid

        resp = client.get("/api/orgs/12/")
        assert resp.status_code == 404

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # 400
        resp = client.put(self.RESOURCE_URL, json=json.dumps({"name":1}))
        assert resp.status_code == 400       

        # test with another url
        invalid_url = "/api/orgs/2/"
        resp_conf = client.put(invalid_url, json=valid)
        assert resp_conf.status_code == 409

    def test_delete(self, client):
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404


class TestUserCollection(object):
    RESOURCE_URL = "/api/users/"

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_get_method("users-all", client, body)
        assert len(body["items"]) == 2
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "name" in item
            assert "email" in item
            assert "pwdhash" in item
            assert "location" in item
            assert "notifications" in item

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and
        also checks that a valid request receives a 201 response with a
        location header that leads into the newly created resource.
        """
        valid = _get_user(number=2)

        #test wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        body = json.loads(client.get(self.RESOURCE_URL).data)
        #id = body["items"][-1]["id"]
        assert resp.status_code == 201
        # test header
        post_user = User.query.filter_by(email = valid["email"]).first()
        id = post_user.id
        string_id = str(id)
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + string_id + "/")
        # see that it still exists
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)

        assert body["name"] == "DanceMonkey"
        
        # remove title field for 400
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        valid = _get_user(number=2)
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409


class TestUserItem(object):
    RESOURCE_URL = "/api/users/1/"
    INVALID_URL = "/api/users/1000/"

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "Melody"
        
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("users-all", client, body)
        _check_control_put_method("edit", client, body, "user")
        _check_control_delete_method("delete", client, body)

        resp = client.get("api/users/20/")
        assert resp.status_code == 404

    def test_put(self, client):
        """Test for valid PUT method"""
        valid = _get_user(number=1)

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # 404 not found
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404


        # test with valid

        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        #check if the data is edited successfully
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == valid["name"]

        # try to add the same organization again
        resp = client.put("api/users/2/", json=valid)
        assert resp.status_code == 409
        
        valid = _get_user(number=1)
        valid["email"] = 1
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        #valid["name"] = "DanceMonkey"

        #valid = _get_user(number=1)

    def test_delete(self, client):
        """Test for valid DELETE method"""
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404


class TestEventsByUser(object):
        RESOURCE_URL = "/api/users/1/events/"
        INVALID_URL = "/api/users/-1/events/"


        def test_get(self, client):
            """Tests for questions by questionnaire GET method."""
            resp = client.get(self.RESOURCE_URL)
            assert resp.status_code == 200
            body = json.loads(resp.data)

            assert len(body["items"]) == 1
            for item in body["items"]:
                _check_control_get_method("self", client, item)
                _check_control_get_method("profile", client, item)
                assert "name" in item
                assert "description" in item
                assert "time" in item
                assert "location" in item
                assert "organization" in item

            _check_namespace(client, body)
            _check_control_get_method("self", client, body)
            _check_control_get_method("profile", client, body)
            _check_control_get_method("users-all", client, body)
            _check_control_delete_method("delete", client, body)
            resp = client.get(self.INVALID_URL)
            assert resp.status_code == 404

class TestUsersByEvent(object):
        RESOURCE_URL = "/api/events/1/users/"
        INVALID_URL = "/api/events/-1/users/"


        def test_get(self, client):
            """Tests for questions by questionnaire GET method."""
            resp = client.get(self.RESOURCE_URL)
            assert resp.status_code == 200
            body = json.loads(resp.data)
            print(body["items"])
            assert len(body["items"]) == 1
            for item in body["items"]:
                _check_control_get_method("self", client, item)
                _check_control_get_method("profile", client, item)
                assert "name" in item
                assert "email" in item
                assert "pwdhash" in item
                assert "location" in item
                assert "notifications" in item

            _check_namespace(client, body)
            _check_control_get_method("self", client, body)
            _check_control_get_method("profile", client, body)
            _check_control_get_method("events-all", client, body)
            _check_control_delete_method("delete", client, body)
            resp = client.get(self.INVALID_URL)
            assert resp.status_code == 404

class TestOrgsByUser(object):
        RESOURCE_URL = "/api/users/1/orgs/"
        INVALID_URL = "/api/users/-1/orgs/"

        def test_get(self, client):
            # Tests for questions by questionnaire GET method.
            resp = client.get(self.RESOURCE_URL)
            assert resp.status_code == 200
            body = json.loads(resp.data)

            assert len(body["items"]) == 1
            for item in body["items"]:
                _check_control_get_method("self", client, item)
                _check_control_get_method("profile", client, item)
                assert "name" in item

            _check_namespace(client, body)
            _check_control_get_method("self", client, body)
            _check_control_get_method("profile", client, body)
            _check_control_get_method("users-all", client, body)
            _check_control_delete_method("delete", client, body)
            resp = client.get(self.INVALID_URL)
            assert resp.status_code == 404

class TestUsersOfOrg(object):
        RESOURCE_URL = "/api/orgs/1/users/"
        INVALID_URL = "/api/orgs/-1/users/"

        def test_get(self, client):
            # Tests for questions by questionnaire GET method.
            resp = client.get(self.RESOURCE_URL)
            assert resp.status_code == 200
            body = json.loads(resp.data)
            assert len(body["items"]) == 1
            
            for item in body["items"]:
                _check_control_get_method("self", client, item)
                _check_control_get_method("profile", client, item)
                assert "name" in item
                assert "email" in item
                assert "pwdhash" in item
                assert "location" in item
                assert "notifications" in item

            _check_namespace(client, body)
            _check_control_get_method("self", client, body)
            _check_control_get_method("profile", client, body)
            _check_control_get_method("orgs-all", client, body)
            _check_control_delete_method("delete", client, body)
            resp = client.get(self.INVALID_URL)
            assert resp.status_code == 404
