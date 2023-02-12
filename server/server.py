# KumoVoice server

from typing import Union
from fastapi import FastAPI
from fastapi import Depends, FastAPI, Response, status 
from pydantic import BaseModel
import requests
from fastapi.security import HTTPBearer
from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse
from fastapi.responses import StreamingResponse
import uvicorn
import sys
import os
import argparse
import tomllib
import pathlib
from pprint import pprint
from fastapi import File, UploadFile
import json
import json_stream
import json_stream.requests
import base64
# parsing command line arguments for config file
parser = argparse.ArgumentParser(
                    prog = 'KumoVoice',
                    description = 'Server for Wit.ai and Rasa NLU integration for a voice to voice assistant',
                    epilog = 'Enjoy the program! :)')       # positional argument
parser.add_argument('-c', '--config',required=False)      # option that takes a value
args = parser.parse_args()

# check if config file exists
current_path = pathlib.Path(__file__).parent.parent.absolute()
config_toml = "config.toml"
config_path = os.path.join(current_path,config_toml)
if args.config:
    # validate config file path
    if os.path.exists(args.config):
        config_path = args.config
    else:
        print(f"'{args.config}' is not a file or does not exist")
        sys.exit(1)
if not os.path.exists(config_path):
    print(f"{config_toml} file not found in the default path in the server directory")
    sys.exit(1)
    
# read config file
with open(config_path,mode='rb') as f:
    config = tomllib.load(f)

app = FastAPI()

@app.get("/")
def read_root():
    return {"KumoVoice": "Hi, I am KumoVoice, a voice to voice assistant. Check the documentation for more info on what API endpoints are available."}


class TextMessage(BaseModel):
    sender: str
    message: str

@app.post("/text_converse")
def text_converse(post_body : TextMessage):
    '''
        expects a json object with sender and message keys
    '''
    pprint(post_body.json())
    # forward the request to rasa server
    url_rasa = f'http{"s" if config["server"]["rasa_SSL"] else ""}://{config["server"]["rasa_host"]}:{config["server"]["rasa_port"]}/webhooks/rest/webhook'
    response_rasa = requests.post(url = url_rasa ,data = post_body.json())
    if response_rasa.status_code != 200:
        return Response(status_code = response_rasa.status_code, content = response_rasa.content, header = dict(response_rasa.headers))
    # get the tracker slot data
    url_tracker = f'http{"s" if config["server"]["rasa_SSL"] else ""}://{config["server"]["rasa_host"]}:{config["server"]["rasa_port"]}/conversations/{post_body.sender}/tracker'
    response_tracker = requests.get(url = url_tracker)
    if response_tracker.status_code != 200:
        return Response(status_code = response_tracker.status_code, content = response_tracker.content, header = dict(response_tracker.headers))
    try:
        response = [response_rasa.json()[0], response_tracker.json()]
    except IndexError:
        response = [response_rasa.json(), response_tracker.json()]
    return response


@app.post("/audio_converse")
async def audio_converse(request : Request):
    '''
        expect a json object with sender and audio keys. The audio data should be a base64 to utf-8 encoded string for the audio file
    '''
    
    # get the audio file from the request and send it to wit.ai
    url_wit_speech_to_text = f'http{"s" if config["server"]["wit_SSL"] else ""}://{config["server"]["wit_host"]}:{config["server"]["wit_port"]}/dictation'
    wit_request_header_speech_to_text = dict()
    wit_request_header_speech_to_text['Authorization'] = f'Bearer {config["server"]["wit_API"]}'
    wit_request_header_speech_to_text['Content-Type'] = 'audio/wav'
    # TODO streaming request
    data = await request.body()
    data_dict = json.loads(data)
    wit_request_body_speech_to_text = base64.b64decode(data_dict['audio'])
    response_wit_speech_to_text = requests.post(url = url_wit_speech_to_text ,data =  wit_request_body_speech_to_text ,headers= wit_request_header_speech_to_text,stream=True)
    if response_wit_speech_to_text.status_code != 200:
        return Response(status_code = response_wit_speech_to_text.status_code, content = response_wit_speech_to_text.content, headers = dict(response_wit_speech_to_text.headers))
    wit_content = response_wit_speech_to_text.content.decode('utf-8').split('\r\n')
    try:
        response_dict = json.loads(wit_content[-2])
    except IndexError:
        response_dict = json.loads(wit_content[-1])

    # forward the request to rasa server
    rasa_body = dict()
    rasa_body['sender'] = data_dict['sender']
    rasa_body['message'] = response_dict['text']
    url_rasa = f'http{"s" if config["server"]["rasa_SSL"] else ""}://{config["server"]["rasa_host"]}:{config["server"]["rasa_port"]}/webhooks/rest/webhook'
    rasa_request_header = dict()
    rasa_request_header['Content-Type'] = 'application/json'
    rasa_body = json.dumps(rasa_body)
    response_rasa = requests.post(url = url_rasa ,data = rasa_body,headers=rasa_request_header)
    if response_rasa.status_code != 200:
        return Response(status_code = response_rasa.status_code, content = response_rasa.content, headers = dict(response_rasa.headers))
    
    # get the tracker slot data
    url_tracker = f'http{"s" if config["server"]["rasa_SSL"] else ""}://{config["server"]["rasa_host"]}:{config["server"]["rasa_port"]}/conversations/{data_dict["sender"]}/tracker'
    response_tracker = requests.get(url = url_tracker)
    if response_tracker.status_code != 200:
        return Response(status_code = response_tracker.status_code, content = response_tracker.content, headers = dict(response_tracker.headers))
    
    
    # get the audio synthetisite from wit.ai
    url_wit_text_to_speech = f'http{"s" if config["server"]["wit_SSL"] else ""}://{config["server"]["wit_host"]}:{config["server"]["wit_port"]}/synthesize'
    wit_request_header_text_to_speech = dict()
    wit_request_header_text_to_speech['Authorization'] = f'Bearer {config["server"]["wit_API"]}'
    wit_request_header_text_to_speech['Content-Type'] = 'application/json'
    wit_request_header_text_to_speech['Accept'] = 'audio/wav'
    response_rasa = response_rasa.json()
    wit_request = {
                "q": response_rasa[0]['text'],
                "voice": "Rebecca",
                # "style": "soft",
                # "speed": 150,
                # "pitch": 110,
                # "gain": 95
                }
    wit_request_body_text_to_speech = json.dumps(wit_request)
    response_wit_text_to_speech = requests.post(url = url_wit_text_to_speech ,data = wit_request_body_text_to_speech ,headers= wit_request_header_text_to_speech,stream=False)
    if response_wit_text_to_speech.status_code != 200:
        return Response(status_code = response_wit_text_to_speech.status_code, content = response_wit_text_to_speech.content, headers = dict(response_wit_text_to_speech.headers))
    # compose the final response
    response = dict()
    response['sender'] = data_dict['sender']
    response['message'] = response_rasa[0]['text']
    response['audio'] = base64.b64encode(response_wit_text_to_speech.content).decode('utf-8')
    response['tracker'] = response_tracker.json()
    # get audio wav final file
    return Response(status_code=200, content=json.dumps(response), headers={'Content-Type': 'application/json'})

if __name__ == "__main__":
    uvicorn.run("__main__:app", host=config['server']['self_host'], port=config['server']['self_port'], reload=True)