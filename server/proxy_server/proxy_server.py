import os
import sys
import time

import uvicorn
import tomllib
import torch
import datetime

from pprint import pprint

from fastapi import FastAPI, Request, status
from fastapi.responses import StreamingResponse, Response
from uvicorn.config import LOGGING_CONFIG

from proxy_model import ProxyModel
from pydantic import BaseModel

from transformers import BertTokenizerFast, BertForTokenClassification, pipeline


description = """ This server is the standard communication server that perfoms the following tasks:
                    - ASR transcription
                    - Text to text conversation with the rasa model
                    - TTS synthesis
            """

# start the server
app = FastAPI(description=description)


data = {}

@app.on_event('startup')
def init_data():
    with open('config.toml', "rb") as f:
        config = tomllib.load(f)

    data['server'] = ProxyModel(config)

    device = config["settings"]["device"]
    ner_tok = BertTokenizerFast.from_pretrained("osiria/bert-italian-uncased-ner")
    ner_model = BertForTokenClassification.from_pretrained("osiria/bert-italian-uncased-ner").to(device)

    ner = pipeline("ner", model=ner_model, tokenizer=ner_tok, aggregation_strategy="first", device=device)

    data['ner'] = ner
    # data['device'] = device
    
    return data


class TextResponse(BaseModel):
    response: str


class AudioResponse(Response):
    media_type = "audio/raw"


@app.get("/")
def read_root():
    return {
        "Server": "Check the documentation for more info on what API endpoints are available."
    }


@app.post("/start_scripted", response_class=AudioResponse)
async def pipe(request: Request) -> StreamingResponse:
    start_time = time.time()
    agent_response = await data['server'].text_to_text("/start")
    print("--- %s seconds ---" % (time.time() - start_time))

    print(agent_response)
    print("REQUEST end: ", datetime.datetime.now())
    print("**********")

    return StreamingResponse(data['server'].text_to_speech_chunked(agent_response['model_out']), media_type="audio/wav")


@app.post("/pipeline", response_class=AudioResponse)
async def pipe(request: Request) -> StreamingResponse:
    start_time = time.time()
    print("REQUEST START: ", datetime.datetime.now())
    user_input = await data['server'].speech_to_text(request)
    print("--- %s seconds ---" % (time.time() - start_time))

    print(user_input)

    start_time = time.time()
    agent_response = await data['server'].text_to_text(user_input)
    print("--- %s seconds ---" % (time.time() - start_time))

    print(agent_response)
    print("REQUEST end: ", datetime.datetime.now())
    print("**********")

    return StreamingResponse(data['server'].text_to_speech_chunked(agent_response['model_out']), media_type="audio/wav")


@app.post("/asr", response_class=TextResponse)
async def asr(request: Request):    
    text = await data['server'].speech_to_text(request)

    return Response(
        status_code=status.HTTP_200_OK,
        content=json.dumps({"response": text}),
        media_type="application/json",
    )

@app.post("/tts", response_class=AudioResponse)
async def tts(request: Request):
    request_data = await request.json()

    speech = await data['server'].text_to_speech(request_data['text'])

    return Response(status_code=status.HTTP_200_OK, content=speech.content, media_type="audio/wav")


@app.post("/ner", response_class=AudioResponse)
async def name_recognition(request: Request):
    text = await data['server'].speech_to_text(request)

    detected_names = data['ner'](text.lower())
    name = [n['word'] for n in detected_names if n['entity_group']=='PER']

    if name:
        resp = "Piacere di conoscerti, {}".format(name[0])
    else:
        resp = "Piacere di conoscerti"

    speech = await data['server'].text_to_speech(resp)

    return Response(status_code=status.HTTP_200_OK, content=speech.content, media_type="audio/wav")


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
