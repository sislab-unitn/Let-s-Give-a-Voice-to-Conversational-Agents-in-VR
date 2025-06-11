import os
import sys
import tomllib
import time

import soundfile as sf
import uvicorn
from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from tts_model import TTSModel


global tts_model

description = """ This server is the standard TTS server that perfoms the speech synthesis from text. """
app = FastAPI(description=description)


data = {}

@app.on_event('startup')
def init_data():
    with open('config.toml', "rb") as f:
        config = tomllib.load(f)

    tts_model = TTSModel(config)
    data['tts_model'] = tts_model
    
    return data



class AudioResponseChunked(Response):
    media_type = "audio/raw"

class AudioResponse(Response):
    media_type = "audio/wav"

@app.get("/")
def read_root():
    return {
        "TTS Server": "This server is the standard TTS server that perfoms the speech synthesis from text. "
    }


@app.post("/tts", response_class=AudioResponseChunked)
async def tts(request: Request):
    """
    Performs the inference on the TTS model from a POST request
    - the request body should be a JSON object with the key "text" and the value being the text to be synthesized
    
    Returns a PCM_16 audio file in streaming format. The file is:
    - `PCM_16`
    - `signed integer 16 bit`
    - `16000Hz` sampling rate
    - `mono` channel
    
    The audio has chunks delimited by 100 16bit zeros of silence that delimit the chunks for punctuation.
    
    """
    body = await request.json()
    # if body is empty
    if body == b"":
        return Response(
            status_code=status.HTTP_400_BAD_REQUEST, content="Empty request body"
        )
    # perfom the inference
    text = body["text"]
    start_time = time.time()
    voice = data['tts_model'].tts_synthesis_chunked(text)
    print("--- %s seconds ---" % (time.time() - start_time))
    
    return StreamingResponse(
        status_code=status.HTTP_200_OK, content=voice, media_type="audio/raw"
    )


@app.get("/tts_synthesis", response_class=AudioResponseChunked)
async def tts_synthesis(text: str):
    """
    Performs the inference on the TTS model from a GET request
    - the text encoded in the url is the text to be synthesized
    
    Returns a PCM_16 audio file in streaming format. The file is:
    - `PCM_16`
    - `signed integer 16 bit`
    - `24000Hz` sampling rate
    - `mono` channel
    
    The audio has chunks delimited by 100 16bit zeros of silence that delimit the chunks for punctuation.
    
    """
    voice = data['tts_model'].tts_synthesis_chunked(text)
    return StreamingResponse(
        status_code=status.HTTP_200_OK, content=voice, media_type="audio/raw"
    )


@app.get("/tts_synthesis_full", response_class=AudioResponse)
async def tts_synthesis(text: str):
    """
    Performs the inference on the TTS model from a GET request
    - the text encoded in the url is the text to be synthesized
    Returns a PCM_16 audio file in streaming format. The file is:
    - `PCM_16`
    - `signed integer 16 bit`
    - `24000Hz` sampling rate
    - `mono` channel
    
    """
    voice = await data['tts_model'].tts_synthesis(text)
    return Response(status_code=status.HTTP_200_OK, content=voice, media_type="audio/wav")


if __name__ == "__main__":
    with open('config.toml', "rb") as f:
        config = tomllib.load(f)

    uvicorn.run(
        "__main__:app",
        host=config["server"]["self_host"],
        port=config["server"]["self_port"],
        reload=True,
        workers=4
    )

