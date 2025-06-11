import json
import os
import sys
import tomllib

import uvicorn
from fastapi import FastAPI, Request, Response, status
from pydantic import BaseModel
from uvicorn.config import LOGGING_CONFIG

from asr_model import ASRModel


description = """ This is the ASR model used. Check the documentation for more info. """
app = FastAPI(description=description)


data = {}

@app.on_event('startup')
def init_data():
    data['asr_model'] = ASRModel()
    
    return data


class ASRResponse(BaseModel):
    text: str
    is_final: bool
    class Config:
        schema_extra = {
            "example": {
                "text" : "Hello",
                "is_final" : True
            }
        }

@app.get("/")
def read_root():
    return {
        "ASR Server": "This is the ASR model used. Check the documentation for more info. "
    }


@app.post("/asr", response_model=ASRResponse)
async def asr(request: Request):
    """
    Performs the inference on the ASR model from a POST request
    - the request body should be an audio file. Any soundfile accepted by soundfile.read() SHOULD supported
    - response is a JSON object with the key "text" as the transcription of the audio file. It also has the key "is_final" which is always True
    """
    print("here")
    body = await request.body()
    print("data")
    # if body is empty
    if body == b"":
        return Response(
            status_code=status.HTTP_400_BAD_REQUEST, content="Empty request body"
        )
    # perfom the inference
    text = data['asr_model'].asr_dictation(body)
    print(text)
    body = {"is_final": True, "text": text}

    return Response(
        status_code=status.HTTP_200_OK,
        content=json.dumps(body),
        media_type="application/json",
    )


# main entry point
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
