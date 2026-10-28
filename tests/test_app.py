import pytest

import app as aceest


@pytest.fixture
def client():
    aceest.clients.clear()
    aceest._next_id = 1
    aceest.app.config["TESTING"] = True
    with aceest.app.test_client() as c:
        yield c


def make_client(c, **overrides):
    payload = {"name": "Ravi", "program": "FL", "weight": 80, "height": 175}
    payload.update(overrides)
    return c.post("/clients", json=payload)


def test_index(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.get_json()["status"] == "running"


def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok"}


def test_list_programs(client):
    data = client.get("/programs").get_json()
    assert set(data) == {"FL", "MG", "BG"}


def test_get_program_case_insensitive(client):
    r = client.get("/programs/mg")
    assert r.status_code == 200
    assert r.get_json()["name"] == "Muscle Gain"


def test_unknown_program(client):
    assert client.get("/programs/XX").status_code == 404


def test_add_client(client):
    r = make_client(client)
    assert r.status_code == 201
    body = r.get_json()
    assert body["id"] == 1
    assert body["bmi"] == 26.1
    assert body["calories"] == 1920


def test_add_client_missing_name(client):
    assert make_client(client, name=" ").status_code == 400


def test_add_client_bad_program(client):
    assert make_client(client, program="ZZ").status_code == 400


@pytest.mark.parametrize("field,value", [("weight", -5), ("height", 0), ("weight", "abc"), ("height", None)])
def test_add_client_bad_numbers(client, field, value):
    assert make_client(client, **{field: value}).status_code == 400


def test_get_and_list_clients(client):
    make_client(client)
    assert client.get("/clients/1").get_json()["name"] == "Ravi"
    assert len(client.get("/clients").get_json()) == 1


def test_get_missing_client(client):
    assert client.get("/clients/99").status_code == 404


def test_delete_client(client):
    make_client(client)
    assert client.delete("/clients/1").status_code == 204
    assert client.get("/clients/1").status_code == 404
    assert client.delete("/clients/1").status_code == 404


def test_calc_bmi():
    assert aceest.calc_bmi(70, 175) == 22.9
    with pytest.raises(ValueError):
        aceest.calc_bmi(70, 0)


def test_calc_calories():
    assert aceest.calc_calories("MG", 70) == 2450
    with pytest.raises(KeyError):
        aceest.calc_calories("XX", 70)
