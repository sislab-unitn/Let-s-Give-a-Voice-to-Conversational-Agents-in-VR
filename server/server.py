# KumoVoice server
from fastapi import  FastAPI, Request
from fastapi.responses import StreamingResponse
import uvicorn
from uvicorn.config import LOGGING_CONFIG
import sys
from pprint import pprint
import time

from config_parser import config_parser
from server_model import ServerModel

config = config_parser(sys.argv[1:])
server = ServerModel(config)



# start the server
app = FastAPI()


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
    response_rasa = await server.rasa_session.post(url = url_rasa ,data = request.stream())
    response_rasa.raise_for_status()
    # get the tracker slot data
    url_tracker = f'http{"s" if config["server"]["rasa_SSL"] else ""}://{config["server"]["rasa_host"]}:{config["server"]["rasa_port"]}/conversations/{request.stream()}/tracker'
    response_tracker = await server.rasa_session.get(url = url_tracker)
    response_tracker.raise_for_status()
    try:
        response = [response_rasa.json()[0], response_tracker.json()]
    except IndexError:
        response = [response_rasa.json(), response_tracker.json()]
    return response


@app.post("/audio_converse_stream")
async def audio_converse_stream( sender : str, request: Request):
    '''
    This function is used to stream audio from the client to the server. Expecting the audio to be in mp3 format.
    '''
    # get the audio file from the request and send it to tts.ai
    timer = time.time()
    message = await server.speech_to_text(request)
    timer = time.time() - timer
    pprint (f"speech_to_text: {timer}")
    pprint(message)
    # rasa response
    timer = time.time()
    response = await server.text_to_text(message, sender)
    timer = time.time() - timer
    pprint (f"text_to_text: {timer}")
    pprint(response)
    # synthesise the response
    return StreamingResponse(server.text_to_speech(response), media_type="audio/wav") 

@app.get( "/get_tracker" )
async def get_tracker(sender:str, request : Request):
    return await server.get_tracker_data(sender)
# main entry point
if __name__ == "__main__":
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s [%(name)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    uvicorn.run("__main__:app", host=config['server']['self_host'], port=config['server']['self_port'], reload=True)