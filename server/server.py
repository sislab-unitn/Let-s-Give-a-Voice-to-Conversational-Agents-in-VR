# KumoVoice server

from typing import Generator, AsyncGenerator, Iterable
from fastapi import FastAPI
from fastapi import Depends, FastAPI, Request, Response, status 
from pydantic import BaseModel
import httpx
from fastapi.responses import StreamingResponse
import uvicorn
import sys
import os
import argparse
import tomllib
import pathlib
from pprint import pprint
import json
import base64
import asyncio
import re

# parsing command line arguments for config file
parser = argparse.ArgumentParser(
                    prog = 'KumoVoice',
                    description = 'Server for Wit.ai and Rasa NLU integration for a voice to voice assistant',
                    epilog = 'Enjoy the program! :)')       # positional argument
parser.add_argument('-c', '--config',required=False)      # option that takes a value
args = parser.parse_args()

# check if config file exists
current_path = pathlib.Path(__file__).parent.absolute()
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


# create session for rasa and wit in order to reuse the connection and reduce latency for successive connections
wit_session = httpx.AsyncClient()
rasa_session = httpx.AsyncClient()



# start the server
app = FastAPI()

@app.get("/")
def read_root():
    return {"KumoVoice": "Hi, I am KumoVoice, a voice to voice assistant. Check the documentation for more info on what API endpoints are available."}



@app.post("/text_converse")
async def text_converse(request : Request):
    '''
        expects a json object with sender and message keys
        example: {"sender":"user","message":"hello"}
        
    '''
    # forward the request to rasa server
    url_rasa = f'http{"s" if config["server"]["rasa_SSL"] else ""}://{config["server"]["rasa_host"]}:{config["server"]["rasa_port"]}/webhooks/rest/webhook'
    response_rasa = await rasa_session.post(url = url_rasa ,data = request.stream())
    response_rasa.raise_for_status()
    # get the tracker slot data
    url_tracker = f'http{"s" if config["server"]["rasa_SSL"] else ""}://{config["server"]["rasa_host"]}:{config["server"]["rasa_port"]}/conversations/{request.stream()}/tracker'
    response_tracker = await rasa_session.get(url = url_tracker)
    response_tracker.raise_for_status()
    try:
        response = [response_rasa.json()[0], response_tracker.json()]
    except IndexError:
        response = [response_rasa.json(), response_tracker.json()]
    return response



# @app.post("/audio_converse")
# @app.put("/audio_converse")
# async def audio_converse(request : Request):
#     '''
#         expect a json object with sender and audio keys. The audio data should be a base64 to utf-8 encoded string for the audio file. 
#         Both PUT and POST are accepted because Unity is not able to send a POST request without reEncoding the file.
#     '''
    
#     wit_session = httpx.Client()
#     wit_header = {'Authorization':f'Bearer {config["server"]["wit_API"]}'}
#     wit_first = wit_session.get(f'http{"s" if config["server"]["wit_SSL"] else ""}://{config["server"]["wit_host"]}:{config["server"]["wit_port"]}/message?q=hello',headers=wit_header)
#     rasa_session = httpx.Client()
#     rasa_first = rasa_session.get(f'http{"s" if config["server"]["rasa_SSL"] else ""}://{config["server"]["rasa_host"]}:{config["server"]["rasa_port"]}')

#     # get the audio file from the request and send it to wit.ai
#     url_wit_speech_to_text = f'http{"s" if config["server"]["wit_SSL"] else ""}://{config["server"]["wit_host"]}:{config["server"]["wit_port"]}/dictation'
#     wit_request_header_speech_to_text = dict()
#     wit_request_header_speech_to_text['Authorization'] = f'Bearer {config["server"]["wit_API"]}'
#     wit_request_header_speech_to_text['Content-Type'] = 'audio/wav'
#     # TODO streaming request
#     data = await request.body()
#     data_dict = json.loads(data)
#     wit_request_body_speech_to_text = base64.b64decode(data_dict['audio'])
#     response_wit_speech_to_text = wit_session.post(url = url_wit_speech_to_text ,data =  wit_request_body_speech_to_text ,headers= wit_request_header_speech_to_text)
#     if response_wit_speech_to_text.status_code != 200:
#         return Response(status_code = response_wit_speech_to_text.status_code, content = response_wit_speech_to_text.content, headers = dict(response_wit_speech_to_text.headers))
#     wit_content = response_wit_speech_to_text.content.decode('utf-8').split('\r\n')
#     try:
#         response_dict = json.loads(wit_content[-2])
#     except IndexError:
#         response_dict = json.loads(wit_content[-1])

#     # forward the request to rasa server
#     rasa_body = dict()
#     rasa_body['sender'] = data_dict['sender']
#     rasa_body['message'] = response_dict['text']
#     url_rasa = f'http{"s" if config["server"]["rasa_SSL"] else ""}://{config["server"]["rasa_host"]}:{config["server"]["rasa_port"]}/webhooks/rest/webhook'
#     rasa_request_header = dict()
#     rasa_request_header['Content-Type'] = 'application/json'
#     rasa_body = json.dumps(rasa_body)
#     response_rasa = rasa_session.post(url = url_rasa ,data = rasa_body,headers=rasa_request_header)
#     if response_rasa.status_code != 200:
#         return Response(status_code = response_rasa.status_code, content = response_rasa.content, headers = dict(response_rasa.headers))
    
#     # get the tracker slot data
#     url_tracker = f'http{"s" if config["server"]["rasa_SSL"] else ""}://{config["server"]["rasa_host"]}:{config["server"]["rasa_port"]}/conversations/{data_dict["sender"]}/tracker'
#     response_tracker = rasa_session.get(url = url_tracker)
#     if response_tracker.status_code != 200:
#         return Response(status_code = response_tracker.status_code, content = response_tracker.content, headers = dict(response_tracker.headers))
    
    
#     # get the audio synthetisite from wit.ai
#     url_wit_text_to_speech = f'http{"s" if config["server"]["wit_SSL"] else ""}://{config["server"]["wit_host"]}:{config["server"]["wit_port"]}/synthesize'
#     wit_request_header_text_to_speech = dict()
#     wit_request_header_text_to_speech['Authorization'] = f'Bearer {config["server"]["wit_API"]}'
#     wit_request_header_text_to_speech['Content-Type'] = 'application/json'
#     wit_request_header_text_to_speech['Accept'] = 'audio/wav'
#     response_rasa = response_rasa.json()
#     wit_request = {
#                 "q": response_rasa[0]['text'],
#                 "voice": "Rebecca",
#                 # "style": "soft",
#                 # "speed": 150,
#                 # "pitch": 110,
#                 # "gain": 95
#                 }
#     wit_request_body_text_to_speech = json.dumps(wit_request)
#     response_wit_text_to_speech = wit_session.post(url = url_wit_text_to_speech ,data = wit_request_body_text_to_speech ,headers= wit_request_header_text_to_speech)
#     if response_wit_text_to_speech.status_code != 200:
#         return Response(status_code = response_wit_text_to_speech.status_code, content = response_wit_text_to_speech.content, headers = dict(response_wit_text_to_speech.headers))
#     # compose the final response
#     response = dict()
#     response['sender'] = data_dict['sender']
#     response['message'] = response_dict['text']
#     response['response'] = response_rasa[0]['text']
#     response['audio'] = base64.b64encode(response_wit_text_to_speech.content).decode('utf-8')
#     response['slots'] = response_tracker.json()['slots']
#     # get audio wav final file
#     return Response(status_code=200, content=json.dumps(response), headers={'Content-Type': 'application/json'})



@app.post("/audio_converse_download")
@app.put("/audio_converse_download")
@app.get("/audio_converse_download")
async def audio_converse_download( sender : str, request: Request):
    '''
    This function is used to stream audio from the client to the server. Expecting the audio to be in wav format.
    '''
    import requests
    wit_session = requests.Session()
    rasa_session = requests.Session()

    async def speech_to_text(request) -> str:
       # get the audio file from the request and send it to wit.ai
        url_wit_speech_to_text = f'http{"s" if config["server"]["wit_SSL"] else ""}://{config["server"]["wit_host"]}:{config["server"]["wit_port"]}/dictation'
        wit_request_header_speech_to_text = dict()
        wit_request_header_speech_to_text['Authorization'] = f'Bearer {config["server"]["wit_API"]}'
        wit_request_header_speech_to_text['Content-Type'] = 'audio/wav'
        data = await request.body()
        response_wit_speech_to_text = wit_session.post(url = url_wit_speech_to_text ,data = data ,headers= wit_request_header_speech_to_text)
        response_wit_speech_to_text.raise_for_status()
        wit_content = response_wit_speech_to_text.content.decode('utf-8').split('\r\n')
        try:
            response_dict = json.loads(wit_content[-2])
        except IndexError:
            response_dict = json.loads(wit_content[-1])
        return response_dict['text']
    
    async def text_to_text( input : str, sender : str) -> str:
        # forward the request to rasa server
        rasa_body = dict()
        rasa_body['sender'] = sender
        rasa_body['message'] = input
        url_rasa = f'http{"s" if config["server"]["rasa_SSL"] else ""}://{config["server"]["rasa_host"]}:{config["server"]["rasa_port"]}/webhooks/rest/webhook'
        rasa_request_header = dict()
        rasa_request_header['Content-Type'] = 'application/json'
        rasa_body = json.dumps(rasa_body)
        response_rasa = rasa_session.post(url = url_rasa ,data = rasa_body,headers=rasa_request_header)
        response_rasa.raise_for_status()
        # get the tracker slot data
        url_tracker = f'http{"s" if config["server"]["rasa_SSL"] else ""}://{config["server"]["rasa_host"]}:{config["server"]["rasa_port"]}/conversations/{sender}/tracker'
        response_tracker = rasa_session.get(url = url_tracker)
        response_tracker.raise_for_status()
        
        response = response_rasa.json()[0]["text"]
        return response
    
    async def text_to_speech( text : str ) -> bytes:
        # get the audio synthetisite from wit.ai
        url_wit_text_to_speech = f'http{"s" if config["server"]["wit_SSL"] else ""}://{config["server"]["wit_host"]}:{config["server"]["wit_port"]}/synthesize'
        wit_request_header_text_to_speech = dict()
        wit_request_header_text_to_speech['Authorization'] = f'Bearer {config["server"]["wit_API"]}'
        wit_request_header_text_to_speech['Content-Type'] = 'application/json'
        wit_request_header_text_to_speech['Accept'] = 'audio/wav'
        wit_request = {
                    "q": text,
                    "voice": "Rebecca",
                    # "style": "soft",
                    # "speed": 150,
                    # "pitch": 110,
                    # "gain": 95
                    }
        wit_request_body_text_to_speech = json.dumps(wit_request)
        response_wit_text_to_speech = wit_session.post(url = url_wit_text_to_speech ,data = wit_request_body_text_to_speech,headers=wit_request_header_text_to_speech)
        return response_wit_text_to_speech.content
    
    # get the audio file from the request and send it to wit.ai

    message = await speech_to_text(request)
    pprint(message)
    # rasa response
    response = await text_to_text(message, sender)
    pprint(response)
    # synthesise the response
    audio = await text_to_speech(response)
    return Response(status_code=200, content=audio, headers={'Content-Type': 'audio/wav'})

@app.post("/audio_converse_stream")
@app.put("/audio_converse_stream")
@app.get("/audio_converse_stream")
async def audio_converse_stream( sender : str, request: Request):
    '''
    This function is used to stream audio from the client to the server. Expecting the audio to be in mp3 format.
    '''
    
    async def speech_to_text(request) -> str:
       # get the audio file from the request and send it to wit.ai
        url_wit_speech_to_text = f'http{"s" if config["server"]["wit_SSL"] else ""}://{config["server"]["wit_host"]}:{config["server"]["wit_port"]}/dictation'
        wit_request_header_speech_to_text = dict()
        wit_request_header_speech_to_text['Authorization'] = f'Bearer {config["server"]["wit_API"]}'
        wit_request_header_speech_to_text['Content-Type'] = 'audio/wav'
        wit_request_header_speech_to_text['Transfer-Encoding'] = 'chunked'
        data = request.stream()
        response_wit_speech_to_text = await wit_session.post(url = url_wit_speech_to_text ,data = data ,headers= wit_request_header_speech_to_text,timeout=10)
        response_wit_speech_to_text.raise_for_status()
        wit_content = response_wit_speech_to_text.content.decode('utf-8').split('\r\n')
        try:
            response_dict = json.loads(wit_content[-2])
        except IndexError:
            response_dict = json.loads(wit_content[-1])
        return response_dict['text']
    
    async def text_to_text( input : str, sender : str) -> str:
        # forward the request to rasa server
        rasa_body = dict()
        rasa_body['sender'] = sender
        rasa_body['message'] = input
        url_rasa = f'http{"s" if config["server"]["rasa_SSL"] else ""}://{config["server"]["rasa_host"]}:{config["server"]["rasa_port"]}/webhooks/rest/webhook'
        rasa_request_header = dict()
        rasa_request_header['Content-Type'] = 'application/json'
        rasa_body = json.dumps(rasa_body)
        response_rasa = await rasa_session.post(url = url_rasa ,data = rasa_body,headers=rasa_request_header)
        response_rasa.raise_for_status()
        # get the tracker slot data
        url_tracker = f'http{"s" if config["server"]["rasa_SSL"] else ""}://{config["server"]["rasa_host"]}:{config["server"]["rasa_port"]}/conversations/{sender}/tracker'
        response_tracker = await rasa_session.get(url = url_tracker)
        response_tracker.raise_for_status()
        
        response = response_rasa.json()[0]["text"]
        return response
    
    async def text_to_speech( text : str ) -> AsyncGenerator:
        # get the audio synthetisite from wit.ai
        url_wit_text_to_speech = f'http{"s" if config["server"]["wit_SSL"] else ""}://{config["server"]["wit_host"]}:{config["server"]["wit_port"]}/synthesize'
        wit_request_header_text_to_speech = dict()
        wit_request_header_text_to_speech['Authorization'] = f'Bearer {config["server"]["wit_API"]}'
        wit_request_header_text_to_speech['Content-Type'] = 'application/json'
        wit_request_header_text_to_speech['Accept'] = 'audio/wav'
        wit_request = {
                    "q": text,
                    "voice": "Rebecca",
                    # "style": "soft",
                    # "speed": 150,
                    # "pitch": 110,
                    # "gain": 95
                    }
        wit_request_body_text_to_speech = json.dumps(wit_request)
        async with wit_session.stream('POST', url_wit_text_to_speech,headers=wit_request_header_text_to_speech,data=wit_request_body_text_to_speech,timeout=10) as response:
            async for chunk in response.aiter_bytes():
                yield chunk
    
    # get the audio file from the request and send it to wit.ai
    message = await speech_to_text(request)
    pprint(message)
    # rasa response
    response = await text_to_text(message, sender)
    pprint(response)
    # synthesise the response
    return StreamingResponse(text_to_speech(response), media_type="audio/wav") 

@app.get( "/get_tracker" )
async def get_tracker(sender:str, request : Request):
    async def get_tracker( sender : str) -> str:
        # forward the request to rasa server
        rasa_request_header = dict()
        rasa_request_header['Content-Type'] = 'application/json'
        url_tracker = f'http{"s" if config["server"]["rasa_SSL"] else ""}://{config["server"]["rasa_host"]}:{config["server"]["rasa_port"]}/conversations/{sender}/tracker'
        response_tracker = await rasa_session.get(url = url_tracker)
        response_tracker.raise_for_status()
        
        response =  response_tracker.json()
        return response['slots']

# @app.get("/audio_stream")
# async def audio_converse_stream( sender : str,text:str, request: Request):
#     '''
#     This function is used to stream audio from the client to the server. Expecting the audio to be in mp3 format.
#     '''
    
    
#     async def text_to_speech( text : str ) -> AsyncGenerator:
#         # get the audio synthetisite from wit.ai
#         url_wit_text_to_speech = f'http{"s" if config["server"]["wit_SSL"] else ""}://{config["server"]["wit_host"]}:{config["server"]["wit_port"]}/synthesize'
#         wit_request_header_text_to_speech = dict()
#         wit_request_header_text_to_speech['Authorization'] = f'Bearer {config["server"]["wit_API"]}'
#         wit_request_header_text_to_speech['Content-Type'] = 'application/json'
#         wit_request_header_text_to_speech['Accept'] = 'audio/mpeg'
#         wit_request = {
#                     "q": text,
#                     "voice": "Rebecca",
#                     # "style": "soft",
#                     # "speed": 150,
#                     # "pitch": 110,
#                     # "gain": 95
#                     }
#         wit_request_body_text_to_speech = json.dumps(wit_request)
#         async with wit_session.stream('POST', url_wit_text_to_speech,headers=wit_request_header_text_to_speech,data=wit_request_body_text_to_speech,timeout=10) as response:
#             async for chunk in response.aiter_bytes():
#                 yield chunk

#     # synthesise the response
#     return StreamingResponse(text_to_speech(text), media_type="audio/mpeg") 

# @app.get("/audio_stream_chunked")
# async def audio_converse_stream_chunked( sender : str,text:str, request: Request):
#     '''
#     This function is used to stream audio from the client to the server. Expecting the audio to be in mp3 format.
#     '''
    
    
#     async def text_to_speech( text : str ) -> AsyncGenerator:
#         # get the audio synthetisite from wit.ai
#         url_wit_text_to_speech = f'http{"s" if config["server"]["wit_SSL"] else ""}://{config["server"]["wit_host"]}:{config["server"]["wit_port"]}/synthesize'
#         wit_request_header_text_to_speech = dict()
#         wit_request_header_text_to_speech['Authorization'] = f'Bearer {config["server"]["wit_API"]}'
#         wit_request_header_text_to_speech['Content-Type'] = 'application/json'
#         wit_request_header_text_to_speech['Accept'] = 'audio/pcm'
#         # split the text into sentences based on punctuation
        
#         tokens = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s",text)
#         pprint(tokens)
#         for token in tokens:
#             wit_request = {
#                         "q": token,
#                         "voice": "Rebecca",
#                         # "style": "soft",
#                         # "speed": 150,
#                         # "pitch": 110,
#                         # "gain": 95
#                         }
#             wit_request_body_text_to_speech = json.dumps(wit_request)
#             async with wit_session.stream('POST', url_wit_text_to_speech,headers=wit_request_header_text_to_speech,data=wit_request_body_text_to_speech,timeout=10) as response:
#                 async for chunk in response.aiter_bytes():
#                     yield chunk

#     # synthesise the response
    return StreamingResponse(text_to_speech(text), media_type="audio/pcm") 

# main entry point
if __name__ == "__main__":
    uvicorn.run("__main__:app", host=config['server']['self_host'], port=config['server']['self_port'], reload=True)