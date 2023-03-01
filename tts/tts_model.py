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
import time
import speechbrain
import torch
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
import io
import soundfile as sf
import json
import re

parser = argparse.ArgumentParser(
                    prog = 'TTS Server',
                    description = 'Server for Speech Synthesis',
                    epilog = 'Enjoy the program! :)')       # positional argument
parser.add_argument('-c', '--config',required=False)      # option that takes a value
# parser.add_argument('-d','--device',required=False)
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
pprint(config_path)
# read config file
with open(config_path,mode='r') as f:
    config = tomllib.loads(f.read())
        

device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")

# load xvector containing speaker's voice characteristics from a dataset
embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)
    
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

# processor = torch.compile(processor)
# model = torch.compile(model)
# vocoder = torch.compile(vocoder)

print (f"Running on device: {model.device}")
app = FastAPI()

# streaming for tts synthesis in chunks
async def tts_synthesis_chunked(data : str)-> AsyncGenerator:
    io_buffer = io.BytesIO()
    lines = re.split(r';|,|\*|\n|\\|\/|\?|\.|\=|\+|\!|\:|\"', data)
    for line in lines:
        if line != '':
            timer = time.time()
            inputs = processor(text=line, return_tensors="pt")
            speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)
            # current position in the file
            cursor = io_buffer.tell()
            # print(cursor)
            sf.write(io_buffer, speech.numpy(), samplerate=16000,subtype="PCM_16",format = "RAW")
            end = io_buffer.tell()
            # print (end)
            io_buffer.seek(cursor)
            timer = time.time() - timer
            pprint (f"Time taken for inference: {timer}")
            yield io_buffer.read((end - cursor))
        # do something with the chunk

async def tts_synthesis(data : str)-> AsyncGenerator:
    io_buffer = io.BytesIO()
    inputs = processor(text=data, return_tensors="pt")
    speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)
    sf.write(io_buffer, speech.numpy(), samplerate=16000,subtype="PCM_16",format = "WAV")
    return io_buffer.getbuffer()

@app.get("/")
def read_root():
    return {"TTS Server": "This is the TTS model used. Check the documentation for more info. Link to the pretrained model on 🤗 https://huggingface.co/microsoft/speecht5_tts "}

@app.post("/tts")
async def tts(request : Request):
    data = await request.json()
    # if body is empty
    if data == b'':
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content="Empty request body")
    # perfom the inference
    text = data['text']
    print(text)
    voice = tts_synthesis_chunked(text)
    return StreamingResponse(status_code=status.HTTP_200_OK, content = voice, media_type="audio/raw")

@app.get("/tts_test")
async def tts_test(text : str):
    voice = tts_synthesis_chunked(text)
    return StreamingResponse(status_code=status.HTTP_200_OK, content = voice, media_type="audio/raw")

# main entry point
if __name__ == "__main__":
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s [%(name)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    uvicorn.run("__main__:app", host=config['server']['self_host'], port=config['server']['self_port'], reload=True)