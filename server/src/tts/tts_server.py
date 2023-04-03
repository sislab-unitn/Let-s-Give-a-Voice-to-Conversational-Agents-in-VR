import os
import sys

import soundfile as sf
import uvicorn
from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.responses import StreamingResponse
from uvicorn.config import LOGGING_CONFIG

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))
from src.config_parser import config_parser
from src.tts.tts_model import TTSModel

config = config_parser(
    sys.argv[1:], current_path=os.path.dirname(os.path.abspath(__file__))
)
tts_model = TTSModel(config)

app = FastAPI()


@app.get("/")
def read_root():
    return {
        "TTS Server": "This is the TTS model used. Check the documentation for more info. Link to the pretrained model on 🤗 https://huggingface.co/microsoft/speecht5_tts "
    }


@app.post("/tts")
async def tts(speaker:str,request: Request):
    """
    Performs the inference on the TTS model from a POST request
    - the request body should be a JSON object with the key "text" and the value being the text to be synthesized
    - response is a PCM_16 audio file
    """
    if speaker not in tts_model.speaker_embeddings.keys():
        return Response(
            status_code=status.HTTP_400_BAD_REQUEST, content="Speaker not available"
        )
    data = await request.json()
    # if body is empty
    if data == b"":
        return Response(
            status_code=status.HTTP_400_BAD_REQUEST, content="Empty request body"
        )
    # perfom the inference
    text = data["text"]
    print(text)
    voice = tts_model.tts_synthesis_chunked(speaker,text)
    return StreamingResponse(
        status_code=status.HTTP_200_OK, content=voice, media_type="audio/raw"
    )


@app.get("/tts_synthesis")
async def tts_synthesis(speaker:str,text: str):
    """
    Performs the inference on the TTS model from a GET request
    - the text encoded in the url is the text to be synthesized
    - response is a PCM_16 audio file
    """
    if speaker not in tts_model.speaker_embeddings.keys():
        return Response(
            status_code=status.HTTP_400_BAD_REQUEST, content="Speaker not available"
        )
    voice = tts_model.tts_synthesis_chunked(speaker,text)
    return StreamingResponse(
        status_code=status.HTTP_200_OK, content=voice, media_type="audio/raw"
    )
@app.get("/tts_synthesis_full")
async def tts_synthesis(speaker:str,text: str):
    """
    Performs the inference on the TTS model from a GET request
    - the text encoded in the url is the text to be synthesized
    - response is a PCM_16 audio file
    """
    if speaker not in tts_model.speaker_embeddings.keys():
        return Response(
            status_code=status.HTTP_400_BAD_REQUEST, content="Speaker not available"
        )
    voice = await tts_model.tts_synthesis(speaker,text)
    return Response(status_code=status.HTTP_200_OK, content=voice, media_type="audio/raw")
@app.get("/tts_speakers")
async def tts_speakers():
    """
    Returns a list of available speakers
    """
    speakers = await tts_model.speakers_available()
    return speakers

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
