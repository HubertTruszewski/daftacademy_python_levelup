from fastapi import FastAPI, Header
from hashlib import sha512
import datetime
import random
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Cookie, Query
import uvicorn
import base64
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse, Response

app = FastAPI()
app.counter = 0
app.session_token = []
app.token = []
app.list_of_patients = []


class HelloResp(BaseModel):
    msg: str


class MethodResponse(BaseModel):
    method: str


class Person(BaseModel):
    name: str
    surname: str


class Patient(BaseModel):
    id: int
    name: str
    surname: str
    register_date: str
    vaccination_date: str


@app.get("/")
def root():
    return {"message": "Hello world!"}


@app.get("/hello/{name}", response_model=HelloResp)
async def read_item(name: str):
    return HelloResp(msg=f"Hello {name}")


@app.get('/counter')
def counter():
    app.counter += 1
    return app.counter


@app.get("/method", response_model=MethodResponse)
def method_get():
    return MethodResponse(method="GET")


@app.put("/method", response_model=MethodResponse)
def method_put():
    return MethodResponse(method="PUT")


@app.post("/method", response_model=MethodResponse)
def method_post(response: Response):
    response.status_code = 201
    return MethodResponse(method="POST")


@app.options("/method", response_model=MethodResponse)
def method_options():
    return MethodResponse(method="OPTIONS")


@app.delete("/method", response_model=MethodResponse)
def method_delete():
    return MethodResponse(method="DELETE")


@app.get("/auth")
async def auth_get(response: Response, password: str = None, password_hash: str = None):
    print(password)
    print(password_hash)
    if password is None or password_hash is None or len(password_hash) == 0 or len(password) == 0:
        response.status_code = 401
        return
    encoded_password = password.encode()
    hashed = sha512(encoded_password).hexdigest()
    if hashed == password_hash:
        response.status_code = 204
    else:
        response.status_code = 401


@app.post("/register", response_model=Patient)
async def register_post(person: Person, response: Response):
    len_name = len(''.join([i for i in person.name if i.isalpha()]))
    len_surname = len(''.join([i for i in person.surname if i.isalpha()]))
    len_sum = len_name + len_surname
    response_date = datetime.date.today()
    date_to_add = datetime.timedelta(days=len_sum)
    vaccination_date = response_date + date_to_add
    person_id = len(app.list_of_patients)+1
    response.status_code = 201
    patient = Patient(id=person_id, name=person.name, surname=person.surname,
                      register_date=response_date.isoformat(), vaccination_date=vaccination_date.isoformat())
    app.list_of_patients.append(patient)
    return patient


@app.get("/patient/{id}", response_model=Patient)
async def patient_get(id: int, response: Response):
    if id < 1:
        response.status_code = 400
    elif id > len(app.list_of_patients):
        response.status_code = 404
    else:
        response.status_code = 200
        return app.list_of_patients[id-1]


@app.get("/hello")
async def hello():
    today_date = datetime.date.today().isoformat()
    content = "<h1>Hello! Today date is {}</h1>".format(today_date)
    return HTMLResponse(content=content)


def check_password_and_generate_token(header):
    auth_header = header
    decoded_data = auth_header.split(" ")[1]
    decoded_data_bytes = decoded_data.encode('ascii')
    base_decode_result = base64.b64decode(decoded_data_bytes)
    result = base_decode_result.decode('ascii')
    user, password = tuple(result.split(":"))
    if user == "4dm1n" and password == "NotSoSecurePa$$":
        random_num = random.randint(0, 1000)
        token = sha512((user+password+str(random_num)).encode())
        return token.hexdigest()
    return False


@app.post("/login_session")
async def login_session(response: Response, Authorization: str = Header(None)):
    token = check_password_and_generate_token(Authorization)
    if token:
        if len(app.session_token) == 3:
            app.session_token = app.session_token[1:]
        app.session_token.append(token)
        response.set_cookie(key="session_token", value=token)
        response.status_code = 201
        return "OK"
    raise HTTPException(status_code=401, detail='Unauthorized')


@app.post("/login_token")
async def login_token(response: Response, Authorization: str = Header(None)):
    token = check_password_and_generate_token(Authorization)
    if token:
        if len(app.token) == 3:
            app.token = app.token[1:]
        app.token.append(token)
        response.status_code = 201
        return {"token": token}
    raise HTTPException(status_code=401, detail='Unauthorized')


@app.get('/welcome_session')
async def welcome_session(format: str = Query(None), session_token=Cookie(None)):
    if session_token is None or session_token not in app.session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if format == 'json':
        msg = {"message": "Welcome!"}
        json_msg = jsonable_encoder(msg)
        return JSONResponse(content=json_msg)
    elif format == 'html':
        return HTMLResponse('<h1>Welcome!</h1>')
    else:
        return PlainTextResponse('Welcome!')


@app.get('/welcome_token')
async def welcome_token(format: str = Query(None),  token: str = ""):
    if token is False or token not in app.token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if format == 'json':
        msg = {"message": "Welcome!"}
        json_msg = jsonable_encoder(msg)
        return JSONResponse(content=json_msg)
    elif format == 'html':
        return HTMLResponse('<h1>Welcome!</h1>')
    else:
        return PlainTextResponse('Welcome!')


@app.delete("/logout_session")
async def logout_session(format: str = Query(None), session_token=Cookie(None)):
    if session_token is False or session_token not in app.session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    app.session_token.remove(session_token)
    resp = RedirectResponse("/logged_out?format={}".format(format), status_code=302)
    return resp


@app.delete("/logout_token")
async def logout_token(format: str = Query(None), token: str = Query(None)):
    if token is False or token not in app.token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    app.token.remove(token)
    resp = RedirectResponse("/logged_out?format={}".format(format), status_code=302)
    return resp


@app.get("/logged_out")
async def logged_out(format: str = Query(None)):
    if format == "json":
        msg = {"message": "Logged out!"}
        json_msg = jsonable_encoder(msg)
        return JSONResponse(json_msg)
    elif format == "html":
        msg = "<h1>Logged out!</h1>"
        return HTMLResponse(content=msg)
    else:
        return PlainTextResponse(content="Logged out!")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
