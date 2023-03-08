from fastapi import Depends, FastAPI, Request, Response, status 
from fastapi.responses import StreamingResponse
import uvicorn
from uvicorn.config import LOGGING_CONFIG
import soundfile as sf
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_parser import config_parser
from tts_model import TTSModel

config = config_parser(sys.argv[1:], current_path = os.path.dirname(os.path.abspath(__file__)))
tts_model = TTSModel(config)

app = FastAPI()

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
    voice = tts_model.tts_synthesis_chunked(text)
    return StreamingResponse(status_code=status.HTTP_200_OK, content = voice, media_type="audio/raw")

@app.get("/tts_synthesis")
async def tts_test(text : str):
    voice = tts_model.tts_synthesis_chunked(text)
    return StreamingResponse(status_code=status.HTTP_200_OK, content = voice, media_type="audio/raw")

# main entry point
if __name__ == "__main__":
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s [%(name)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    uvicorn.run("__main__:app", host=config['server']['self_host'], port=config['server']['self_port'], reload=True)