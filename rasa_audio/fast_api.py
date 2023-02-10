from typing import Union
from fastapi import FastAPI
from fastapi import Depends, FastAPI, Response, status 
from pydantic import BaseModel
import requests
from fastapi.security import HTTPBearer
from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse

wit_URL = "https://api.wit.ai/"
app = FastAPI()

token_auth_scheme = HTTPBearer()

# class Item(BaseModel):

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/message")
def message(q:str,v:str ="20221114",token: str = Depends(token_auth_scheme)):
    r = requests.get(url = wit_URL+'message', params = {"q":q,"v":v},headers={'Authorization': 'Bearer ' + token.credentials})
    return r.json()
@app.get("/language")
def language(q:str,v:str ="20221114",token: str = Depends(token_auth_scheme)):
    r = requests.get(url = wit_URL+'language', params = {"q":q,"v":v},headers={'Authorization': 'Bearer ' + token.credentials})
    return r.json()
@app.get("/intents")
def intents(v:str ="20221114",token: str = Depends(token_auth_scheme)):
    r = requests.get(url = wit_URL+'intents', params = {"v":v},headers={'Authorization': 'Bearer ' + token.credentials})
    return r.json()
@app.get("/entities")
def entities(v:str ="20221114",token: str = Depends(token_auth_scheme)):
    r = requests.get(url = wit_URLE+'entities', params = {"v":v},headers={'Authorization': 'Bearer ' + token.credentials})
    return r.json()
@app.get("/traits")
def traits(v:str ="20221114",token: str = Depends(token_auth_scheme)):
    r = requests.get(url = wit_URL+'traits', params = {"v":v},headers={'Authorization': 'Bearer ' + token.credentials})
    return r.json()
@app.get("/utterances")
def utterances(v:str ="20221114",token: str = Depends(token_auth_scheme)):
    r = requests.get(url = wit_URL+'utterances', params = {"v":v},headers={'Authorization': 'Bearer ' + token.credentials})
    return r.json()
@app.get("/app")
def get_app(v:str ="20221114",token: str = Depends(token_auth_scheme)):
    r = requests.get(url = wit_URL+'app', params = {"v":v},headers={'Authorization': 'Bearer ' + token.credentials})
    return r.json()
@app.get("/voices")
def voices(v:str ="20221114",token: str = Depends(token_auth_scheme)):
    r = requests.get(url = wit_URL+'voices', params = {"v":v},headers={'Authorization': 'Bearer ' + token.credentials})
    return r.json()