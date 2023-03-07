from typing import Generator, AsyncGenerator, Iterable
from fastapi import FastAPI
from fastapi import Depends, FastAPI, Request, Response, status 
from fastapi.responses import StreamingResponse
import uvicorn
from uvicorn.config import LOGGING_CONFIG
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
import torch
from speechbrain.pretrained import EncoderDecoderASR
import io
import soundfile as sf
import json

parser = argparse.ArgumentParser(
                    prog = 'ASR Server',
                    description = 'Server for Automatic Speech Recognition',
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
pprint(config_path)
# read config file
with open(config_path,mode='r') as f:
    config = tomllib.loads(f.read())
        

device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
model = EncoderDecoderASR.from_hparams(source="speechbrain/asr-wav2vec2-commonvoice-en", savedir="pretrained_models/asr-wav2vec2-commonvoice-en",run_opts={"device":'cpu'})
# model = torch.compile(model)
print (f"Running on device: {model.device}")
app = FastAPI()


def asr_dictation(data : bytes)-> str:
    waveform, samplerate = sf.read(file=io.BytesIO(data), dtype='float32')
    waveform = torch.tensor(waveform)
    waveform = model.audio_normalizer(waveform, samplerate)
    batch = waveform.unsqueeze(0)
    rel_length = torch.tensor([1.0])
    predicted_words, _ = model.transcribe_batch(batch, rel_length)
    return predicted_words[0].lower()


@app.get("/")
def read_root():
    return {"ASR Server": "This is the ASR model used. Check the documentation for more info. Link to the pretrained model on 🤗 https://huggingface.co/speechbrain/asr-wav2vec2-commonvoice-en "}

@app.post("/asr")
async def asr(request : Request):
    data = await request.body()
    # if body is empty
    if data == b'':
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content="Empty request body")
    # perfom the inference
    text = asr_dictation(data)
    print (text)
    body = {'is_final' : True,
            'text' : text }
    
    return Response(status_code=status.HTTP_200_OK, content= json.dumps(body), media_type="application/json")

# main entry point
if __name__ == "__main__":
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s [%(name)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    uvicorn.run("__main__:app", host=config['server']['self_host'], port=config['server']['self_port'], reload=True)