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

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/text_converse")
def message(q:str,v:str ="20221114",token: str = Depends(token_auth_scheme)):
    r = requests.get(url = wit_URL+'message', params = {"q":q,"v":v},headers={'Authorization': 'Bearer ' + token.credentials})
    return r.json()
@app.get("/audio_converse")
def language(q:str,v:str ="20221114",token: str = Depends(token_auth_scheme)):
    r = requests.get(url = wit_URL+'language', params = {"q":q,"v":v},headers={'Authorization': 'Bearer ' + token.credentials})
    return r.json()