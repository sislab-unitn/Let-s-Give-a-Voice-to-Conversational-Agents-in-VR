# KumoVoice server
import os
import sys
import time
from pprint import pprint

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, Response
from uvicorn.config import LOGGING_CONFIG


from config_parser import config_parser
from server_model import ServerModel
from pydantic import BaseModel

config = config_parser(
    sys.argv[1:], current_path=os.path.dirname(os.path.abspath(__file__))
)
server = ServerModel(config)

description = """ This server is the standard communication server that perfoms the following tasks:
                    - ASR transcription
                    - Text to text conversation with the rasa model
                    - TTS synthesis
            """

# start the server
app = FastAPI(description=description)

class TextResponse(BaseModel):
    response: str
    tracker: dict
    class Config:
        schema_extra = {
            "example": {
                "response": "Hey, I'm Kumo, a movie and tv show assistant. I can help you find movies and tv shows to watch. What would you like to do?",
                "tracker" :
                {
                    "transcription" : "Hello",
                    "response" : "Hey, I'm Kumo, a movie and tv show assistant. I can help you find movies and tv shows to watch. What would you like to do?"
                }
            }
        }
class TrackerResponse(BaseModel):
    
    transcription: str
    response: str
    other : dict | None
    class Config:
        schema_extra = {
            "example": {
                "transcription" : "Hello",
                "response" : "Hey, I'm Kumo, a movie and tv show assistant. I can help you find movies and tv shows to watch. What would you like to do?"

            }
        }
class AudioResponse(Response):
    media_type = "audio/raw"

@app.get("/")
def read_root():
    return {
        "Server": "Check the documentation for more info on what API endpoints are available."
    }

@app.get("/text_converse", response_model=TextResponse)
async def text_converse(bot: str,sender:str,message:str):
    """
    Performs 1 step of the conversation using the rasa model.
    - use bot param to specify which bot to use
    - Returns a json object with the response from the rasa model and the tracker data
    """
    # forward the request to rasa server
    # url_rasa = f'http{"s" if config["server"]["rasa_SSL"] else ""}://{config["server"]["rasa_host"]}:{config["server"]["rasa_port"]}/webhooks/rest/webhook'
    # response_rasa = await server.rasa_session.post(url=url_rasa, data=request.stream())
    # response_rasa.raise_for_status()
    response = await server.text_to_text(bot, message, sender)
    # get the tracker slot data
    tracker = await server.get_tracker_data(bot, sender)
    return {"response": response, "tracker": tracker}
@app.post("/text_converse", response_model=TextResponse )
async def text_converse(bot: str, request: Request):
    """
    Performs 1 step of the conversation using the rasa model.
    - use bot param to specify which bot to use
    - Expects a json object with 'sender' and 'message' keys
    - example: 
        ```json
        {
            "sender":"user",
            "message":"hello"
        }
        ```
    - Returns a json object with the response from the rasa model and the tracker data
    """
    # forward the request to rasa server
    # url_rasa = f'http{"s" if config["server"]["rasa_SSL"] else ""}://{config["server"]["rasa_host"]}:{config["server"]["rasa_port"]}/webhooks/rest/webhook'
    # response_rasa = await server.rasa_session.post(url=url_rasa, data=request.stream())
    # response_rasa.raise_for_status()
    response_json = await request.json()
    try:
        text = response_json["message"]
        sender = response_json["sender"]
    except KeyError:
        return {"error": "Invalid request body"}
    response = await server.text_to_text(bot, text, sender)
    # get the tracker slot data
    tracker = await server.get_tracker_data(bot, sender)

    return {"response": response, "tracker": tracker}


@app.post("/audio_converse_stream", response_class=AudioResponse)
async def audio_converse_stream(bot: str, sender: str, request: Request) -> StreamingResponse:
    """
    This function is used to stream audio from the client to the server. Expecting the audio to be in any format supported by the soundfile.read().
    Returns a PCM_16 audio file in streaming format. The file is:
    - `PCM_16`
    - `signed integer 16 bit`
    - `16000Hz` sampling rate
    - `mono` channel
    
    The audio has chunks delimited by 100 16bit zeros of silence that delimit the chunks for punctuation.
    
    """
    # get the audio file from the request and send it to tts.ai
    timer = time.time()
    message = await server.speech_to_text(request)
    timer = time.time() - timer
    pprint(f"speech_to_text: {timer}")
    pprint(message)
    # rasa response
    timer = time.time()
    response = await server.text_to_text(bot, message, sender)
    if response == "":
        response = "Sorry, I didn't understand that."
    timer = time.time() - timer
    pprint(f"text_to_text: {timer}")
    pprint(response)
    # synthesise the response
    speaker = server.bots[bot]['speaker_voice']
    return StreamingResponse(server.text_to_speech(speaker,response), media_type="audio/wav")


@app.get("/get_tracker", response_model=TrackerResponse)
async def get_tracker(bot: str, sender: str, request: Request):
    """
    Get tracker information for a specific sender from the rasa server.
    """
    return await server.get_tracker_data(bot, sender)


# main entry point
if __name__ == "__main__":
    LOGGING_CONFIG["formatters"]["default"][
        "fmt"
    ] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"][
        "fmt"
    ] = '%(asctime)s [%(name)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    uvicorn.run(
        "__main__:app",
        host=config["server"]["self_host"],
        port=config["server"]["self_port"],
        reload=True,
    )
