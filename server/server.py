# KumoVoice server

from typing import Generator, AsyncGenerator, Iterable
from fastapi import FastAPI
from fastapi import Depends, FastAPI, Request, Response, status 
from fastapi.responses import StreamingResponse
import uvicorn
from uvicorn.config import LOGGING_CONFIG
import httpx
import sys
import os
import argparse
try:
    import tomllib
except:
    import toml as tomllib
import pathlib
from pprint import pprint
import json
import base64
import asyncio
import re
import time

# parsing command line arguments for config file
parser = argparse.ArgumentParser(
                    prog = 'KumoVoice',
                    description = 'Server for tts.ai and Rasa NLU integration for a voice to voice assistant',
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
with open(config_path,mode='r') as f:
    config = tomllib.loads(f.read())


# create session for rasa and tts in order to reuse the connection and reduce latency for successive connections

rasa_session = httpx.AsyncClient()
asr_session = httpx.AsyncClient()
tts_session = httpx.AsyncClient()



# start the server
app = FastAPI()



async def speech_to_text(request) -> str:
    # get the audio file from the request and send it to tts.ai
    url_asr_speech_to_text = f'http{"s" if config["server"]["asr_SSL"] else ""}://{config["server"]["asr_host"]}:{config["server"]["asr_port"]}/asr'
    asr_request_header_speech_to_text = dict()
    #asr_request_header_speech_to_text['Authorization'] = f'Bearer {config["server"]["asr_API"]}'
    asr_request_header_speech_to_text['Content-Type'] = 'audio/wav'
    asr_request_header_speech_to_text['Transfer-Encoding'] = 'chunked'
    data = request.stream()
    response_asr_speech_to_text = await asr_session.post(url = url_asr_speech_to_text ,data = data ,headers= asr_request_header_speech_to_text,timeout=10)
    response_asr_speech_to_text.raise_for_status()
    asr_content = response_asr_speech_to_text.content.decode('utf-8').split('\r\n')
    try:
        response_dict = json.loads(asr_content[-2])
    except IndexError:
        response_dict = json.loads(asr_content[-1])
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
    # url_tracker = f'http{"s" if config["server"]["rasa_SSL"] else ""}://{config["server"]["rasa_host"]}:{config["server"]["rasa_port"]}/conversations/{sender}/tracker'
    # response_tracker = await rasa_session.get(url = url_tracker)
    # response_tracker.raise_for_status()
    
    response = response_rasa.json()[0]["text"]
    return response

async def text_to_speech( text : str ) -> AsyncGenerator:
    # get the audio synthetisite from tts.ai
    url_tts_text_to_speech = f'http{"s" if config["server"]["tts_SSL"] else ""}://{config["server"]["tts_host"]}:{config["server"]["tts_port"]}/tts'
    tts_request_header_text_to_speech = dict()
    tts_request_header_text_to_speech['Content-Type'] = 'application/json'
    tts_request_header_text_to_speech['Accept'] = 'audio/raw'
    tts_request = {
                "text": text,
                }
    tts_request_body_text_to_speech = json.dumps(tts_request)
    async with tts_session.stream('POST', url_tts_text_to_speech,headers=tts_request_header_text_to_speech,data=tts_request_body_text_to_speech,timeout=10) as response:
        async for chunk in response.aiter_bytes():
            yield chunk


@app.get("/")
def read_root():
    return {"KumoVoice": "Hi, I am KumoVoice, a voice to voice assistant. Check the documentation for more info on what API endpoints are available."}



@app.post("/text_converse")
async def text_converse(request : Request):
    '''
        expects a json object ttsh sender and message keys
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

async def get_tracker_data( sender : str) -> bytes:
    # forward the request to rasa server
    rasa_request_header = dict()
    rasa_request_header['Content-Type'] = 'application/json'
    url_tracker = f'http{"s" if config["server"]["rasa_SSL"] else ""}://{config["server"]["rasa_host"]}:{config["server"]["rasa_port"]}/conversations/{sender}/tracker'
    response_tracker = await rasa_session.get(url = url_tracker)
    response_tracker.raise_for_status()
    
    response = response_tracker.json()
    
    try:
        answer = response['slots']['results_data']
        if answer == None:
            answer = dict()
    except KeyError:
        answer = dict()
    try:
        answer['transcription'] = response['latest_message']['text']
    except KeyError:
        answer['transcription'] = ''
    try:
        answer['response'] = response['events'][-2]['text']
    except KeyError:
        answer['response'] = ''
    # pprint(answer)
    return answer
# # @app.post("/audio_converse_download")
# # @app.put("/audio_converse_download")
# # @app.get("/audio_converse_download")
# # async def audio_converse_download( sender : str, request: Request):
# #     '''
# #     This function is used to stream audio from the client to the server. Expecting the audio to be in wav format.
# #     '''
# #     import requests
# #     asr_session = requests.Session()
# #     rasa_session = requests.Session()

# #     async def speech_to_text(request) -> str:
# #        # get the audio file from the request and send it to asr.ai
# #         url_asr_speech_to_text = f'http{"s" if config["server"]["asr_SSL"] else ""}://{config["server"]["asr_host"]}:{config["server"]["asr_port"]}/asr'
# #         asr_request_header_speech_to_text = dict()
# #         #asr_request_header_speech_to_text['Authorization'] = f'Bearer {config["server"]["asr_API"]}'
# #         asr_request_header_speech_to_text['Content-Type'] = 'audio/wav'
# #         data = await request.body()
# #         response_asr_speech_to_text = asr_session.post(url = url_asr_speech_to_text ,data = data ,headers= asr_request_header_speech_to_text)
# #         response_asr_speech_to_text.raise_for_status()
# #         asr_content = response_asr_speech_to_text.content.decode('utf-8').split('\r\n')
# #         try:
# #             response_dict = json.loads(asr_content[-2])
# #         except IndexError:
# #             response_dict = json.loads(asr_content[-1])
# #         return response_dict['text']
    
# #     async def text_to_text( input : str, sender : str) -> str:
# #         # forward the request to rasa server
# #         rasa_body = dict()
# #         rasa_body['sender'] = sender
# #         rasa_body['message'] = input
# #         url_rasa = f'http{"s" if config["server"]["rasa_SSL"] else ""}://{config["server"]["rasa_host"]}:{config["server"]["rasa_port"]}/webhooks/rest/webhook'
# #         rasa_request_header = dict()
# #         rasa_request_header['Content-Type'] = 'application/json'
# #         rasa_body = json.dumps(rasa_body)
# #         response_rasa = rasa_session.post(url = url_rasa ,data = rasa_body,headers=rasa_request_header)
# #         response_rasa.raise_for_status()
# #         # get the tracker slot data
# #         url_tracker = f'http{"s" if config["server"]["rasa_SSL"] else ""}://{config["server"]["rasa_host"]}:{config["server"]["rasa_port"]}/conversations/{sender}/tracker'
# #         response_tracker = rasa_session.get(url = url_tracker)
# #         response_tracker.raise_for_status()
        
# #         response = response_rasa.json()[0]["text"]
# #         return response
    
# #     async def text_to_speech( text : str ) -> bytes:
# #         # get the audio synthetisite from tts.ai
# #         url_tts_text_to_speech = f'http{"s" if config["server"]["tts_SSL"] else ""}://{config["server"]["tts_host"]}:{config["server"]["tts_port"]}/tts'
# #         tts_request_header_text_to_speech = dict()
# #         tts_request_header_text_to_speech['Content-Type'] = 'application/json'
# #         tts_request_header_text_to_speech['Accept'] = 'audio/raw'
# #         tts_request = {
# #                     "text": text,
# #                     }
# #         tts_request_body_text_to_speech = json.dumps(tts_request)
# #         response_tts_text_to_speech = tts_session.post(url = url_tts_text_to_speech ,data = tts_request_body_text_to_speech,headers=tts_request_header_text_to_speech)
# #         return response_tts_text_to_speech.content
    
#     # get the audio file from the request and send it to tts.ai

#     message = await speech_to_text(request)
#     pprint(message)
#     # rasa response
#     response = await text_to_text(message, sender)
#     pprint(response)
#     # synthesise the response
#     audio = await text_to_speech(response)
#     return Response(status_code=200, content=audio, headers={'Content-Type': 'audio/wav'})


@app.post("/audio_converse_stream")
@app.put("/audio_converse_stream")
@app.get("/audio_converse_stream")
async def audio_converse_stream( sender : str, request: Request):
    '''
    This function is used to stream audio from the client to the server. Expecting the audio to be in mp3 format.
    '''
    # get the audio file from the request and send it to tts.ai
    timer = time.time()
    message = await speech_to_text(request)
    timer = time.time() - timer
    pprint (f"speech_to_text: {timer}")
    pprint(message)
    # rasa response
    timer = time.time()
    response = await text_to_text(message, sender)
    timer = time.time() - timer
    pprint (f"text_to_text: {timer}")
    pprint(response)
    # synthesise the response
    return StreamingResponse(text_to_speech(response), media_type="audio/wav") 

@app.get( "/get_tracker" )
async def get_tracker(sender:str, request : Request):
    return await get_tracker_data(sender)
# main entry point
if __name__ == "__main__":
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s [%(name)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    uvicorn.run("__main__:app", host=config['server']['self_host'], port=config['server']['self_port'], reload=True)