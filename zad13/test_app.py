from fastapi.testclient import TestClient
from main import app
import pytest
import datetime

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'message': 'Hello world!'}


@pytest.mark.parametrize("name", ["Zenek", "Marek", "Alojzy Niezdąży"])
def test_hello_name(name):
    name = 'Kamila'
    response = client.get(f"/hello/{name}")
    assert response.status_code == 200
    assert response.json() == {"msg": f'Hello {name}'}


def test_counter():
    response = client.get("/counter")
    assert response.status_code == 200
    assert response.text == "1"
    # 2nd Try
    response = client.get("/counter")
    assert response.status_code == 200
    assert response.text == "2"


def test_get_method():
    response = client.get("/method")
    assert response.status_code == 200
    assert response.json() == {'method': 'GET'}


def test_put_method():
    response = client.put("/method")
    assert response.status_code == 200
    assert response.json() == {'method': 'PUT'}


def test_post_method():
    response = client.post("/method")
    assert response.status_code == 201
    assert response.json() == {'method': 'POST'}


def test_options_method():
    response = client.options("/method")
    assert response.status_code == 200
    assert response.json() == {'method': 'OPTIONS'}


def test_delete_method():
    response = client.delete("/method")
    assert response.status_code == 200
    assert response.json() == {'method': 'DELETE'}


def test_auth_param1():
    response = client.get("/auth?password=haslo&password_hash=013c6889f799cd986a735118e1888727d1435f7f623d05d58c61bf2cd8b49ac90105e5786ceaabd62bbc27336153d0d316b2d13b36804080c44aa6198c533215")
    assert response.status_code == 204


def test_auth_param2():
    response = client.get("/auth?password=haslo&password_hash=f34ad4b3ae1e2cf33092e2abb60dc0444781c15d0e2e9ecdb37e4b14176a0164027b05900e09fa0f61a1882e0b89fbfa5dcfcc9765dd2ca4377e2c794837e091")
    assert response.status_code == 401


def test_register():
    person_data = {"name": "Jan", "surname": "Nowak"}
    response = client.post("/register", json=person_data)
    result = response.json()
    assert response.status_code == 201
    actual_id = result['id']
    assert result['name'] == "Jan"
    assert result['surname'] == "Nowak"
    assert result['register_date'] == datetime.date.today().isoformat()
    assert result['vaccination_date'] == (datetime.date.today()+datetime.timedelta(days=8)).isoformat()

    person_data = {"name": "Jan", "surname": "Kowalski"}
    response = client.post("/register", json=person_data)
    result = response.json()
    assert result['id'] == actual_id + 1
    assert result['name'] == "Jan"
    assert result['surname'] == "Kowalski"
    assert result['register_date'] == datetime.date.today().isoformat()
    assert result['vaccination_date'] == (datetime.date.today()+datetime.timedelta(days=11)).isoformat()


def test_patient():
    person_data = {"name": "Jan", "surname": "Nowak"}
    response = client.post("/register", json=person_data)
    response = client.get("/patient/1")
    assert response.json()['name'] == "Jan"


def test_today_date():
    response = client.get("/hello")
    today_date = datetime.date.today().isoformat()
    expected_text = "<h1>Hello! Today date is {}</h1>".format(today_date)
    assert response.headers['content-type'] == 'text/html; charset=utf-8'
    assert expected_text == response.text


def test_session_login():
    request = client.post("/login_session", headers={"Authorization": "Base NGRtMW46Tm90U29TZWN1cmVQYSQk"})
    assert bool(request.cookies.get("session_token")) is True


def test_session_login_bad():
    request = client.post("/login_session", headers={"Authorization": "Base NGRtMW46Tm90U29TZWN1cmVQYStk"})
    assert request.status_code == 401


def test_token_login():
    request = client.post("/login_token", headers={"Authorization": "Base NGRtMW46Tm90U29TZWN1cmVQYSQk"})
    assert bool(request.json()['token']) is True


def test_token_login_bad():
    request = client.post("/login_token", headers={"Authorization": "Base NGRtMW46Tm90U29TZWN1cmVQYStk"})
    assert request.status_code == 401


def test_welcome_session():
    client.post("/login_session", headers={"Authorization": "Base NGRtMW46Tm90U29TZWN1cmVQYSQk"})
    token = "e8b95475a7443b0ab27514d214373ac2508d9272c6080fab22191f6028c488ac65bbf2973b2366b80cd859cd92ea9f083710e3a0d994d7c5e62c4b85cacb63ae"
    request = client.get("/welcome_session", cookies={"session_token": token})
    assert request.status_code == 200
    assert request.text == "Welcome!"
    assert request.headers['content-type'] == 'text/plain; charset=utf-8'


def test_welcome_session_json():
    client.post("/login_session", headers={"Authorization": "Base NGRtMW46Tm90U29TZWN1cmVQYSQk"})
    token = "e8b95475a7443b0ab27514d214373ac2508d9272c6080fab22191f6028c488ac65bbf2973b2366b80cd859cd92ea9f083710e3a0d994d7c5e62c4b85cacb63ae"
    request = client.get("/welcome_session?format=json", cookies={"session_token": token})
    assert request.status_code == 200
    assert request.json()['message'] == "Welcome!"
    assert request.headers['content-type'] == 'application/json'


def test_welcome_session_html():
    client.post("/login_session", headers={"Authorization": "Base NGRtMW46Tm90U29TZWN1cmVQYSQk"})
    token = "e8b95475a7443b0ab27514d214373ac2508d9272c6080fab22191f6028c488ac65bbf2973b2366b80cd859cd92ea9f083710e3a0d994d7c5e62c4b85cacb63ae"
    request = client.get("/welcome_session?format=html", cookies={"session_token": token})
    assert request.status_code == 200
    assert request.text == "<h1>Welcome!</h1>"
    assert request.headers['content-type'] == 'text/html; charset=utf-8'


def test_welcome_session_bad():
    client.post("/login_session", headers={"Authorization": "Base NGRtMW46Tm90U29TZWN1cmVQYSQk"})
    token = "e8b95475a7443b0ab27514d214373ac2508d9272c6080fab22791f6028c488ac65bbf2973b2366b80cd859cd92ea9f083710e3a0d994d7c5e62c4b85cacb63ae"
    request = client.get("/welcome_session?format=json", cookies={"session_token": token})
    assert request.status_code == 401


def test_welcome_token():
    client.post("/login_token", headers={"Authorization": "Base NGRtMW46Tm90U29TZWN1cmVQYSQk"})
    token = "e8b95475a7443b0ab27514d214373ac2508d9272c6080fab22191f6028c488ac65bbf2973b2366b80cd859cd92ea9f083710e3a0d994d7c5e62c4b85cacb63ae"
    request = client.get(f"/welcome_token?token={token}")
    assert request.status_code == 200
    assert request.text == "Welcome!"
    assert request.headers['content-type'] == 'text/plain; charset=utf-8'


def test_welcome_token_json():
    client.post("/login_token", headers={"Authorization": "Base NGRtMW46Tm90U29TZWN1cmVQYSQk"})
    token = "e8b95475a7443b0ab27514d214373ac2508d9272c6080fab22191f6028c488ac65bbf2973b2366b80cd859cd92ea9f083710e3a0d994d7c5e62c4b85cacb63ae"
    request = client.get(f"/welcome_token?format=json&token={token}")
    assert request.status_code == 200
    assert request.json()['message'] == "Welcome!"
    assert request.headers['content-type'] == 'application/json'


def test_welcome_token_html():
    client.post("/login_token", headers={"Authorization": "Base NGRtMW46Tm90U29TZWN1cmVQYSQk"})
    token = "e8b95475a7443b0ab27514d214373ac2508d9272c6080fab22191f6028c488ac65bbf2973b2366b80cd859cd92ea9f083710e3a0d994d7c5e62c4b85cacb63ae"
    request = client.get(f"/welcome_token?format=html&token={token}")
    assert request.status_code == 200
    assert request.text == "<h1>Welcome!</h1>"
    assert request.headers['content-type'] == 'text/html; charset=utf-8'


def test_welcome_token_bad():
    client.post("/login_token", headers={"Authorization": "Base NGRtMW46Tm90U29TZWN1cmVQYSQk"})
    token = "e8b95475a7443b7ab27514d214373ac2508d9272c6080fab22191f6028c488ac65bbf2973b2366b80cd859cd92ea9f083710e3a0d994d7c5e62c4b85cacb63ae"
    request = client.get(f"/welcome_token?format=html&token={token}")
    assert request.status_code == 401


def test_logout_token():
    client.post("/login_token", headers={"Authorization": "Base NGRtMW46Tm90U29TZWN1cmVQYSQk"})
    token = "e8b95475a7443b0ab27514d214373ac2508d9272c6080fab22191f6028c488ac65bbf2973b2366b80cd859cd92ea9f083710e3a0d994d7c5e62c4b85cacb63ae"
    request = client.delete(f"/logout_token?token={token}&format=html")
    assert request.status_code == 302
