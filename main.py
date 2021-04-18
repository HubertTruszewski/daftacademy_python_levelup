from fastapi import FastAPI
from hashlib import sha512
import datetime
from pydantic import BaseModel
from starlette.responses import Response

app = FastAPI()
app.counter = 0
app.list_of_patients = []


class HelloResp(BaseModel):
    msg: str


class MethodResponse(BaseModel):
    method: str


class Person(BaseModel):
    name: str
    surname: str


# class Patient(BaseModel):
#     id: int
#     name: str
#     surname: str
#     register_date: str
#     vaccination_date: str


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
async def auth_get(password: str, password_hash: str, response: Response):
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
    len_sum = len(person.name) + len(person.surname)
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
