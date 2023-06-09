import json
import os
import sys

import uvicorn
from fastapi import FastAPI, Request, Response, status
from pydantic import BaseModel
from uvicorn.config import LOGGING_CONFIG

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))
print (sys.path)
import src
from src.config_parser import config_parser
from src.asr.asr_model import ASRModel

config = config_parser(
    sys.argv[1:], current_path=os.path.dirname(os.path.abspath(__file__))
)
asr_model = ASRModel(config)

description = """ This is the ASR model used. Check the documentation for more info. Link to the pretrained model on 🤗 https://huggingface.co/speechbrain/asr-wav2vec2-commonvoice-en """
app = FastAPI(description=description)

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
        "ASR Server": "This is the ASR model used. Check the documentation for more info. Link to the pretrained model on 🤗 https://huggingface.co/speechbrain/asr-wav2vec2-commonvoice-en "
    }


@app.post("/asr", response_model=ASRResponse)
async def asr(request: Request):
    """
    Performs the inference on the ASR model from a POST request
    - the request body should be an audio file. Any soundfile accepted by soundfile.read() SHOULD supported
    - response is a JSON object with the key "text" as the transcription of the audio file. It also has the key "is_final" which is always True
    """
    data = await request.body()
    # if body is empty
    if data == b"":
        return Response(
            status_code=status.HTTP_400_BAD_REQUEST, content="Empty request body"
        )
    # perfom the inference
    text = asr_model.asr_dictation(data)
    print(text)
    body = {"is_final": True, "text": text}

    return Response(
        status_code=status.HTTP_200_OK,
        content=json.dumps(body),
        media_type="application/json",
    )


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
