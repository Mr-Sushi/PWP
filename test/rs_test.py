import json
import os
import pytest
import sys
import tempfile
from datetime import datetime
from jsonschema import validate
from eventhub import app, db
from eventhub.models import Event, User, Organization
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError



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
        time=datetime.strptime("20.02.2020 20:20", "%d.%m.%Y %H:%M"),
        description="Something",
        location="Oulu",
        organization="1"
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
    db.session.add(org1)
    db.session.add(org2)

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


def _get_event(number=1):
    event_dict = {
        "name": "Karaoke",
        "time": "9:23",
        "description": "Something",
        "location": "Routa, Oulu",
        "organization": 1
    }
    return json.dumps(event_dict)

def _get_org():
    return {
        "name" : "OTiT"
    }

def _get_user(number=1):
    user_dict = {
        "name": "DanceMonkey",
        "email": "test@163.com",
        "password": "password",
        "location": "University of Oulu",
        "notifications": 0
    }
    
    return json.dumps(user_dict)


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
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201


class TestEventCollection(object):
    RESOURCE_URL = "/api/events/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_namespace(client, body)
        _check_control_post_method("eventhub:add-event", client, body)
        assert len(body["event_list"]) == 1
        for item in body["event_list"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "id" in item
            assert "name" in item
            assert "description" in item

    def test_post(self, client):
        valid = _get_event(number=2)

        # test with valid and see that it exists afterward

        resp = client.post(self.RESOURCE_URL, json=valid)
        body = json.loads(client.get(self.RESOURCE_URL).data)
        id = body["event_list"][-1]["id"]
        assert resp.status_code == 201

        assert resp.headers["Location"].endswith(self.RESOURCE_URL + str(id) + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "event-2"
        assert body["description"] == "test"

        # test with wrong content type(must be json)
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # remove title field for 400
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400


class TestEventItem(object):
    RESOURCE_URL = "/api/events/<id>/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "PWP Meeting"
        assert body["description"] == "Test event"
        assert body["time"] == datetime.strptime("20.02.2020 20:20", "%d.%m.%Y %H:%M")
        assert body["location"] == "Oulu"
        assert body["organization"] =="OTiT"
        _check_namespace(client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("eventhub:events-all", client, body)
        _check_control_put_method("edit", client, body, "event")

    def test_put(self, client):
        valid = _get_event(number=3)
        # test with valid
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # remove field title for 400
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 405

        valid = _get_event(number=4)
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == valid["name"] and body["description"] == valid["description"]

    def test_delete(self, client):
        """Test for valid DELETE method"""
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404


class TestOrgCollection():
    RESOURCE_URL = "/api/orgs/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)

        assert len(body["orgs_list"]) == 1
        for item in body["orgs_list"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "name" in item

            _check_namespace(client, body)
        _check_control_get_method("self", client, body)

        _check_namespace(client, body)
        for item in body["orgs_list"]:
            assert item["name"] == "Something"
            _check_namespace(client, item)
            _check_control_get_method("profile", client, item)
            _check_control_get_method("events-all", client, item)
            _check_control_put_method("edit", client, item, "org")

    def test_post_valid_request(self,client):
        valid = _get_org()
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code ==201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + valid["name"] + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "extra-sensor-1"

    def test_post(self, client):
        valid = _get_org()
        

        # test with wrong content type(must be json)
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # remove title field for 400
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400


class TestOrgItem(object):
    RESOURCE_URL = "/api/orgs/<id>/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)

        assert len(body["name"]) == 1
        for item in body["name"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "name" in item

            _check_namespace(client, body)
        _check_control_get_method("self", client, body)
        _check_control_get_method("profile", client, body)


        _check_namespace(client, body)
        for item in body["name"]:
            assert item["name"] == "Something"
            assert item["description"] == "Test Org"
            _check_namespace(client, item)
            _check_control_get_method("profile", client, item)
            _check_control_get_method("eventhub:events-all", client, item)
            _check_control_put_method("edit", client, item, "org")

    def test_put(self, client):
        #　user = _get_user(5)
        # resp_post = client.post("/api/users/", json=user)
        resp_put = client.put("/api/users/3/events/1/")

        # test with valid
        assert resp_put.status_code == 204

        # test with another url
        resp_conf = client.put(self.RESOURCE_URL)
        assert resp_conf.status_code == 409

    def test_delete(self, client):
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)


class TestUserEvent(object):
    RESOURCE_URL = "/api/events/<event_id>/users/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)

        assert len(body["followed_events"]) == 1
        for event in body["followed_events"]:
            _check_control_get_method("self", client)
            _check_control_get_method("profile", client)
            assert "name" in event
            assert "time" in event
            assert "description" in event
            assert "location" in event
            assert "organization" in event

            # _check_namespace(client, body)
        _check_control_get_method("self", client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("eventhub:users-all", client, body)
        _check_control_delete_method("eventhub:delete", client, body)

        _check_namespace(client, body)
        for item in body["items"]:
            assert item["name"] == "PWP Meeting"
            assert item["description"] == "Test event"
            _check_namespace(client, item)
            _check_control_get_method("profile", client, item)
            _check_control_get_method("eventhub:events-all", client, item)
            _check_control_put_method("edit", client, item, "event")



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
        _check_control_post_method("eventhub:add-user", client, body)
        _check_control_post_method("eventhub:all-user", client, body)
        assert len(body["items"]) == 2
        for item in body["items"]:
            _check_control_get_method("self", client, item)
            _check_control_get_method("profile", client, item)
            assert "name" in item

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and
        also checks that a valid request receives a 201 response with a
        location header that leads into the newly created resource.
        """
        valid = _get_user(number=2)

        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        body = json.loads(client.get(self.RESOURCE_URL).data)
        id = body["items"][-1]["id"]
        # assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + str(id) + "/")

        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)

        assert body["username"] == "user-2"
        assert body["name"] == "test user"

        # test with wrong content type(must be json)
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # remove title field for 400
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400


class TestUserItem(object):
    RESOURCE_URL = "/api/users/<id>/"

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
        assert body["username"] == 'user-1'
        assert body["name"] == "user-1"
        body["name"] = "asdasdas"
        _check_namespace(client, body)
        _check_control_get_method("self", client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("eventhub:users-all", client, body)
        _check_control_put_method("edit", client, body, "user")
        _check_control_delete_method("eventhub:delete", client, body)


    def test_put(self, client):
        """Test for valid PUT method"""
        valid = _get_user(number=1)

        # test with valid

        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # remove field title for 400
        valid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 405

        valid["name"] = "ggs"
        # resp_put = client.put(self.RESOURCE_URL, json=valid)

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        print(body)
        assert body["name"] == valid["name"] and body["username"] == valid["username"]

    def test_delete(self, client):
        """Test for valid DELETE method"""
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404


class TestUserOrg(object):
    RESOURCE_URL = "/api/orgs/<org_id>/users/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)

        assert len(body["orgs"]) == 1
        for org in body["orgs"]:
            _check_control_get_method("self", client)
            _check_control_get_method("profile", client)
            assert "name" in org

            # _check_namespace(client, body)
        _check_control_get_method("self", client, body)
        _check_control_get_method("profile", client, body)
        _check_control_get_method("eventhub:users-all", client, body)
        _check_control_delete_method("eventhub:delete", client, body)


        _check_namespace(client, body)
        for item in body["organization"]:
            assert item["name"] == org.name
            _check_namespace(client, item)
            _check_control_get_method("profile", client, item)
            _check_control_get_method("eventhub:events-all", client, item)
            _check_control_put_method("edit", client, item, "org")