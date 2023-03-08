from fastapi import  FastAPI, Request, Response, status 
import uvicorn
from uvicorn.config import LOGGING_CONFIG
import sys
import os
import json


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_parser import config_parser
from asr_model import ASRModel

config = config_parser(sys.argv[1:],current_path = os.path.dirname(os.path.abspath(__file__)))
asr_model = ASRModel(config)

app = FastAPI()


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
    text = asr_model.asr_dictation(data)
    print(text)
    body = {'is_final' : True,
            'text' : text }
    
    return Response(status_code=status.HTTP_200_OK, content= json.dumps(body), media_type="application/json")

# main entry point
if __name__ == "__main__":
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s [%(name)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    uvicorn.run("__main__:app", host=config['server']['self_host'], port=config['server']['self_port'], reload=True)